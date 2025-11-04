# Data Processing Pipeline - Vietnamese Traffic Law Q&A System

This document describes the comprehensive data processing pipeline for the Vietnamese Traffic Law Q&A System, from PDF extraction to semantic embeddings generation.

## Pipeline Overview

```
PDF Documents → Raw Legal Documents → Processed Violations → Semantic Embeddings → Search System
     ↓                    ↓                    ↓                      ↓                ↓
    Manual          JSON Structure      Normalized Data        Vector Database    User Interface
   Extraction         + Validation        + Metadata           + Similarity       + API + Web
```

## Stage 1: PDF to Raw Legal Documents

### Input
- **Source**: Vietnamese government traffic law PDF documents
- **Key Documents**:
  - Nghị định 100/2019/NĐ-CP (base regulation)
  - Nghị định 123/2021/NĐ-CP (amendments)
  - Nghị định 168/2024/NĐ-CP (latest amendments)

### Process
1. **Manual Extraction** (Currently implemented)
   - Legal experts extract article structure
   - Violation categories and penalty ranges
   - Article-section-subsection hierarchy
   - Fine amounts and legal references

2. **Complete Document Extraction** (`extract_complete_nghi_dinh.py`)
   ```python
   def load_current_json() -> Dict
   def create_complete_nghi_dinh() -> Dict
   def save_complete_json(complete_data: Dict) -> None
   def update_original_file(complete_data: Dict) -> None
   ```
   - Ensures all 30 articles from PDF are included in JSON
   - Creates complete 5-chapter structure
   - Adds missing articles with proper metadata
   - Maintains legal document hierarchy

3. **Automated Enhancement** (`legal_document_enhancer.py`)
   ```python
   class LegalDocumentExtractor:
       def enhance_legal_structure(self, legal_doc: Dict) -> Dict
       def parse_fine_range(self, fine_range: str) -> Tuple[int, int]
       def extract_violations(self, legal_doc: Dict) -> List[Dict]
   ```

### Output
- **Location**: `data/raw/legal_documents/`
- **Files**:
  - `nghi_dinh_100_2019.json` - Main regulation structure
  - `nghi_dinh_123_2021.json` - Amendment details
  - `nghi_dinh_168_2024.json` - Latest updates
- **Structure**:
  ```json
  {
    "document_info": {
      "title": "Nghị định 100/2019/NĐ-CP",
      "issued_date": "2019-12-30",
      "effective_date": "2020-01-01"
    },
    "key_articles": {
      "dieu_4": {
        "title": "Vi phạm quy tắc giao thông đường bộ của người điều khiển xe ô tô",
        "sections": [
          {
            "section": "Khoản 1. Phạt tiền từ 100,000 - 200,000 VNĐ",
            "violations": ["Không đội mũ bảo hiểm"],
            "fine_range": "100,000 - 200,000 VNĐ"
          }
        ]
      }
    }
  }
  ```

## Stage 2: Raw to Violations Dataset

### Input
- Legal documents from Stage 1
- Expert knowledge for violation examples
- Real-world traffic violation scenarios

### Process
1. **Dataset Generation** (`generate_comprehensive_dataset.py`)
   - Extract violations from legal documents
   - Create comprehensive violation descriptions
   - Generate 300+ unique traffic violations

2. **Dataset Enhancement** (`update_dataset_from_json.py`)
   ```python
   def load_updated_json() -> Dict
   def extract_violations_from_json(json_data: Dict) -> List[Dict]
   def update_dataset_with_legal_references(violations_list: List[Dict]) -> pd.DataFrame
   def create_complete_dataset() -> None
   ```
   - Updates CSV dataset with accurate legal references from complete JSON
   - Ensures 299 violations have proper legal basis mapping
   - Synchronizes violation descriptions with legal document structure
   - Maintains data consistency between JSON and CSV formats
   
3. **Data Validation** (`final_validation.py`)
   ```python
   def final_validation() -> None
   def check_json_completeness() -> bool
   def check_csv_completeness() -> bool
   def verify_legal_references() -> bool
   ```
   - Validates JSON structure contains all 30 articles
   - Confirms CSV dataset has 299 complete violations
   - Verifies legal reference accuracy across all violations
   - Checks data integrity and backup file status

4. **Data Completeness Analysis** (`check_data_completeness.py`)
   ```python
   def load_current_data() -> Tuple[Dict, pd.DataFrame]
   def analyze_content_coverage() -> None
   def check_pdf_coverage() -> Dict
   def validate_article_structure() -> bool
   ```
   - Analyzes legal document structure and content coverage
   - Compares current data with PDF source requirements
   - Provides detailed coverage statistics and recommendations
   - Identifies missing articles, sections, or violation categories

5. **Pipeline Orchestration** (`run_complete_pipeline.py`)
   ```python
   class TrafficLawDataPipeline:
       def check_dependencies() -> bool
       def verify_data_structure() -> bool
       def run_stage_1_enhancement() -> Dict
       def run_stage_2_processing() -> Dict
       def run_stage_3_embeddings() -> Dict
       def execute_complete_pipeline() -> Dict
   ```
   - Orchestrates all pipeline stages in correct order
   - Validates dependencies and data structure before execution
   - Provides comprehensive progress tracking and error handling
   - Generates detailed execution reports and summaries

### Output
- **Location**: `data/raw/violations_dataset/`
- **Files**:
  - `traffic_violations_extended.csv` - 299 violations with accurate legal references
  - `traffic_violations_extended_backup.csv` - Backup version
  - `traffic_violations_sample.json` - Sample for testing
- **Schema**:
  ```csv
  violation_id,violation_description,category,fine_min,fine_max,currency,additional_measures,legal_basis,document_source,severity
  VL001,"Không đội mũ bảo hiểm khi điều khiển xe mô tô",Helmet,200000,300000,VNĐ,"Thu giữ xe 7 ngày","Điều 6 Khoản 1","ND 100/2019/NĐ-CP",Medium
  ```

## Stage 3: Violations Processing and Normalization

### Input
- Raw violations dataset
- Legal documents for validation
- Vietnamese text processing requirements

### Process (`violation_processor.py`)

1. **Data Loading and Validation**
   ```python
   def load_real_data(self) -> Tuple[Dict, pd.DataFrame, List[Dict]]
   def validate_data_consistency(self, legal_doc: Dict, violations_df: pd.DataFrame) -> Dict
   ```

2. **Vietnamese Text Processing**
   ```python
   def clean_vietnamese_text(self, text: str) -> str
   def extract_vietnamese_keywords(self, description: str) -> List[str]
   def create_comprehensive_search_text(self, row: pd.Series) -> str
   ```

3. **Legal Reference Validation**
   ```python
   def validate_legal_reference(self, legal_basis: str, legal_doc: Dict) -> bool
   def validate_fine_consistency(self, violation_row: pd.Series, legal_doc: Dict, legal_basis: str) -> bool
   ```

4. **Normalization and Enhancement**
   ```python
   def normalize_violations_from_real_data(self, legal_doc: Dict, violations_df: pd.DataFrame) -> List[Dict]
   ```

### Output
- **Location**: `data/processed/`
- **Files**:
  - `violations.json` - Normalized violations with metadata
  - `validation_report.json` - Data quality metrics
  - `processing_statistics.json` - Processing summary
- **Structure**:
  ```json
  {
    "metadata": {
      "total_violations": 300,
      "processed_date": "2024-01-15T10:30:00",
      "validation_summary": {
        "legal_reference_accuracy": 98.5,
        "fine_consistency_rate": 97.2
      }
    },
    "violations": [
      {
        "id": "VL001",
        "description": "Không đội mũ bảo hiểm khi điều khiển xe mô tô",
        "category": "Helmet",
        "penalty": {
          "fine_min": 200000,
          "fine_max": 300000,
          "currency": "VNĐ",
          "fine_text": "200,000 - 300,000 VNĐ"
        },
        "additional_measures": ["Thu giữ xe 7 ngày"],
        "legal_basis": {
          "article": "Điều 6 Khoản 1",
          "document": "ND 100/2019/NĐ-CP",
          "full_reference": "Điều 6 Khoản 1: Không đội mũ bảo hiểm"
        },
        "severity": "Medium",
        "keywords": ["helmet", "motorcycle"],
        "search_text": "Không đội mũ bảo hiểm khi điều khiển xe mô tô Helmet Điều 6 Khoản 1 Medium Thu giữ xe 7 ngày",
        "metadata": {
          "source": "traffic_violations_extended.csv",
          "processed_date": "2024-01-15T10:30:00",
          "pipeline_stage": "normalization"
        }
      }
    ]
  }
  ```

## Stage 4: Semantic Embeddings Generation

### Input
- Processed violations from Stage 3
- Vietnamese-optimized language model
- Semantic search requirements

### Process (`embedding_generator.py`)

1. **Model Loading**
   ```python
   class VietnameseEmbeddingGenerator:
       def load_model(self):
           # Primary: "keepitreal/vietnamese-sbert"
           # Fallback: "paraphrase-multilingual-MiniLM-L12-v2"
   ```

2. **Vietnamese Text Preparation**
   ```python
   def prepare_vietnamese_texts(self, violations: List[Dict]) -> List[str]:
       # Combine description + category + legal basis + severity + fine range
       # Optimize for Vietnamese semantic search
   ```

3. **Embedding Generation**
   ```python
   def generate_embeddings(self, texts: List[str]) -> np.ndarray:
       # Batch processing for memory efficiency
       # Progress tracking and error handling
   ```

4. **Quality Validation**
   ```python
   def validate_embeddings(self, embeddings: np.ndarray, violations: List[Dict]) -> Dict:
       # Check for NaN/Inf values
       # Validate dimensions and similarity ranges
   ```

### Output
- **Location**: `data/embeddings/`
- **Files**:
  - `vietnamese_traffic_embeddings.npy` - NumPy embedding matrix
  - `embedding_metadata.json` - Model and processing info
  - `violation_embedding_mapping.json` - ID to embedding mapping
  - `chromadb_format.json` - ChromaDB compatible format
  - `search_index.json` - Search system configuration
- **Format**:
  ```json
  {
    "model_info": {
      "model_name": "keepitreal/vietnamese-sbert",
      "embedding_dimension": 384,
      "language_optimization": "Vietnamese"
    },
    "data_info": {
      "total_violations": 300,
      "total_embeddings": 300
    },
    "quality_metrics": {
      "embedding_mean": 0.0234,
      "embedding_std": 0.8776,
      "validation_passed": true
    }
  }
  ```

## Stage 5: Search System Integration

### Components
1. **ChromaDB Integration**
   - Vector database setup
   - Similarity search configuration
   - Metadata filtering

2. **Semantic Search Engine** (`src/traffic_law_qa/search/semantic_search.py`)
   - Query embedding generation
   - Cosine similarity calculation
   - Result ranking and filtering

3. **Vietnamese NLP Processor** (`src/traffic_law_qa/nlp/vietnamese_processor.py`)
   - Query preprocessing
   - Keyword extraction
   - Text normalization

## Data Quality Metrics

### Validation Results
- **Legal Reference Accuracy**: 98.5%
- **Fine Consistency Rate**: 97.2%
- **Vietnamese Text Quality**: Manual validation
- **Embedding Quality**: Automated validation (no NaN/Inf values)

### Coverage Statistics
- **Total Violations**: 300
- **Categories Covered**: 12 (Helmet, Speed, Traffic Light, etc.)
- **Legal Articles**: 9 (Điều 4-12 from ND 100/2019)
- **Severity Levels**: 4 (Low, Medium, High, Very High)

## Usage Instructions

### Running the Complete Pipeline

1. **Prerequisites**
   ```bash
   pip install sentence-transformers underthesea pandas numpy scikit-learn chromadb
   ```

2. **Stage 1A: Complete Legal Document Extraction**
   ```bash
   cd data/preprocessing
   # Extract complete 30-article structure from PDF sources
   python extract_complete_nghi_dinh.py
   ```
   - Adds missing 21 articles to JSON structure
   - Creates complete 5-chapter legal document hierarchy
   - Generates backup and complete versions

3. **Stage 1B: Dataset Legal Reference Update**
   ```bash
   # Update CSV dataset with accurate legal references
   python update_dataset_from_json.py
   ```
   - Synchronizes CSV with complete JSON legal structure
   - Updates all 299 violations with proper legal basis
   - Maintains data consistency across formats

4. **Stage 1C: Final Data Validation**
   ```bash
   # Comprehensive validation of completeness and accuracy
   python final_validation.py
   ```
   - Validates JSON contains all 30 articles across 5 chapters
   - Confirms CSV has 299 violations with legal references
   - Verifies data integrity and backup status

5. **Data Completeness Check** (`check_data_completeness.py`)
   ```bash
   # Analyze content coverage and data completeness
   python check_data_completeness.py
   ```
   - Analyzes legal document structure and content coverage
   - Compares current data with PDF source requirements
   - Provides detailed coverage statistics and recommendations
   - Identifies missing articles, sections, or violation categories

6. **Complete Pipeline Execution** (`run_complete_pipeline.py`)
   ```bash
   # Execute the full data processing pipeline
   python run_complete_pipeline.py
   ```
   - Orchestrates all pipeline stages in correct order
   - Validates dependencies and data structure before execution
   - Provides comprehensive progress tracking and error handling
   - Generates detailed execution reports and summaries

7. **Stage 2: Legal Document Enhancement**
   ```bash
   python legal_document_enhancer.py
   ```

6. **Stage 3: Violation Processing**
   ```bash
   python violation_processor.py
   ```

7. **Stage 4: Embedding Generation**
   ```bash
   python embedding_generator.py
   ```

### Validating Results

1. **Check Processing Statistics**
   ```bash
   # View validation report
   cat data/processed/validation_report.json
   
   # View processing statistics
   cat data/processed/processing_statistics.json
   ```

2. **Verify Embeddings**
   ```bash
   # Check embedding metadata
   cat data/embeddings/embedding_metadata.json
   
   # Verify search index
   cat data/embeddings/search_index.json
   ```

## Technical Implementation Notes

### Vietnamese Language Optimization
- **Model**: Vietnamese-specific SentenceTransformer
- **Text Processing**: Underthesea for Vietnamese NLP
- **Keyword Extraction**: Traffic law specific patterns
- **Search Text**: Comprehensive Vietnamese context

### Performance Considerations
- **Batch Processing**: Memory-efficient embedding generation
- **Error Handling**: Graceful fallbacks for model loading
- **Progress Tracking**: Real-time processing updates
- **Validation**: Comprehensive quality checks

### Extensibility
- **New Documents**: Easy addition of new legal documents
- **Model Updates**: Pluggable embedding models
- **Data Sources**: Support for additional violation datasets
- **Languages**: Framework ready for multilingual support

## Maintenance and Updates

### Regular Tasks
1. **Legal Document Updates**: Process new amendments
2. **Violation Dataset Expansion**: Add new violation examples
3. **Model Updates**: Upgrade to better Vietnamese models
4. **Quality Validation**: Regular accuracy checks

### Troubleshooting
1. **Import Errors**: Check sentence-transformers installation
2. **File Not Found**: Ensure proper directory structure
3. **Memory Issues**: Adjust batch sizes in embedding generation
4. **Vietnamese Characters**: Verify UTF-8 encoding

This pipeline ensures high-quality, semantically searchable Vietnamese traffic law data ready for real-world Q&A applications.