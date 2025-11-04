#!/usr/bin/env python3
"""
Script to generate embeddings for violations data - final stage of pipeline: pdf->raw->processed->embeddings
"""

import json
import os
from datetime import datetime
from typing import Dict, List

def load_json_file(file_path: str) -> Dict:
    """Load JSON file safely"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

def prepare_embeddings_data():
    """Prepare data for embeddings generation"""
    
    violations_file = r"c:\Users\Mr Hieu\Documents\vietnamese-traffic-law-qa\data\processed\violations.json"
    embeddings_dir = r"c:\Users\Mr Hieu\Documents\vietnamese-traffic-law-qa\data\embeddings"
    
    # Create embeddings directory if it doesn't exist
    os.makedirs(embeddings_dir, exist_ok=True)
    
    print("Loading violations.json...")
    violations_data = load_json_file(violations_file)
    
    if not violations_data:
        print("Error: Could not load violations.json")
        return
    
    violations = violations_data.get('violations', [])
    print(f"Preparing {len(violations)} violations for embeddings...")
    
    # Prepare data for embeddings
    embeddings_input = []
    
    for violation in violations:
        # Create comprehensive text for embedding
        description = violation.get('description', '')
        category = violation.get('category', '')
        keywords = ' '.join(violation.get('keywords', []))
        legal_basis = violation.get('legal_basis', {}).get('full_reference', '')
        severity = violation.get('severity', '')
        penalty_text = violation.get('penalty', {}).get('fine_text', '')
        
        # Combine all text for embedding
        embedding_text = f"{description} {category} {keywords} {legal_basis} {severity} {penalty_text}".strip()
        
        # Create embedding input record
        embedding_record = {
            'id': violation.get('id'),
            'text': embedding_text,
            'metadata': {
                'description': description,
                'category': category,
                'legal_basis': legal_basis,
                'severity': severity,
                'keywords': violation.get('keywords', []),
                'penalty': violation.get('penalty', {}),
                'additional_measures': violation.get('additional_measures', [])
            }
        }
        
        embeddings_input.append(embedding_record)
    
    # Save embeddings input data
    embeddings_input_file = os.path.join(embeddings_dir, 'violations_for_embeddings.json')
    
    embeddings_data = {
        'metadata': {
            'total_records': len(embeddings_input),
            'source_file': 'violations.json',
            'prepared_date': datetime.now().isoformat(),
            'pipeline_stage': 'embeddings_preparation',
            'text_fields_combined': ['description', 'category', 'keywords', 'legal_basis', 'severity', 'penalty_text']
        },
        'records': embeddings_input
    }
    
    with open(embeddings_input_file, 'w', encoding='utf-8') as f:
        json.dump(embeddings_data, f, ensure_ascii=False, indent=2)
    
    print(f"Saved embeddings input data to: {embeddings_input_file}")
    
    # Create summary statistics
    summary_stats = {
        'total_violations': len(violations),
        'categories': {},
        'severities': {},
        'documents': {},
        'avg_description_length': 0,
        'keywords_distribution': {}
    }
    
    # Calculate statistics
    total_desc_length = 0
    for violation in violations:
        # Categories
        category = violation.get('category', 'Unknown')
        summary_stats['categories'][category] = summary_stats['categories'].get(category, 0) + 1
        
        # Severities
        severity = violation.get('severity', 'Unknown')
        summary_stats['severities'][severity] = summary_stats['severities'].get(severity, 0) + 1
        
        # Documents
        doc = violation.get('legal_basis', {}).get('document', 'Unknown')
        summary_stats['documents'][doc] = summary_stats['documents'].get(doc, 0) + 1
        
        # Description length
        desc_length = len(violation.get('description', ''))
        total_desc_length += desc_length
        
        # Keywords
        for keyword in violation.get('keywords', []):
            summary_stats['keywords_distribution'][keyword] = summary_stats['keywords_distribution'].get(keyword, 0) + 1
    
    summary_stats['avg_description_length'] = round(total_desc_length / len(violations), 2) if violations else 0
    
    # Save summary statistics
    summary_file = os.path.join(embeddings_dir, 'violations_summary_stats.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary_stats, f, ensure_ascii=False, indent=2)
    
    print(f"Saved summary statistics to: {summary_file}")
    
    # Update violations.json metadata to indicate embeddings preparation
    violations_data['metadata']['pipeline_stage'] = 'embeddings_ready'
    violations_data['metadata']['embeddings_prepared_date'] = datetime.now().isoformat()
    violations_data['metadata']['embeddings_input_file'] = embeddings_input_file
    
    with open(violations_file, 'w', encoding='utf-8') as f:
        json.dump(violations_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nEmbeddings Preparation Complete:")
    print(f"- Total violations prepared: {len(violations)}")
    print(f"- Categories: {len(summary_stats['categories'])}")
    print(f"- Severities: {len(summary_stats['severities'])}")
    print(f"- Average description length: {summary_stats['avg_description_length']} characters")
    print(f"- Most common keywords: {sorted(summary_stats['keywords_distribution'].items(), key=lambda x: x[1], reverse=True)[:5]}")
    
    return embeddings_input_file, summary_file

if __name__ == "__main__":
    prepare_embeddings_data()