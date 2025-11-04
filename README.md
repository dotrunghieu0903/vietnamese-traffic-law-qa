# Vietnamese Traffic Law Q&A System

## Project Overview
A comprehensive semantic search system for Vietnamese traffic law violations and penalties. The system uses natural language processing and machine learning to understand complex Vietnamese queries about traffic violations and provides accurate penalty information, legal basis, and additional measures.

## Features

### 🔍 Semantic Search
- Natural language understanding for Vietnamese traffic violation queries
- Intelligent matching between user descriptions and legal violations
- Support for complex, multi-violation scenarios

### 🚦 Comprehensive Coverage
- 300+ traffic violations from Vietnamese legal documents
- Based on Nghị định 100/2019/NĐ-CP and amendments (123/2021, 168/2024)
- Detailed penalty information including fines and additional measures

### 🖥️ User Interfaces
- **Web API**: RESTful API for integration with other systems
- **Streamlit App**: Interactive web interface for end users
- **Vietnamese Language Support**: Full Vietnamese text processing

### 🧠 AI-Powered
- Sentence transformers for multilingual semantic understanding
- Vietnamese-specific text preprocessing
- Similarity-based ranking of search results

## Quick Start

### Prerequisites
- Python 3.9+
- pip or conda package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/dotrunghieu0903/vietnamese-traffic-law-qa.git
   cd vietnamese-traffic-law-qa
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your settings
   ```

5. **Generate sample data**
   ```bash
   python scripts/sample_data.py
   ```

### Running the Application

#### Start the API Server
```bash
# From project root
python -m uvicorn src.traffic_law_qa.api.main:app --reload --host 0.0.0.0 --port 8000
```

#### Start the Streamlit Interface
```bash
# In a new terminal
streamlit run src/traffic_law_qa/ui/streamlit_app.py
```

Access the application:
- **API Documentation**: http://localhost:8000/docs
- **Streamlit Interface**: http://localhost:8501

## Usage Examples

### API Usage
```python
import requests

# Search for violations
response = requests.post("http://localhost:8000/search", json={
    "query": "Đi xe máy vượt đèn đỏ không đội mũ bảo hiểm",
    "max_results": 5,
    "similarity_threshold": 0.7
})

results = response.json()
print(f"Found {results['total_results']} violations")
```

### Web Interface
1. Open http://localhost:8501
2. Enter a violation description in Vietnamese
3. Adjust search parameters if needed
4. View detailed results with penalties and legal basis

## Project Structure

```
VNI-TrafficLawQA/
├── src/traffic_law_qa/          # Main application code
│   ├── api/                     # FastAPI application
│   ├── core/                    # Configuration and settings
│   ├── data/                    # Data models and processing
│   ├── nlp/                     # Vietnamese NLP utilities
│   ├── search/                  # Semantic search engine
│   └── ui/                      # Streamlit interface
├── data/                        # Data storage
│   ├── raw/                     # Original legal documents
│   ├── processed/               # Processed violation data
│   └── embeddings/              # Vector embeddings
├── tests/                       # Test files
├── scripts/                     # Utility scripts
└── docs/                        # Documentation
```

## Development

### Adding New Violations
1. Add violation data to `data/processed/violations.json`
2. Regenerate embeddings: `python scripts/train_embeddings.py`
3. Restart the API server

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/ tests/
flake8 src/ tests/
```

## Legal Data Sources

This system processes information from:
- **Nghị định 100/2019/NĐ-CP**: Base traffic violation regulations
- **Nghị định 123/2021/NĐ-CP**: First set of amendments
- **Nghị định 168/2024/NĐ-CP**: Latest amendments

## Technical Details

### NLP Pipeline
1. **Text Preprocessing**: Vietnamese-specific cleaning and normalization
2. **Tokenization**: Word segmentation using underthesea
3. **Embedding Generation**: Multilingual sentence transformers
4. **Similarity Matching**: Cosine similarity for semantic search

### Search Algorithm
1. Preprocess user query with Vietnamese NLP
2. Generate query embedding using sentence transformer
3. Calculate cosine similarity with violation embeddings
4. Rank results by similarity score
5. Filter by threshold and return top matches

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with appropriate tests
4. Submit a pull request

## License

This project is for educational and research purposes. Please ensure compliance with Vietnamese legal regulations when using this system.

## Support

For issues and questions:
- Create an issue on the project repository
- Check the documentation in `docs/`
- Review API documentation at `/docs` endpoint

## Disclaimer

This system provides information for reference only. Always consult with legal professionals and official sources for authoritative legal advice regarding traffic violations and penalties.
