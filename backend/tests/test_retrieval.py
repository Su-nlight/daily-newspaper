from app.services import retrieval


def test_retrieve_with_story_id_anchors_on_that_story():
    docs = retrieval.retrieve_for_query(query="tell me more", story_id="story-ransomware-shift")
    assert docs
    assert docs[0].id == "story-ransomware-shift"


def test_retrieve_with_unknown_story_id_returns_empty():
    docs = retrieval.retrieve_for_query(query="tell me more", story_id="does-not-exist")
    assert docs == []


def test_retrieve_by_query_matches_keywords():
    docs = retrieval.retrieve_for_query(query="semiconductor chip packaging Japan India")
    assert docs
    assert docs[0].id == "story-semiconductor-alliance"


def test_retrieve_no_match_returns_empty():
    docs = retrieval.retrieve_for_query(query="zzqqxxnonsense")
    assert docs == []


def test_retrieve_respects_category_scope():
    docs = retrieval.retrieve_for_query(query="security", category="cybersecurity")
    assert docs
    assert all(doc.category == "cybersecurity" for doc in docs)
