import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from system.model import Model
from scripts.category_detector import VehicleCategoryDetector
from system.utils import print_results
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Vietnamese Traffic Law QA - CLI Interface')
    parser.add_argument('--query', '-q', type=str, required=True, help='The query to search for')
    parser.add_argument('--top-k', '-k', type=int, default=10, help='Number of results to return (default: 10)')
    parser.add_argument('--document-name', '-d', type=str, help='The name of the document to search for', choices=['ND100', 'ND168'])
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    query = args.query
    detector = VehicleCategoryDetector()
    vehicle_patterns = [keywords for keywords in detector.vehicle_patterns] 
    business_patterns = [keywords for keywords in detector.business_patterns]
    fallback_patterns = [keywords for keywords in detector.fallback_categories]

    model = Model(uri="neo4j+s://7aa78485.databases.neo4j.io", auth=("neo4j", "iX59KTgWRNyZvmkh3dDBGe0Dwbm-_XQGdP1KCW_m7rs"))

    print(f"\n{'='*60}")
    print(f"SEARCHING: {query}")
    print(f"{'='*60}\n")
    
    results = model.hybrid_search(
        query, 
        vehicle_patterns, 
        business_patterns, 
        fallback_patterns, 
        top_k=args.top_k, 
        verbose=args.verbose,
        decree_filter=args.document_name
    )
    print_results(results)