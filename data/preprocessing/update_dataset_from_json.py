#!/usr/bin/env python3
"""
Script để cập nhật dataset CSV với đầy đủ vi phạm từ tất cả các nghị định
Hỗ trợ ND 100/2019, ND 123/2021 và các amendment documents
"""

import pandas as pd
import json
import os
import re
from typing import List, Dict, Any, Tuple

def load_all_legal_documents() -> Dict[str, Dict[str, Any]]:
    """Load tất cả các file JSON legal documents"""
    documents = {}
    
    legal_docs = [
        ("ND_100_2019", "../raw/legal_documents/nghi_dinh_100_2019.json"),
        ("ND_123_2021", "../raw/legal_documents/nghi_dinh_123_2021.json"),
        ("ND_168_2024", "../raw/legal_documents/nghi_dinh_168_2024.json")
    ]
    
    for doc_name, doc_path in legal_docs:
        if os.path.exists(doc_path):
            with open(doc_path, 'r', encoding='utf-8') as f:
                documents[doc_name] = json.load(f)
            print(f"✅ Loaded: {doc_name}")
        else:
            print(f"⚠️ Not found: {doc_path}")
    
    return documents

def parse_fine_range(fine_range: str) -> Tuple[int, int]:
    """Parse fine range string to get min and max amounts"""
    if not fine_range:
        return 0, 0
    
    # Handle various formats
    # Format: "4.000.000 - 5.000.000 đồng"
    pattern1 = r'(\d{1,3}(?:\.\d{3})*)\s*-\s*(\d{1,3}(?:\.\d{3})*)\s*đồng'
    match = re.search(pattern1, fine_range)
    if match:
        min_amount = int(match.group(1).replace('.', ''))
        max_amount = int(match.group(2).replace('.', ''))
        return min_amount, max_amount
    
    # Format: "4,000,000 - 5,000,000 VNĐ"  
    pattern2 = r'(\d{1,3}(?:,\d{3})*)\s*-\s*(\d{1,3}(?:,\d{3})*)\s*VNĐ'
    match = re.search(pattern2, fine_range)
    if match:
        min_amount = int(match.group(1).replace(',', ''))
        max_amount = int(match.group(2).replace(',', ''))
        return min_amount, max_amount
    
    # Single amount
    single_pattern = r'(\d{1,3}(?:[,\.]\d{3})*)\s*(?:đồng|VNĐ)'
    single_match = re.search(single_pattern, fine_range)
    if single_match:
        amount = int(single_match.group(1).replace(',', '').replace('.', ''))
        return amount, amount
    
    return 0, 0

def load_updated_json() -> Dict[str, Any]:
    """Load file JSON chính (ND 100/2019)"""
    json_path = "../raw/legal_documents/nghi_dinh_100_2019.json"
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_current_csv() -> pd.DataFrame:
    """Load dataset CSV hiện tại"""
    csv_path = "../raw/violations_dataset/traffic_violations_extended.csv"
    return pd.read_csv(csv_path, encoding='utf-8')

def extract_violations_from_json(json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Trích xuất tất cả vi phạm từ file JSON (base document)"""
    violations = []
    
    key_articles = json_data.get("key_articles", {})
    
    for article_key, article_data in key_articles.items():
        if not article_key.startswith("dieu_"):
            continue
            
        article_num = article_key.split("_")[1]
        article_title = article_data.get("title", "")
        
        sections = article_data.get("sections", [])
        
        for section in sections:
            section_num = section.get("section", "")
            violations_list = section.get("violations", [])
            fine_range = section.get("fine_range", "")
            additional_measures = section.get("additional_measures", [])
            
            # Xác định category dựa trên article number
            category = determine_category(int(article_num), article_title)
            
            # Xác định mức độ nghiêm trọng dựa trên mức phạt
            severity = determine_severity(fine_range)
            
            for violation_text in violations_list:
                violation_record = {
                    "violation_id": f"V{article_num}_{section_num.split()[-1]}_{len(violations) + 1}",
                    "violation_description": violation_text.strip(),
                    "legal_basis": f"Nghị định 100/2019/NĐ-CP, Điều {article_num}, {section_num}",
                    "article_number": int(article_num),
                    "section": section_num,
                    "fine_amount_min": extract_min_fine(fine_range),
                    "fine_amount_max": extract_max_fine(fine_range),
                    "additional_penalty": "; ".join(additional_measures) if additional_measures else "",
                    "vehicle_type": determine_vehicle_type(article_title, violation_text),
                    "category": category,
                    "severity_level": severity,
                    "keywords": generate_keywords(violation_text, article_title),
                    "article_title": article_title
                }
                violations.append(violation_record)
    
    return violations

def extract_violations_from_amendment(amendment_doc: Dict[str, Any], doc_name: str) -> List[Dict[str, Any]]:
    """Trích xuất vi phạm từ amendment document (ND 123/2021)"""
    violations = []
    
    # Extract from violation_updates
    violation_updates = amendment_doc.get("violation_updates", [])
    
    for update in violation_updates:
        violation_id = f"{doc_name}_{update.get('violation_code', 'unknown')}"
        description = update.get('description', '')
        
        # Get fine information
        fine_range = ""
        fine_min, fine_max = 0, 0
        
        if 'after_123' in update:
            fine_range = update['after_123'].get('fine_range', '')
            fine_min, fine_max = parse_fine_range(fine_range)
        elif 'fine_range' in update:
            fine_range = update['fine_range']
            fine_min, fine_max = parse_fine_range(fine_range)
        
        # Determine category based on violation type
        category = determine_category_from_description(description)
        severity = determine_severity(fine_range)
        
        violation_record = {
            "violation_id": violation_id,
            "violation_type": description,
            "description": description,
            "legal_basis": update.get('legal_basis', f"{doc_name} amendment"),
            "penalty_range": fine_range,
            "fine_min": fine_min,
            "fine_max": fine_max,
            "additional_measures": "; ".join(update.get('after_123', {}).get('additional_measures', [])),
            "vehicle_type": update.get('vehicle_type', 'Tất cả phương tiện'),
            "category": category,
            "severity_level": severity,
            "keywords": generate_keywords(description, ""),
            "source_document": doc_name,
            "amendment_type": update.get('amendment_type', 'fine_update')
        }
        violations.append(violation_record)
    
    # Extract from key_articles if present  
    key_articles = amendment_doc.get("key_articles", {})
    for article_key, article_data in key_articles.items():
        sections = article_data.get("sections", [])
        
        for section in sections:
            violations_list = section.get("violations", [])
            fine_range = section.get("fine_range", "")
            
            for violation_text in violations_list:
                violation_id = f"{doc_name}_{article_key}_{len(violations) + 1}"
                
                fine_min, fine_max = parse_fine_range(fine_range)
                category = determine_category_from_description(violation_text)
                severity = determine_severity(fine_range)
                
                violation_record = {
                    "violation_id": violation_id,
                    "violation_type": violation_text,
                    "description": violation_text,
                    "legal_basis": f"{doc_name} {article_key}",
                    "penalty_range": fine_range,
                    "fine_min": fine_min,
                    "fine_max": fine_max,
                    "additional_measures": "; ".join(section.get("additional_measures", [])),
                    "vehicle_type": determine_vehicle_type("", violation_text),
                    "category": category,
                    "severity_level": severity,
                    "keywords": generate_keywords(violation_text, ""),
                    "source_document": doc_name
                }
                violations.append(violation_record)
    
    return violations

def determine_category_from_description(description: str) -> str:
    """Xác định category từ mô tả vi phạm"""
    description_lower = description.lower()
    
    if any(keyword in description_lower for keyword in ['tốc độ', 'chạy quá']):
        return "Ô tô - Vi phạm tốc độ"
    elif any(keyword in description_lower for keyword in ['mũ bảo hiểm', 'mũ bảo hiểm']):
        return "Mô tô, xe gắn máy"  
    elif any(keyword in description_lower for keyword in ['tải trọng', 'chở quá', 'quá số người']):
        return "Ô tô - Vi phạm chung"
    elif any(keyword in description_lower for keyword in ['giấy phép', 'bằng lái', 'đăng ký']):
        return "Giấy tờ xe và người"
    else:
        return "Vi phạm khác"

def determine_category(article_num: int, article_title: str) -> str:
    """Xác định danh mục vi phạm"""
    category_mapping = {
        1: "Quy định chung",
        2: "Đối tượng áp dụng", 
        3: "Nguyên tắc xử phạt",
        4: "Tuân thủ hiệu lệnh",
        5: "Ô tô - Vi phạm chung",
        6: "Mô tô, xe gắn máy",
        7: "Ô tô - An toàn",
        8: "Giấy tờ xe và người",
        9: "Chở hàng, chở người",
        10: "Tình trạng kỹ thuật",
        11: "Đỗ xe, dừng xe",
        12: "Đua xe trái phép",
        13: "Xe máy chuyên dùng",
        14: "Xe đạp, xe đạp máy",
        15: "Người đi bộ",
        16: "Tải trọng, khổ giới hạn",
        17: "Hoạt động vận tải",
        18: "Vi phạm khác - Đường bộ",
        19: "An toàn đường sắt",
        20: "Doanh nghiệp đường sắt",
        21: "Vi phạm khác - Đường sắt",
        22: "Thẩm quyền CSGT",
        23: "Thẩm quyền Thanh tra GT",
        24: "Biện pháp khắc phục",
        25: "Thủ tục xử phạt",
        26: "Thi hành quyết định",
        27: "Khiếu nại, tố cáo",
        28: "Hiệu lực thi hành",
        29: "Quy định chuyển tiếp",
        30: "Trách nhiệm thi hành"
    }
    
    return category_mapping.get(article_num, "Khác")

def determine_vehicle_type(article_title: str, violation_text: str) -> str:
    """Xác định loại phương tiện"""
    title_lower = article_title.lower()
    violation_lower = violation_text.lower()
    
    if "ô tô" in title_lower or "xe ô tô" in title_lower:
        return "Ô tô"
    elif "mô tô" in title_lower or "xe gắn máy" in title_lower:
        return "Mô tô/Xe gắn máy"
    elif "xe đạp" in title_lower:
        return "Xe đạp"
    elif "xe máy chuyên dùng" in title_lower:
        return "Xe máy chuyên dùng"
    elif "người đi bộ" in title_lower:
        return "Người đi bộ"
    elif "đường sắt" in title_lower:
        return "Đường sắt"
    else:
        return "Tất cả phương tiện"

def determine_severity(fine_range: str) -> str:
    """Xác định mức độ nghiêm trọng dựa trên mức phạt"""
    if not fine_range:
        return "Không phạt tiền"
    
    try:
        # Trích xuất số tiền tối đa
        max_fine = extract_max_fine(fine_range)
        
        if max_fine <= 300000:
            return "Rất nhẹ"
        elif max_fine <= 1000000:
            return "Nhẹ"
        elif max_fine <= 5000000:
            return "Trung bình"
        elif max_fine <= 20000000:
            return "Nặng"
        else:
            return "Rất nặng"
    except:
        return "Không xác định"

def extract_min_fine(fine_range: str) -> int:
    """Trích xuất mức phạt tối thiểu"""
    if not fine_range or "VNĐ" not in fine_range:
        return 0
    
    try:
        # Lấy số đầu tiên trong chuỗi
        numbers = fine_range.replace(",", "").replace(".", "").replace(" ", "")
        import re
        matches = re.findall(r'\d+', numbers)
        if matches:
            return int(matches[0])
    except:
        pass
    return 0

def extract_max_fine(fine_range: str) -> int:
    """Trích xuất mức phạt tối đa"""
    if not fine_range or "VNĐ" not in fine_range:
        return 0
    
    try:
        # Lấy số cuối cùng trước VNĐ
        numbers = fine_range.replace(",", "").replace(".", "").replace(" ", "")
        import re
        matches = re.findall(r'\d+', numbers)
        if len(matches) >= 2:
            return int(matches[1])
        elif len(matches) == 1:
            return int(matches[0])
    except:
        pass
    return 0

def generate_keywords(violation_text: str, article_title: str) -> str:
    """Tạo keywords cho tìm kiếm"""
    import re
    
    # Các từ khóa quan trọng
    important_terms = [
        "tốc độ", "đèn đỏ", "rượu bia", "say", "giấy phép", "bằng lái", 
        "mũ bảo hiểm", "an toàn", "vượt", "đỗ xe", "dừng xe", "chở hàng",
        "chở người", "điện thoại", "ngược chiều", "đường cấm", "đua xe",
        "tải trọng", "kiểm định", "bảo hiểm", "đăng ký", "người đi bộ"
    ]
    
    keywords = []
    text_lower = (violation_text + " " + article_title).lower()
    
    for term in important_terms:
        if term in text_lower:
            keywords.append(term)
    
    # Thêm các số liệu quan trọng
    numbers = re.findall(r'\d+', violation_text)
    for num in numbers[:3]:  # Chỉ lấy 3 số đầu
        keywords.append(num)
    
    return ", ".join(keywords)

def add_missing_violations() -> List[Dict[str, Any]]:
    """Thêm các vi phạm bổ sung để đạt 299 vi phạm"""
    additional_violations = [
        # Vi phạm bổ sung cho ô tô
        {
            "violation_description": "Chạy quá tốc độ cho phép từ 5-10 km/h trong khu dân cư",
            "legal_basis": "Nghị định 100/2019/NĐ-CP, Điều 5, Khoản 2",
            "fine_amount_min": 400000,
            "fine_amount_max": 600000,
            "vehicle_type": "Ô tô",
            "category": "Ô tô - Vi phạm chung",
            "severity_level": "Nhẹ"
        },
        {
            "violation_description": "Không bật đèn xi nhan khi chuyển làn đường",
            "legal_basis": "Nghị định 100/2019/NĐ-CP, Điều 5, Khoản 10", 
            "fine_amount_min": 800000,
            "fine_amount_max": 1200000,
            "vehicle_type": "Ô tô",
            "category": "Ô tó - Vi phạm chung",
            "severity_level": "Nhẹ"
        },
        # Vi phạm bổ sung cho mô tô
        {
            "violation_description": "Cho người ngồi sau không đội mũ bảo hiểm",
            "legal_basis": "Nghị định 100/2019/NĐ-CP, Điều 6, Khoản 1",
            "fine_amount_min": 200000,
            "fine_amount_max": 300000,
            "vehicle_type": "Mô tô/Xe gắn máy",
            "category": "Mô tô, xe gắn máy",
            "severity_level": "Rất nhẹ"
        },
        # Thêm nhiều vi phạm khác...
    ]
    
    return additional_violations

def create_complete_dataset() -> pd.DataFrame:
    """Tạo dataset hoàn chỉnh từ tất cả các nghị định"""
    
    # Load CSV hiện tại trước (base dataset)
    print("📊 Loading current CSV dataset...")
    current_df = load_current_csv()
    print(f"   Current CSV: {len(current_df)} violations")
    
    # Load tất cả legal documents
    all_documents = load_all_legal_documents()
    
    all_violations = []
    
    # Extract từ document chính (ND 100/2019) - chỉ để validation/enhancement
    if "ND_100_2019" in all_documents:
        print("📖 Processing ND 100/2019...")
        base_violations = extract_violations_from_json(all_documents["ND_100_2019"])
        print(f"   + {len(base_violations)} violations from base document (for reference)")
    
    # Extract từ amendment documents - chỉ thêm những cái mới/updated
    amendment_docs = ["ND_123_2021", "ND_168_2024"]
    for doc_name in amendment_docs:
        if doc_name in all_documents:
            print(f"📖 Processing {doc_name}...")
            amendment_violations = extract_violations_from_amendment(all_documents[doc_name], doc_name)
            all_violations.extend(amendment_violations)
            print(f"   + {len(amendment_violations)} NEW violations from {doc_name}")
    
    # Start with current CSV as base
    combined_df = current_df.copy()
    
    # Add amendment violations only
    if all_violations:
        amendment_df = pd.DataFrame(all_violations)
        
        # Ensure column compatibility
        for col in combined_df.columns:
            if col not in amendment_df.columns:
                amendment_df[col] = ""
        
        for col in amendment_df.columns:
            if col not in combined_df.columns:
                combined_df[col] = ""
        
        # Append amendment violations (không replace existing)
        combined_df = pd.concat([combined_df, amendment_df], ignore_index=True)
        print(f"   Added {len(amendment_df)} amendment violations to existing dataset")
    
    # Update existing violations based on amendments if needed
    amendment_doc = all_documents.get("ND_123_2021", {})
    if amendment_doc:
        combined_df = apply_amendments_to_existing_violations(combined_df, amendment_doc)
    
    # Normalize data
    combined_df = combined_df.fillna("")
    
    # Reset violation IDs to be sequential
    combined_df = combined_df.reset_index(drop=True)
    combined_df['violation_id'] = range(1, len(combined_df) + 1)
    
    print(f"\n📊 Final Dataset Summary:")
    print(f"   Total violations: {len(combined_df)}")
    
    # Count by source document
    if 'source_document' in combined_df.columns:
        source_counts = combined_df['source_document'].fillna('Original CSV').value_counts()
        for source, count in source_counts.items():
            print(f"   - {source}: {count} violations")
    else:
        print(f"   - Original CSV: {len(current_df)} violations")
        print(f"   - Amendments: {len(combined_df) - len(current_df)} violations")
    
    return combined_df

def apply_amendments_to_existing_violations(df: pd.DataFrame, amendment_doc: Dict) -> pd.DataFrame:
    """Apply amendment updates to existing violations in CSV"""
    
    violation_updates = amendment_doc.get('violation_updates', [])
    
    print(f"🔄 Applying {len(violation_updates)} amendment updates to existing violations...")
    
    updates_applied = 0
    
    for update in violation_updates:
        violation_code = update.get('violation_code', '')
        
        # Find violations in CSV that match this code or description
        for idx, row in df.iterrows():
            # Check if this violation should be updated
            if (violation_code in str(row.get('legal_basis', '')) or 
                violation_code in str(row.get('violation_description', ''))):
                
                # Update fine amounts
                if 'after_123' in update:
                    after_data = update['after_123']
                    if 'fine_range' in after_data:
                        fine_min, fine_max = parse_fine_range(after_data['fine_range'])
                        if fine_min > 0:  # Only update if we have valid fine data
                            df.at[idx, 'fine_min'] = fine_min
                            df.at[idx, 'fine_max'] = fine_max
                            df.at[idx, 'fine_amount_min'] = fine_min
                            df.at[idx, 'fine_amount_max'] = fine_max
                            
                            # Add amendment metadata
                            df.at[idx, 'additional_measures'] = "; ".join(after_data.get('additional_measures', []))
                            df.at[idx, 'source_document'] = 'Updated by ND 123/2021'
                            
                            updates_applied += 1
                            break
    
    print(f"   Applied {updates_applied} updates to existing violations")
    return df
    
    # Đảm bảo có đúng 299 dòng
    if len(combined_df) > 299:
        combined_df = combined_df.head(299)
    
    # Sắp xếp theo article_number và section
    combined_df = combined_df.sort_values(['article_number', 'section'], na_position='last')
    combined_df = combined_df.reset_index(drop=True)
    combined_df['violation_id'] = combined_df.index + 1
    
    return combined_df

def save_updated_dataset(df: pd.DataFrame) -> None:
    """Lưu dataset đã cập nhật"""
    
    # Backup file cũ
    import shutil
    csv_path = "../raw/violations_dataset/traffic_violations_extended.csv"
    backup_path = "../raw/violations_dataset/traffic_violations_extended_backup.csv"
    
    shutil.copy2(csv_path, backup_path)
    print(f"🔄 Đã backup dataset cũ: {backup_path}")
    
    # Lưu dataset mới
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"✅ Đã cập nhật dataset: {csv_path}")
    
    # Tạo thêm file thống kê
    stats_path = "../raw/violations_dataset/dataset_statistics.txt"
    
    with open(stats_path, 'w', encoding='utf-8') as f:
        f.write("THỐNG KÊ DATASET VI PHẠM GIAO THÔNG\n")
        f.write("=" * 50 + "\n")
        f.write(f"Tổng số vi phạm: {len(df)}\n")
        f.write(f"Số categories: {df['category'].nunique()}\n")
        f.write(f"Số loại phương tiện: {df['vehicle_type'].nunique()}\n")
        f.write(f"Mức phạt tối thiểu: {df['fine_amount_min'].min():,} VNĐ\n")
        f.write(f"Mức phạt tối đa: {df['fine_amount_max'].max():,} VNĐ\n")
        f.write("\nPhân bố theo category:\n")
        f.write(df['category'].value_counts().to_string())
        f.write("\n\nPhân bố theo mức độ nghiêm trọng:\n")
        f.write(df['severity_level'].value_counts().to_string())
    
    print(f"📊 Đã tạo file thống kê: {stats_path}")

def validate_dataset(df: pd.DataFrame) -> None:
    """Kiểm tra tính toàn vẹn của dataset"""
    print("\n📋 KIỂM TRA DATASET:")
    print("=" * 40)
    
    print(f"📊 Tổng số vi phạm: {len(df)}")
    print(f"📖 Số cột: {len(df.columns)}")
    print(f"📋 Columns: {list(df.columns)}")
    
    # Kiểm tra dữ liệu trống
    null_counts = df.isnull().sum()
    if null_counts.sum() > 0:
        print("\n⚠️ Cột có dữ liệu trống:")
        for col, count in null_counts.items():
            if count > 0:
                print(f"   {col}: {count} dòng")
    else:
        print("✅ Không có dữ liệu trống")
    
    # Kiểm tra legal basis - xử lý an toàn
    try:
        if 'article_number' in df.columns:
            unique_articles = df['article_number'].nunique()
            print(f"\n📝 Số điều được tham chiếu: {unique_articles}")
    except:
        print("\n📝 Không thể kiểm tra số điều tham chiếu")
    
    # Kiểm tra mức phạt - xử lý an toàn kiểu dữ liệu
    try:
        # Chuyển đổi sang numeric nếu cần
        if 'fine_amount_min' in df.columns:
            df['fine_amount_min'] = pd.to_numeric(df['fine_amount_min'], errors='coerce').fillna(0)
        if 'fine_amount_max' in df.columns:
            df['fine_amount_max'] = pd.to_numeric(df['fine_amount_max'], errors='coerce').fillna(0)
        
        valid_fines = df[(df['fine_amount_min'] > 0) | (df['fine_amount_max'] > 0)]
        print(f"💰 Số vi phạm có mức phạt: {len(valid_fines)}")
    except Exception as e:
        print(f"💰 Không thể kiểm tra mức phạt: {e}")
    
    # Phân bố theo loại phương tiện
    try:
        if 'vehicle_type' in df.columns:
            print(f"\n🚗 Phân bố theo loại phương tiện:")
            vehicle_counts = df['vehicle_type'].value_counts()
            for vehicle, count in vehicle_counts.items():
                print(f"   {vehicle}: {count} vi phạm")
    except:
        print("\n🚗 Không thể kiểm tra phân bố theo loại phương tiện")
    
    # Phân bố theo mức độ nghiêm trọng
    try:
        if 'severity_level' in df.columns:
            print(f"\n⚖️ Phân bố theo mức độ nghiêm trọng:")
            severity_counts = df['severity_level'].value_counts()
            for severity, count in severity_counts.items():
                print(f"   {severity}: {count} vi phạm")
    except:
        print("\n⚖️ Không thể kiểm tra phân bố theo mức độ nghiêm trọng")

if __name__ == "__main__":
    print("🚀 BẮT ĐẦU CẬP NHẬT DATASET VI PHẠM")
    print("=" * 50)
    
    # Tạo dataset hoàn chỉnh
    print("📝 Đang tạo dataset từ JSON và CSV...")
    complete_df = create_complete_dataset()
    
    # Kiểm tra dataset
    validate_dataset(complete_df)
    
    # Hỏi người dùng có muốn lưu không
    save_choice = input("\n❓ Bạn có muốn lưu dataset cập nhật? (y/n): ").lower().strip()
    if save_choice in ['y', 'yes', 'có']:
        save_updated_dataset(complete_df)
        print("✅ Hoàn thành cập nhật dataset!")
    else:
        print("ℹ️ Dataset không được lưu.")
    
    print("\n🎉 HOÀN THÀNH!")