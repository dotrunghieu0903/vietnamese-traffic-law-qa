#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phân tích chi tiết sự khác biệt giữa DOCX và JSON
"""

import json
import os
from typing import Dict, Any

def analyze_differences():
    """Phân tích chi tiết sự khác biệt"""
    
    original_json = r"c:\Users\hieudt22\Documents\VNI-TrafficLawQA\data\raw\legal_documents\nghi_dinh_100_2019.json"
    updated_json = r"c:\Users\hieudt22\Documents\VNI-TrafficLawQA\data\processed\nghi_dinh_100_2019_updated.json"
    
    # Đọc dữ liệu
    with open(original_json, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    with open(updated_json, 'r', encoding='utf-8') as f:
        updated_data = json.load(f)
    
    original_articles = original_data.get("key_articles", {})
    updated_articles = updated_data.get("key_articles", {})
    
    print("📊 PHÂN TÍCH CHI TIẾT SỰ KHÁC BIỆT")
    print("=" * 60)
    
    print(f"\n📈 THỐNG KÊ TỔNG QUAN:")
    print(f"   - File JSON gốc: {len(original_articles)} điều")
    print(f"   - File DOCX: {len(updated_articles)} điều")
    print(f"   - Tăng thêm: {len(updated_articles) - len(original_articles)} điều")
    
    # Tìm điều mới
    new_articles = []
    for key in updated_articles:
        if key not in original_articles:
            new_articles.append(key)
    
    print(f"\n📝 CÁC ĐIỀU MỚI ĐƯỢC THÊM VÀO ({len(new_articles)} điều):")
    
    # Sắp xếp theo số điều
    new_articles_sorted = sorted(new_articles, key=lambda x: int(x.split('_')[1]) if x.split('_')[1].isdigit() else 999)
    
    for i, article_key in enumerate(new_articles_sorted):
        if i < 20:  # Hiển thị 20 điều đầu tiên
            article = updated_articles[article_key]
            article_num = article_key.replace('dieu_', '')
            title = article.get('title', 'Không có tiêu đề')
            print(f"   • Điều {article_num}: {title[:80]}{'...' if len(title) > 80 else ''}")
        elif i == 20:
            print(f"   ... và {len(new_articles_sorted) - 20} điều khác")
            break
    
    # Kiểm tra các điều đã có trong JSON gốc
    print(f"\n🔍 KIỂM TRA CÁC ĐIỀU ĐÃ CÓ TRONG JSON GỐC:")
    common_articles = []
    for key in original_articles:
        if key in updated_articles:
            common_articles.append(key)
    
    print(f"   - Số điều có trong cả hai: {len(common_articles)}")
    
    # So sánh tiêu đề
    title_differences = []
    for key in common_articles:
        original_title = original_articles[key].get('title', '')
        updated_title = updated_articles[key].get('title', '')
        
        if original_title.strip() != updated_title.strip():
            title_differences.append({
                'article': key,
                'original': original_title,
                'updated': updated_title
            })
    
    if title_differences:
        print(f"\n⚠️ KHÁC BIỆT VỀ TIÊU ĐỀ ({len(title_differences)} điều):")
        for diff in title_differences[:10]:  # Hiển thị 10 khác biệt đầu tiên
            article_num = diff['article'].replace('dieu_', '')
            print(f"   • Điều {article_num}:")
            print(f"     JSON gốc: {diff['original'][:60]}{'...' if len(diff['original']) > 60 else ''}")
            print(f"     DOCX:     {diff['updated'][:60]}{'...' if len(diff['updated']) > 60 else ''}")
            print()
    
    # Hiển thị cấu trúc của một số điều mới
    print(f"\n📋 MẪU CẤU TRÚC CỦA MỘT SỐ ĐIỀU MỚI:")
    sample_new_articles = new_articles_sorted[:5]
    
    for article_key in sample_new_articles:
        article = updated_articles[article_key]
        article_num = article_key.replace('dieu_', '')
        title = article.get('title', '')
        sections = article.get('sections', [])
        
        print(f"\n   📄 Điều {article_num}: {title}")
        print(f"      Số khoản: {len(sections)}")
        
        if sections:
            first_section = sections[0]
            content = first_section.get('content', '')
            violations = first_section.get('violations', [])
            fine_range = first_section.get('fine_range', '')
            
            print(f"      Khoản đầu: {content[:100]}{'...' if len(content) > 100 else ''}")
            if violations:
                print(f"      Vi phạm: {len(violations)} loại")
            if fine_range:
                print(f"      Mức phạt: {fine_range}")
    
    # Kiểm tra tính đầy đủ
    print(f"\n✅ ĐÁNH GIÁ TÍNH ĐẦY ĐỦ:")
    
    # Kiểm tra chuỗi điều từ 1 đến 86
    missing_articles = []
    for i in range(1, 87):
        article_key = f"dieu_{i}"
        if article_key not in updated_articles:
            missing_articles.append(i)
    
    if missing_articles:
        print(f"   ⚠️ Còn thiếu các điều: {', '.join(map(str, missing_articles))}")
    else:
        print(f"   ✅ Đã có đầy đủ các điều từ 1 đến 86")
    
    # Kiểm tra điều ngoài phạm vi
    extra_articles = []
    for key in updated_articles:
        try:
            article_num = int(key.replace('dieu_', ''))
            if article_num > 86:
                extra_articles.append(article_num)
        except:
            extra_articles.append(key)
    
    if extra_articles:
        print(f"   📝 Có thêm các điều ngoài phạm vi 1-86: {extra_articles}")
    
    return {
        'original_count': len(original_articles),
        'updated_count': len(updated_articles),
        'new_articles': len(new_articles),
        'title_differences': len(title_differences),
        'missing_articles': missing_articles,
        'extra_articles': extra_articles
    }

def create_summary_report():
    """Tạo báo cáo tóm tắt"""
    print(f"\n" + "="*60)
    print(f"📋 BÁO CÁO TÓM TẮT QUAY TRÌNH CẬP NHẬT")
    print(f"="*60)
    
    stats = analyze_differences()
    
    print(f"\n🎯 KẾT QUẢ:")
    print(f"   ✅ Đã trích xuất thành công dữ liệu từ file ND100.docx")
    print(f"   ✅ Đã tăng từ {stats['original_count']} điều lên {stats['updated_count']} điều")
    print(f"   ✅ Đã thêm {stats['new_articles']} điều mới")
    
    if not stats['missing_articles']:
        print(f"   ✅ Dữ liệu hoàn chỉnh từ Điều 1 đến Điều 86")
    else:
        print(f"   ⚠️ Còn thiếu {len(stats['missing_articles'])} điều")
    
    print(f"\n📂 FILES ĐÃ TẠO:")
    print(f"   📄 File JSON cập nhật: data/processed/nghi_dinh_100_2019_updated.json")
    print(f"   📄 File JSON gốc (giữ nguyên): data/raw/legal_documents/nghi_dinh_100_2019.json")
    
    print(f"\n🔍 KHUYẾN NGHỊ:")
    if stats['title_differences'] > 0:
        print(f"   • Cần xem xét {stats['title_differences']} điều có khác biệt về tiêu đề")
    
    if stats['missing_articles']:
        print(f"   • Cần kiểm tra lại các điều thiếu: {', '.join(map(str, stats['missing_articles']))}")
    
    print(f"   • File DOCX là nguồn dữ liệu chính xác nhất (86 điều đầy đủ)")
    print(f"   • Nên sử dụng file JSON đã cập nhật cho các phân tích tiếp theo")

if __name__ == "__main__":
    create_summary_report()