import os
from src.multimodal import preprocess_image, extract_decisions, DecisionExtraction

def test_preprocess_image():
    img_path = "tests/images/clean.jpg"
    assert os.path.exists(img_path)
    processed = preprocess_image(img_path, max_size=500)
    assert os.path.exists(processed)
    os.remove(processed)

def test_extract_decisions_mock():
    res = extract_decisions("tests/images/clean.jpg")
    assert isinstance(res, DecisionExtraction)
    assert res.project.value == "Blue Whale"
    assert res.database.confidence >= 0.6
