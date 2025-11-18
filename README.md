# 🚦 Vietnamese Traffic Law Q&A System - Knowledge Graph & Semantic Reasoning

## 🎯 Project Overview
Advanced semantic search and knowledge representation system for Vietnamese traffic law violations. Features **Knowledge Graph**, **Semantic Reasoning**, and **Intelligent Q&A** capabilities with Vietnamese natural language understanding.

### 🏆 Key Innovations
- **Knowledge Graph**: Biểu diễn tri thức với mối quan hệ Hành vi → Mức phạt → Điều luật → Biện pháp bổ sung  
- **Semantic Reasoning**: Suy luận ngữ nghĩa với Intent Detection và Entity Extraction
- **Vietnamese NLP**: Xử lý tiếng Việt tự nhiên chuyên sâu cho lĩnh vực luật giao thông
- **Intelligent Search**: Tìm kiếm thông minh với Vector Embeddings và Graph Traversal

## 🚀 Features

### 🧠 Knowledge Representation
- **Knowledge Graph** với 436+ vi phạm giao thông
- **Node Types**: Behavior, Penalty, Law Article, Additional Measures
- **Relation Types**: Leads to penalty, Based on law, Has additional, Similar to
- **Graph Statistics**: Density analysis, connectivity metrics

### 🔍 Semantic Search & Reasoning  
- **Intent Detection**: penalty_inquiry, law_reference, behavior_check, similar_cases
- **Entity Extraction**: Vehicle types, Speed, Alcohol levels, Keywords
- **Semantic Similarity**: Cosine similarity với sentence embeddings
- **Reasoning Paths**: Chuỗi suy luận từ hành vi đến biện pháp xử lý

### 🎭 Intelligent Q&A
- **Natural Vietnamese**: Hiểu câu hỏi tiếng Việt tự nhiên
- **Confidence Scoring**: High/Medium/Low/None confidence levels
- **Citation Support**: Trích dẫn chính xác từ văn bản pháp lý
- **Unknown Handling**: "Không biết / Không có dữ liệu" cho trường hợp không tìm thấy

### 📊 Advanced Analytics
- **System Dashboard**: Thống kê knowledge graph và hiệu suất
- **Benchmark Tools**: Đánh giá hiệu quả so với LLM thuần túy
- **Performance Metrics**: Success rate, processing time, intent accuracy

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- 4GB+ RAM (for sentence transformer models)
- pip package manager

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
   pip install -r requirements-knowledge.txt
   ```

4. **Run Quick Demo**
   ```bash
   python demo.py
   ```

### Running the Full System

#### Method 1: Streamlit Web Interface (Recommended)
```bash
cd src/traffic_law_qa/ui
streamlit run streamlit_app.py
```
Access at: **http://localhost:8501**

#### Method 2: Command Line Demo
```bash
python demo.py
```

#### Method 3: Python Integration
```python
from traffic_law_qa.knowledge.qa_system import TrafficLawQASystem

# Initialize system
qa_system = TrafficLawQASystem("data/processed/violations.json")

# Ask question
result = qa_system.ask_question("Đi xe máy vượt đèn đỏ bị phạt bao nhiêu?")
print(result['answer'])
```

## 💡 Usage Examples

### Smart Q&A Interface
```
User: "Tôi đi xe máy vượt đèn đỏ, không đội mũ bảo hiểm thì bị phạt bao nhiêu?"

System: 
✅ Confidence: HIGH
🎭 Intent: penalty_inquiry

💬 Trả lời:
**Hành vi vi phạm:** Không tuân thủ hiệu lệnh của đèn tín hiệu giao thông

**Mức phạt:** 4,000,000 - 6,000,000 VNĐ

**Biện pháp bổ sung:**
- Tước quyền sử dụng Giấy phép lái xe từ 1 đến 3 tháng

📚 Trích dẫn pháp lý:
📋 Điều 6 Nghị định 100/2019/NĐ-CP
```

### Knowledge Graph Exploration
```python
# Get behavior chain: Behavior → Penalty → Law → Additional Measures
chain = qa_system.knowledge_graph.get_behavior_penalty_chain("behavior_123")

# Find similar behaviors
similar = qa_system.reasoning_engine.get_similar_behaviors("behavior_123", limit=5)

# Query knowledge paths
paths = qa_system.knowledge_graph.query_knowledge_paths(
    "behavior_123", 
    [NodeType.PENALTY, NodeType.LAW_ARTICLE]
)
```

### System Benchmarking
```python
# Test system performance
test_queries = [
    "Đi xe máy vượt đèn đỏ",
    "Không đội mũ bảo hiểm", 
    "Lái xe sau khi uống rượu"
]

benchmark = qa_system.benchmark_system(test_queries)
print(f"Success rate: {benchmark['success_rate']*100:.1f}%")
print(f"Average time: {benchmark['average_processing_time']:.3f}s")
```

## 📁 Project Structure

```
vietnamese-traffic-law-qa/
├── src/traffic_law_qa/
│   ├── knowledge/               # 🧠 Knowledge Graph & Semantic Reasoning
│   │   ├── knowledge_graph.py   # Knowledge Graph implementation
│   │   ├── semantic_reasoning.py # Semantic reasoning engine
│   │   └── qa_system.py         # Integrated QA system
│   ├── api/                     # FastAPI application
│   ├── core/                    # Configuration and settings  
│   ├── data/                    # Data models
│   ├── nlp/                     # Vietnamese NLP utilities
│   ├── search/                  # Semantic search engine
│   └── ui/                      # 🖥️ Advanced Streamlit interface
├── data/
│   ├── processed/
│   │   └── violations.json      # 📊 436+ processed violations
│   └── raw/legal_documents/     # Original legal documents
├── demo.py                      # 🎯 Quick demo script
├── test_knowledge_system.py     # 🧪 Comprehensive test suite
├── KNOWLEDGE_GRAPH_DESIGN.md    # 📖 Technical documentation
└── requirements-knowledge.txt   # Additional ML dependencies
```

## 🔬 Testing & Development

### Running Tests
```bash
# Run comprehensive test suite
python test_knowledge_system.py

# Unit tests only
python -m pytest test_knowledge_system.py::TestKnowledgeGraph -v

# Integration test with real data  
python test_knowledge_system.py
```

### System Benchmarking
```bash
# Quick benchmark
python demo.py

# Web interface benchmark (tab "Đánh giá hiệu suất")
streamlit run src/traffic_law_qa/ui/streamlit_app.py
```

### Performance Tuning
- **Similarity Threshold**: Adjust 0.3-0.9 (default: 0.6)
- **Max Results**: Limit results for faster response
- **Embedding Cache**: Automatic caching for repeated queries
- **Model Selection**: Use different sentence transformer models

## Legal Data Sources

This system processes information from:
- **Nghị định 100/2019/NĐ-CP**: Base traffic violation regulations
- **Nghị định 123/2021/NĐ-CP**: First set of amendments
- **Nghị định 168/2024/NĐ-CP**: Latest amendments

## 🔧 Technical Architecture

### Knowledge Graph Engine
```
Knowledge Nodes (2000+):
├── BEHAVIOR (436 hành vi vi phạm)
├── PENALTY (436 mức phạt) 
├── LAW_ARTICLE (các điều luật)
├── ADDITIONAL_MEASURE (biện pháp bổ sung)
└── Relations (1500+ mối quan hệ)
```

### Semantic Reasoning Pipeline
1. **Intent Detection**: Phân loại ý định người dùng
2. **Entity Extraction**: Trích xuất thông tin (xe máy, tốc độ, nồng độ cồn...)
3. **Query Preprocessing**: Chuẩn hóa tiếng Việt
4. **Semantic Search**: Vector similarity với sentence transformers
5. **Knowledge Reasoning**: Suy luận trên knowledge graph
6. **Result Synthesis**: Tổng hợp câu trả lời với trích dẫn

### AI Models Used
- **Sentence Transformer**: `paraphrase-multilingual-MiniLM-L12-v2`
- **Graph Engine**: NetworkX with custom algorithms
- **Vietnamese NLP**: Custom patterns and entity recognition
- **Similarity**: Cosine similarity with threshold filtering

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
