# robBookUtils

## Overview
robBookUtils is a suite of Python utilities for advanced text and markdown file analysis, designed for writers, editors, and researchers. Each tool is a standalone script with a consistent CLI and JSON output, making it easy to integrate into larger workflows.

## RobTextStats.py

### Version
- 1.0.0

### Features
- Efficient, single-pass analysis of text and markdown files
- Basic, advanced, and LLM-oriented metrics
- Frequency and n-gram analysis
- Sentiment and emotion lexicon analysis
- Aggregation and overall statistics across multiple files
- Output in structured JSON format
- CLI with rich options for filtering and output

### Usage
```sh
python RobTextStats.py [targets] [options]
```
- `targets`: Files, folders, or glob patterns to analyze (e.g., `*.md` or `docs/`)

#### Options
- `-o, --output <file>`: Output JSON file (default: print to console)
- `--advanced`: Include advanced metrics
- `--llm`: Include LLM metrics
- `--text_analytics`: Include text analytics (frequency, n-grams, sentiment, emotion)
- `--overall`: Output only overall totals/averages across all files
- `--help-metric <METRIC>`: Show detailed help for a specific metric
- `--list-metrics`: List all available metrics
- `--version`: Show version and exit

#### Example
```sh
python RobTextStats.py "docs/*.md" --advanced --llm --text_analytics --overall -o results.json
```

### Output Structure
- `basic`: Basic statistics (word count, sentence count, readability, etc.)
- `advanced`: Advanced statistics (lexical diversity, sentence/word medians, etc.)
- `llm`: LLM-oriented metrics (token count, entropy, compression, etc.)
- `text_analytics`: Frequency, n-grams, sentiment, and emotion analysis
- `file_info`: Metadata for each file

### Extending robBookUtils
- Each script should follow the same CLI and output conventions as RobTextStats.py
- Add new scripts for other text utilities as needed
- Document new features and changes in CHANGELOG.md

## Changelog
See [CHANGELOG.md](CHANGELOG.md) for release history.