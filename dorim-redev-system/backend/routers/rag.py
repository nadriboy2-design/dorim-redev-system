# dorim-redev-system/backend/routers/rag.py
import os
from fastapi import APIRouter
from pydantic import BaseModel
import anthropic
from rag_engine import rag_engine

router = APIRouter(tags=["rag"])
_anthropic = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


class RagQuery(BaseModel):
    question: str


@router.post("/rag/query")
def rag_query(body: RagQuery):
    """법령 질의 → RAG 검색 → Claude Sonnet 답변 생성."""
    chunks = rag_engine.query(body.question, n_results=3)
    context = "\n\n".join(f"[{c['source']}]\n{c['text']}" for c in chunks)

    system_prompt = (
        "당신은 서울시 역세권 재개발 전문 법률 자문 AI입니다. "
        "다음 법령 조항을 참고하여 정확하고 보수적인 자문을 제공하십시오. "
        "불확실한 내용은 반드시 '법무사·변호사 확인 필요'라고 명시하십시오.\n\n"
        f"[참고 법령]\n{context}"
    )

    try:
        message = _anthropic.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            messages=[{"role": "user", "content": body.question}],
            system=system_prompt,
        )
        return {
            "data": {
                "answer": message.content[0].text,
                "sources": [{"source": c["source"], "excerpt": c["text"][:100]} for c in chunks],
            },
            "error": None,
        }
    except Exception as exc:
        return {"data": None, "error": str(exc)}


@router.post("/rag/embed-docs")
def embed_docs():
    """docs/legal/ 문서 재임베딩 (업데이트 시 호출)."""
    count = rag_engine.embed_all_docs()
    return {"data": {"embedded_chunks": count}, "error": None}
