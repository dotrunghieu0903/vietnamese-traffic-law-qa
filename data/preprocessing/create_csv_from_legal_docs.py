#!/usr/bin/env python3
"""
Script tạo file CSV từ mỗi file JSON nghị định trong raw/legal_documents
Tạo 1 file CSV tương ứng cho mỗi nghị định trong violations_dataset folder
"""

import os
import json
import pandas as pd
from pathlib import Path
import re

def extract_violations_from_nd_100_2019(data, document_name):
    """
    Extract violations từ Nghị định 100/2019 (base document với key_articles structure)
    """
    violations = []
    
    if 'key_articles' not in data:
        return violations
    
    for article_key, article_data in data['key_articles'].items():
        if isinstance(article_data, dict) and 'sections' in article_data:
            article_title = article_data.get('title', '')
            
            for section in article_data['sections']:
                section_name = section.get('section', '')
                fine_range = section.get('fine_range', '')
                additional_measures = section.get('additional_measures', [])
                
                # Get violations from this section
                section_violations = section.get('violations', [])
                
                for i, violation_desc in enumerate(section_violations):
                    violation_record = {
                        'violation_id': f"{article_key}_{section_name}_{i+1}".replace(' ', '_'),
                        'description': violation_desc,
                        'fine_amount': fine_range,
                        'additional_penalty': '; '.join(additional_measures) if additional_measures else '',
                        'legal_basis': f"Nghị định 100/2019/NĐ-CP - {article_key.upper().replace('_', ' ')}",
                        'article': article_key.upper().replace('_', ' '),
                        'article_title': article_title,
                        'section': section_name,
                        'source_document': document_name,
                        'document_type': 'base_regulation',
                        'effective_date': data.get('document_info', {}).get('effective_date', ''),
                        'issued_date': data.get('document_info', {}).get('issued_date', '')
                    }
                    violations.append(violation_record)
    
    return violations

def extract_violations_from_nd_123_2021(data, document_name):
    """
    Extract violations từ Nghị định 123/2021 (amendment document)
    """
    violations = []
    
    # Check for key_articles structure (similar to ND 100)
    if 'key_articles' in data:
        for article_key, article_data in data['key_articles'].items():
            if isinstance(article_data, dict) and 'sections' in article_data:
                article_title = article_data.get('title', '')
                
                for section in article_data['sections']:
                    section_name = section.get('section', '')
                    fine_range = section.get('fine_range', '')
                    additional_measures = section.get('additional_measures', [])
                    section_violations = section.get('violations', [])
                    
                    for i, violation_desc in enumerate(section_violations):
                        violation_record = {
                            'violation_id': f"{article_key}_{section_name}_{i+1}".replace(' ', '_'),
                            'description': violation_desc,
                            'fine_amount': fine_range,
                            'additional_penalty': '; '.join(additional_measures) if additional_measures else '',
                            'legal_basis': f"Nghị định 123/2021/NĐ-CP - {article_key.upper().replace('_', ' ')}",
                            'article': article_key.upper().replace('_', ' '),
                            'article_title': article_title,
                            'section': section_name,
                            'source_document': document_name,
                            'document_type': 'amendment',
                            'amendment_type': section.get('amendment_type', 'update'),
                            'target_article': section.get('target_article', ''),
                            'old_fine': section.get('old_fine', ''),
                            'new_fine': section.get('new_fine', ''),
                            'effective_date': data.get('document_info', {}).get('effective_date', ''),
                            'issued_date': data.get('document_info', {}).get('issued_date', '')
                        }
                        violations.append(violation_record)
    
    # Check for violation_updates structure
    elif 'violation_updates' in data:
        for update in data['violation_updates']:
            violation_record = {
                'violation_id': update.get('violation_id', f"update_{len(violations)+1}"),
                'description': update.get('updated_description', update.get('description', '')),
                'fine_amount': update.get('new_fine_amount', update.get('fine_amount', '')),
                'additional_penalty': update.get('additional_penalty', ''),
                'legal_basis': update.get('legal_basis', ''),
                'article': update.get('article_reference', ''),
                'source_document': document_name,
                'document_type': 'amendment',
                'amendment_type': update.get('change_type', 'update'),
                'original_fine': update.get('original_fine_amount', ''),
                'effective_date': update.get('effective_date', ''),
                'issued_date': data.get('document_info', {}).get('issued_date', '')
            }
            violations.append(violation_record)
    
    return violations

def extract_violations_from_nd_168_2024(data, document_name):
    """
    Extract violations từ Nghị định 168/2024 (newer amendment document)
    """
    violations = []
    
    # Check for new_violations structure
    if 'new_violations' in data:
        for violation in data['new_violations']:
            violation_record = {
                'violation_id': violation.get('violation_code', f"168_{len(violations)+1}"),
                'description': violation.get('description', ''),
                'fine_amount': violation.get('fine_range', ''),
                'additional_penalty': '; '.join(violation.get('additional_measures', [])),
                'legal_basis': f"Nghị định 168/2024/NĐ-CP",
                'article': violation.get('violation_code', ''),
                'article_title': violation.get('category', ''),
                'section': '',
                'source_document': document_name,
                'document_type': 'new_amendment',
                'category': violation.get('category', ''),
                'severity_level': violation.get('severity_level', ''),
                'effective_date': data.get('effective_date', ''),
                'issued_date': data.get('issue_date', '')
            }
            violations.append(violation_record)
    
    # Check for key_changes structure
    if 'key_changes' in data:
        for change in data['key_changes']:
            if change.get('change_type') in ['Tăng mức phạt', 'Tăng mức phạt nghiêm trọng', 'Mới']:
                violation_record = {
                    'violation_id': f"change_{change.get('article_modified', '')}_1".replace(' ', '_'),
                    'description': change.get('description', ''),
                    'fine_amount': change.get('new_fine', change.get('fine_range', '')),
                    'additional_penalty': '; '.join(change.get('additional_measures', [])),
                    'legal_basis': f"Nghị định 168/2024/NĐ-CP - {change.get('article_modified', '')}",
                    'article': change.get('article_modified', ''),
                    'article_title': change.get('description', ''),
                    'section': '',
                    'source_document': document_name,
                    'document_type': 'amendment_change',
                    'amendment_type': change.get('change_type', ''),
                    'old_fine': change.get('old_fine', ''),
                    'new_fine': change.get('new_fine', ''),
                    'effective_date': data.get('effective_date', ''),
                    'issued_date': data.get('issue_date', '')
                }
                violations.append(violation_record)
    
    return violations

def process_legal_document(json_file_path):
    """
    Process một legal document JSON file và extract violations
    """
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Get document name from filename
    document_name = Path(json_file_path).stem
    
    # Determine document type and extract violations accordingly
    if '100_2019' in document_name:
        violations = extract_violations_from_nd_100_2019(data, document_name)
    elif '123_2021' in document_name:
        violations = extract_violations_from_nd_123_2021(data, document_name)
    elif '168_2024' in document_name:
        violations = extract_violations_from_nd_168_2024(data, document_name)
    else:
        print(f"⚠️ Unknown document format: {document_name}")
        violations = []
    
    return violations, data

def create_csv_from_json():
    """
    Main function để tạo CSV files từ JSON files
    """
    print("🔧 CREATING CSV FILES FROM LEGAL DOCUMENTS JSON")
    print("=" * 55)
    
    # Paths
    legal_docs_dir = Path("../raw/legal_documents")
    violations_dataset_dir = Path("../raw/violations_dataset")
    
    # Create output directory if not exists
    violations_dataset_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all JSON files
    json_files = list(legal_docs_dir.glob("*.json"))
    
    if not json_files:
        print("❌ No JSON files found in legal_documents directory")
        return
    
    print(f"📚 Found {len(json_files)} legal documents:")
    for json_file in json_files:
        print(f"   📄 {json_file.name}")
    
    total_violations = 0
    processed_files = []
    
    for json_file in json_files:
        print(f"\n🔄 Processing: {json_file.name}")
        
        try:
            # Extract violations from JSON
            violations, doc_data = process_legal_document(json_file)
            
            if violations:
                # Create DataFrame
                df = pd.DataFrame(violations)
                
                # Define output CSV filename
                csv_filename = f"{json_file.stem}_violations.csv"
                csv_path = violations_dataset_dir / csv_filename
                
                # Save to CSV
                df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                
                print(f"  ✅ Created: {csv_filename}")
                print(f"     📊 Violations: {len(violations)}")
                print(f"     📁 Location: {csv_path}")
                
                # Show document info
                doc_info = doc_data.get('document_info', doc_data)
                title = doc_info.get('title', doc_info.get('title', 'Unknown'))
                effective_date = doc_info.get('effective_date', doc_data.get('effective_date', 'Unknown'))
                
                print(f"     📋 Title: {title}")
                print(f"     📅 Effective: {effective_date}")
                
                # Show sample violations
                if len(violations) > 0:
                    sample = violations[0]
                    print(f"     🔍 Sample: {sample.get('description', 'No description')[:60]}...")
                
                total_violations += len(violations)
                processed_files.append((csv_filename, len(violations)))
                
            else:
                print(f"  ⚠️ No violations found in {json_file.name}")
                
        except Exception as e:
            print(f"  ❌ Error processing {json_file.name}: {e}")
    
    # Summary
    print(f"\n📊 PROCESSING SUMMARY")
    print("=" * 30)
    print(f"📚 Documents processed: {len(json_files)}")
    print(f"📄 CSV files created: {len(processed_files)}")
    print(f"📋 Total violations: {total_violations}")
    
    print(f"\n📁 Created CSV files:")
    for filename, count in processed_files:
        print(f"   📄 {filename}: {count} violations")
    
    # Show file structure
    print(f"\n📂 OUTPUT DIRECTORY: {violations_dataset_dir}")
    csv_files = list(violations_dataset_dir.glob("*.csv"))
    for csv_file in csv_files:
        size_kb = csv_file.stat().st_size / 1024
        print(f"   📄 {csv_file.name} ({size_kb:.1f} KB)")

def main():
    """Main function"""
    print("🚀 LEGAL DOCUMENTS TO CSV CONVERTER")
    print("=" * 45)
    print("Purpose: Create individual CSV files for each legal document")
    print("Input: raw/legal_documents/*.json")
    print("Output: raw/violations_dataset/*_violations.csv")
    
    # Change to preprocessing directory
    os.chdir("c:/Users/hieudt22/Documents/VNI-TrafficLawQA/data/preprocessing")
    
    # Process documents
    create_csv_from_json()
    
    print(f"\n✅ CONVERSION COMPLETE!")
    print("Each legal document now has its corresponding CSV file in violations_dataset.")

if __name__ == "__main__":
    main()