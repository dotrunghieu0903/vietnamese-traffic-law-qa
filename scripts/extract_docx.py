#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to extract text content from DOCX file
"""

from docx import Document
import json

def extract_docx_content(docx_path):
    """Extract text content from DOCX file"""
    try:
        doc = Document(docx_path)
        
        # Extract all paragraphs
        content = []
        for para in doc.paragraphs:
            if para.text.strip():  # Only non-empty paragraphs
                content.append(para.text.strip())
        
        # Extract tables if any
        tables_content = []
        for table in doc.tables:
            table_data = []
            for row in table.rows:
                row_data = []
                for cell in row.cells:
                    row_data.append(cell.text.strip())
                table_data.append(row_data)
            tables_content.append(table_data)
        
        return {
            "text_content": content,
            "tables": tables_content
        }
    
    except Exception as e:
        print(f"Error reading DOCX file: {e}")
        return None

if __name__ == "__main__":
    docx_path = r"c:\Users\Mr Hieu\Documents\vietnamese-traffic-law-qa\docs\ND100-2019.docx"
    output_path = r"c:\Users\Mr Hieu\Documents\vietnamese-traffic-law-qa\docs\ND100-2019-extracted.json"
    
    content = extract_docx_content(docx_path)
    
    if content:
        # Save to JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        
        print(f"Content successfully extracted to: {output_path}")
        
        # Also print the content to console
        print("\n=== EXTRACTED CONTENT ===")
        for i, para in enumerate(content["text_content"], 1):
            print(f"{i}. {para}")
        
        if content["tables"]:
            print("\n=== TABLES ===")
            for i, table in enumerate(content["tables"], 1):
                print(f"\nTable {i}:")
                for row in table:
                    print(" | ".join(row))
    else:
        print("Failed to extract content from DOCX file")