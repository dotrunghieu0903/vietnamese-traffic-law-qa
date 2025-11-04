#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kiểm tra chất lượng dữ liệu trích xuất từ DOCX
"""

import json
import re
from typing import Dict, List, Any

def validate_extracted_data():
    """Kiểm tra và xác thực dữ liệu đã trích xuất"""
    
    updated_json = r"c:\Users\hieudt22\Documents\VNI-TrafficLawQA\data\processed\nghi_dinh_100_2019_updated.json"
    
    with open(updated_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    articles = data.get("key_articles", {})
    
    print("🔍 KIỂM TRA CHẤT LƯỢNG DỮ LIỆU TRÍCH XUẤT")
    print("=" * 60)
    
    # 1. Kiểm tra tính đầy đủ
    print(f"\n1️⃣ KIỂM TRA TÍNH ĐẦY ĐỦ:")
    expected_articles = set(f"dieu_{i}" for i in range(1, 87))
    actual_articles = set(articles.keys())
    
    missing = expected_articles - actual_articles
    extra = actual_articles - expected_articles
    
    print(f"   • Điều mong muốn: 1-86 ({len(expected_articles)} điều)")
    print(f"   • Điều thực tế: {len(actual_articles)} điều")
    print(f"   • Thiếu: {len(missing)} điều")
    print(f"   • Thừa: {len(extra)} điều")
    
    if missing:
        print(f"   • Các điều thiếu: {sorted([int(x.split('_')[1]) for x in missing])}")
    if extra:
        print(f"   • Các điều thừa: {list(extra)}")
    
    # 2. Kiểm tra chất lượng tiêu đề
    print(f"\n2️⃣ KIỂM TRA CHẤT LƯỢNG TIÊU ĐỀ:")
    
    problematic_titles = []
    good_titles = []
    
    for key, article in articles.items():
        title = article.get('title', '')
        article_num = key.replace('dieu_', '')
        
        # Kiểm tra tiêu đề có vấn đề
        if (not title or 
            title.strip() == ';' or 
            title.strip() == f'Điều {article_num}' or 
            len(title.strip()) < 5):
            problematic_titles.append((key, title))
        else:
            good_titles.append((key, title))
    
    print(f"   • Tiêu đề tốt: {len(good_titles)} điều")
    print(f"   • Tiêu đề có vấn đề: {len(problematic_titles)} điều")
    
    if problematic_titles:
        print(f"\n   📋 Một số tiêu đề có vấn đề:")
        for key, title in problematic_titles[:10]:
            article_num = key.replace('dieu_', '')
            print(f"      - Điều {article_num}: '{title}'")
    
    # 3. Kiểm tra nội dung sections
    print(f"\n3️⃣ KIỂM TRA CHẤT LƯỢNG NỘI DUNG:")
    
    articles_with_sections = 0
    articles_with_violations = 0
    articles_with_fines = 0
    empty_sections = 0
    
    for key, article in articles.items():
        sections = article.get('sections', [])
        
        if sections:
            articles_with_sections += 1
            
            for section in sections:
                content = section.get('content', '')
                violations = section.get('violations', [])
                fine_range = section.get('fine_range', '')
                
                if not content.strip() or content.strip() == ',':
                    empty_sections += 1
                
                if violations:
                    articles_with_violations += 1
                    break
            
            # Kiểm tra mức phạt
            for section in sections:
                if section.get('fine_range'):
                    articles_with_fines += 1
                    break
    
    print(f"   • Điều có sections: {articles_with_sections}/{len(articles)}")
    print(f"   • Điều có vi phạm: {articles_with_violations}/{len(articles)}")
    print(f"   • Điều có mức phạt: {articles_with_fines}/{len(articles)}")
    print(f"   • Sections trống: {empty_sections}")
    
    # 4. Kiểm tra mẫu nội dung tốt
    print(f"\n4️⃣ MẪU NỘI DUNG TỐT:")
    
    quality_articles = []
    for key, article in articles.items():
        title = article.get('title', '')
        sections = article.get('sections', [])
        
        # Điều có tiêu đề tốt và có sections với nội dung
        if (len(title.strip()) > 10 and 
            sections and 
            any(len(s.get('content', '').strip()) > 20 for s in sections)):
            quality_articles.append((key, article))
    
    print(f"   • Số điều chất lượng tốt: {len(quality_articles)}")
    
    # Hiển thị 3 mẫu tốt
    for i, (key, article) in enumerate(quality_articles[:3]):
        article_num = key.replace('dieu_', '')
        title = article['title']
        sections = article['sections']
        
        print(f"\n   📄 Mẫu {i+1} - Điều {article_num}:")
        print(f"      Tiêu đề: {title}")
        print(f"      Số sections: {len(sections)}")
        
        if sections:
            first_section = sections[0]
            content = first_section.get('content', '')
            violations = first_section.get('violations', [])
            fine_range = first_section.get('fine_range', '')
            
            print(f"      Nội dung: {content[:80]}{'...' if len(content) > 80 else ''}")
            if violations:
                print(f"      Vi phạm: {len(violations)} loại")
            if fine_range:
                print(f"      Mức phạt: {fine_range}")
    
    # 5. Đánh giá tổng thể
    print(f"\n5️⃣ ĐÁNH GIÁ TỔNG THỂ:")
    
    completeness_score = (len(actual_articles) / 86) * 100
    title_quality_score = (len(good_titles) / len(articles)) * 100 if articles else 0
    content_quality_score = (len(quality_articles) / len(articles)) * 100 if articles else 0
    
    print(f"   • Điểm tính đầy đủ: {completeness_score:.1f}%")
    print(f"   • Điểm chất lượng tiêu đề: {title_quality_score:.1f}%")
    print(f"   • Điểm chất lượng nội dung: {content_quality_score:.1f}%")
    
    overall_score = (completeness_score + title_quality_score + content_quality_score) / 3
    print(f"   • Điểm tổng thể: {overall_score:.1f}%")
    
    if overall_score >= 80:
        print(f"   ✅ CHẤT LƯỢNG TỐT - Dữ liệu sẵn sàng sử dụng")
    elif overall_score >= 60:
        print(f"   ⚠️ CHẤT LƯỢNG TRUNG BÌNH - Cần cải thiện một số điểm")
    else:
        print(f"   ❌ CHẤT LƯỢNG THẤP - Cần xử lý lại dữ liệu")
    
    return {
        'completeness_score': completeness_score,
        'title_quality_score': title_quality_score,
        'content_quality_score': content_quality_score,
        'overall_score': overall_score,
        'problematic_titles': len(problematic_titles),
        'quality_articles': len(quality_articles),
        'missing_articles': len(missing),
        'extra_articles': len(extra)
    }

def suggest_improvements():
    """Đề xuất cải thiện"""
    print(f"\n6️⃣ ĐỀ XUẤT CẢI THIỆN:")
    print(f"   🔧 Để cải thiện chất lượng dữ liệu:")
    print(f"   1. Cải thiện thuật toán trích xuất tiêu đề từ DOCX")
    print(f"   2. Bổ sung logic nhận diện vi phạm và mức phạt")
    print(f"   3. Làm sạch dữ liệu các ký tự đặc biệt (';', ',')")
    print(f"   4. Xử lý các trường hợp đặc biệt trong format DOCX")
    print(f"   5. Thêm validation rules để đảm bảo tính nhất quán")
    
    print(f"\n   📋 Hành động tiếp theo:")
    print(f"   • So sánh thủ công một số điều quan trọng với file DOCX gốc")
    print(f"   • Cải thiện script trích xuất để xử lý tốt hơn")
    print(f"   • Tạo bộ test cases để validation")
    print(f"   • Backup dữ liệu tốt trước khi cập nhật")

if __name__ == "__main__":
    stats = validate_extracted_data()
    suggest_improvements()
    
    print(f"\n" + "="*60)
    print(f"✅ HOÀN THÀNH KIỂM TRA CHẤT LƯỢNG")
    print(f"Điểm tổng thể: {stats['overall_score']:.1f}%")
    print(f"="*60)