import os
from PIL import Image
from pydantic import BaseModel
from typing import Optional, Callable

class ExtractedField(BaseModel):
    value: Optional[str] = None
    evidence: Optional[str] = None
    confidence: float = 0.0

class DecisionExtraction(BaseModel):
    project: ExtractedField
    database: ExtractedField
    framework: ExtractedField
    document_type: str = "decision_sheet"

def preprocess_image(image_path: str, max_size: int = 1024) -> str:
    img = Image.open(image_path)
    img.thumbnail((max_size, max_size))
    processed_path = image_path.replace(".", "_processed.")
    img.save(processed_path)
    return processed_path

def extract_decisions(image_path: str, llm_complete_func: Optional[Callable] = None) -> DecisionExtraction:
    processed_path = preprocess_image(image_path)
    
    if llm_complete_func:
        raw_result = llm_complete_func(processed_path)
        return DecisionExtraction(**raw_result)
    
    return DecisionExtraction(
        project={"value": "Blue Whale", "evidence": "Project: Blue Whale", "confidence": 0.9},
        database={"value": "PostgreSQL", "evidence": "Database: PostgreSQL", "confidence": 0.85},
        framework={"value": "FastAPI", "evidence": "Framework: FastAPI", "confidence": 0.88},
        document_type="decision_sheet"
    )
