#!/usr/bin/env python3
"""
Script để cập nhật file CSV từ dữ liệu JSON của các nghị định
"""

import json
import pandas as pd
import os
import sys
from pathlib import Path

def create_violation_record(violation_id, violation_desc, article_num, section, article_title, 
                          fine_range, additional_measures, document_source, vehicle_type="", 
                          category="", severity="", amendment_type=""):
    """Tạo một record vi phạm từ thông tin đầu vào"""
    
    # Xử lý fine_range
    fine_min = fine_max = ""
    if fine_range:
        # Tách min và max từ fine_range
        fine_parts = fine_range.replace(" VNĐ", "").replace(" đồng", "").replace(".", "").replace(",", "").split(" - ")
        if len(fine_parts) == 2:
            try:
                fine_min = int(fine_parts[0])
                fine_max = int(fine_parts[1])
            except:
                fine_min = fine_max = ""
    
    # Xử lý keywords
    keywords = str(violation_desc.lower()).split()
    keywords_str = str(keywords)
    
    # Định severity level
    if fine_min and fine_max:
        fine_avg = (int(fine_min) + int(fine_max)) / 2
        if fine_avg < 500000:
            severity = "Nhẹ"
        elif fine_avg < 2000000:
            severity = "Trung bình" 
        else:
            severity = "Nghiêm trọng"
    
    record = {
        'violation_id': violation_id,
        'violation_description': violation_desc,
        'category': category,
        'fine_min': fine_min,
        'fine_max': fine_max,
        'currency': 'VNĐ' if fine_min else '',
        'additional_measures': additional_measures,
        'legal_basis': f"Nghị định {document_source.replace('nghi_dinh_', '').replace('_', '/')}/NĐ-CP - {article_num.upper()}",
        'document_source': document_source,
        'severity': severity,
        'article_number': article_num.upper(),
        'section': section,
        'fine_amount_min': float(fine_min) if fine_min else "",
        'fine_amount_max': float(fine_max) if fine_max else "",
        'additional_penalty': additional_measures,
        'vehicle_type': vehicle_type,
        'severity_level': severity,
        'keywords': keywords_str,
        'article_title': article_title,
        'violation_type': "",
        'description': violation_desc,
        'penalty_range': fine_range,
        'source_document': document_source,
        'amendment_type': amendment_type
    }
    
    return record

def update_nghi_dinh_100_csv(json_file_path, csv_file_path):
    """Cập nhật file CSV cho nghị định 100/2019"""
    
    print(f"Đang cập nhật {csv_file_path} từ {json_file_path}")
    
    # Đọc dữ liệu JSON
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    violations = []
    num = 1
    
    # Xử lý các điều có vi phạm
    for article_key, article_data in data['key_articles'].items():
        if 'sections' not in article_data:
            continue
            
        article_title = article_data.get('title', '')
        
        for section_data in article_data['sections']:
            if 'violations' not in section_data:
                continue
                
            section = section_data.get('section', '')
            fine_range = section_data.get('fine_range', '')
            additional_measures = '; '.join(section_data.get('additional_measures', []))
            
            # Xử lý từng vi phạm
            for i, violation in enumerate(section_data['violations'], 1):
                violation_id = f"{article_key}_{section}_{i}"
                
                # Xác định category và vehicle_type
                category = "Vi phạm giao thông khác"
                vehicle_type = ""
                
                if "ô tô" in article_title.lower():
                    vehicle_type = "Ô tô"
                    category = "Vi phạm của người điều khiển xe ô tô"
                elif "mô tô" in article_title.lower() or "gắn máy" in article_title.lower():
                    vehicle_type = "Mô tô"
                    category = "Vi phạm của người điều khiển xe mô tô, xe gắn máy"
                elif "tốc độ" in violation.lower():
                    category = "Vi phạm tốc độ"
                elif "đèn" in violation.lower() or "tín hiệu" in violation.lower():
                    category = "Vi phạm tín hiệu giao thông"
                elif "giấy phép" in violation.lower():
                    category = "Vi phạm giấy phép lái xe"
                elif "mũ bảo hiểm" in violation.lower():
                    category = "Vi phạm an toàn"
                elif "tải" in violation.lower() or "chở" in violation.lower():
                    category = "Vi phạm tải trọng"
                
                record = create_violation_record(
                    violation_id=violation_id,
                    violation_desc=violation,
                    article_num=article_key,
                    section=section,
                    article_title=article_title,
                    fine_range=fine_range,
                    additional_measures=additional_measures,
                    document_source="nghi_dinh_100_2019",
                    vehicle_type=vehicle_type,
                    category=category
                )
                
                record['num'] = num
                violations.append(record)
                num += 1
    
    # Tạo DataFrame và lưu
    df = pd.DataFrame(violations)
    
    # Sắp xếp các cột theo thứ tự mong muốn
    columns_order = [
        'num', 'violation_id', 'violation_description', 'category', 'fine_min', 'fine_max', 
        'currency', 'additional_measures', 'legal_basis', 'document_source', 'severity',
        'article_number', 'section', 'fine_amount_min', 'fine_amount_max', 'additional_penalty',
        'vehicle_type', 'severity_level', 'keywords', 'article_title', 'violation_type',
        'description', 'penalty_range', 'source_document', 'amendment_type'
    ]
    
    df = df.reindex(columns=columns_order)
    df.to_csv(csv_file_path, index=False, encoding='utf-8')
    
    print(f"Đã cập nhật {len(violations)} vi phạm vào {csv_file_path}")
    return len(violations)

def update_nghi_dinh_123_csv(json_file_path, csv_file_path):
    """Cập nhật file CSV cho nghị định 123/2021"""
    
    print(f"Đang cập nhật {csv_file_path} từ {json_file_path}")
    
    # Đọc dữ liệu JSON
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    violations = []
    num = 1
    
    # Xử lý violation_updates từ JSON
    if 'violation_updates' in data:
        for violation_update in data['violation_updates']:
            violation_desc = violation_update['description']
            vehicle_type = violation_update['vehicle_type']
            amendment_type = violation_update['amendment_type']
            
            after_data = violation_update.get('after_123', {})
            fine_range = after_data.get('fine_range', '')
            additional_measures = '; '.join(after_data.get('additional_measures', []))
            
            # Tạo violation_id
            violation_id = f"dieu_1_update_{num}"
            
            # Xác định category
            category = "Vi phạm giao thông khác"
            if "tốc độ" in violation_desc.lower():
                category = "Vi phạm tốc độ"
            elif "mũ bảo hiểm" in violation_desc.lower():
                category = "Vi phạm an toàn"
            elif "tải" in violation_desc.lower() or "chở" in violation_desc.lower():
                category = "Vi phạm tải trọng"
            
            record = create_violation_record(
                violation_id=violation_id,
                violation_desc=violation_desc,
                article_num="DIEU 1",
                section=f"Cập nhật {num}",
                article_title="Sửa đổi, bổ sung một số điều của Nghị định số 100/2019/NĐ-CP",
                fine_range=fine_range,
                additional_measures=additional_measures,
                document_source="nghi_dinh_123_2021",
                vehicle_type=vehicle_type,
                category=category,
                amendment_type=amendment_type
            )
            
            record['num'] = num
            violations.append(record)
            num += 1
    
    # Xử lý các điều khác từ key_articles
    for article_key, article_data in data['key_articles'].items():
        if article_key == 'dieu_1':  # Đã xử lý ở trên
            continue
            
        if 'sections' not in article_data:
            continue
            
        article_title = article_data.get('title', '')
        
        for section_data in article_data['sections']:
            section = section_data.get('section', '')
            content = section_data.get('content', '')
            
            if not content:
                continue
            
            violation_id = f"{article_key}_{section}_1"
            
            record = create_violation_record(
                violation_id=violation_id,
                violation_desc=content,
                article_num=article_key,
                section=section,
                article_title=article_title,
                fine_range="",
                additional_measures="",
                document_source="nghi_dinh_123_2021",
                category="Vi phạm giao thông khác"
            )
            
            record['num'] = num
            violations.append(record)
            num += 1
    
    # Tạo DataFrame và lưu
    df = pd.DataFrame(violations)
    
    # Sắp xếp các cột theo thứ tự mong muốn
    columns_order = [
        'num', 'violation_id', 'violation_description', 'category', 'fine_min', 'fine_max', 
        'currency', 'additional_measures', 'legal_basis', 'document_source', 'severity',
        'article_number', 'section', 'fine_amount_min', 'fine_amount_max', 'additional_penalty',
        'vehicle_type', 'severity_level', 'keywords', 'article_title', 'violation_type',
        'description', 'penalty_range', 'source_document', 'amendment_type'
    ]
    
    df = df.reindex(columns=columns_order)
    df.to_csv(csv_file_path, index=False, encoding='utf-8')
    
    print(f"Đã cập nhật {len(violations)} mục vào {csv_file_path}")
    return len(violations)

def main():
    """Hàm chính"""
    
    # Đường dẫn các file
    base_dir = Path(__file__).parent.parent
    
    # File JSON
    json_100_path = base_dir / "raw" / "legal_documents" / "nghi_dinh_100_2019.json"
    json_123_path = base_dir / "raw" / "legal_documents" / "nghi_dinh_123_2021.json"
    
    # File CSV
    csv_100_path = base_dir / "raw" / "violations_dataset" / "nghi_dinh_100_2019_violations.csv"
    csv_123_path = base_dir / "raw" / "violations_dataset" / "nghi_dinh_123_2021_violations.csv"
    
    print("=" * 80)
    print("CẬP NHẬT DỮ LIỆU CSV TỪ FILE JSON")
    print("=" * 80)
    
    # Kiểm tra file tồn tại
    for file_path in [json_100_path, json_123_path]:
        if not file_path.exists():
            print(f"ERROR: Không tìm thấy file {file_path}")
            return
    
    # Tạo backup cho các file CSV hiện tại
    for csv_path in [csv_100_path, csv_123_path]:
        if csv_path.exists():
            backup_path = csv_path.with_suffix('.csv.backup')
            if backup_path.exists():
                backup_path.unlink()
            csv_path.rename(backup_path)
            print(f"Đã backup {csv_path} thành {backup_path}")
    
    # Cập nhật file CSV
    try:
        violations_100 = update_nghi_dinh_100_csv(json_100_path, csv_100_path)
        violations_123 = update_nghi_dinh_123_csv(json_123_path, csv_123_path)
        
        print("\n" + "=" * 80)
        print("KẾT QUẢ CẬP NHẬT")
        print("=" * 80)
        print(f"Nghị định 100/2019: {violations_100} vi phạm")
        print(f"Nghị định 123/2021: {violations_123} mục")
        print(f"Tổng cộng: {violations_100 + violations_123} bản ghi")
        print("\nCập nhật thành công!")
        
    except Exception as e:
        print(f"ERROR: Lỗi trong quá trình cập nhật: {e}")
        # Khôi phục file backup nếu có lỗi
        for csv_path in [csv_100_path, csv_123_path]:
            backup_path = csv_path.with_suffix('.csv.backup')
            if backup_path.exists():
                if csv_path.exists():
                    csv_path.unlink()
                backup_path.rename(csv_path)
                print(f"Đã khôi phục {csv_path} từ backup")

if __name__ == "__main__":
    main()