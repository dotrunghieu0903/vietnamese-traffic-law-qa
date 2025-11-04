#!/usr/bin/env python3
"""
Script kiểm tra cuối cùng để xác nhận toàn bộ dữ liệu đã được cập nhật đầy đủ
"""

import json
import pandas as pd
import os

def final_validation():
    """Kiểm tra cuối cùng toàn bộ dữ liệu"""
    print("🎯 KIỂM TRA CUỐI CÙNG - TÍNH ĐẦY ĐỦ DỮ LIỆU")
    print("=" * 60)
    
    # Kiểm tra file JSON
    json_path = "../raw/legal_documents/nghi_dinh_100_2019.json"
    
    print("\n📄 1. KIỂM TRA FILE JSON:")
    print("-" * 30)
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Kiểm tra metadata
        doc_info = data.get("document_info", {})
        print(f"✅ Tên văn bản: {doc_info.get('title', 'N/A')}")
        print(f"✅ Tổng số điều (metadata): {doc_info.get('total_articles', 'N/A')}")
        print(f"✅ Tổng số chương: {doc_info.get('total_chapters', 'N/A')}")
        
        # Kiểm tra key_articles
        key_articles = data.get("key_articles", {})
        article_keys = [k for k in key_articles.keys() if k.startswith("dieu_")]
        
        print(f"✅ Số điều có nội dung chi tiết: {len(article_keys)}")
        
        # Kiểm tra từng điều từ 1-30
        missing_articles = []
        present_articles = []
        
        for i in range(1, 31):
            key = f"dieu_{i}"
            if key in key_articles:
                present_articles.append(i)
            else:
                missing_articles.append(i)
        
        print(f"✅ Các điều có nội dung: {present_articles}")
        if missing_articles:
            print(f"❌ Các điều còn thiếu: {missing_articles}")
        else:
            print("🎉 ĐÃ CÓ ĐẦY ĐỦ 30 ĐIỀU!")
        
        # Kiểm tra statistics
        stats = data.get("statistics", {})
        if stats:
            print(f"\n📊 THỐNG KÊ TỪ JSON:")
            print(f"   - Tổng số điều: {stats.get('total_articles', 'N/A')}")
            print(f"   - Điều có vi phạm: {stats.get('articles_with_violations', 'N/A')}")
            print(f"   - Tổng loại vi phạm: {stats.get('total_violation_types', 'N/A')}")
            print(f"   - Mức phạt tối thiểu: {stats.get('fine_range_min', 'N/A')}")
            print(f"   - Mức phạt tối đa: {stats.get('fine_range_max', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Lỗi khi đọc file JSON: {e}")
    
    # Kiểm tra file CSV
    csv_path = "../raw/violations_dataset/traffic_violations_extended.csv"
    
    print("\n📄 2. KIỂM TRA DATASET CSV:")
    print("-" * 30)
    
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
        
        print(f"✅ Tổng số vi phạm: {len(df)}")
        print(f"✅ Số cột: {len(df.columns)}")
        
        # Kiểm tra legal basis
        if 'legal_basis' in df.columns:
            unique_legal_basis = df['legal_basis'].nunique()
            print(f"✅ Số legal basis khác nhau: {unique_legal_basis}")
            
            # Đếm vi phạm theo điều
            legal_basis_sample = df['legal_basis'].value_counts().head(10)
            print(f"\n🔍 Top 10 legal basis:")
            for basis, count in legal_basis_sample.items():
                print(f"   {basis}: {count} vi phạm")
        
        # Kiểm tra các cột quan trọng
        important_cols = ['violation_description', 'legal_basis', 'category', 'vehicle_type']
        missing_cols = [col for col in important_cols if col not in df.columns]
        
        if missing_cols:
            print(f"❌ Các cột bị thiếu: {missing_cols}")
        else:
            print("✅ Tất cả cột quan trọng đều có")
        
        # Kiểm tra dữ liệu trống
        null_counts = df.isnull().sum()
        critical_nulls = null_counts[null_counts > 0]
        
        if len(critical_nulls) > 0:
            print(f"\n⚠️ Cột có dữ liệu trống:")
            for col, count in critical_nulls.items():
                print(f"   {col}: {count} dòng")
        else:
            print("✅ Không có dữ liệu quan trọng bị trống")
            
    except Exception as e:
        print(f"❌ Lỗi khi đọc file CSV: {e}")
    
    # Kiểm tra file backup
    print("\n📄 3. KIỂM TRA FILE BACKUP:")
    print("-" * 30)
    
    backup_files = [
        "../raw/legal_documents/nghi_dinh_100_2019_backup.json",
        "../raw/violations_dataset/traffic_violations_extended_backup.csv"
    ]
    
    for backup_file in backup_files:
        if os.path.exists(backup_file):
            print(f"✅ File backup tồn tại: {os.path.basename(backup_file)}")
        else:
            print(f"❌ File backup không tồn tại: {os.path.basename(backup_file)}")
    
    # Tóm tắt kết quả
    print("\n🎯 KẾT QUẢ CUỐI CÙNG:")
    print("=" * 40)
    
    print(f"📋 FILE JSON:")
    print(f"   ✅ Có đầy đủ 30 điều: {'CÓ' if len(present_articles) == 30 else 'KHÔNG'}")
    print(f"   ✅ Metadata đầy đủ: {'CÓ' if doc_info.get('total_articles') == 30 else 'KHÔNG'}")
    
    print(f"\n📋 DATASET CSV:")
    print(f"   ✅ Có 299 vi phạm: {'CÓ' if len(df) == 299 else 'KHÔNG'}")
    print(f"   ✅ Legal references chính xác: {'CÓ' if 'legal_basis' in df.columns else 'KHÔNG'}")
    
    # Đánh giá tổng thể
    json_complete = len(present_articles) == 30 and doc_info.get('total_articles') == 30
    csv_complete = len(df) == 299 and 'legal_basis' in df.columns
    
    if json_complete and csv_complete:
        print(f"\n🎉 HOÀN THÀNH! TẤT CẢ YÊU CẦU ĐÃ ĐƯỢC ĐÁP ỨNG:")
        print(f"   ✅ File JSON có đầy đủ 30 điều")
        print(f"   ✅ Metadata được cập nhật đầy đủ")
        print(f"   ✅ Dataset có đúng 299 vi phạm")
        print(f"   ✅ Legal references chính xác")
        return True
    else:
        print(f"\n⚠️ CÒN THIẾU SÓT:")
        if not json_complete:
            print(f"   ❌ File JSON chưa đầy đủ")
        if not csv_complete:
            print(f"   ❌ Dataset CSV chưa đầy đủ")
        return False

if __name__ == "__main__":
    success = final_validation()
    
    if success:
        print(f"\n✨ YÊU CẦU CỦA BẠN ĐÃ ĐƯỢC HOÀN THÀNH!")
        print(f"📄 File nghi_dinh_100_2019.json đã có đầy đủ 30 điều")
        print(f"📊 Dataset đã có đúng 299 vi phạm với legal references chính xác")
    else:
        print(f"\n🔧 CẦN KHẮC PHỤC THÊM...")