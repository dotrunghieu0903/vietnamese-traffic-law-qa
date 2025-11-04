"""Streamlit web interface for Traffic Law Q&A system."""

import streamlit as st
import requests
import json
import time
from typing import List, Dict, Any

# Page configuration
st.set_page_config(
    page_title="Hệ thống Q&A Luật Giao thông Việt Nam",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
API_BASE_URL = "http://localhost:8000"

def main():
    """Main Streamlit application."""
    st.title("🚦 Hệ thống Q&A Luật Giao thông Việt Nam")
    st.markdown("*Tra cứu vi phạm giao thông và mức phạt theo ngữ nghĩa*")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Cài đặt")
        
        max_results = st.slider(
            "Số kết quả tối đa",
            min_value=1,
            max_value=20,
            value=10,
            help="Số lượng kết quả tối đa hiển thị"
        )
        
        similarity_threshold = st.slider(
            "Ngưỡng tương đồng",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Ngưỡng tối thiểu cho độ tương đồng ngữ nghĩa"
        )
        
        st.markdown("---")
        
        # Statistics
        if st.button("📊 Thống kê hệ thống"):
            display_statistics()
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🔍 Tìm kiếm vi phạm")
        
        # Search input
        query = st.text_area(
            "Mô tả hành vi vi phạm:",
            placeholder="Ví dụ: Đi xe máy vượt đèn đỏ ở ngã tư, không đội mũ bảo hiểm...",
            height=100,
            help="Nhập mô tả chi tiết về hành vi vi phạm giao thông"
        )
        
        # Search button
        col_search, col_example = st.columns([1, 1])
        
        with col_search:
            search_button = st.button("🔍 Tìm kiếm", type="primary")
        
        with col_example:
            if st.button("💡 Ví dụ mẫu"):
                st.session_state.example_query = True
        
        # Handle example query
        if hasattr(st.session_state, 'example_query') and st.session_state.example_query:
            query = "Đi xe máy vượt đèn đỏ, không đội mũ bảo hiểm, chở theo 3 người"
            st.session_state.example_query = False
            st.rerun()
        
        # Search results
        if search_button and query:
            with st.spinner("Đang tìm kiếm..."):
                results = search_violations(query, max_results, similarity_threshold)
                display_search_results(results, query)
    
    with col2:
        st.header("📋 Thông tin hướng dẫn")
        
        st.info(
            """
            **Cách sử dụng:**
            
            1. Nhập mô tả chi tiết hành vi vi phạm
            2. Điều chỉnh cài đặt tìm kiếm nếu cần
            3. Nhấn "Tìm kiếm" để xem kết quả
            
            **Ví dụ truy vấn:**
            - "Đi xe máy vượt đèn đỏ"
            - "Đỗ xe sai quy định trên vỉa hè"
            - "Lái xe ô tô quá tốc độ cho phép"
            - "Không có bằng lái xe khi tham gia giao thông"
            """
        )
        
        st.warning(
            """
            **Lưu ý:**
            - Kết quả chỉ mang tính chất tham khảo
            - Cần tham khảo ý kiến chuyên gia pháp lý
            - Thông tin dựa trên Nghị định 100/2019/NĐ-CP và các văn bản sửa đổi
            """
        )


def search_violations(query: str, max_results: int, similarity_threshold: float) -> Dict[str, Any]:
    """Search for violations using the API."""
    try:
        payload = {
            "query": query,
            "max_results": max_results,
            "similarity_threshold": similarity_threshold
        }
        
        response = requests.post(
            f"{API_BASE_URL}/search",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Lỗi API: {response.status_code}")
            return {}
    
    except requests.exceptions.ConnectionError:
        st.error("Không thể kết nối đến API. Vui lòng đảm bảo server đang chạy.")
        return {}
    except Exception as e:
        st.error(f"Lỗi: {str(e)}")
        return {}


def display_search_results(results: Dict[str, Any], query: str):
    """Display search results in a formatted way."""
    if not results:
        return
    
    st.markdown("---")
    st.header(f"📋 Kết quả tìm kiếm cho: *{query}*")
    
    if not results.get("results"):
        st.warning("Không tìm thấy vi phạm phù hợp. Thử điều chỉnh từ khóa hoặc giảm ngưỡng tương đồng.")
        return
    
    # Summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Số kết quả", results["total_results"])
    with col2:
        st.metric("Thời gian xử lý", f"{results['processing_time']:.2f}s")
    with col3:
        st.metric("Điểm tương đồng cao nhất", f"{max([r['similarity_score'] for r in results['results']]):.2f}")
    
    # Results
    for i, result in enumerate(results["results"]):
        with st.expander(f"🎯 Vi phạm #{i+1} - Độ tương đồng: {result['similarity_score']:.2f}"):
            display_violation_details(result)


def display_violation_details(result: Dict[str, Any]):
    """Display detailed information about a violation."""
    violation = result["violation"]
    penalty = violation["penalty"]
    
    # Basic info
    st.subheader("📝 Mô tả vi phạm")
    st.write(violation["description"])
    
    # Penalty information
    st.subheader("💰 Thông tin xử phạt")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Mức phạt tiền:**")
        if penalty["fine_amount_min"] == penalty["fine_amount_max"]:
            st.write(f"💵 {penalty['fine_amount_min']:,} VNĐ")
        else:
            st.write(f"💵 {penalty['fine_amount_min']:,} - {penalty['fine_amount_max']:,} VNĐ")
    
    with col2:
        st.write("**Loại vi phạm:**")
        st.write(f"🏷️ {violation['violation_type']}")
    
    # Additional measures
    if penalty["additional_measures"]:
        st.write("**Biện pháp bổ sung:**")
        for measure in penalty["additional_measures"]:
            st.write(f"• {measure}")
    
    # Legal basis
    st.write("**Căn cứ pháp lý:**")
    st.write(f"📋 {penalty['legal_basis']}")
    
    # Keywords
    if result.get("matched_keywords"):
        st.write("**Từ khóa khớp:**")
        keywords_html = " ".join([f"<span style='background-color: #ffd700; padding: 2px 4px; border-radius: 3px;'>{kw}</span>" for kw in result["matched_keywords"]])
        st.markdown(keywords_html, unsafe_allow_html=True)


def display_statistics():
    """Display system statistics."""
    try:
        response = requests.get(f"{API_BASE_URL}/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            
            st.sidebar.markdown("### 📊 Thống kê hệ thống")
            st.sidebar.write(f"**Tổng số vi phạm:** {stats['total_violations']}")
            st.sidebar.write(f"**Embeddings:** {'✅ Đã tạo' if stats['embeddings_generated'] else '❌ Chưa tạo'}")
            
            st.sidebar.write("**Phân loại vi phạm:**")
            for vtype, count in stats["violation_types"].items():
                st.sidebar.write(f"• {vtype}: {count}")
        
        else:
            st.sidebar.error("Không thể lấy thống kê")
    
    except Exception as e:
        st.sidebar.error(f"Lỗi: {str(e)}")


if __name__ == "__main__":
    main()