# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-04-02
### Added
- Added `RobTextAnalyzer.py` with `JournalMetricsAnalyzer`/`RobTextAnalyzer` class for category-based journal and text metric analysis
- Added `RobTextAnalyzer_Lexicon.json` to support the new text analyzer metrics
- Added `RobPsychSignalAnalyzer.py` with multi-category psychological signal analysis from raw text
- Added `RobPsychSignalAnalyzer_Lexicon.json` for psychological signal lexicon-driven scoring

### Changed
- Expanded lexical coverage across analyzer lexicon categories for broader English term matching
- Reformatted lexicon JSON files for improved human readability while preserving deterministic structure and valid JSON

## [1.0.0] - 2026-03-17
### Added
- Initial release of RobTextStats.py
- Single-pass text and markdown analysis
- Basic, advanced, and LLM metrics
- Aggregation and overall stats
- CLI with --advanced, --llm, --text_analytics, --overall, --output, --help-metric, --list-metrics, --version
- Sentiment and emotion lexicon analysis
- Output in JSON format
- Per-file and overall aggregation
