from flask import Flask, render_template, request, jsonify, make_response
from threading import Thread, Event
import time
import requests
import csv
from io import StringIO
from dea_research_tool import DEAResearchTool

app = Flask(__name__)
search_thread = None
stop_event = Event()
results = []

def search_worker(query, max_results):
    """Worker function to search for research papers"""
    global results
    
    # Clear previous results
    results.clear()
    max_results = min(int(max_results), 1000)
    
    # Initialize research tool
    tool = DEAResearchTool(output_dir="web_output")
    found = 0
    
    # Step 1: Search Nature papers
    try:
        for paper in tool.search_papers(query, max_results=max_results):
            if stop_event.is_set() or found >= max_results:
                break
                
            results.append({
                "title": paper["title"],
                "authors": paper.get("authors", []),
                "url": paper["url"]
            })
            found += 1
            time.sleep(0.3)  # Reduced delay for better responsiveness
    except Exception as e:
        print(f"Error searching Nature papers: {e}")
    
    # Step 2: Search PubMed Central
    if not stop_event.is_set() and found < max_results:
        try:
            pmc_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term={query}&retmax={max_results}&retmode=json"
            response = requests.get(pmc_url)
            response.raise_for_status()
            
            data = response.json()
            pmc_ids = data.get('esearchresult', {}).get('idlist', [])
            
            for pmc_id in pmc_ids[:max_results-found]:  # Only process what we need
                if stop_event.is_set() or found >= max_results:
                    break
                    
                url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmc_id}/"
                paper = tool.fetch_pubmed_paper(url)
                
                if "error" not in paper:
                    results.append({
                        "title": paper["title"],
                        "authors": paper.get("authors", []),
                        "url": url
                    })
                    found += 1
                    time.sleep(0.3)
        except Exception as e:
            print(f"Error searching PubMed Central: {e}")
    
    print(f"Search completed. Found {found} papers.")

@app.route("/")
def index():
    """Render the main page"""
    return render_template("pager.html")

@app.route("/start", methods=["POST"])
def start():
    """Start the search process"""
    global search_thread, stop_event
    
    # Get search parameters
    query = request.json.get("query", "dielectric elastomer actuator")
    max_results = int(request.json.get("max_results", 100))
    
    # Reset search state
    stop_event.clear()
    
    # Start search in a new thread
    search_thread = Thread(target=search_worker, args=(query, max_results))
    search_thread.daemon = True  # Thread will exit when main thread exits
    search_thread.start()
    
    return "Started"

@app.route("/stop", methods=["POST"])
def stop():
    """Stop the search process"""
    stop_event.set()
    return "Stopped"

@app.route("/results")
def get_results():
    """Get the current results"""
    return jsonify(results)

@app.route("/export_csv")
def export_csv():
    """Export results to CSV"""
    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Title', 'Authors', 'URL'])
    
    # Write data
    for paper in results:
        authors = ', '.join(paper.get('authors', []))
        writer.writerow([paper['title'], authors, paper['url']])
    
    # Create response
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=dea_papers.csv"
    response.headers["Content-type"] = "text/csv"
    
    return response

if __name__ == "__main__":
    app.run(debug=True, port=5001) 