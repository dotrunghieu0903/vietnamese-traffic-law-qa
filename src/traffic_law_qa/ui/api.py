# api.py
import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from system.model import Model
from scripts.category_detector import VehicleCategoryDetector
from system.utils import extract_entities_with_llm


# --------- KHỞI TẠO FastAPI App ----------
app = FastAPI(
    title="Vietnamese Traffic Law Search API",
    description="Hybrid (vector + BM25) search trên Neo4j cho luật giao thông",
    version="1.0.0",
)

# Cho phép gọi từ web tĩnh (Vercel/localhost/…)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------- LOAD DETECTOR & MODEL ----------
detector = VehicleCategoryDetector()
vehicle_patterns = [k for k in detector.vehicle_patterns]
business_patterns = [k for k in detector.business_patterns]
fallback_patterns = [k for k in detector.fallback_categories]


# ---------  Neo4j database connection ----------
NEO4J_URI  = os.getenv("NEO4J_URI", "neo4j+s://7aa78485.databases.neo4j.io")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASS", "iX59KTgWRNyZvmkh3dDBGe0Dwbm-_XQGdP1KCW_m7rs")

model = Model(uri=NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))


# API /search receive JSON include: question, top_k, verbose
class SearchRequest(BaseModel):
    question: str
    top_k: int = 10
    verbose: bool = False


@app.post("/search")
def search(req: SearchRequest):
    """
    Nhận câu hỏi tiếng Việt tự nhiên, trả về danh sách điều luật phù hợp.
    """
    # Dùng LLM để bóc tách intent & category (chỉ để trả về cho frontend)
    extraction = extract_entities_with_llm(
        req.question,
        vehicle_patterns,
        business_patterns,
        fallback_patterns,
    )
    target_category = extraction.get("category")
    query_intent = extraction.get("intent")

    # Gọi hybrid_search để lấy kết quả
    raw_results = model.hybrid_search(
        req.question,
        vehicle_patterns,
        business_patterns,
        fallback_patterns,
        top_k=req.top_k,
        verbose=req.verbose,
    )
    # print('raw_results: ', raw_results)
    # hybrid_search trả về list các phần tử:
    # { "data": item, "score": tổng RRF }
    # trong đó item có: id, text, category, fine_min, fine_max, law_article, law_clause, extra, vector_score/bm25_score
    results = []
    for r in raw_results:
        data = r["data"]
        score = float(r["score"])
        fine_min = data.get("fine_min")
        fine_max = data.get("fine_max")

        if fine_min is not None and fine_max is not None:
            fine_text = f"{fine_min:,} - {fine_max:,} VNĐ".replace(",", ".")
        elif fine_min is not None:
            fine_text = f"Tối thiểu {fine_min:,} VNĐ".replace(",", ".")
        else:
            fine_text = ""

        # print('results: ', results)
        results.append(
            {
                "id": data.get("id"),
                "description": data.get("text"),
                "vehicle_category": data.get("category"),
                "fine_min": fine_min,
                "fine_max": fine_max,
                "fine_text": fine_text,
                "law_article": data.get("law_article"),
                "law_clause": data.get("law_clause"),
                "extra_penalties": data.get("extra") or [],
                "score": score,
            }
        )

    return {
        "query": req.question,
        "detected_category": target_category,
        "detected_intent": query_intent,
        "results": results,
    }


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
