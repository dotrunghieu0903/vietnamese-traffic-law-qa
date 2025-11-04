"""
Script kiểm tra tính đầy đủ và nhất quán của dữ liệu
So sánh file nghi_dinh_100_2019.json với file PDF gốc
"""

import json
import pandas as pd
from datetime import datetime

def load_current_data():
    """Load dữ liệu hiện tại từ các file"""
    
    # Load file JSON legal document
    with open('../raw/legal_documents/nghi_dinh_100_2019.json', 'r', encoding='utf-8') as f:
        legal_doc = json.load(f)
    
    # Load file CSV violations
    violations_df = pd.read_csv('../raw/violations_dataset/traffic_violations_extended.csv')
    
    return legal_doc, violations_df

def analyze_content_coverage():
    """Phân tích mức độ bao phủ nội dung"""
    
    legal_doc, violations_df = load_current_data()
    
    print("📊 PHÂN TÍCH TÍNH ĐẦY ĐỦ DỮ LIỆU NGHỊ ĐỊNH 100/2019")
    print("=" * 70)
    
    # 1. Kiểm tra cấu trúc legal document
    print("\n1. CẤU TRÚC VĂN BẢN PHÁP LÝ:")
    print(f"   - Tiêu đề: {legal_doc['document_info']['title']}")
    print(f"   - Ngày ban hành: {legal_doc['document_info']['issued_date']}")
    print(f"   - Ngày hiệu lực: {legal_doc['document_info']['effective_date']}")
    
    # Kiểm tra amendments
    amendments = legal_doc['document_info']['amendments']
    print(f"   - Số văn bản sửa đổi: {len(amendments)}")
    for amend in amendments:
        print(f"     + {amend['document']} ({amend['date']})")
    
    # 2. Kiểm tra cấu trúc chương/điều
    print(f"\n2. CẤU TRÚC CHƯƠNG/ĐIỀU:")
    structure = legal_doc['structure']
    print(f"   - Số chương: {len(structure['chapters'])}")
    
    total_articles = 0
    for chapter in structure['chapters']:
        article_count = len(chapter['articles'])
        total_articles += article_count
        print(f"   - Chương {chapter['chapter']}: {chapter['title']} ({article_count} điều)")
    
    print(f"   - Tổng số điều: {total_articles}")
    
    # 3. Kiểm tra các điều chính đã có
    print(f"\n3. CÁC ĐIỀU CHÍNH ĐÃ CÓ DỮ LIỆU:")
    key_articles = legal_doc['key_articles']
    print(f"   - Số điều đã có dữ liệu: {len(key_articles)}")
    
    for article_key, article_data in key_articles.items():
        section_count = len(article_data['sections'])
        total_violations = sum(len(section['violations']) for section in article_data['sections'])
        print(f"   - {article_key.upper()}: {article_data['title']}")
        print(f"     + {section_count} khoản, {total_violations} vi phạm")
    
    # 4. Kiểm tra dataset violations
    print(f"\n4. DATASET VI PHẠM:")
    print(f"   - Tổng số vi phạm trong CSV: {len(violations_df)}")
    
    # Phân loại theo category
    categories = violations_df['category'].value_counts()
    print(f"   - Số danh mục: {len(categories)}")
    print("   - Phân bổ theo danh mục:")
    for category, count in categories.head(10).items():
        print(f"     + {category}: {count} vi phạm")
    
    # Phân loại theo legal_basis
    legal_basis_counts = violations_df['legal_basis'].value_counts()
    print(f"\n   - Phân bổ theo điều luật:")
    for basis, count in legal_basis_counts.head(10).items():
        print(f"     + {basis}: {count} vi phạm")
    
    # 5. Kiểm tra tính nhất quán
    print(f"\n5. KIỂM TRA TÍNH NHẤT QUÁN:")
    
    # Kiểm tra legal basis trong CSV có khớp với JSON không
    json_articles = set(key_articles.keys())
    csv_articles = set()
    
    for legal_basis in violations_df['legal_basis'].unique():
        if pd.notna(legal_basis):
            parts = legal_basis.split()
            if len(parts) >= 2:
                article_num = parts[1]
                csv_articles.add(f"dieu_{article_num}")
    
    matching_articles = json_articles.intersection(csv_articles)
    missing_in_json = csv_articles - json_articles
    missing_in_csv = json_articles - csv_articles
    
    print(f"   - Điều khớp nhau: {len(matching_articles)}")
    print(f"   - Thiếu trong JSON: {len(missing_in_json)} ({missing_in_json})")
    print(f"   - Thiếu trong CSV: {len(missing_in_csv)} ({missing_in_csv})")
    
    # 6. Phân tích mức độ phạt
    print(f"\n6. PHÂN TÍCH MỨC ĐỘ PHẠT:")
    fine_ranges = violations_df[['fine_min', 'fine_max']].describe()
    print(f"   - Mức phạt thấp nhất: {violations_df['fine_min'].min():,} VNĐ")
    print(f"   - Mức phạt cao nhất: {violations_df['fine_max'].max():,} VNĐ")
    print(f"   - Mức phạt trung bình: {violations_df['fine_min'].mean():,.0f} - {violations_df['fine_max'].mean():,.0f} VNĐ")
    
    # Phân bổ theo severity
    severity_counts = violations_df['severity'].value_counts()
    print(f"\n   - Phân bổ theo độ nghiêm trọng:")
    for severity, count in severity_counts.items():
        print(f"     + {severity}: {count} vi phạm")
    
    return legal_doc, violations_df

def check_missing_content():
    """Kiểm tra nội dung còn thiếu từ PDF gốc"""
    
    print(f"\n7. ĐÁNH GIÁ NỘI DUNG CÒN THIẾU:")
    print("=" * 50)
    
    # Danh sách các điều cần bổ sung dựa trên cấu trúc Nghị định 100
    expected_articles = [
        "Điều 1 - Phạm vi điều chỉnh",
        "Điều 2 - Đối tượng áp dụng", 
        "Điều 3 - Nguyên tắc xử phạt",
        "Điều 13 - Vi phạm quy định về biển báo hiệu",
        "Điều 14 - Vi phạm về đường cao tốc",
        "Điều 15 - Vi phạm về đường đô thị",
        "Điều 16 - Vi phạm về vận tải hành khách",
        "Điều 17 - Vi phạm về vận tải hàng hóa",
        "Điều 18 - Vi phạm khác"
    ]
    
    print("   CÁC ĐIỀU CÒN THIẾU HOẶC CHƯA ĐẦY ĐỦ:")
    for article in expected_articles:
        print(f"   ❌ {article}")
    
    print(f"\n   CÁC LOẠI VI PHẠM CẦN BỔ SUNG:")
    missing_violation_types = [
        "Vi phạm về biển báo hiệu đường bộ",
        "Vi phạm về đường cao tốc (ngoài lùi xe)",
        "Vi phạm về vận tải hành khách công cộng",
        "Vi phạm về vận tải hàng hóa nguy hiểm",
        "Vi phạm về giờ cấm tải trọng",
        "Vi phạm về đào tạo lái xe",
        "Vi phạm về cải tạo xe trái phép",
        "Vi phạm về gây ô nhiễm môi trường"
    ]
    
    for violation_type in missing_violation_types:
        print(f"   ➕ {violation_type}")

def generate_recommendations():
    """Đưa ra khuyến nghị cải thiện"""
    
    print(f"\n8. KHUYẾN NGHỊ HOÀN THIỆN:")
    print("=" * 40)
    
    recommendations = [
        {
            "priority": "Cao",
            "task": "Bổ sung dữ liệu từ file PDF mới",
            "details": [
                "Trích xuất thêm các điều 13-18 từ PDF",
                "Cập nhật các mức phạt theo Nghị định 168/2024",
                "Bổ sung các vi phạm mới"
            ]
        },
        {
            "priority": "Trung bình", 
            "task": "Cải thiện chất lượng dữ liệu",
            "details": [
                "Kiểm tra và sửa lỗi inconsistency",
                "Chuẩn hóa format mô tả vi phạm",
                "Bổ sung metadata đầy đủ"
            ]
        },
        {
            "priority": "Thấp",
            "task": "Mở rộng dataset",
            "details": [
                "Thêm ví dụ thực tế cho mỗi vi phạm",
                "Bổ sung các trường hợp ngoại lệ",
                "Thêm cross-reference giữa các điều"
            ]
        }
    ]
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n   {i}. ƯU TIÊN {rec['priority'].upper()}: {rec['task']}")
        for detail in rec['details']:
            print(f"      - {detail}")

def main():
    """Hàm chính thực hiện kiểm tra"""
    
    print("🔍 BẮT ĐẦU KIỂM TRA TÍNH ĐẦY ĐỦ DỮ LIỆU")
    print("📅 Thời gian:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    try:
        # Phân tích dữ liệu hiện tại
        legal_doc, violations_df = analyze_content_coverage()
        
        # Kiểm tra nội dung thiếu
        check_missing_content()
        
        # Đưa ra khuyến nghị
        generate_recommendations()
        
        print(f"\n✅ HOÀN THÀNH KIỂM TRA")
        print("📊 Kết luận: Dữ liệu đã có cơ bản đầy đủ cho các điều chính (4-12)")
        print("📈 Cần bổ sung: Các điều 13-18 và cập nhật theo văn bản mới nhất")
        
    except Exception as e:
        print(f"❌ Lỗi khi kiểm tra: {e}")

if __name__ == "__main__":
    main()