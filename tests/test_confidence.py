from src.confidence import decide

def test_decide_accepted():
    extraction = {
        "document_type": "decision_sheet",
        "project": {"value": "Blue Whale", "evidence": "Project: Blue Whale", "confidence": 0.9},
        "database": {"value": "PostgreSQL", "evidence": "Database: PostgreSQL", "confidence": 0.8},
        "framework": {"value": "FastAPI", "evidence": "Framework: FastAPI", "confidence": 0.85}
    }
    res = decide(extraction)
    assert res["route"] == "accepted"

def test_decide_confirm():
    extraction = {
        "document_type": "decision_sheet",
        "project": {"value": "Blue Whale", "evidence": "Project: Blue Whale", "confidence": 0.5},
        "database": {"value": "MongoDB", "evidence": "Database: MongoDB", "confidence": 0.8},
        "framework": {"value": "FastAPI", "evidence": "Framework: FastAPI", "confidence": 0.85}
    }
    res = decide(extraction)
    assert res["route"] == "confirm"

def test_decide_review():
    extraction = {
        "document_type": "decision_sheet",
        "project": {"value": "Blue Whale", "evidence": None, "confidence": 0.9},
        "database": {"value": "PostgreSQL", "evidence": "Database: PostgreSQL", "confidence": 0.8},
        "framework": {"value": "FastAPI", "evidence": "Framework: FastAPI", "confidence": 0.85}
    }
    res = decide(extraction)
    assert res["route"] == "review"

def test_decide_rejected():
    extraction = {
        "document_type": "unrelated",
        "project": {"value": None, "evidence": None, "confidence": 0.1}
    }
    res = decide(extraction)
    assert res["route"] == "rejected"
