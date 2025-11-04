#!/usr/bin/env python3
"""
Script phân tích và báo cáo các file CSV đã tạo từ legal documents
"""

import os
import pandas as pd
from pathlib import Path

def analyze_violations_csv():
    """
    Phân tích các file CSV violations đã tạo
    """
    print("📊 ANALYSIS OF CREATED CSV FILES")
    print("=" * 40)
    
    violations_dir = Path("../raw/violations_dataset")
    csv_files = list(violations_dir.glob("*_violations.csv"))
    
    if not csv_files:
        print("❌ No CSV files found")
        return
    
    print(f"📂 Found {len(csv_files)} CSV files:")
    
    total_violations = 0
    document_summary = {}
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            size_kb = csv_file.stat().st_size / 1024
            
            print(f"\n📄 {csv_file.name}")
            print(f"   📏 Size: {size_kb:.1f} KB")
            print(f"   📊 Violations: {len(df)}")
            print(f"   📋 Columns: {len(df.columns)}")
            
            # Show document info
            if 'source_document' in df.columns:
                source_doc = df['source_document'].iloc[0] if len(df) > 0 else 'Unknown'
                print(f"   📚 Source: {source_doc}")
            
            if 'document_type' in df.columns:
                doc_types = df['document_type'].value_counts()
                print(f"   📂 Types: {dict(doc_types)}")
            
            if 'effective_date' in df.columns:
                effective_date = df['effective_date'].iloc[0] if len(df) > 0 else 'Unknown'
                print(f"   📅 Effective: {effective_date}")
            
            # Show sample violations
            if len(df) > 0:
                sample_desc = df['description'].iloc[0]
                print(f"   🔍 Sample: {sample_desc[:50]}...")
                
                # Fine examples
                if 'fine_amount' in df.columns:
                    unique_fines = df['fine_amount'].dropna().unique()[:3]
                    print(f"   💰 Fine examples: {list(unique_fines)}")
            
            total_violations += len(df)
            document_summary[csv_file.stem] = {
                'violations': len(df),
                'size_kb': size_kb,
                'doc_type': df['document_type'].iloc[0] if 'document_type' in df.columns and len(df) > 0 else 'Unknown'
            }
            
        except Exception as e:
            print(f"   ❌ Error analyzing {csv_file.name}: {e}")
    
    # Summary
    print(f"\n📊 OVERALL SUMMARY")
    print("=" * 25)
    print(f"📚 Total documents: {len(csv_files)}")
    print(f"📋 Total violations: {total_violations}")
    
    # Document breakdown
    print(f"\n📂 Document Breakdown:")
    for doc_name, info in document_summary.items():
        print(f"   📄 {doc_name}: {info['violations']} violations ({info['size_kb']:.1f} KB) - {info['doc_type']}")
    
    # Document types summary
    doc_types_summary = {}
    for info in document_summary.values():
        doc_type = info['doc_type']
        if doc_type not in doc_types_summary:
            doc_types_summary[doc_type] = {'count': 0, 'violations': 0}
        doc_types_summary[doc_type]['count'] += 1
        doc_types_summary[doc_type]['violations'] += info['violations']
    
    print(f"\n📊 By Document Type:")
    for doc_type, stats in doc_types_summary.items():
        print(f"   📂 {doc_type}: {stats['count']} documents, {stats['violations']} violations")

def show_file_structure():
    """
    Hiển thị cấu trúc file cuối cùng
    """
    print(f"\n📁 FINAL FILE STRUCTURE")
    print("=" * 30)
    
    structure = {
        "Legal Documents (Input)": "../raw/legal_documents/*.json",
        "Violations CSVs (Output)": "../raw/violations_dataset/*_violations.csv"
    }
    
    for category, pattern in structure.items():
        print(f"\n📂 {category}:")
        base_path = pattern.split('*')[0]
        glob_pattern = pattern.split('/')[-1]
        
        if os.path.exists(base_path):
            files = list(Path(base_path).glob(glob_pattern))
            for f in sorted(files):
                size_kb = f.stat().st_size / 1024
                print(f"   📄 {f.name} ({size_kb:.1f} KB)")
        else:
            print(f"   ❌ Directory not found: {base_path}")

def compare_violations_across_documents():
    """
    So sánh violations giữa các nghị định
    """
    print(f"\n🔍 COMPARISON ACROSS DOCUMENTS")
    print("=" * 35)
    
    violations_dir = Path("../raw/violations_dataset")
    csv_files = list(violations_dir.glob("*_violations.csv"))
    
    # Load all data
    all_data = {}
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            doc_name = csv_file.stem.replace('_violations', '')
            all_data[doc_name] = df
        except Exception as e:
            print(f"❌ Error loading {csv_file.name}: {e}")
    
    if not all_data:
        print("❌ No data to compare")
        return
    
    # Compare fine ranges
    print(f"💰 Fine Range Comparison:")
    for doc_name, df in all_data.items():
        if 'fine_amount' in df.columns:
            fines = df['fine_amount'].dropna().tolist()
            print(f"   📄 {doc_name}: {len(fines)} fines")
            
            # Extract max fine amounts for comparison
            max_fines = []
            for fine in fines:
                try:
                    # Extract numbers from fine string
                    import re
                    numbers = re.findall(r'[\d,]+', str(fine))
                    if numbers:
                        # Get the highest number
                        max_num = max([int(num.replace(',', '')) for num in numbers])
                        max_fines.append(max_num)
                except:
                    pass
            
            if max_fines:
                avg_max_fine = sum(max_fines) / len(max_fines)
                print(f"      Average max fine: {avg_max_fine:,.0f} VNĐ")
    
    # Compare document evolution
    print(f"\n📅 Document Evolution:")
    doc_dates = {}
    for doc_name, df in all_data.items():
        if 'effective_date' in df.columns and len(df) > 0:
            effective_date = df['effective_date'].iloc[0]
            doc_dates[doc_name] = effective_date
            print(f"   📄 {doc_name}: {effective_date}")
    
    # Show amendment relationships
    print(f"\n🔄 Amendment Relationships:")
    base_docs = [doc for doc in all_data.keys() if '100_2019' in doc]
    amendment_docs = [doc for doc in all_data.keys() if doc not in base_docs]
    
    print(f"   📚 Base documents: {base_docs}")
    print(f"   📝 Amendment documents: {amendment_docs}")

def main():
    """Main function"""
    print("📋 VIOLATIONS CSV ANALYSIS REPORT")
    print("=" * 40)
    
    # Change to preprocessing directory
    os.chdir("c:/Users/hieudt22/Documents/VNI-TrafficLawQA/data/preprocessing")
    
    analyze_violations_csv()
    show_file_structure()
    compare_violations_across_documents()
    
    print(f"\n🎉 ANALYSIS COMPLETE!")
    print("✅ All legal documents successfully converted to CSV format")
    print("📊 Individual CSV files ready for semantic search and analysis")
    print("🔄 Data structure optimized for Vietnamese Traffic Law Q&A system")

if __name__ == "__main__":
    main()