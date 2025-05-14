#!/usr/bin/env python3
"""
DEA Research Tool - A tool to fetch and analyze Dielectric Elastomer Actuator research papers

This tool can:
1. Fetch papers from scientific repositories like Nature, arXiv, etc.
2. Extract key information from the papers
3. Organize and present findings in a structured format
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import os
import argparse
import time
from datetime import datetime
import pandas as pd
from urllib.parse import urlparse
from typing import Dict, List, Tuple, Optional, Any


class DEAResearchTool:
    """Main class for the DEA Research Tool"""
    
    def __init__(self, output_dir: str = "dea_research_output"):
        """Initialize the DEA Research Tool
        
        Args:
            output_dir: Directory to save output files
        """
        self.output_dir = output_dir
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def fetch_nature_paper(self, url: str) -> Dict[str, Any]:
        """Fetch paper from Nature
        
        Args:
            url: URL of the Nature paper
            
        Returns:
            Dictionary containing paper information
        """
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract paper information
            title = soup.find('h1').text.strip() if soup.find('h1') else "Title not found"
            
            # Extract authors
            authors_section = soup.find('ul', class_='c-article-author-list')
            authors = []
            if authors_section:
                author_items = authors_section.find_all('li')
                for author_item in author_items:
                    author_name = author_item.find('a')
                    if author_name:
                        authors.append(author_name.text.strip())
            
            # Extract abstract
            abstract_section = soup.find('div', {'id': 'Abs1-content'}) or soup.find('section', {'id': 'abstract'})
            abstract = abstract_section.text.strip() if abstract_section else "Abstract not found"
            
            # Extract publication date
            pub_date_elem = soup.find('time')
            pub_date = pub_date_elem.text.strip() if pub_date_elem else "Publication date not found"
            
            # Extract DOI
            doi_elem = soup.find('a', {'data-track-action': 'view doi'})
            doi = doi_elem.text.strip() if doi_elem else "DOI not found"
            
            return {
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "publication_date": pub_date,
                "doi": doi,
                "url": url,
                "source": "Nature"
            }
            
        except Exception as e:
            print(f"Error fetching paper from {url}: {e}")
            return {
                "title": "Error fetching paper",
                "url": url,
                "error": str(e)
            }
    
    def fetch_arxiv_paper(self, url: str) -> Dict[str, Any]:
        """Fetch paper from arXiv
        
        Args:
            url: URL of the arXiv paper
            
        Returns:
            Dictionary containing paper information
        """
        try:
            # Extract arXiv ID from URL
            arxiv_id = url.split('/')[-1]
            api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
            
            response = requests.get(api_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'xml')
            
            # Extract paper information
            entry = soup.find('entry')
            
            title = entry.find('title').text.strip()
            
            authors = []
            for author in entry.find_all('author'):
                name = author.find('name').text.strip()
                authors.append(name)
            
            abstract = entry.find('summary').text.strip()
            pub_date = entry.find('published').text.strip()
            
            return {
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "publication_date": pub_date,
                "url": url,
                "source": "arXiv"
            }
            
        except Exception as e:
            print(f"Error fetching paper from {url}: {e}")
            return {
                "title": "Error fetching paper",
                "url": url,
                "error": str(e)
            }
    
    def fetch_pubmed_paper(self, url: str) -> Dict[str, Any]:
        """Fetch paper from PubMed Central
        
        Args:
            url: URL of the PubMed Central paper
            
        Returns:
            Dictionary containing paper information
        """
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title and authors using hgroup h1
            hgroup = soup.find('hgroup')
            title = ""
            authors = []
            
            if hgroup:
                h1 = hgroup.find('h1')
                if h1:
                    title = h1.text.strip()
                
                # Find author elements
                author_elements = soup.find_all('div', class_='contrib-group')
                for author_group in author_elements:
                    author_names = author_group.find_all('a', class_='author-name')
                    for author in author_names:
                        authors.append(author.text.strip())
            
            # Extract abstract
            abstract_section = soup.find('div', class_='abstract')
            abstract = abstract_section.text.strip() if abstract_section else "Abstract not found"
            
            # Extract publication date
            pub_date_elem = soup.find('time')
            pub_date = pub_date_elem.text.strip() if pub_date_elem else "Publication date not found"
            
            return {
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "publication_date": pub_date,
                "url": url,
                "source": "PubMed Central"
            }
            
        except Exception as e:
            print(f"Error fetching paper from {url}: {e}")
            return {
                "title": "Error fetching paper",
                "url": url,
                "error": str(e)
            }
    
    def fetch_paper(self, url: str) -> Dict[str, Any]:
        """Fetch paper from URL
        
        Args:
            url: URL of the paper
            
        Returns:
            Dictionary containing paper information
        """
        domain = urlparse(url).netloc
        
        if "nature.com" in domain:
            return self.fetch_nature_paper(url)
        elif "arxiv.org" in domain:
            return self.fetch_arxiv_paper(url)
        elif "ncbi.nlm.nih.gov" in domain:
            return self.fetch_pubmed_paper(url)
        else:
            return {
                "title": "Unsupported source",
                "url": url,
                "error": f"Source {domain} is not supported yet"
            }
    
    def search_papers(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for papers using a query
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of dictionaries containing paper information
        """
        # This is a simplified implementation
        # In a real-world scenario, you would use APIs from different sources
        
        results = []
        
        # Search Nature
        try:
            nature_search_url = f"https://www.nature.com/search?q={query}&order=relevance&journal="
            response = requests.get(nature_search_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.find_all('article')
            
            for article in articles[:max_results]:
                title_elem = article.find('h3')
                link_elem = article.find('a', {'data-track-action': 'view article'})
                
                if title_elem and link_elem:
                    title = title_elem.text.strip()
                    link = "https://www.nature.com" + link_elem['href']
                    
                    results.append({
                        "title": title,
                        "url": link,
                        "source": "Nature"
                    })
        except Exception as e:
            print(f"Error searching Nature: {e}")
        
        return results
    
    def extract_key_info(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key information from paper
        
        Args:
            paper: Dictionary containing paper information
            
        Returns:
            Dictionary with extracted key information
        """
        # This is a simplified implementation
        # In a real-world scenario, you would use NLP techniques for better extraction
        
        key_info = {
            "dea_type": [],
            "materials": [],
            "performance_metrics": {
                "strain": None,
                "energy_density": None,
                "response_time": None
            },
            "applications": []
        }
        
        # Extract DEA type
        dea_types = ["dielectric elastomer actuator", "DEA", "dielectric elastomer"]
        for dea_type in dea_types:
            if dea_type.lower() in paper.get("abstract", "").lower():
                key_info["dea_type"].append(dea_type)
        
        # Extract materials
        materials = ["silicone", "acrylic", "polyurethane", "VHB", "PDMS"]
        for material in materials:
            if material.lower() in paper.get("abstract", "").lower():
                key_info["materials"].append(material)
        
        # Extract performance metrics
        abstract = paper.get("abstract", "").lower()
        
        # Extract strain
        strain_pattern = r'(\d+\.?\d*)%\s*(?:strain|area\s*strain)'
        strain_matches = re.findall(strain_pattern, abstract)
        if strain_matches:
            key_info["performance_metrics"]["strain"] = f"{strain_matches[0]}%"
        
        # Extract energy density
        energy_pattern = r'(\d+\.?\d*)\s*(?:j/kg|joule/kg|j\s*kg-1)'
        energy_matches = re.findall(energy_pattern, abstract)
        if energy_matches:
            key_info["performance_metrics"]["energy_density"] = f"{energy_matches[0]} J/kg"
        
        # Extract applications
        applications = ["soft robot", "wearable", "haptic", "sensor", "energy harvesting"]
        for app in applications:
            if app.lower() in abstract:
                key_info["applications"].append(app)
        
        return key_info
    
    def save_to_json(self, data: List[Dict[str, Any]], filename: str) -> None:
        """Save data to JSON file
        
        Args:
            data: Data to save
            filename: Name of the file
        """
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Data saved to {filepath}")
    
    def save_to_csv(self, data: List[Dict[str, Any]], filename: str) -> None:
        """Save data to CSV file
        
        Args:
            data: Data to save
            filename: Name of the file
        """
        # Flatten nested dictionaries
        flattened_data = []
        for item in data:
            flat_item = {}
            for key, value in item.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        flat_item[f"{key}_{sub_key}"] = sub_value
                else:
                    flat_item[key] = value
            flattened_data.append(flat_item)
        
        df = pd.DataFrame(flattened_data)
        filepath = os.path.join(self.output_dir, filename)
        df.to_csv(filepath, index=False)
        
        print(f"Data saved to {filepath}")
    
    def generate_report(self, papers: List[Dict[str, Any]]) -> str:
        """Generate a report from the papers
        
        Args:
            papers: List of papers
            
        Returns:
            Report as a string
        """
        report = "# DEA Research Report\n\n"
        report += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += f"Total papers analyzed: {len(papers)}\n\n"
        
        # Summary of papers by source
        sources = {}
        for paper in papers:
            source = paper.get("source", "Unknown")
            sources[source] = sources.get(source, 0) + 1
        
        report += "## Sources\n\n"
        for source, count in sources.items():
            report += f"- {source}: {count} papers\n"
        report += "\n"
        
        # Summary of DEA types
        dea_types = {}
        for paper in papers:
            key_info = paper.get("key_info", {})
            for dea_type in key_info.get("dea_type", []):
                dea_types[dea_type] = dea_types.get(dea_type, 0) + 1
        
        report += "## DEA Types\n\n"
        for dea_type, count in dea_types.items():
            report += f"- {dea_type}: {count} papers\n"
        report += "\n"
        
        # Summary of materials
        materials = {}
        for paper in papers:
            key_info = paper.get("key_info", {})
            for material in key_info.get("materials", []):
                materials[material] = materials.get(material, 0) + 1
        
        report += "## Materials\n\n"
        for material, count in materials.items():
            report += f"- {material}: {count} papers\n"
        report += "\n"
        
        # Summary of applications
        applications = {}
        for paper in papers:
            key_info = paper.get("key_info", {})
            for app in key_info.get("applications", []):
                applications[app] = applications.get(app, 0) + 1
        
        report += "## Applications\n\n"
        for app, count in applications.items():
            report += f"- {app}: {count} papers\n"
        report += "\n"
        
        # List of papers
        report += "## Papers\n\n"
        for i, paper in enumerate(papers, 1):
            report += f"### {i}. {paper.get('title', 'No title')}\n\n"
            report += f"- **Source**: {paper.get('source', 'Unknown')}\n"
            report += f"- **URL**: {paper.get('url', 'No URL')}\n"
            report += f"- **Authors**: {', '.join(paper.get('authors', ['Unknown']))}\n"
            report += f"- **Publication Date**: {paper.get('publication_date', 'Unknown')}\n"
            
            key_info = paper.get("key_info", {})
            report += f"- **DEA Types**: {', '.join(key_info.get('dea_type', ['Not specified']))}\n"
            report += f"- **Materials**: {', '.join(key_info.get('materials', ['Not specified']))}\n"
            
            performance = key_info.get("performance_metrics", {})
            report += "- **Performance Metrics**:\n"
            report += f"  - Strain: {performance.get('strain', 'Not specified')}\n"
            report += f"  - Energy Density: {performance.get('energy_density', 'Not specified')}\n"
            report += f"  - Response Time: {performance.get('response_time', 'Not specified')}\n"
            
            report += f"- **Applications**: {', '.join(key_info.get('applications', ['Not specified']))}\n"
            report += "\n"
        
        return report
    
    def process_papers(self, urls: List[str]) -> None:
        """Process papers from URLs
        
        Args:
            urls: List of paper URLs
        """
        papers = []
        
        for url in urls:
            print(f"Processing {url}...")
            paper = self.fetch_paper(url)
            
            if "error" not in paper:
                key_info = self.extract_key_info(paper)
                paper["key_info"] = key_info
            
            papers.append(paper)
            
            # Be nice to the servers
            time.sleep(1)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.save_to_json(papers, f"dea_papers_{timestamp}.json")
        self.save_to_csv(papers, f"dea_papers_{timestamp}.csv")
        
        # Generate report
        report = self.generate_report(papers)
        report_path = os.path.join(self.output_dir, f"dea_report_{timestamp}.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"Report generated: {report_path}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='DEA Research Tool - Fetch and analyze DEA research papers')
    parser.add_argument('--urls', nargs='+', help='URLs of papers to process')
    parser.add_argument('--search', type=str, help='Search query')
    parser.add_argument('--max-results', type=int, default=10, help='Maximum number of search results')
    parser.add_argument('--output-dir', type=str, default='dea_research_output', help='Output directory')
    
    args = parser.parse_args()
    
    tool = DEAResearchTool(output_dir=args.output_dir)
    
    if args.urls:
        tool.process_papers(args.urls)
    elif args.search:
        print(f"Searching for '{args.search}'...")
        results = tool.search_papers(args.search, max_results=args.max_results)
        
        if results:
            print(f"Found {len(results)} results")
            urls = [result["url"] for result in results]
            tool.process_papers(urls)
        else:
            print("No results found")
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 