# dorim-redev-system/backend/tests/test_rag.py
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag_engine import RagEngine

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "docs", "legal")

@pytest.fixture(scope="module")
def rag(tmp_path_factory):
    db_dir = str(tmp_path_factory.mktemp("chroma"))
    engine = RagEngine(
        docs_dir=DOCS_DIR,
        db_dir=db_dir,
    )
    engine.embed_all_docs()
    return engine

def test_query_returns_results(rag):
    results = rag.query("사전검토 동의율이 몇 퍼센트인가요?")
    assert len(results) > 0
    assert "text" in results[0]
    assert "source" in results[0]

def test_query_far_limit(rag):
    results = rag.query("1차 역세권 용적률 상한은?")
    texts = " ".join(r["text"] for r in results)
    assert "700" in texts

def test_query_contractor_timing(rag):
    results = rag.query("시공사 선정은 언제 가능한가요?")
    texts = " ".join(r["text"] for r in results)
    assert "조합설립" in texts
