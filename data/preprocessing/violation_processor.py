"""
Vietnamese Traffic Violations Data Processor
Normalize and validate violation data from CSV and legal documents
Supports ND 100/2019 and ND 123/2021 processing
"""

import json
import pandas as pd
from typing import Dict, List, Tuple
import re
from datetime import datetime
import os


class ViolationProcessor:
    """Process and normalize Vietnamese traffic violation data"""
    
    def __init__(self):
        self.processed_violations = []
        self.legal_documents = {}
        
    def load_legal_documents(self) -> Dict[str, Dict]:
        """Load all available legal documents"""
        legal_docs = {}
        
        # Base documents
        base_docs = [
            '../raw/legal_documents/nghi_dinh_100_2019.json',
            '../raw/legal_documents/nghi_dinh_123_2021.json',
            '../raw/legal_documents/nghi_dinh_168_2024.json'
        ]
        
        for doc_path in base_docs:
            if os.path.exists(doc_path):
                doc_name = os.path.basename(doc_path).replace('.json', '')
                with open(doc_path, 'r', encoding='utf-8') as f:
                    legal_docs[doc_name] = json.load(f)
                print(f"✅ Loaded: {doc_name}")
            else:
                print(f"⚠️ Not found: {doc_path}")
        
        self.legal_documents = legal_docs
        return legal_docs
        
    def load_real_data(self) -> Tuple[Dict, pd.DataFrame, List[Dict]]:
        """Load actual data files from the project"""
        # Load all legal documents
        legal_docs = self.load_legal_documents()
        
        # Primary legal document (base)
        primary_doc = legal_docs.get('nghi_dinh_100_2019', {})
        
        # Load violations CSV with exact column names from real file
        violations_csv_path = '../raw/violations_dataset/traffic_violations_extended.csv'
        violations_df = pd.read_csv(violations_csv_path)
        
        # Load sample JSON for validation
        sample_json_path = '../raw/violations_dataset/traffic_violations_sample.json'
        with open(sample_json_path, 'r', encoding='utf-8') as f:
            sample_violations = json.load(f)
        
        return primary_doc, violations_df, sample_violations
    
    def validate_data_consistency(self, legal_doc: Dict, violations_df: pd.DataFrame) -> Dict:
        """Validate consistency between legal document and violations data"""
        validation_report = {
            "legal_references_valid": [],
            "legal_references_invalid": [],
            "fine_ranges_consistent": [],
            "fine_ranges_inconsistent": [],
            "summary": {}
        }
        
        total_violations = len(violations_df)
        
        for _, row in violations_df.iterrows():
            legal_basis = row['legal_basis']
            violation_id = row['violation_id']
            
            # Check if legal reference exists in legal document
            if self.validate_legal_reference(legal_basis, legal_doc):
                validation_report["legal_references_valid"].append(violation_id)
                
                # Check fine consistency
                if self.validate_fine_consistency(row, legal_doc, legal_basis):
                    validation_report["fine_ranges_consistent"].append(violation_id)
                else:
                    validation_report["fine_ranges_inconsistent"].append(violation_id)
            else:
                validation_report["legal_references_invalid"].append(violation_id)
        
        # Create summary
        validation_report["summary"] = {
            "total_violations": total_violations,
            "valid_legal_references": len(validation_report["legal_references_valid"]),
            "invalid_legal_references": len(validation_report["legal_references_invalid"]),
            "consistent_fines": len(validation_report["fine_ranges_consistent"]),
            "inconsistent_fines": len(validation_report["fine_ranges_inconsistent"]),
            "legal_reference_accuracy": len(validation_report["legal_references_valid"]) / total_violations * 100,
            "fine_consistency_rate": len(validation_report["fine_ranges_consistent"]) / max(1, len(validation_report["legal_references_valid"])) * 100
        }
        
        return validation_report
    
    def validate_legal_reference(self, legal_basis: str, legal_doc: Dict) -> bool:
        """Check if legal reference exists in legal document or amendment documents"""
        # First check in primary document
        if self._check_reference_in_document(legal_basis, legal_doc):
            return True
        
        # Check in amendment documents
        for doc_name, doc_data in self.legal_documents.items():
            if 'amendment' in doc_name or '123_2021' in doc_name:
                if self._check_amendment_reference(legal_basis, doc_data):
                    return True
        
        return False
    
    def _check_reference_in_document(self, legal_basis: str, legal_doc: Dict) -> bool:
        """Check reference in a specific document"""
        try:
            # Parse legal basis like "Điều 6 Khoản 1"
            parts = legal_basis.split()
            if len(parts) >= 4:
                article_num = parts[1]
                section_num = parts[3]
                
                article_key = f"dieu_{article_num}"
                
                if article_key in legal_doc.get('key_articles', {}):
                    article = legal_doc['key_articles'][article_key]
                    
                    for section in article.get('sections', []):
                        if f"Khoản {section_num}" in section.get('section', ''):
                            return True
            
            return False
        except Exception:
            return False
    
    def _check_amendment_reference(self, legal_basis: str, amendment_doc: Dict) -> bool:
        """Check reference in amendment document"""
        try:
            # Check in violation_updates
            violation_updates = amendment_doc.get('violation_updates', [])
            for violation in violation_updates:
                violation_code = violation.get('violation_code', '')
                if violation_code in legal_basis:
                    return True
            
            # Check in amendments_summary
            amendments = amendment_doc.get('amendments_summary', {}).get('effective_changes', [])
            for amendment in amendments:
                original_article = amendment.get('original_article', '')
                if any(part in original_article for part in legal_basis.split()):
                    return True
            
            return False
        except Exception:
            return False
    
    def validate_fine_consistency(self, violation_row: pd.Series, legal_doc: Dict, legal_basis: str) -> bool:
        """Check if fine amounts match between violation and legal document"""
        try:
            parts = legal_basis.split()
            if len(parts) >= 4:
                article_num = parts[1]
                section_num = parts[3]
                
                article_key = f"dieu_{article_num}"
                
                if article_key in legal_doc.get('key_articles', {}):
                    article = legal_doc['key_articles'][article_key]
                    
                    for section in article.get('sections', []):
                        if f"Khoản {section_num}" in section.get('section', ''):
                            legal_fine_range = section.get('fine_range', '')
                            
                            # Extract amounts from legal document
                            legal_min, legal_max = self.parse_fine_range(legal_fine_range)
                            
                            # Compare with violation data
                            violation_min = int(violation_row['fine_min'])
                            violation_max = int(violation_row['fine_max'])
                            
                            return legal_min == violation_min and legal_max == violation_max
            
            return False
        except Exception:
            return False
    
    def parse_fine_range(self, fine_range: str) -> Tuple[int, int]:
        """Parse fine range from legal document"""
        if not fine_range:
            return 0, 0
            
        pattern = r'(\d{1,3}(?:,\d{3})*)\s*-\s*(\d{1,3}(?:,\d{3})*)\s*VNĐ'
        match = re.search(pattern, fine_range)
        
        if match:
            min_amount = int(match.group(1).replace(',', ''))
            max_amount = int(match.group(2).replace(',', ''))
            return min_amount, max_amount
        
        return 0, 0
    
    def normalize_violations_from_real_data(self, legal_doc: Dict, violations_df: pd.DataFrame) -> List[Dict]:
        """Process real violation data with exact column structure"""
        processed_violations = []
        
        for _, row in violations_df.iterrows():
            # Handle missing values properly
            additional_measures_str = row['additional_measures'] if pd.notna(row['additional_measures']) else ''
            
            # Handle NaN values for fine amounts
            fine_min = int(row['fine_min']) if pd.notna(row['fine_min']) else 0
            fine_max = int(row['fine_max']) if pd.notna(row['fine_max']) else 0
            currency = row['currency'] if pd.notna(row['currency']) else 'VNĐ'
            
            violation = {
                "id": row['violation_id'],
                "description": self.clean_vietnamese_text(row['violation_description']),
                "category": row['category'],
                "penalty": {
                    "fine_min": fine_min,
                    "fine_max": fine_max,
                    "currency": currency,
                    "fine_text": f"{fine_min:,} - {fine_max:,} {currency}" if fine_min > 0 else "Chưa xác định"
                },
                "additional_measures": self.parse_additional_measures(additional_measures_str),
                "legal_basis": {
                    "article": row['legal_basis'],
                    "document": row['document_source'],
                    "full_reference": self.get_full_legal_reference(row['legal_basis'], legal_doc)
                },
                "severity": row['severity'],
                "keywords": self.extract_vietnamese_keywords(row['violation_description']),
                "search_text": self.create_comprehensive_search_text(row),
                "metadata": {
                    "source": "traffic_violations_extended.csv",
                    "processed_date": datetime.now().isoformat(),
                    "pipeline_stage": "normalization"
                }
            }
            
            processed_violations.append(violation)
        
        return processed_violations
    
    def clean_vietnamese_text(self, text: str) -> str:
        """Clean Vietnamese text with proper handling"""
        if pd.isna(text):
            return ""
        
        # Remove extra spaces
        cleaned = re.sub(r'\s+', ' ', str(text).strip())
        
        # Common Vietnamese traffic law normalizations
        normalizations = {
            'ô tô': 'ô tô',
            'xe máy': 'xe mô tô', 
            'xe gắn máy': 'xe mô tô',
            'mũ bảo hiểm': 'mũ bảo hiểm',
            'GPLX': 'giấy phép lái xe'
        }
        
        for old, new in normalizations.items():
            cleaned = cleaned.replace(old, new)
        
        return cleaned
    
    def extract_vietnamese_keywords(self, description: str) -> List[str]:
        """Extract keywords specific to Vietnamese traffic violations"""
        if pd.isna(description):
            return []
        
        keywords = []
        description_lower = str(description).lower()
        
        # Vietnamese traffic violation keyword mapping
        keyword_mapping = {
            'helmet': ['mũ bảo hiểm', 'không đội mũ', 'helmet'],
            'speed': ['tốc độ', 'vượt tốc độ', 'chạy quá tốc độ', 'speed'],
            'traffic_light': ['đèn đỏ', 'đèn tín hiệu', 'vượt đèn', 'traffic light'],
            'license': ['giấy phép', 'bằng lái', 'GPLX', 'license'],
            'alcohol': ['rượu bia', 'say rượu', 'nồng độ cồn', 'alcohol'],
            'parking': ['đỗ xe', 'dừng xe', 'parking'],
            'racing': ['đua xe', 'racing'],
            'loading': ['chở hàng', 'vượt tải', 'loading'],
            'passenger': ['chở người', 'hành khách', 'passenger'],
            'phone': ['điện thoại', 'phone', 'di động'],
            'direction': ['ngược chiều', 'sai làn', 'direction'],
            'overtaking': ['vượt xe', 'overtaking']
        }
        
        for category, patterns in keyword_mapping.items():
            for pattern in patterns:
                if pattern in description_lower:
                    keywords.append(category)
                    break
        
        return list(set(keywords))
    
    def create_comprehensive_search_text(self, row: pd.Series) -> str:
        """Create search text optimized for Vietnamese semantic search"""
        search_components = [
            str(row['violation_description']),
            str(row['category']),
            str(row['legal_basis']),
            str(row['severity'])
        ]
        
        # Add additional measures if present
        if pd.notna(row['additional_measures']) and row['additional_measures']:
            search_components.append(str(row['additional_measures']))
        
        # Filter out nan/None values
        valid_components = [comp for comp in search_components if comp and comp != 'nan']
        
        return ' '.join(valid_components)
    
    def get_full_legal_reference(self, legal_basis: str, legal_doc: Dict) -> str:
        """Get detailed legal reference from legal document"""
        try:
            parts = legal_basis.split()
            if len(parts) >= 4:
                article_num = parts[1]
                section_num = parts[3]
                
                article_key = f"dieu_{article_num}"
                
                if article_key in legal_doc.get('key_articles', {}):
                    article = legal_doc['key_articles'][article_key]
                    
                    for section in article.get('sections', []):
                        if f"Khoản {section_num}" in section.get('section', ''):
                            violations = section.get('violations', [])
                            if violations:
                                return f"{legal_basis}: {'; '.join(violations)}"
            
            return legal_basis
            
        except Exception:
            return legal_basis
    
    def parse_additional_measures(self, measures_str: str) -> List[str]:
        """Parse additional penalty measures with Vietnamese text handling"""
        if pd.isna(measures_str) or not measures_str or measures_str == '':
            return []
        
        # Split by common Vietnamese separators
        measures = re.split(r'[;,]|và|hoặc', str(measures_str))
        return [measure.strip() for measure in measures if measure.strip()]
    
    def save_processed_data_real_format(self, violations: List[Dict], validation_report: Dict):
        """Save processed data in format matching project structure"""
        # Create output directory
        output_dir = '../processed'
        os.makedirs(output_dir, exist_ok=True)
        
        # Create metadata consistent with existing structure
        output_data = {
            "metadata": {
                "total_violations": len(violations),
                "processed_date": datetime.now().isoformat(),
                "source_documents": ["ND 100/2019/NĐ-CP", "ND 123/2021/NĐ-CP", "ND 168/2024/NĐ-CP"],
                "data_sources": [
                    "data/raw/legal_documents/nghi_dinh_100_2019.json",
                    "data/raw/violations_dataset/traffic_violations_extended.csv"
                ],
                "processing_pipeline": "pdf->raw->processed->embeddings",
                "validation_summary": validation_report.get("summary", {})
            },
            "violations": violations
        }
        
        # Save main processed file
        with open(f'{output_dir}/violations.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        # Save validation report
        with open(f'{output_dir}/validation_report.json', 'w', encoding='utf-8') as f:
            json.dump(validation_report, f, ensure_ascii=False, indent=2)
        
        # Save summary statistics
        self.save_processing_statistics(violations, output_dir)
        
        print(f"✅ Processed data saved to: {output_dir}/violations.json")
        print(f"📊 Validation report saved to: {output_dir}/validation_report.json")
    
    def save_processing_statistics(self, violations: List[Dict], output_dir: str):
        """Save processing statistics for validation"""
        stats = {
            "total_violations": len(violations),
            "categories": {},
            "severity_distribution": {},
            "legal_basis_distribution": {},
            "fine_ranges": {
                "min_fine": min(v['penalty']['fine_min'] for v in violations),
                "max_fine": max(v['penalty']['fine_max'] for v in violations),
                "avg_fine_min": sum(v['penalty']['fine_min'] for v in violations) / len(violations),
                "avg_fine_max": sum(v['penalty']['fine_max'] for v in violations) / len(violations)
            },
            "processing_date": datetime.now().isoformat()
        }
        
        # Count categories
        for violation in violations:
            category = violation['category']
            severity = violation['severity']
            legal_basis = violation['legal_basis']['article']
            
            stats['categories'][category] = stats['categories'].get(category, 0) + 1
            stats['severity_distribution'][severity] = stats['severity_distribution'].get(severity, 0) + 1
            stats['legal_basis_distribution'][legal_basis] = stats['legal_basis_distribution'].get(legal_basis, 0) + 1
        
        with open(f'{output_dir}/processing_statistics.json', 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"📈 Processing statistics saved to: {output_dir}/processing_statistics.json")
    
    def merge_amendment_data(self, base_violations: List[Dict]) -> List[Dict]:
        """Merge amendment data from ND 123/2021 into base violations"""
        merged_violations = base_violations.copy()
        
        # Get amendment document
        amendment_doc = self.legal_documents.get('nghi_dinh_123_2021', {})
        if not amendment_doc:
            print("⚠️ No amendment document found")
            return merged_violations
        
        print("🔄 Merging amendment data...")
        
        # Process violation updates from amendment
        violation_updates = amendment_doc.get('violation_updates', [])
        
        for update in violation_updates:
            violation_code = update.get('violation_code', '')
            
            # Find matching violation in base data
            for violation in merged_violations:
                if violation.get('violation_code') == violation_code:
                    # Update with amendment data
                    self._apply_amendment_update(violation, update)
                    break
            else:
                # Add new violation if not found
                new_violation = self._create_violation_from_amendment(update)
                if new_violation:
                    merged_violations.append(new_violation)
        
        print(f"✅ Merged {len(violation_updates)} amendment updates")
        return merged_violations
    
    def _apply_amendment_update(self, base_violation: Dict, amendment: Dict) -> None:
        """Apply amendment update to base violation"""
        # Update fine information
        if 'after_123' in amendment:
            after_data = amendment['after_123']
            if 'fine_range' in after_data:
                fine_min, fine_max = self.parse_fine_range(after_data['fine_range'])
                base_violation['fine_min'] = fine_min
                base_violation['fine_max'] = fine_max
                base_violation['penalty_range'] = after_data['fine_range']
        
        # Add amendment metadata
        base_violation['amended_by'] = 'ND 123/2021'
        base_violation['amendment_type'] = amendment.get('amendment_type', 'fine_update')
        base_violation['legal_basis_updated'] = amendment.get('legal_basis', '')
    
    def determine_severity_from_fine(self, fine_min: int, fine_max: int) -> str:
        """Determine severity level from fine amounts"""
        max_fine = max(fine_min, fine_max)
        
        if max_fine >= 10000000:  # >= 10 million VND
            return "Very High"
        elif max_fine >= 5000000:  # >= 5 million VND
            return "High"
        elif max_fine >= 1000000:  # >= 1 million VND
            return "Medium"
        elif max_fine >= 100000:   # >= 100k VND
            return "Low"
        else:
            return "Very Low"
    
    def _create_violation_from_amendment(self, amendment: Dict) -> Dict:
        """Create new violation from amendment data"""
        violation_id = f"ND123_{amendment.get('violation_code', 'unknown')}"
        
        fine_range = ""
        fine_min, fine_max = 0, 0
        
        if 'after_123' in amendment:
            fine_range = amendment['after_123'].get('fine_range', '')
            fine_min, fine_max = self.parse_fine_range(fine_range)
        
        return {
            'id': violation_id,
            'description': amendment.get('description', ''),
            'category': 'Amendment Update',
            'penalty': {
                'fine_min': fine_min,
                'fine_max': fine_max,
                'currency': 'VNĐ',
                'fine_text': fine_range
            },
            'additional_measures': amendment.get('after_123', {}).get('additional_measures', []),
            'legal_basis': {
                'article': amendment.get('legal_basis', ''),
                'document': 'ND 123/2021',
                'full_reference': f"ND 123/2021 - {amendment.get('legal_basis', '')}"
            },
            'vehicle_type': amendment.get('vehicle_type', ''),
            'severity': self.determine_severity_from_fine(fine_min, fine_max),
            'keywords': amendment.get('description', '').lower().split(),
            'source_document': 'ND 123/2021',
            'amendment_type': amendment.get('amendment_type', 'new_violation')
        }


def main():
    """Main processing function"""
    print("🚀 Starting Violation Data Processing...")
    
    processor = ViolationProcessor()
    
    # Load real data (includes all legal documents)
    legal_doc, violations_df, sample_violations = processor.load_real_data()
    print(f"📊 Loaded {len(violations_df)} violations from CSV")
    print(f"📚 Loaded {len(processor.legal_documents)} legal documents")
    
    # Validate data consistency first
    print("🔍 Validating data consistency...")
    validation_report = processor.validate_data_consistency(legal_doc, violations_df)
    
    # Print validation summary
    summary = validation_report.get("summary", {})
    print("📋 Validation Results:")
    print(f"   - Total violations: {summary.get('total_violations', 0)}")
    print(f"   - Valid legal references: {summary.get('valid_legal_references', 0)} ({summary.get('legal_reference_accuracy', 0):.1f}%)")
    print(f"   - Consistent fines: {summary.get('consistent_fines', 0)} ({summary.get('fine_consistency_rate', 0):.1f}%)")
    
    # Process violations
    print("⚙️ Processing violations...")
    processed_violations = processor.normalize_violations_from_real_data(legal_doc, violations_df)
    
    # Merge amendment data
    print("🔄 Merging amendment data...")
    final_violations = processor.merge_amendment_data(processed_violations)
    
    # Save processed data with amendments
    processor.save_processed_data_real_format(final_violations, validation_report)
    
    print(f"✅ Successfully processed {len(final_violations)} violations (including amendments)")
    
    # Save amendment-specific data
    amendment_violations = [v for v in final_violations if v.get('source_document') == 'ND 123/2021']
    if amendment_violations:
        amendment_output_path = '../processed/violations_nd_123_2021.json'
        with open(amendment_output_path, 'w', encoding='utf-8') as f:
            json.dump(amendment_violations, f, ensure_ascii=False, indent=2)
        print(f"📝 Amendment violations saved to: {amendment_output_path}")
        print(f"   - Amendment violations: {len(amendment_violations)}")
    
    # Print final summary by document
    doc_summary = {}
    for violation in final_violations:
        source = violation.get('source_document', 'ND 100/2019')
        doc_summary[source] = doc_summary.get(source, 0) + 1
    
    print("\n📊 Final Summary by Document:")
    for doc, count in doc_summary.items():
        print(f"   - {doc}: {count} violations")


if __name__ == "__main__":
    main()