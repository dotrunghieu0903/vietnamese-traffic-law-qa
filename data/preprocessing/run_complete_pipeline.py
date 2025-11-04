"""
Complete Data Processing Pipeline for Vietnamese Traffic Law Q&A System
Execute the full pipeline from legal documents to semantic embeddings
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Add current directory to path for local imports
sys.path.append(os.path.dirname(__file__))

try:
    from violation_processor import ViolationProcessor
    from embedding_generator import VietnameseEmbeddingGenerator
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all preprocessing modules are available")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline_execution.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TrafficLawDataPipeline:
    """Complete data processing pipeline for Vietnamese traffic law system"""
    
    def __init__(self):
        self.pipeline_start_time = datetime.now()
        self.stage_results = {}
        
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are available"""
        logger.info("🔍 Checking pipeline dependencies...")
        
        required_packages = [
            'pandas', 'numpy', 'sentence_transformers', 
            'underthesea', 'chromadb', 'scikit-learn'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logger.error(f"❌ Missing required packages: {missing_packages}")
            logger.info("💡 Install with: pip install " + " ".join(missing_packages))
            return False
        
        logger.info("✅ All dependencies available")
        return True
    
    def verify_data_structure(self) -> bool:
        """Verify required data directories and files exist"""
        logger.info("📁 Verifying data structure...")
        
        required_paths = [
            '../raw/legal_documents',
            '../raw/violations_dataset', 
            '../processed',
            '../embeddings',
            '.'
        ]
        
        missing_paths = []
        for path in required_paths:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
                logger.info(f"📂 Created directory: {path}")
        
        # Check for required source files
        required_files = [
            '../raw/legal_documents/nghi_dinh_100_2019.json',
            '../raw/violations_dataset/traffic_violations_extended.csv'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            logger.error(f"❌ Missing required files: {missing_files}")
            return False
        
        logger.info("✅ Data structure verified")
        return True
    
    def stage_1_legal_document_enhancement(self) -> bool:
        """Stage 1: Enhance legal document structure"""
        logger.info("🚀 Stage 1: Legal Document Enhancement")
        
        try:
            # Import and run the legal document enhancer main function
            from legal_document_enhancer import main as enhance_legal_documents
            enhance_legal_documents()
            
            self.stage_results['stage_1'] = {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'results': {
                    "message": "Legal documents enhanced successfully",
                    "output_file": "../processed/enhanced_legal_document.json"
                }
            }
            
            logger.info("✅ Stage 1 completed: Legal documents enhanced successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Stage 1 failed: {e}")
            self.stage_results['stage_1'] = {
                'status': 'failed',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
            return False
    
    def stage_2_violation_processing(self) -> bool:
        """Stage 2: Process and normalize violation data"""
        logger.info("🚀 Stage 2: Violation Data Processing")
        
        try:
            processor = ViolationProcessor()
            
            # Load data
            legal_doc, violations_df, sample_violations = processor.load_real_data()
            
            # Validate consistency
            validation_report = processor.validate_data_consistency(legal_doc, violations_df)
            
            # Process violations
            processed_violations = processor.normalize_violations_from_real_data(legal_doc, violations_df)
            
            # Save results
            processor.save_processed_data_real_format(processed_violations, validation_report)
            
            self.stage_results['stage_2'] = {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'results': {
                    'total_violations': len(processed_violations),
                    'validation_summary': validation_report.get('summary', {}),
                    'output_files': ['violations.json', 'validation_report.json', 'processing_statistics.json']
                }
            }
            
            logger.info(f"✅ Stage 2 completed: Processed {len(processed_violations)} violations")
            return True
            
        except Exception as e:
            logger.error(f"❌ Stage 2 failed: {e}")
            self.stage_results['stage_2'] = {
                'status': 'failed',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
            return False
    
    def stage_3_embedding_generation(self) -> bool:
        """Stage 3: Generate semantic embeddings"""
        logger.info("🚀 Stage 3: Semantic Embeddings Generation")
        
        try:
            generator = VietnameseEmbeddingGenerator()
            results = generator.generate_complete_embeddings()
            
            self.stage_results['stage_3'] = {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'results': results
            }
            
            logger.info(f"✅ Stage 3 completed: Generated embeddings with shape {results['embeddings_shape']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Stage 3 failed: {e}")
            self.stage_results['stage_3'] = {
                'status': 'failed', 
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
            return False
    
    def generate_pipeline_report(self):
        """Generate comprehensive pipeline execution report"""
        pipeline_end_time = datetime.now()
        execution_time = pipeline_end_time - self.pipeline_start_time
        
        report = {
            "pipeline_info": {
                "name": "Vietnamese Traffic Law Data Processing Pipeline",
                "version": "1.0.0",
                "execution_date": self.pipeline_start_time.isoformat(),
                "completion_date": pipeline_end_time.isoformat(),
                "total_execution_time": str(execution_time)
            },
            "stage_results": self.stage_results,
            "pipeline_summary": {
                "total_stages": 3,
                "successful_stages": len([s for s in self.stage_results.values() if s['status'] == 'success']),
                "failed_stages": len([s for s in self.stage_results.values() if s['status'] == 'failed']),
                "overall_status": "success" if all(s['status'] == 'success' for s in self.stage_results.values()) else "partial_failure"
            },
            "output_directories": {
                "processed_data": "../processed/",
                "embeddings": "../embeddings/", 
                "logs": "pipeline_execution.log"
            }
        }
        
        # Save report
        report_file = 'pipeline_execution_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📊 Pipeline execution report saved to: {report_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("🎉 VIETNAMESE TRAFFIC LAW DATA PIPELINE SUMMARY")
        print("="*60)
        print(f"📅 Execution Time: {execution_time}")
        print(f"✅ Successful Stages: {report['pipeline_summary']['successful_stages']}/3")
        print(f"📊 Overall Status: {report['pipeline_summary']['overall_status'].upper()}")
        
        for stage_name, stage_data in self.stage_results.items():
            status_emoji = "✅" if stage_data['status'] == 'success' else "❌"
            print(f"{status_emoji} {stage_name.replace('_', ' ').title()}: {stage_data['status'].upper()}")
            
            if stage_data['status'] == 'success' and 'results' in stage_data:
                results = stage_data['results']
                if 'total_violations' in results:
                    print(f"   📊 Processed {results['total_violations']} violations")
                if 'embeddings_shape' in results:
                    print(f"   🔢 Generated embeddings: {results['embeddings_shape']}")
        
        print("\n📁 Output Files:")
        if os.path.exists('../processed/violations.json'):
            print("   ✓ ../processed/violations.json - Normalized violations data")
        if os.path.exists('../embeddings/vietnamese_traffic_embeddings.npy'):
            print("   ✓ ../embeddings/vietnamese_traffic_embeddings.npy - Semantic embeddings")
        if os.path.exists('../embeddings/chromadb_format.json'):
            print("   ✓ ../embeddings/chromadb_format.json - ChromaDB ready format")
        
        print("\n💡 Next Steps:")
        print("   1. Test semantic search with generated embeddings")
        print("   2. Deploy ChromaDB with embeddings data")
        print("   3. Launch Streamlit interface for Q&A system")
        print("="*60)
        
        return report
    
    def execute_complete_pipeline(self) -> bool:
        """Execute the complete data processing pipeline"""
        logger.info("🚀 Starting Vietnamese Traffic Law Data Processing Pipeline")
        
        # Check dependencies
        if not self.check_dependencies():
            return False
        
        # Verify data structure
        if not self.verify_data_structure():
            return False
        
        # Execute stages
        stages = [
            ("Legal Document Enhancement", self.stage_1_legal_document_enhancement),
            ("Violation Data Processing", self.stage_2_violation_processing),
            ("Semantic Embeddings Generation", self.stage_3_embedding_generation)
        ]
        
        for stage_name, stage_function in stages:
            logger.info(f"▶️ Executing: {stage_name}")
            success = stage_function()
            
            if not success:
                logger.error(f"❌ Pipeline stopped at: {stage_name}")
                break
        
        # Generate final report
        report = self.generate_pipeline_report()
        
        return report['pipeline_summary']['overall_status'] == 'success'


def main():
    """Main function to execute the pipeline"""
    pipeline = TrafficLawDataPipeline()
    
    try:
        success = pipeline.execute_complete_pipeline()
        
        if success:
            logger.info("🎉 Pipeline completed successfully!")
            return 0
        else:
            logger.error("❌ Pipeline completed with errors")
            return 1
            
    except KeyboardInterrupt:
        logger.info("⏹️ Pipeline execution interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"💥 Pipeline execution failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)