# robBookUtils

## Overview
robBookUtils is a suite of Python utilities for advanced text analysis, designed for writers, editors, and researchers.

The project currently includes:
- `RobTextStats.py`: file-oriented text and markdown analytics with CLI output
- `RobTextAnalyzer.py`: in-memory journal/text metrics analyzer class with category selection
- `RobPsychSignalAnalyzer.py`: in-memory psychological signal analyzer class with category selection

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

## RobTextAnalyzer.py

### Version
- 1.0.0

### Purpose
- Computes broad journal/text metrics from a raw string input
- Returns fully serialized JSON
- Supports category-specific or all-category analysis

### Class API
- Class: `JournalMetricsAnalyzer`
- Alias: `RobTextAnalyzer`
- Method: `analyze(text: str, categories: list[str] | None = None) -> str`

### Category Modes
- `categories=None`: compute all categories
- `categories=[...]`: compute only requested categories

### Example
```python
from RobTextAnalyzer import RobTextAnalyzer

analyzer = RobTextAnalyzer("RobTextAnalyzer_Lexicon.json")
result_json = analyzer.analyze(
	"I felt overwhelmed this morning, but I recovered and made progress by lunch.",
	categories=["emotional_lexicon_metrics", "motivation_goal_orientation"]
)
print(result_json)
```

## RobPsychSignalAnalyzer.py

### Version
- 1.0.0

### Purpose
- Analyzes free text for psychological, emotional, cognitive, identity, social, temporal, and linguistic signals
- Returns structured JSON for selected categories plus summary metadata

### Class API
- Class: `RobPsychSignalAnalyzer`
- Method: `analyze(text: str, categories: list[str] | "all") -> str`

### Available Categories
- `core_affect`
- `cognitive_patterns`
- `identity`
- `social`
- `behavioral_intent`
- `regulation`
- `temporal`
- `somatic`
- `existential`
- `linguistic_structure`
- `thought_speed`
- `meta_signals`

### Example
```python
from RobPsychSignalAnalyzer import RobPsychSignalAnalyzer

analyzer = RobPsychSignalAnalyzer("RobPsychSignalAnalyzer_Lexicon.json")
result_json = analyzer.analyze(
	"I keep overthinking, but I reached out to a friend and felt calmer.",
	categories="all"
)
print(result_json)
```

## Lexicon Files
- `RobTextAnalyzer_Lexicon.json`: expanded metric lexicon used by `RobTextAnalyzer.py`
- `RobPsychSignalAnalyzer_Lexicon.json`: lexicon used by `RobPsychSignalAnalyzer.py`

## Changelog
See [CHANGELOG.md](CHANGELOG.md) for release history.