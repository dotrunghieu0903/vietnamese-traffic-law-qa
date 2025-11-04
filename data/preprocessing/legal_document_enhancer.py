"""
Vietnamese Traffic Law Data Processing Pipeline
Extract and enhance legal document structure from existing JSON data
Supports both ND 100/2019 and ND 123/2021 processing
"""

import json
import re
from typing import Dict, List, Optional
from datetime import datetime
import os


class LegalDocumentExtractor:
    """Extract and enhance Vietnamese legal document structure"""
    
    def __init__(self):
        self.document_structure = {}
        self.supported_documents = {
            'ND_100_2019': 'nghi_dinh_100_2019.json',
            'ND_123_2021': 'nghi_dinh_123_2021.json',
            'ND_168_2024': 'nghi_dinh_168_2024.json'
        }
        
    def detect_document_type(self, legal_data: Dict) -> str:
        """Detect document type based on content"""
        doc_info = legal_data.get('document_info', {})
        title = doc_info.get('title', '')
        
        if '100/2019' in title:
            return 'ND_100_2019'
        elif '123/2021' in title:
            return 'ND_123_2021'
        elif '168/2024' in title:
            return 'ND_168_2024'
        else:
            # Fallback detection
            if 'amends_document' in doc_info or 'amendments_summary' in legal_data:
                return 'ND_123_2021'  # Amendment document
            return 'ND_100_2019'  # Default to base document
        
    def process_existing_legal_data(self, json_path: str) -> Dict:
        """Process existing legal document JSON data instead of extracting from PDF"""
        with open(json_path, 'r', encoding='utf-8') as f:
            legal_data = json.load(f)
        
        # Validate and enhance the existing structure
        enhanced_data = self.enhance_legal_structure(legal_data)
        return enhanced_data
    
    def enhance_legal_structure(self, legal_data: Dict) -> Dict:
        """Enhance existing legal data with additional metadata"""
        enhanced = legal_data.copy()
        
        # Detect document type for appropriate processing
        doc_type = self.detect_document_type(legal_data)
        
        # Add violation extraction metadata
        total_violations = 0
        total_sections = 0
        
        # Process based on document type
        if doc_type == 'ND_123_2021':
            total_violations, total_sections = self._process_amendment_document(enhanced)
        else:
            total_violations, total_sections = self._process_base_document(enhanced)
        
        # Add processing metadata
        enhanced['processing_metadata'] = {
            "document_type": doc_type,
            "total_articles": len(legal_data.get('key_articles', {})),
            "total_sections": total_sections,
            "total_violations_extracted": total_violations,
            "processing_date": datetime.now().isoformat(),
            "data_source": "manual_extraction",
            "pipeline_stage": "raw_enhancement"
        }
        
        return enhanced
    
    def _process_base_document(self, legal_data: Dict) -> tuple:
        """Process base document (ND 100/2019)"""
        total_violations = 0
        total_sections = 0
        
        for article_key, article in legal_data.get('key_articles', {}).items():
            sections = article.get('sections', [])
            total_sections += len(sections)
            
            for section in sections:
                violations = section.get('violations', [])
                total_violations += len(violations)
                
                # Add fine amount parsing
                fine_range = section.get('fine_range', '')
                section['fine_min'], section['fine_max'] = self.parse_fine_range(fine_range)
                
                # Add violation categorization
                section['violation_categories'] = self.categorize_violations(violations)
        
        return total_violations, total_sections
    
    def _process_amendment_document(self, legal_data: Dict) -> tuple:
        """Process amendment document (ND 123/2021)"""
        total_violations = 0
        total_sections = 0
        
        # Process key_articles if present
        for article_key, article in legal_data.get('key_articles', {}).items():
            sections = article.get('sections', [])
            total_sections += len(sections)
            
            for section in sections:
                violations = section.get('violations', [])
                total_violations += len(violations)
                
                # Process fine changes for amendments
                if 'fine_range' in section:
                    section['fine_min'], section['fine_max'] = self.parse_fine_range(section['fine_range'])
                
                if 'old_fine' in section and 'new_fine' in section:
                    section['old_fine_min'], section['old_fine_max'] = self.parse_fine_range(section['old_fine'])
                    section['new_fine_min'], section['new_fine_max'] = self.parse_fine_range(section['new_fine'])
                
                # Add violation categorization
                section['violation_categories'] = self.categorize_violations(violations)
        
        # Process violation_updates if present
        violation_updates = legal_data.get('violation_updates', [])
        for violation in violation_updates:
            total_violations += 1
            
            # Parse fine information
            if 'after_123' in violation and 'fine_range' in violation['after_123']:
                fine_range = violation['after_123']['fine_range']
                violation['after_123']['fine_min'], violation['after_123']['fine_max'] = self.parse_fine_range(fine_range)
            
            if 'before_123' in violation and 'fine_range' in violation['before_123']:
                fine_range = violation['before_123']['fine_range']
                violation['before_123']['fine_min'], violation['before_123']['fine_max'] = self.parse_fine_range(fine_range)
        
        return total_violations, total_sections
    
    def parse_fine_range(self, fine_range: str) -> tuple:
        """Parse fine range string to get min and max amounts"""
        if not fine_range:
            return 0, 0
            
        # Pattern for Vietnamese fine format: "4,000,000 - 6,000,000 VNĐ"
        pattern = r'(\d{1,3}(?:,\d{3})*)\s*-\s*(\d{1,3}(?:,\d{3})*)\s*VNĐ'
        match = re.search(pattern, fine_range)
        
        if match:
            min_amount = int(match.group(1).replace(',', ''))
            max_amount = int(match.group(2).replace(',', ''))
            return min_amount, max_amount
        
        # Handle single amount format
        single_pattern = r'(\d{1,3}(?:,\d{3})*)\s*VNĐ'
        single_match = re.search(single_pattern, fine_range)
        if single_match:
            amount = int(single_match.group(1).replace(',', ''))
            return amount, amount
        
        return 0, 0
    
    def categorize_violations(self, violations: List[str]) -> List[str]:
        """Categorize violations by type"""
        categories = []
        
        category_keywords = {
            'speed': ['tốc độ', 'vượt tốc độ', 'chạy quá'],
            'safety_equipment': ['mũ bảo hiểm', 'dây an toàn', 'trang bị'],
            'traffic_signals': ['đèn đỏ', 'đèn tín hiệu', 'tín hiệu giao thông'],
            'documentation': ['giấy phép', 'giấy đăng ký', 'bằng lái'],
            'alcohol_drugs': ['rượu bia', 'say rượu', 'nồng độ cồn', 'ma túy'],
            'parking': ['đỗ xe', 'dừng xe'],
            'direction': ['ngược chiều', 'đường cấm', 'sai làn'],
            'overtaking': ['vượt xe', 'vượt không đúng'],
            'vehicle_condition': ['tình trạng xe', 'đèn chiếu sáng', 'còi'],
            'loading': ['chở hàng', 'tải trọng', 'chở người'],
            'racing': ['đua xe']
        }
        
        for violation in violations:
            violation_lower = violation.lower()
            for category, keywords in category_keywords.items():
                if any(keyword in violation_lower for keyword in keywords):
                    if category not in categories:
                        categories.append(category)
        
        return categories
    
    def save_enhanced_data(self, enhanced_data: Dict, output_path: str):
        """Save enhanced legal data"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Enhanced legal data saved to: {output_path}")


def main():
    """Main processing function"""
    print("🚀 Starting Legal Document Enhancement...")
    
    extractor = LegalDocumentExtractor()
    
    # Process multiple legal documents
    documents_to_process = [
        {
            'input': '../raw/legal_documents/nghi_dinh_100_2019.json',
            'output': '../processed/enhanced_nghi_dinh_100_2019.json'
        },
        {
            'input': '../raw/legal_documents/nghi_dinh_123_2021.json', 
            'output': '../processed/enhanced_nghi_dinh_123_2021.json'
        }
    ]
    
    for doc_config in documents_to_process:
        input_path = doc_config['input']
        output_path = doc_config['output']
        
        if not os.path.exists(input_path):
            print(f"⚠️ File not found: {input_path}")
            continue
            
        print(f"\n📖 Processing: {os.path.basename(input_path)}")
        
        try:
            enhanced_data = extractor.process_existing_legal_data(input_path)
            extractor.save_enhanced_data(enhanced_data, output_path)
            
            # Print summary
            metadata = enhanced_data.get('processing_metadata', {})
            print("📊 Processing Summary:")
            print(f"   - Document Type: {metadata.get('document_type', 'Unknown')}")
            print(f"   - Total Articles: {metadata.get('total_articles', 0)}")
            print(f"   - Total Sections: {metadata.get('total_sections', 0)}")
            print(f"   - Total Violations: {metadata.get('total_violations_extracted', 0)}")
            print(f"   - Processing Date: {metadata.get('processing_date', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Error processing {input_path}: {e}")
    
    print("\n✅ Legal Document Enhancement Complete!")


if __name__ == "__main__":
    main()