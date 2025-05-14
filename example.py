#!/usr/bin/env python3
"""
Example script demonstrating how to use the DEA Research Tool programmatically
"""

from dea_research_tool import DEAResearchTool

def main():
    # Initialize the tool
    tool = DEAResearchTool(output_dir="example_output")
    
    # List of DEA research papers
    paper_urls = [
        "https://www.nature.com/articles/s41467-024-48243-y",  # A large-strain and ultrahigh energy density dielectric elastomer for fast moving soft robot
        "https://www.nature.com/articles/s41467-024-54278-y"   # Soft, tough, and fast polyacrylate dielectric elastomer for non-magnetic motor
    ]
    
    # Process the papers
    tool.process_papers(paper_urls)
    
    # Example of searching for papers
    print("\nSearching for DEA papers...")
    search_results = tool.search_papers("dielectric elastomer actuator soft robot", max_results=5)
    
    if search_results:
        print(f"Found {len(search_results)} papers:")
        for i, result in enumerate(search_results, 1):
            print(f"{i}. {result['title']} - {result['url']}")
    else:
        print("No papers found.")

if __name__ == "__main__":
    main() 