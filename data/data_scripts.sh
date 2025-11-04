python scripts/sample_data.py
powershell "Get-Content 'data/raw/violations_dataset/traffic_violations_extended.csv' | Measure-Object -Line"
# 1. Chạy complete pipeline
python run_complete_pipeline.py

# 2. Generate embeddings cho tất cả documents
python embedding_generator.py

# 3. Test semantic search với amendment queries
# 4. Validate fine consistency across documents