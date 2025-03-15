from fastapi import FastAPI, UploadFile
from transformers import pipeline
import numpy as np

app = FastAPI()

# Load multiple NSFW detection models
nsfw_models = {
    "unfilteredai": pipeline("image-classification", model="UnfilteredAI/NSFW-gen-v2"),
    "aifeifei": pipeline("image-classification", model="aifeifei798/DPO_Pairs-Roleplay-NSFW"),
    "medical": pipeline("image-classification", model="AdaptLLM/medicine-LLM")
}

@app.post("/validate")
async def validate_content(file: UploadFile):
    content = await file.read()
    img = np.frombuffer(content, dtype=np.uint8)
    
    results = {}
    for model_name, classifier in nsfw_models.items():
        results[model_name] = classifier(img)
        
    return {
        "nsfw_score": max(r['score'] for r in results.values()),
        "medical_valid": results['medical'][0]['label'] == 'medical',
        "detailed_scores": results
    }
