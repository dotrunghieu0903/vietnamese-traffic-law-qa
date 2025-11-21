from google import genai
from system.constant import SYSTEM_PROMPT
import json

def extract_entities_with_llm(query, vehicle_patterns, business_patterns, fallback_patterns):
    
    client = genai.Client(api_key="AIzaSyDv3cuC2X3_e2_2Yyejvk5cscNA_6XVnfI")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config= genai.types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT.format(vehicle_patterns, business_patterns, fallback_patterns),
            response_mime_type="application/json",
        ),
        contents=query
    )
    extraction = json.loads(response.text)

    return {"category": extraction['category'], "intent": extraction['intent']}

def print_results(results):
    for i,result in enumerate(results):
        print(f"Top {i+1}: {result['score']:.4f}")
        print("Description: ", result['data']['text'])
        print("Category: ", result['data']['category'])
        print(f"Fine: {result['data']['fine_min']} - {result['data']['fine_max']} VNĐ")
        print(f"Law: {result['data']['law_article']}, {result['data']['law_clause']}")
        print(f"Extra: {result['data']['extra']}")
        print("--------------------------------")
