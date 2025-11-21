from neo4j import GraphDatabase
from system.utils import extract_entities_with_llm
from sentence_transformers import SentenceTransformer

class Model:
    def __init__(self, uri, auth, embedding_model="minhquan6203/paraphrase-vietnamese-law"):
        self.model = SentenceTransformer(embedding_model)
        self.uri = uri
        self.auth = auth
        self.embedding_model = embedding_model

    def hybrid_search(self, query, vehicle_patterns, business_patterns, fallback_patterns, top_k=10, verbose=False):
        driver = GraphDatabase.driver(self.uri, auth=self.auth)
        extraction = extract_entities_with_llm(query, vehicle_patterns, business_patterns, fallback_patterns)
        target_category = extraction['category']
        query_intent = extraction['intent']

        if query_intent == None:
            print("Không biết.")
            return []

        vector = self.model.encode(f"query: {query_intent}").tolist()
        
        print(f"🔍 Filter: {target_category} | Search: {query} | Intent: {query_intent}")
        # 1. Vector Search (Semantic)
        vector = self.model.encode(f"query: {query_intent}").tolist()
        vector_query = """
        CALL db.index.vector.queryNodes('violation_index', 50, $embedding)
        YIELD node, score
        MATCH (node)-[:HAS_FINE]->(fine:Fine)
        MATCH (node)-[:APPLIES_TO]->(veh:VehicleType)
        MATCH (node)-[:DEFINED_IN]->(clause:Clause)-[:BELONGS_TO]->(article:Article)
        OPTIONAL MATCH (node)-[:HAS_ADDITIONAL_PENALTY]->(sup:SupplementaryPenalty)
        RETURN node.id as id, 
               node.description as text, 
               veh.name as category, 
               fine.min as fine_min, 
               fine.max as fine_max, 
               article.name as law_article, 
               clause.name as law_clause, 
               collect(sup.text) as extra, 
               score as vector_score
        """
        
        # 2. Keyword Search (BM25 - Lexical)
        keyword_query = """
        CALL db.index.fulltext.queryNodes("violation_text_index", $text) 
        YIELD node, score
        MATCH (node)-[:HAS_FINE]->(fine:Fine)
        MATCH (node)-[:APPLIES_TO]->(veh:VehicleType)
        MATCH (node)-[:DEFINED_IN]->(clause:Clause)-[:BELONGS_TO]->(article:Article)
        OPTIONAL MATCH (node)-[:HAS_ADDITIONAL_PENALTY]->(sup:SupplementaryPenalty)
        RETURN node.id as id, 
               node.description as text, 
               veh.name as category, 
               fine.min as fine_min, 
               fine.max as fine_max, 
               article.name as law_article, 
               clause.name as law_clause, 
               collect(sup.text) as extra, 
               score as bm25_score
        LIMIT 50
        """
        
        with driver.session() as session:
            vec_results = session.run(vector_query, embedding=vector).data()
            kw_results = session.run(keyword_query, text=query_intent).data()
            
        # 3. RRF Fusion (Merge results)
        final_scores = {}
        k = 60 # Constant used
        
        if verbose:
            print("--------------------------------")
        # Add score from Vector List
        for rank, item in enumerate(vec_results):
            doc_id = item['id']
            if doc_id not in final_scores: final_scores[doc_id] = {"data": item, "score": 0}
            final_scores[doc_id]["score"] += 1 / (k + rank + 1)
            if verbose:
                print(f"Rank {rank+1}: id={item['id']} - Text: {item['text']} - Vector Score: {final_scores[doc_id]['score']:.4f}")
        
        if verbose:
            print("--------------------------------")
        # Add score from Keyword List
        for rank, item in enumerate(kw_results):
            doc_id = item['id']
            if doc_id not in final_scores: final_scores[doc_id] = {"data": item, "score": 0}
            # If item appears in both lists, the score will be very high
            final_scores[doc_id]["score"] += 1 / (k + rank + 1)
            if verbose:
                print(f"Rank {rank+1}: id={item['id']} - Text: {item['text']} - BM25 Score: {final_scores[doc_id]['score']:.4f}")
        
        if verbose:
            print("--------------------------------")
        # 4. Sort and get Top results
        sorted_results = sorted(final_scores.values(), key=lambda x: x['score'], reverse=True)
        return sorted_results[:top_k]