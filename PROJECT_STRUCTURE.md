# Vietnamese Traffic Law Q&A - Project Structure

```
vietnamese-traffic-law-qa/
├── .github/
│   └── copilot-instructions.md          # GitHub Copilot project instructions
├── .gitignore                           # Git ignore file
├── PROJECT_STRUCTURE.md                 # This file - project structure documentation
├── README.md                            # Project overview and setup instructions
├── pyproject.toml                       # Python project configuration
├── requirements.txt                     # Python dependencies
├── data/                               # Data directory
│   ├── data_scripts.sh                 # Data processing scripts
│   ├── embeddings/                     # Vector embeddings storage (gitignored)
│   ├── preprocessing/                  # Data preprocessing utilities
│   │   ├── analysis_report.py
│   │   ├── analyze_csv_results.py
│   │   ├── check_data_completeness.py
│   │   ├── create_csv_from_legal_docs.py
│   │   ├── DATA_PROCESSING_PIPELINE.md
│   │   ├── docx_reader.py
│   │   ├── embedding_generator.py
│   │   ├── extract_complete_nghi_dinh.py
│   │   ├── final_pipeline_report.py
│   │   ├── final_report.py
│   │   ├── final_validation.py
│   │   ├── legal_document_enhancer.py
│   │   ├── quality_check.py
│   │   ├── restore_original_dataset.py
│   │   ├── run_complete_pipeline.py
│   │   ├── update_csv_from_json.py
│   │   ├── update_dataset_from_json.py
│   │   ├── violation_processor.py
│   │   └── __pycache__/
│   ├── processed/                      # Processed legal documents
│   │   ├── nghi_dinh_100_2019.json
│   │   ├── nghi_dinh_123_2021.json
│   │   └── violations.json
│   └── raw/                           # Raw data sources
│       ├── legal_documents/           # Legal document sources
│       │   ├── nghi_dinh_100_2019.json
│       │   ├── nghi_dinh_123_2021.json
│       │   └── nghi_dinh_168_2024.json
│       └── violations_dataset/        # Violation dataset files
│           ├── nghi_dinh_100_2019_violations.csv
│           ├── nghi_dinh_123_2021_violations.csv
│           └── nghi_dinh_168_2024_violations.csv
├── docs/                              # Documentation
│   ├── dataset_consistency_update.md
│   └── dataset_update_summary.md
├── scripts/                           # Utility scripts
│   ├── generate_comprehensive_dataset.py
│   ├── generate_violations_dataset.py
│   └── sample_data.py
├── src/                              # Source code
│   └── traffic_law_qa/               # Main package
│       ├── __init__.py
│       ├── api/                      # API layer
│       │   ├── __init__.py
│       │   ├── main.py
│       │   └── routes/
│       │       └── __init__.py
│       ├── core/                     # Core configurations
│       │   ├── __init__.py
│       │   └── config.py
│       ├── data/                     # Data models and utilities
│       │   ├── __init__.py
│       │   └── models.py
│       ├── nlp/                      # NLP processing modules
│       │   ├── __init__.py
│       │   └── vietnamese_processor.py
│       ├── search/                   # Search engine components
│       │   ├── __init__.py
│       │   └── semantic_search.py
│       └── ui/                       # User interface components
│           ├── __init__.py
│           ├── streamlit_app.py
│           └── components/
│               └── __init__.py
└── tests/                            # Test suite
```

## Directory Descriptions

### `/data/`
- **`embeddings/`**: Vector embeddings for semantic search (excluded from git)
- **`preprocessing/`**: Data processing and transformation scripts
- **`processed/`**: Cleaned and structured legal documents
- **`raw/`**: Original legal documents and violation datasets

### `/src/traffic_law_qa/`
- **`api/`**: FastAPI/Flask REST API endpoints
- **`core/`**: Configuration and settings management
- **`data/`**: Data models and database interactions
- **`nlp/`**: Vietnamese text processing and NLP utilities
- **`search/`**: Semantic search engine implementation
- **`ui/`**: Streamlit web interface components

### `/scripts/`
Utility scripts for data generation and processing

### `/docs/`
Project documentation and analysis reports

### `/tests/`
Unit tests and integration tests