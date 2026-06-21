import summarise

def test_unknown_topic_snaps_to_other(monkeypatch):
    # simulate the LLM returning a topic outside our allowed set
    fake = type("R", (), {"text": '{"summary":"s","why_it_matters":"w","topic":"Crypto"}'})()
    monkeypatch.setattr(summarise.client.models, "generate_content", lambda **k: fake)
    result = summarise.summarise_story("Some title")
    assert result["topic"] == "Other"   # snapped, because "Crypto" isn't allowed

def test_valid_response_parses(monkeypatch):
    fake = type("R", (), {"text": '{"summary":"s","why_it_matters":"w","topic":"AI"}'})()
    monkeypatch.setattr(summarise.client.models, "generate_content", lambda **k: fake)
    result = summarise.summarise_story("Some title")
    assert result["topic"] == "AI"
    assert result["summary"] == "s"

def test_malformed_response_falls_back(monkeypatch):
    # LLM returns broken JSON -> should not crash, should fall back gracefully
    fake = type("R", (), {"text": "this is not json"})()
    monkeypatch.setattr(summarise.client.models, "generate_content", lambda **k: fake)
    result = summarise.summarise_story("My title")
    assert result["topic"] == "Other"
    assert result["summary"] == "My title"   # fallback uses the title