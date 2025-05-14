# Research Tool

A tool to fetch and analyze Dielectric Elastomer Actuator (DEA) research papers from various sources.

## Features

- Fetch papers from scientific repositories like Nature, arXiv, etc.
- Extract key information from papers (materials, performance metrics, applications)
- Generate comprehensive reports in markdown format
- Export data to JSON and CSV formats
- Search for papers using keywords

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd dea-research-tool
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Process specific papers

To process specific papers, use the `--urls` parameter:

```bash
python dea_research_tool.py --urls https://www.nature.com/articles/s41467-024-48243-y https://www.nature.com/articles/s41467-024-54278-y
```

### Search for papers

To search for papers, use the `--search` parameter:

```bash
python dea_research_tool.py --search "dielectric elastomer actuator soft robot"
```

You can limit the number of search results with the `--max-results` parameter:

```bash
python dea_research_tool.py --search "dielectric elastomer actuator" --max-results 5
```

### Specify output directory

To specify the output directory, use the `--output-dir` parameter:

```bash
python dea_research_tool.py --urls https://www.nature.com/articles/s41467-024-48243-y --output-dir my_results
```

## Output

The tool generates the following outputs:

1. JSON file with detailed paper information
2. CSV file with flattened paper information
3. Markdown report with summaries and analysis

All outputs are saved in the specified output directory (default: `dea_research_output`).

## Supported Sources

Currently, the tool supports the following sources:

- Nature journals
- arXiv

More sources will be added in future updates.

## License

MIT 
