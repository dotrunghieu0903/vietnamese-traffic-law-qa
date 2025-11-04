"""
Vietnamese Traffic Law Embeddings Generator
Generate semantic embeddings for Vietnamese traffic violation data
"""

import json
import numpy as np
from typing import List, Dict, Tuple
import os
import pickle
from datetime import datetime
from sentence_transformers import SentenceTransformer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VietnameseEmbeddingGenerator:
    """Generate semantic embeddings for Vietnamese traffic law data"""
    
    def __init__(self, model_name: str = "keepitreal/vietnamese-sbert"):
        """
        Initialize with Vietnamese-optimized SentenceTransformer model
        Args:
            model_name: Vietnamese-specific SBERT model
        """
        self.model_name = model_name
        self.model = None
        self.embeddings = None
        self.metadata = None
        
    def load_model(self):
        """Load Vietnamese SBERT model with error handling"""
        try:
            logger.info(f"Loading Vietnamese SBERT model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("✅ Model loaded successfully")
            
            # Test model with Vietnamese text
            test_text = "Không đội mũ bảo hiểm khi đi xe mô tô"
            test_embedding = self.model.encode(test_text)
            logger.info(f"📊 Model test successful - embedding dimension: {len(test_embedding)}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load model {self.model_name}: {e}")
            logger.info("🔄 Falling back to multilingual model...")
            
            # Fallback to multilingual model
            try:
                self.model_name = "paraphrase-multilingual-MiniLM-L12-v2"
                self.model = SentenceTransformer(self.model_name)
                logger.info(f"✅ Fallback model loaded: {self.model_name}")
            except Exception as fallback_error:
                logger.error(f"❌ Fallback model also failed: {fallback_error}")
                raise Exception("Could not load any suitable model for Vietnamese embeddings")
    
    def load_processed_violations(self) -> List[Dict]:
        """Load processed violations data"""
        processed_file = '../processed/violations.json'
        
        if not os.path.exists(processed_file):
            raise FileNotFoundError(
                f"Processed violations file not found: {processed_file}\n"
                "Please run violation_processor.py first to generate processed data."
            )
        
        with open(processed_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        violations = data.get('violations', [])
        logger.info(f"📊 Loaded {len(violations)} processed violations")
        
        return violations
    
    def prepare_vietnamese_texts(self, violations: List[Dict]) -> List[str]:
        """Prepare optimized Vietnamese texts for embedding generation"""
        texts = []
        
        for violation in violations:
            # Create comprehensive Vietnamese text for semantic search
            text_components = [
                violation['description'],  # Main violation description
                violation['category'],     # Category in Vietnamese
                violation['legal_basis']['article']  # Legal reference
            ]
            
            # Add additional measures if present
            if violation.get('additional_measures'):
                measures_text = ' '.join(violation['additional_measures'])
                text_components.append(measures_text)
            
            # Create severity context in Vietnamese
            severity_mapping = {
                'Low': 'mức độ nhẹ',
                'Medium': 'mức độ trung bình', 
                'High': 'mức độ nặng',
                'Very High': 'mức độ rất nặng'
            }
            
            severity_vn = severity_mapping.get(violation['severity'], violation['severity'])
            text_components.append(f"mức phạt {severity_vn}")
            
            # Create fine range context
            fine_min = violation['penalty']['fine_min']
            fine_max = violation['penalty']['fine_max']
            fine_text = f"phạt tiền {fine_min:,} đến {fine_max:,} VNĐ"
            text_components.append(fine_text)
            
            # Join all components
            comprehensive_text = ' '.join(text_components)
            texts.append(comprehensive_text)
        
        logger.info(f"✅ Prepared {len(texts)} Vietnamese texts for embedding")
        return texts
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for Vietnamese texts"""
        if self.model is None:
            self.load_model()
        
        logger.info("🔄 Generating embeddings for Vietnamese traffic violations...")
        
        try:
            # Generate embeddings in batches for memory efficiency
            batch_size = 32
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_embeddings = self.model.encode(
                    batch_texts,
                    convert_to_numpy=True,
                    show_progress_bar=True,
                    batch_size=min(batch_size, len(batch_texts))
                )
                all_embeddings.append(batch_embeddings)
                
                logger.info(f"📊 Processed batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
            
            # Combine all embeddings
            embeddings = np.vstack(all_embeddings)
            
            logger.info(f"✅ Generated embeddings: shape {embeddings.shape}")
            return embeddings
            
        except Exception as e:
            logger.error(f"❌ Error generating embeddings: {e}")
            raise
    
    def create_embedding_metadata(self, violations: List[Dict], texts: List[str], embeddings: np.ndarray) -> Dict:
        """Create comprehensive metadata for embeddings"""
        metadata = {
            "model_info": {
                "model_name": self.model_name,
                "embedding_dimension": embeddings.shape[1],
                "model_type": "sentence-transformers",
                "language_optimization": "Vietnamese"
            },
            "data_info": {
                "total_violations": len(violations),
                "total_embeddings": embeddings.shape[0],
                "source_file": "data/processed/violations.json",
                "text_preparation": "comprehensive Vietnamese text with legal context"
            },
            "processing_info": {
                "generation_date": datetime.now().isoformat(),
                "embedding_method": "batch processing with progress tracking",
                "optimization": "Vietnamese traffic law semantic search"
            },
            "quality_metrics": {
                "embedding_mean": float(np.mean(embeddings)),
                "embedding_std": float(np.std(embeddings)),
                "embedding_range": [float(np.min(embeddings)), float(np.max(embeddings))],
                "text_lengths": {
                    "min_length": min(len(text) for text in texts),
                    "max_length": max(len(text) for text in texts),
                    "avg_length": sum(len(text) for text in texts) / len(texts)
                }
            },
            "violation_ids": [v['id'] for v in violations]
        }
        
        return metadata
    
    def save_embeddings(self, embeddings: np.ndarray, metadata: Dict, texts: List[str], violations: List[Dict]):
        """Save embeddings and metadata in multiple formats"""
        output_dir = '../embeddings'
        os.makedirs(output_dir, exist_ok=True)
        
        # Save embeddings as numpy array
        embeddings_file = f"{output_dir}/vietnamese_traffic_embeddings.npy"
        np.save(embeddings_file, embeddings)
        logger.info(f"💾 Embeddings saved to: {embeddings_file}")
        
        # Save metadata as JSON
        metadata_file = f"{output_dir}/embedding_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        logger.info(f"📋 Metadata saved to: {metadata_file}")
        
        # Save mapping between violations and embeddings
        mapping_data = {
            "embeddings_info": {
                "file": "vietnamese_traffic_embeddings.npy",
                "shape": embeddings.shape,
                "dtype": str(embeddings.dtype)
            },
            "violation_mapping": [
                {
                    "embedding_index": i,
                    "violation_id": violations[i]['id'],
                    "violation_description": violations[i]['description'],
                    "search_text": texts[i],
                    "category": violations[i]['category']
                }
                for i in range(len(violations))
            ]
        }
        
        mapping_file = f"{output_dir}/violation_embedding_mapping.json"
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump(mapping_data, f, ensure_ascii=False, indent=2)
        logger.info(f"🗺️ Mapping saved to: {mapping_file}")
        
        # Save embeddings for ChromaDB compatibility
        chromadb_data = {
            "embeddings": embeddings.tolist(),
            "documents": texts,
            "metadatas": [
                {
                    "violation_id": violations[i]['id'],
                    "category": violations[i]['category'],
                    "severity": violations[i]['severity'],
                    "legal_basis": violations[i]['legal_basis']['article'],
                    "fine_min": violations[i]['penalty']['fine_min'],
                    "fine_max": violations[i]['penalty']['fine_max']
                }
                for i in range(len(violations))
            ],
            "ids": [violations[i]['id'] for i in range(len(violations))]
        }
        
        chromadb_file = f"{output_dir}/chromadb_format.json"
        with open(chromadb_file, 'w', encoding='utf-8') as f:
            json.dump(chromadb_data, f, ensure_ascii=False, indent=2)
        logger.info(f"🔗 ChromaDB format saved to: {chromadb_file}")
        
        # Save search index for quick similarity searches
        search_index = {
            "model_name": self.model_name,
            "embeddings_file": "vietnamese_traffic_embeddings.npy",
            "dimension": embeddings.shape[1],
            "violation_count": len(violations),
            "search_ready": True,
            "last_updated": datetime.now().isoformat()
        }
        
        index_file = f"{output_dir}/search_index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(search_index, f, ensure_ascii=False, indent=2)
        logger.info(f"🔍 Search index saved to: {index_file}")
    
    def validate_embeddings(self, embeddings: np.ndarray, violations: List[Dict]) -> Dict:
        """Validate generated embeddings quality"""
        validation_results = {
            "basic_validation": {
                "shape_correct": embeddings.shape[0] == len(violations),
                "no_nan_values": not np.isnan(embeddings).any(),
                "no_inf_values": not np.isinf(embeddings).any(),
                "dimension_consistent": len(set([emb.shape[0] for emb in embeddings])) == 1
            },
            "quality_metrics": {
                "mean_embedding_norm": float(np.mean(np.linalg.norm(embeddings, axis=1))),
                "std_embedding_norm": float(np.std(np.linalg.norm(embeddings, axis=1))),
                "min_similarity": float(np.min(np.dot(embeddings, embeddings.T))),
                "max_similarity": float(np.max(np.dot(embeddings, embeddings.T)))
            },
            "validation_passed": True
        }
        
        # Check if validation passed
        basic_checks = validation_results["basic_validation"]
        validation_results["validation_passed"] = all(basic_checks.values())
        
        if validation_results["validation_passed"]:
            logger.info("✅ Embedding validation passed")
        else:
            logger.warning("⚠️ Embedding validation failed")
            for check, result in basic_checks.items():
                if not result:
                    logger.warning(f"   - {check}: FAILED")
        
        return validation_results
    
    def generate_complete_embeddings(self) -> Dict:
        """Complete pipeline for generating Vietnamese traffic law embeddings"""
        logger.info("🚀 Starting Vietnamese Traffic Law Embedding Generation")
        
        # Load processed violations
        violations = self.load_processed_violations()
        
        # Prepare Vietnamese texts
        texts = self.prepare_vietnamese_texts(violations)
        
        # Generate embeddings
        embeddings = self.generate_embeddings(texts)
        
        # Validate embeddings
        validation_results = self.validate_embeddings(embeddings, violations)
        
        # Create metadata
        metadata = self.create_embedding_metadata(violations, texts, embeddings)
        metadata["validation_results"] = validation_results
        
        # Save all outputs
        self.save_embeddings(embeddings, metadata, texts, violations)
        
        logger.info("✅ Vietnamese traffic law embeddings generation completed successfully")
        
        return {
            "embeddings_shape": embeddings.shape,
            "model_used": self.model_name,
            "validation_passed": validation_results["validation_passed"],
            "output_files": [
                "vietnamese_traffic_embeddings.npy",
                "embedding_metadata.json", 
                "violation_embedding_mapping.json",
                "chromadb_format.json",
                "search_index.json"
            ]
        }


def main():
    """Main function for embedding generation"""
    generator = VietnameseEmbeddingGenerator()
    
    try:
        results = generator.generate_complete_embeddings()
        
        print("\n🎉 Embedding Generation Summary:")
        print(f"   - Embeddings shape: {results['embeddings_shape']}")
        print(f"   - Model used: {results['model_used']}")
        print(f"   - Validation passed: {results['validation_passed']}")
        print(f"   - Output files: {len(results['output_files'])}")
        
        for file in results['output_files']:
            print(f"     ✓ {file}")
            
    except Exception as e:
        logger.error(f"❌ Embedding generation failed: {e}")
        raise


if __name__ == "__main__":
    main()