"""
Advanced Streamlit web interface for Vietnamese Traffic Law Q&A system.
Integrates Knowledge Graph and Semantic Reasoning capabilities.
"""

import streamlit as st
import json
import time
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

# Also try adding the project root
project_root = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(project_root))

from traffic_law_qa.knowledge.qa_system import TrafficLawQASystem
from traffic_law_qa.knowledge.knowledge_graph import NodeType

# Page configuration
st.set_page_config(
    page_title="Hệ thống Q&A Luật Giao thông Việt Nam - Tri thức Ngữ nghĩa",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Constants
VIOLATIONS_DATA_PATH = Path(__file__).parent.parent.parent.parent / "data" / "processed" / "violations.json"

@st.cache_resource
def load_qa_system():
    """Load and cache the QA system."""
    try:
        return TrafficLawQASystem(str(VIOLATIONS_DATA_PATH))
    except Exception as e:
        st.error(f"Không thể khởi tạo hệ thống: {e}")
        return None


def main():
    """Main Streamlit application with knowledge graph integration."""
    
    # Header
    st.title("🚦 Hệ thống Q&A Luật Giao thông Việt Nam")
    st.markdown("*Hệ thống Tri thức Ngữ nghĩa với Đồ thị Tri thức và Suy luận Semantic*")
    
    # Load QA system
    qa_system = load_qa_system()
    if not qa_system:
        st.error("Không thể khởi động hệ thống. Vui lòng kiểm tra dữ liệu.")
        return
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Cài đặt hệ thống")
        
        # Search parameters
        st.subheader("🔍 Tham số tìm kiếm")
        max_results = st.slider(
            "Số kết quả tối đa",
            min_value=1,
            max_value=20,
            value=5,
            help="Số lượng kết quả tối đa hiển thị"
        )
        
        similarity_threshold = st.slider(
            "Ngưỡng tương đồng ngữ nghĩa",
            min_value=0.3,
            max_value=0.9,
            value=0.6,
            step=0.05,
            help="Ngưỡng tối thiểu cho độ tương đồng (0.6 = khuyến nghị)"
        )
        
        st.markdown("---")
        
        # System information
        st.subheader("📊 Thông tin hệ thống")
        if st.button("Xem thống kê chi tiết"):
            display_system_dashboard(qa_system)
            
        # Display basic stats
        stats = qa_system.get_system_statistics()
        st.metric("Tổng số vi phạm", stats['knowledge_graph']['node_types'].get('behavior', 0))
        st.metric("Nodes trong Knowledge Graph", stats['knowledge_graph']['total_nodes'])
        st.metric("Relations", stats['knowledge_graph']['total_relations'])
        
        st.markdown("---")
        
        # Advanced features
        st.subheader("🚀 Tính năng nâng cao")
        if st.button("🧠 Khám phá Knowledge Graph"):
            st.session_state.show_kg_explorer = True
            
        if st.button("🔬 Benchmark hệ thống"):
            st.session_state.show_benchmark = True
    
    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 Tìm kiếm thông minh", 
        "🧠 Khám phá tri thức", 
        "📊 Phân tích hệ thống",
        "🔬 Đánh giá hiệu suất"
    ])
    
    with tab1:
        display_smart_search_interface(qa_system, max_results, similarity_threshold)
        
    with tab2:
        display_knowledge_explorer(qa_system)
        
    with tab3:
        display_system_dashboard(qa_system)
        
    with tab4:
        display_benchmark_interface(qa_system)


def display_smart_search_interface(qa_system: TrafficLawQASystem, max_results: int, similarity_threshold: float):
    """Display the main search interface with advanced features."""
    
    st.header("🔍 Tìm kiếm thông minh với Suy luận Ngữ nghĩa")
    
    # Example queries
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.subheader("💡 Ví dụ mẫu")
        example_queries = [
            "Đi xe máy vượt đèn đỏ",
            "Không đội mũ bảo hiểm khi lái xe máy", 
            "Lái xe ô tô quá tốc độ 20km/h",
            "Đỗ xe trên vỉa hè",
            "Uống rượu bia rồi lái xe với nồng độ 0.3mg/l",
            "Không có bằng lái xe",
            "Chở quá số người quy định",
            "Vượt đèn vàng tại ngã tư"
        ]
        
        for i, example in enumerate(example_queries):
            if st.button(f"📝 {example}", key=f"example_{i}"):
                st.session_state.selected_query = example
    
    with col1:
        # Search input
        query = st.text_area(
            "Nhập câu hỏi về luật giao thông (tiếng Việt tự nhiên):",
            value=st.session_state.get('selected_query', ''),
            placeholder="Ví dụ: Tôi đi xe máy không đội mũ bảo hiểm, vượt đèn đỏ thì bị phạt bao nhiêu tiền?",
            height=120,
            help="Hệ thống hiểu tiếng Việt tự nhiên. Bạn có thể hỏi như nói chuyện bình thường."
        )
        
        # Search controls
        col_search, col_clear = st.columns([2, 1])
        
        with col_search:
            search_button = st.button("🔍 Tìm kiếm với AI", type="primary", width="stretch")
            
        with col_clear:
            if st.button("🗑️ Xóa", width="stretch"):
                st.session_state.selected_query = ""
                st.rerun()
        
        # Search results
        if search_button and query.strip():
            with st.spinner("🧠 Hệ thống đang phân tích câu hỏi và suy luận..."):
                start_time = time.time()
                
                try:
                    results = qa_system.ask_question(
                        query, 
                        max_results=max_results,
                        similarity_threshold=similarity_threshold
                    )
                    
                    search_time = time.time() - start_time
                    display_intelligent_results(results, search_time)
                    
                except Exception as e:
                    st.error(f"Lỗi khi xử lý câu hỏi: {str(e)}")


def display_intelligent_results(results: Dict[str, Any], search_time: float):
    """Display results with intelligent analysis and reasoning."""
    
    st.markdown("---")
    st.header("📋 Kết quả phân tích")
    
    # Performance metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("⏱️ Thời gian", f"{search_time:.2f}s")
    with col2:
        confidence = results.get('confidence', 'none')
        confidence_color = {'high': '🟢', 'medium': '🟡', 'low': '🟠', 'none': '🔴', 'error': '❌'}
        st.metric("🎯 Độ tin cậy", f"{confidence_color.get(confidence, '❓')} {confidence}")
    with col3:
        similarity = results.get('similarity_score', 0)
        st.metric("🔗 Độ tương đồng", f"{similarity:.2f}")
    with col4:
        intent_type = results.get('intent', {}).get('type', 'unknown')
        st.metric("🎭 Intent", intent_type.replace('_', ' ').title())
    
    # Main answer
    if results.get('confidence') in ['high', 'medium']:
        st.success("✅ **Tìm thấy thông tin phù hợp**")
        
        # Display answer with formatting
        answer = results.get('answer', '')
        st.markdown(f"### 💬 Trả lời:\n{answer}")
        
        # Similar cases
        similar_cases = results.get('similar_cases', [])
        if similar_cases:
            st.markdown("### 🔄 Các trường hợp tương tự:")
            for i, case in enumerate(similar_cases[:3]):
                with st.expander(f"Trường hợp {i+1} - Độ tương đồng: {case['similarity']:.2f}"):
                    st.write(f"**Mô tả:** {case['description']}")
                    st.write(f"**Phân loại:** {case.get('category', 'N/A')}")
        
        # Citations and legal references
        citations = results.get('citations', [])
        if citations:
            st.markdown("### 📚 Trích dẫn pháp lý:")
            for citation in citations:
                st.info(f"📋 **{citation['source']}** ({citation.get('type', 'legal_document')})")
                
    elif results.get('confidence') == 'none':
        st.warning("⚠️ **Không tìm thấy thông tin phù hợp**")
        st.markdown(results.get('answer', 'Không có dữ liệu phù hợp.'))
        
        suggestions = results.get('additional_info', {}).get('suggestions', [])
        if suggestions:
            st.markdown("### 💡 Gợi ý:")
            for suggestion in suggestions:
                st.write(f"• {suggestion}")
    else:
        st.error("❌ **Đã xảy ra lỗi**")
        st.write(results.get('answer', 'Lỗi không xác định.'))
    
    # Advanced information
    with st.expander("🔧 Thông tin kỹ thuật (dành cho nhà phát triển)"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.json({
                'intent_analysis': results.get('intent', {}),
                'processing_metrics': {
                    'search_time': f"{search_time:.3f}s",
                    'total_results_found': results.get('additional_info', {}).get('total_results_found', 0),
                    'similarity_threshold_used': 0.6
                }
            })
            
        with col2:
            matched_entities = results.get('additional_info', {}).get('matched_entities', [])
            if matched_entities:
                st.write("**Entities được trích xuất:**")
                for entity in matched_entities:
                    st.write(f"• {entity.get('text', 'N/A')} ({entity.get('type', 'N/A')})")


def display_knowledge_explorer(qa_system: TrafficLawQASystem):
    """Display knowledge graph exploration interface."""
    
    st.header("🧠 Khám phá Đồ thị Tri thức")
    st.markdown("*Khám phá mối quan hệ giữa Hành vi → Mức phạt → Điều luật → Biện pháp bổ sung*")
    
    # Node type statistics
    stats = qa_system.get_system_statistics()
    kg_stats = stats['knowledge_graph']
    
    st.subheader("📊 Thống kê Nodes theo loại")
    
    # Create visualization
    node_types = kg_stats['node_types']
    if node_types:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Pie chart
            fig_pie = px.pie(
                values=list(node_types.values()),
                names=list(node_types.keys()),
                title="Phân bố Node Types"
            )
            st.plotly_chart(fig_pie, width="stretch")
            
        with col2:
            # Bar chart
            fig_bar = px.bar(
                x=list(node_types.keys()),
                y=list(node_types.values()),
                title="Số lượng Nodes theo loại"
            )
            st.plotly_chart(fig_bar, width="stretch")
    
    # Relationship statistics
    st.subheader("🔗 Thống kê Relations")
    relation_types = kg_stats.get('relation_types', {})
    if relation_types:
        df_relations = pd.DataFrame([
            {'Loại quan hệ': k.replace('_', ' ').title(), 'Số lượng': v}
            for k, v in relation_types.items()
        ])
        st.dataframe(df_relations, width="stretch")
    
    # Sample exploration
    st.subheader("🔍 Khám phá mẫu")
    
    behavior_nodes = qa_system.knowledge_graph.find_nodes_by_type(NodeType.BEHAVIOR)
    if behavior_nodes:
        selected_behavior = st.selectbox(
            "Chọn một hành vi để khám phá:",
            options=[(node.id, node.label) for node in behavior_nodes[:20]],
            format_func=lambda x: x[1]
        )
        
        if selected_behavior:
            behavior_id = selected_behavior[0]
            chain = qa_system.knowledge_graph.get_behavior_penalty_chain(behavior_id)
            
            st.markdown(f"### 🔄 Chuỗi tri thức cho: *{selected_behavior[1]}*")
            
            # Display chain
            if chain:
                # Behavior
                behavior = chain.get('behavior')
                if behavior:
                    st.markdown(f"**🎭 Hành vi:** {behavior.label}")
                    if behavior.properties.get('category'):
                        st.markdown(f"**📂 Danh mục:** {behavior.properties['category']}")
                
                # Penalties
                penalties = chain.get('penalties', [])
                if penalties:
                    st.markdown("**💰 Mức phạt:**")
                    for penalty in penalties:
                        fine_min = penalty.properties.get('fine_min', 0)
                        fine_max = penalty.properties.get('fine_max', 0)
                        if fine_min and fine_max:
                            st.write(f"• {fine_min:,} - {fine_max:,} VNĐ")
                        else:
                            st.write(f"• {penalty.label}")
                
                # Law articles
                law_articles = chain.get('law_articles', [])
                if law_articles:
                    st.markdown("**⚖️ Căn cứ pháp lý:**")
                    for law in law_articles:
                        st.write(f"• {law.label}")
                
                # Additional measures
                additional_measures = chain.get('additional_measures', [])
                if additional_measures:
                    st.markdown("**🔧 Biện pháp bổ sung:**")
                    for measure in additional_measures:
                        st.write(f"• {measure.label}")
            
            # Similar behaviors
            st.markdown("### 🔄 Hành vi tương tự")
            similar_behaviors = qa_system.reasoning_engine.get_similar_behaviors(behavior_id, limit=5)
            
            if similar_behaviors:
                for similar_node, similarity in similar_behaviors:
                    st.write(f"• **{similar_node.label}** (độ tương đồng: {similarity:.3f})")
            else:
                st.write("Không tìm thấy hành vi tương tự.")


def display_system_dashboard(qa_system: TrafficLawQASystem):
    """Display comprehensive system dashboard."""
    
    st.header("📊 Dashboard Hệ thống")
    
    # Get comprehensive statistics
    stats = qa_system.get_system_statistics()
    
    # System overview
    st.subheader("🏗️ Tổng quan hệ thống")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📝 Tổng Vi phạm",
            stats['knowledge_graph']['node_types'].get('behavior', 0),
            help="Số lượng hành vi vi phạm trong cơ sở dữ liệu"
        )
        
    with col2:
        st.metric(
            "🧠 Knowledge Nodes",
            stats['knowledge_graph']['total_nodes'],
            help="Tổng số nodes trong knowledge graph"
        )
        
    with col3:
        st.metric(
            "🔗 Relations",
            stats['knowledge_graph']['total_relations'],
            help="Tổng số mối quan hệ giữa các nodes"
        )
        
    with col4:
        density = stats['knowledge_graph'].get('graph_density', 0)
        st.metric(
            "📊 Graph Density",
            f"{density:.3f}",
            help="Mật độ kết nối của knowledge graph (0-1)"
        )
    
    # Capabilities overview
    st.subheader("🚀 Khả năng hệ thống")
    
    capabilities = stats.get('system_info', {}).get('capabilities', {
        'intent_detection': True,
        'entity_extraction': True, 
        'semantic_search': True,
        'knowledge_reasoning': True,
        'vietnamese_nlp': True
    })
    cap_cols = st.columns(len(capabilities))
    
    for i, (cap_name, enabled) in enumerate(capabilities.items()):
        with cap_cols[i]:
            status_icon = "✅" if enabled else "❌"
            cap_display = cap_name.replace('_', ' ').title()
            st.metric(cap_display, status_icon)
    
    # Performance metrics
    st.subheader("⚡ Hiệu suất")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Embedding Model:** {stats['system_info']['embedding_model']}
        
        **Cache Status:** {stats['system_info']['embeddings_cached']} embeddings đã cache
        
        **Last Updated:** {stats['system_info']['last_updated'][:19]}
        """)
        
    with col2:
        avg_degree = stats['knowledge_graph'].get('average_degree', 0)
        st.info(f"""
        **Average Node Degree:** {avg_degree:.2f}
        
        **Graph Connectivity:** {'Good' if density > 0.1 else 'Sparse'}
        
        **Data Quality:** {'High' if stats['knowledge_graph']['total_nodes'] > 1000 else 'Medium'}
        """)


def display_benchmark_interface(qa_system: TrafficLawQASystem):
    """Display system benchmarking interface."""
    
    st.header("🔬 Đánh giá Hiệu suất Hệ thống")
    st.markdown("*So sánh hiệu quả giữa các phương pháp tìm kiếm và LLM*")
    
    # Predefined test queries
    test_queries = [
        "Đi xe máy vượt đèn đỏ",
        "Không đội mũ bảo hiểm",
        "Lái xe sau khi uống rượu",
        "Chở quá số người quy định",
        "Đỗ xe sai quy định",
        "Không có bằng lái xe",
        "Vượt quá tốc độ cho phép",
        "Sử dụng điện thoại khi lái xe",
        "Không tuân thủ biển báo giao thông",
        "Lái xe ô tô không có bảo hiểm"
    ]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 Bộ test queries")
        
        # Allow custom queries
        custom_queries = st.text_area(
            "Thêm câu hỏi test (mỗi dòng một câu):",
            placeholder="Nhập các câu hỏi để test, mỗi dòng một câu",
            height=100
        )
        
        if custom_queries.strip():
            additional_queries = [q.strip() for q in custom_queries.split('\n') if q.strip()]
            all_queries = test_queries + additional_queries
        else:
            all_queries = test_queries
            
        st.write(f"**Tổng số queries để test:** {len(all_queries)}")
        
        # Run benchmark
        if st.button("🚀 Chạy Benchmark", type="primary"):
            with st.spinner("Đang chạy benchmark..."):
                benchmark_results = qa_system.benchmark_system(all_queries)
                display_benchmark_results(benchmark_results)
                
    with col2:
        st.subheader("📋 Test Queries mặc định")
        for i, query in enumerate(test_queries, 1):
            st.write(f"{i}. {query}")


def display_benchmark_results(results: Dict[str, Any]):
    """Display benchmark results with detailed analysis."""
    
    st.markdown("---")
    st.header("📊 Kết quả Benchmark")
    
    # Overall metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📝 Tổng Queries", results['total_queries'])
    with col2:
        st.metric("✅ Thành công", results['successful_answers'])
    with col3:
        success_rate = results['success_rate'] * 100
        st.metric("🎯 Tỷ lệ thành công", f"{success_rate:.1f}%")
    with col4:
        avg_time = results['average_processing_time']
        st.metric("⏱️ Thời gian TB", f"{avg_time:.3f}s")
    
    # Confidence distribution
    st.subheader("📊 Phân bố Độ tin cậy")
    
    conf_dist = results['confidence_distribution']
    if conf_dist:
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart for confidence
            fig_conf = px.pie(
                values=list(conf_dist.values()),
                names=list(conf_dist.keys()),
                title="Phân bố Confidence",
                color_discrete_map={
                    'high': '#28a745',
                    'medium': '#ffc107', 
                    'low': '#fd7e14',
                    'none': '#dc3545'
                }
            )
            st.plotly_chart(fig_conf, width="stretch")
            
        with col2:
            # Intent distribution
            intent_dist = results['intent_distribution']
            if intent_dist:
                fig_intent = px.bar(
                    x=list(intent_dist.keys()),
                    y=list(intent_dist.values()),
                    title="Phân bố Intent Types"
                )
                st.plotly_chart(fig_intent, width="stretch")
    
    # Detailed results
    st.subheader("📋 Chi tiết từng Query")
    
    query_results = results.get('query_results', [])
    if query_results:
        df_results = pd.DataFrame(query_results)
        
        # Add color coding for confidence
        def color_confidence(val):
            colors = {
                'high': 'background-color: #d4edda',
                'medium': 'background-color: #fff3cd',
                'low': 'background-color: #f8d7da',
                'none': 'background-color: #f8d7da'
            }
            return colors.get(val, '')
        
        if 'confidence' in df_results.columns:
            styled_df = df_results.style.applymap(color_confidence, subset=['confidence'])
            st.dataframe(styled_df, width="stretch")
        else:
            st.dataframe(df_results, width="stretch")
    
    # Performance analysis
    st.subheader("📈 Phân tích Hiệu suất")
    
    if success_rate >= 80:
        st.success("🎉 **Hiệu suất Xuất sắc!** Hệ thống hoạt động rất tốt với tỷ lệ thành công cao.")
    elif success_rate >= 60:
        st.warning("⚠️ **Hiệu suất Khá tốt.** Có thể cải thiện thêm độ chính xác.")
    else:
        st.error("❌ **Cần cải thiện.** Hệ thống cần được tối ưu hóa thêm.")
        
    # Recommendations
    st.subheader("💡 Khuyến nghị cải thiện")
    
    recommendations = []
    
    if results['confidence_distribution'].get('none', 0) > results['total_queries'] * 0.3:
        recommendations.append("🔧 Cần mở rộng cơ sở dữ liệu để cover nhiều trường hợp hơn")
        
    if avg_time > 2.0:
        recommendations.append("⚡ Cần tối ưu hóa tốc độ xử lý (hiện tại > 2s)")
        
    if results['confidence_distribution'].get('high', 0) < results['total_queries'] * 0.5:
        recommendations.append("🎯 Cần cải thiện độ chính xác của semantic search")
        
    if recommendations:
        for rec in recommendations:
            st.write(f"• {rec}")
    else:
        st.success("✅ Hệ thống đang hoạt động ở mức tối ưu!")


if __name__ == "__main__":
    main()


