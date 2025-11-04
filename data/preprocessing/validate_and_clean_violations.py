#!/usr/bin/env python3
"""
Script to update validation and clean data according to pipeline: pdf->raw->processed->embeddings
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Set

def load_json_file(file_path: str) -> Dict:
    """Load JSON file safely"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

def validate_legal_reference(legal_basis: Dict) -> bool:
    """Validate if legal reference is properly formatted"""
    if not legal_basis:
        return False
    
    article = legal_basis.get('article', '')
    document = legal_basis.get('document', '')
    full_reference = legal_basis.get('full_reference', '')
    
    # Check if has basic components
    if not article or not full_reference:
        return False
    
    # Check for common patterns
    valid_patterns = [
        r'Điều \d+',  # Điều X
        r'Khoản \d+',  # Khoản X
        r'Nghị định \d+',  # Nghị định X
        r'NĐ-CP'  # NĐ-CP
    ]
    
    has_valid_pattern = any(re.search(pattern, full_reference) for pattern in valid_patterns)
    return has_valid_pattern

def validate_fine_consistency(penalty: Dict) -> bool:
    """Check if fine information is consistent"""
    fine_min = penalty.get('fine_min', 0)
    fine_max = penalty.get('fine_max', 0)
    fine_text = penalty.get('fine_text', '')
    
    # If no numeric values, check if text indicates undefined
    if fine_min == 0 and fine_max == 0:
        return fine_text in ['Chưa xác định', 'Không áp dụng']
    
    # If has numeric values, they should be positive and min <= max
    if fine_min > 0 or fine_max > 0:
        return fine_min <= fine_max and fine_min >= 0 and fine_max >= 0
    
    return True

def extract_keywords_from_description(description: str) -> List[str]:
    """Extract relevant keywords from violation description"""
    keywords = []
    
    keyword_map = {
        'helmet': ['mũ bảo hiểm', 'nón bảo hiểm'],
        'license': ['giấy phép', 'bằng lái', 'GPLX'],
        'speed': ['tốc độ', 'km/h', 'vượt tốc'],
        'alcohol': ['rượu', 'bia', 'cồn', 'say'],
        'phone': ['điện thoại', 'di động'],
        'traffic_light': ['đèn đỏ', 'đèn tín hiệu', 'đèn giao thông'],
        'parking': ['đỗ xe', 'dừng xe', 'đậu xe'],
        'overtaking': ['vượt xe', 'vượt qua'],
        'direction': ['ngược chiều', 'một chiều'],
        'passenger': ['hành khách', 'chở người'],
        'loading': ['chở hàng', 'tải trọng'],
        'racing': ['đua xe']
    }
    
    description_lower = description.lower()
    for keyword, phrases in keyword_map.items():
        if any(phrase in description_lower for phrase in phrases):
            keywords.append(keyword)
    
    return keywords

def categorize_violation(description: str, legal_basis: Dict) -> str:
    """Categorize violation based on description and legal basis"""
    desc_lower = description.lower()
    article = legal_basis.get('article', '').lower()
    
    # Define category patterns
    categories = {
        'Giấy tờ': ['giấy phép', 'bằng lái', 'đăng ký', 'kiểm định', 'bảo hiểm'],
        'Tốc độ': ['tốc độ', 'km/h', 'vượt tốc'],
        'Tín hiệu giao thông': ['đèn đỏ', 'đèn tín hiệu', 'đèn giao thông', 'đèn vàng'],
        'Chất có cồn': ['rượu', 'bia', 'cồn', 'say'],
        'Trang bị bảo hộ': ['mũ bảo hiểm', 'dây an toàn', 'nón bảo hiểm'],
        'Dừng đỗ xe': ['đỗ xe', 'dừng xe', 'đậu xe', 'vỉa hè'],
        'Vượt xe': ['vượt xe', 'vượt qua'],
        'Hành vi điều khiển': ['điều khiển', 'lái xe', 'buồn ngủ', 'một tay'],
        'Chở hàng': ['chở hàng', 'tải trọng', 'che đậy'],
        'Đua xe': ['đua xe'],
        'Mô tô, xe gắn máy': ['xe máy', 'mô tô', 'xe gắn máy'],
        'Ô tô': ['ô tô', 'xe ô tô']
    }
    
    for category, keywords in categories.items():
        if any(keyword in desc_lower for keyword in keywords):
            return category
    
    # Check by legal article
    if 'điều 5' in article:
        return 'Ô tô - Vi phạm chung'
    elif 'điều 6' in article:
        return 'Mô tô, xe gắn máy'
    elif 'điều 7' in article:
        return 'Ô tô - An toàn'
    elif 'điều 11' in article:
        return 'Dừng đỗ xe'
    
    return 'Chưa phân loại'

def determine_severity(penalty: Dict, additional_measures: List) -> str:
    """Determine violation severity based on penalty and additional measures"""
    fine_max = penalty.get('fine_max', 0)
    has_license_revocation = any('tước' in str(measure).lower() for measure in additional_measures)
    has_vehicle_seizure = any('tạm giữ' in str(measure).lower() or 'tước xe' in str(measure).lower() for measure in additional_measures)
    
    if fine_max == 0:
        return 'Chưa xác định'
    elif fine_max >= 15000000 or has_vehicle_seizure:
        return 'Rất nghiêm trọng'
    elif fine_max >= 4000000 or has_license_revocation:
        return 'Nghiêm trọng'
    elif fine_max >= 1000000:
        return 'Trung bình'
    else:
        return 'Nhẹ'

def clean_and_validate_violations():
    """Main function to clean and validate violations data"""
    
    violations_file = r"c:\Users\Mr Hieu\Documents\vietnamese-traffic-law-qa\data\processed\violations.json"
    
    print("Loading violations.json...")
    violations_data = load_json_file(violations_file)
    
    if not violations_data:
        print("Error: Could not load violations.json")
        return
    
    violations = violations_data.get('violations', [])
    print(f"Processing {len(violations)} violations...")
    
    # Validation counters
    valid_legal_refs = 0
    invalid_legal_refs = 0
    consistent_fines = 0
    inconsistent_fines = 0
    updated_violations = 0
    
    # Process each violation
    for i, violation in enumerate(violations):
        description = violation.get('description', '').strip()
        if not description:
            continue
            
        # Validate and update legal basis
        legal_basis = violation.get('legal_basis', {})
        if validate_legal_reference(legal_basis):
            valid_legal_refs += 1
        else:
            invalid_legal_refs += 1
        
        # Validate penalty consistency
        penalty = violation.get('penalty', {})
        if validate_fine_consistency(penalty):
            consistent_fines += 1
        else:
            inconsistent_fines += 1
        
        # Extract and update keywords
        if not violation.get('keywords'):
            keywords = extract_keywords_from_description(description)
            violation['keywords'] = keywords
            updated_violations += 1
        
        # Update category if not properly set
        current_category = violation.get('category', '')
        if current_category in ['Chưa phân loại', '']:
            new_category = categorize_violation(description, legal_basis)
            violation['category'] = new_category
            updated_violations += 1
        
        # Update severity if not properly set
        current_severity = violation.get('severity', '')
        if current_severity in ['Chưa xác định', 'NaN', '']:
            additional_measures = violation.get('additional_measures', [])
            new_severity = determine_severity(penalty, additional_measures)
            violation['severity'] = new_severity
            updated_violations += 1
        
        # Update search text
        category = violation.get('category', '')
        severity = violation.get('severity', '')
        keywords_text = ' '.join(violation.get('keywords', []))
        legal_ref = legal_basis.get('full_reference', '')
        
        search_text = f"{description} {category} {legal_ref} {severity} {keywords_text}".strip()
        violation['search_text'] = search_text
        
        # Update metadata
        if 'metadata' not in violation:
            violation['metadata'] = {}
        
        violation['metadata']['processed_date'] = datetime.now().isoformat()
        violation['metadata']['pipeline_stage'] = 'validation_and_cleaning'
        
        if i % 50 == 0:
            print(f"Processed {i+1}/{len(violations)} violations...")
    
    # Update validation summary
    violations_data['metadata']['validation_summary'] = {
        'total_violations': len(violations),
        'valid_legal_references': valid_legal_refs,
        'invalid_legal_references': invalid_legal_refs,
        'consistent_fines': consistent_fines,
        'inconsistent_fines': inconsistent_fines,
        'legal_reference_accuracy': round((valid_legal_refs / len(violations)) * 100, 2) if violations else 0,
        'fine_consistency_rate': round((consistent_fines / len(violations)) * 100, 2) if violations else 0,
        'last_validation_date': datetime.now().isoformat(),
        'violations_updated': updated_violations
    }
    
    # Update metadata
    violations_data['metadata']['total_violations'] = len(violations)
    violations_data['metadata']['processed_date'] = datetime.now().isoformat()
    violations_data['metadata']['pipeline_stage'] = 'processed'
    
    # Save updated data
    print(f"Saving updated violations.json...")
    with open(violations_file, 'w', encoding='utf-8') as f:
        json.dump(violations_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nValidation Summary:")
    print(f"- Total violations: {len(violations)}")
    print(f"- Valid legal references: {valid_legal_refs}")
    print(f"- Invalid legal references: {invalid_legal_refs}")
    print(f"- Consistent fines: {consistent_fines}")
    print(f"- Inconsistent fines: {inconsistent_fines}")
    print(f"- Violations updated: {updated_violations}")
    print(f"- Legal reference accuracy: {round((valid_legal_refs / len(violations)) * 100, 2)}%")
    print(f"- Fine consistency rate: {round((consistent_fines / len(violations)) * 100, 2)}%")

if __name__ == "__main__":
    clean_and_validate_violations()