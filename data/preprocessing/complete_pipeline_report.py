#!/usr/bin/env python3
"""
Complete pipeline execution script: pdf->raw->processed->embeddings
Final report and data source validation
"""

import json
import os
from datetime import datetime
from typing import Dict

def load_json_file(file_path: str) -> Dict:
    """Load JSON file safely"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

def validate_data_sources():
    """Validate that all data sources listed in violations.json exist and are accessible"""
    
    violations_file = r"c:\Users\Mr Hieu\Documents\vietnamese-traffic-law-qa\data\processed\violations.json"
    violations_data = load_json_file(violations_file)
    
    if not violations_data:
        print("Error: Could not load violations.json")
        return False
    
    data_sources = violations_data.get('metadata', {}).get('data_sources', [])
    base_path = r"c:\Users\Mr Hieu\Documents\vietnamese-traffic-law-qa"
    
    print("Validating data sources...")
    all_sources_valid = True
    
    for source in data_sources:
        full_path = os.path.join(base_path, source)
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            print(f"✓ {source} - {file_size:,} bytes")
        else:
            print(f"✗ {source} - FILE NOT FOUND")
            all_sources_valid = False
    
    return all_sources_valid

def generate_pipeline_report():
    """Generate comprehensive pipeline report"""
    
    # File paths
    violations_file = r"c:\Users\Mr Hieu\Documents\vietnamese-traffic-law-qa\data\processed\violations.json"
    embeddings_file = r"c:\Users\Mr Hieu\Documents\vietnamese-traffic-law-qa\data\embeddings\violations_for_embeddings.json"
    stats_file = r"c:\Users\Mr Hieu\Documents\vietnamese-traffic-law-qa\data\embeddings\violations_summary_stats.json"
    
    # Load data
    violations_data = load_json_file(violations_file)
    embeddings_data = load_json_file(embeddings_file)
    stats_data = load_json_file(stats_file)
    
    # Generate report
    report = {
        "pipeline_report": {
            "generated_date": datetime.now().isoformat(),
            "pipeline_stages": "pdf->raw->processed->embeddings",
            "status": "COMPLETED"
        },
        "data_sources_validation": {
            "sources_validated": True,
            "total_sources": len(violations_data.get('metadata', {}).get('data_sources', [])),
            "source_documents": violations_data.get('metadata', {}).get('source_documents', []),
            "data_sources": violations_data.get('metadata', {}).get('data_sources', [])
        },
        "violations_processing": {
            "total_violations": violations_data.get('metadata', {}).get('total_violations', 0),
            "last_processed": violations_data.get('metadata', {}).get('processed_date', ''),
            "validation_summary": violations_data.get('metadata', {}).get('validation_summary', {}),
            "merge_summary": violations_data.get('metadata', {}).get('merge_summary', {})
        },
        "embeddings_preparation": {
            "total_records": embeddings_data.get('metadata', {}).get('total_records', 0),
            "prepared_date": embeddings_data.get('metadata', {}).get('prepared_date', ''),
            "text_fields_combined": embeddings_data.get('metadata', {}).get('text_fields_combined', [])
        },
        "statistics": {
            "categories": stats_data.get('categories', {}),
            "severities": stats_data.get('severities', {}),
            "documents": stats_data.get('documents', {}),
            "avg_description_length": stats_data.get('avg_description_length', 0),
            "top_keywords": sorted(stats_data.get('keywords_distribution', {}).items(), 
                                 key=lambda x: x[1], reverse=True)[:10]
        },
        "data_quality": {
            "legal_reference_accuracy": violations_data.get('metadata', {}).get('validation_summary', {}).get('legal_reference_accuracy', 0),
            "fine_consistency_rate": violations_data.get('metadata', {}).get('validation_summary', {}).get('fine_consistency_rate', 0),
            "violations_with_keywords": len([v for v in violations_data.get('violations', []) if v.get('keywords')]),
            "violations_categorized": len([v for v in violations_data.get('violations', []) if v.get('category', '') != 'Chưa phân loại'])
        },
        "next_steps": [
            "Generate vector embeddings using Vietnamese language model",
            "Set up semantic search engine (Chroma/Pinecone)",
            "Implement API endpoints for violation lookup",
            "Create user interface for natural language queries",
            "Add more legal documents (Nghị định 168/2024)"
        ]
    }
    
    # Save report
    report_file = r"c:\Users\Mr Hieu\Documents\vietnamese-traffic-law-qa\data\PIPELINE_FINAL_REPORT.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return report, report_file

def print_final_summary(report: Dict):
    """Print comprehensive final summary"""
    
    print("\n" + "="*80)
    print("         VIETNAMESE TRAFFIC LAW Q&A - PIPELINE COMPLETION REPORT")
    print("="*80)
    
    print(f"\n📅 Pipeline Completed: {report['pipeline_report']['generated_date']}")
    print(f"🔄 Pipeline Stages: {report['pipeline_report']['pipeline_stages']}")
    print(f"✅ Status: {report['pipeline_report']['status']}")
    
    print(f"\n📊 DATA PROCESSING SUMMARY:")
    print(f"   • Total Violations Processed: {report['violations_processing']['total_violations']:,}")
    print(f"   • Source Documents: {len(report['data_sources_validation']['source_documents'])}")
    print(f"   • Data Sources: {report['data_sources_validation']['total_sources']}")
    print(f"   • New Violations Added: {report['violations_processing'].get('merge_summary', {}).get('new_violations_added', 0)}")
    
    print(f"\n🎯 DATA QUALITY METRICS:")
    print(f"   • Legal Reference Accuracy: {report['data_quality']['legal_reference_accuracy']:.1f}%")
    print(f"   • Fine Consistency Rate: {report['data_quality']['fine_consistency_rate']:.1f}%")
    print(f"   • Violations with Keywords: {report['data_quality']['violations_with_keywords']:,}")
    print(f"   • Violations Categorized: {report['data_quality']['violations_categorized']:,}")
    
    print(f"\n📈 STATISTICS:")
    print(f"   • Total Categories: {len(report['statistics']['categories'])}")
    print(f"   • Total Severities: {len(report['statistics']['severities'])}")
    print(f"   • Average Description Length: {report['statistics']['avg_description_length']:.1f} characters")
    
    print(f"\n🔝 TOP CATEGORIES:")
    top_categories = sorted(report['statistics']['categories'].items(), key=lambda x: x[1], reverse=True)[:5]
    for category, count in top_categories:
        print(f"   • {category}: {count} violations")
    
    print(f"\n🏷️ TOP KEYWORDS:")
    for keyword, count in report['statistics']['top_keywords'][:5]:
        print(f"   • {keyword}: {count} violations")
    
    print(f"\n📋 DOCUMENTS PROCESSED:")
    for doc, count in report['statistics']['documents'].items():
        if doc != 'Unknown':
            print(f"   • {doc}: {count} violations")
    
    print(f"\n🚀 READY FOR NEXT STEPS:")
    for i, step in enumerate(report['next_steps'], 1):
        print(f"   {i}. {step}")
    
    print(f"\n✅ Pipeline completed successfully! All data is now ready for embeddings generation.")
    print("="*80)

def main():
    """Main execution function"""
    
    print("Starting final pipeline validation and reporting...")
    
    # Validate data sources
    if not validate_data_sources():
        print("❌ Data source validation failed. Please check missing files.")
        return
    
    print("✅ All data sources validated successfully.")
    
    # Generate final report
    report, report_file = generate_pipeline_report()
    
    print(f"📄 Final report saved to: {report_file}")
    
    # Print summary
    print_final_summary(report)
    
    # Update violations.json with final pipeline status
    violations_file = r"c:\Users\Mr Hieu\Documents\vietnamese-traffic-law-qa\data\processed\violations.json"
    violations_data = load_json_file(violations_file)
    
    violations_data['metadata']['pipeline_status'] = 'COMPLETED'
    violations_data['metadata']['pipeline_completion_date'] = datetime.now().isoformat()
    violations_data['metadata']['final_report_path'] = report_file
    
    with open(violations_file, 'w', encoding='utf-8') as f:
        json.dump(violations_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 Pipeline execution completed successfully!")

if __name__ == "__main__":
    main()