# dorim-redev-system/backend/rag_engine.py
"""RAG 엔진 — 클라우드 호환 버전.

클라우드(Render free tier): ChromaDB + SentenceTransformer는 메모리 512MB 한계로
임포트 시 모델 로드 대신 키워드 기반 경량 검색으로 폴백합니다.
로컬 환경: 환경변수 USE_VECTOR_RAG=1 설정 시 벡터 검색 활성화.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

COLLECTION_NAME = "dorim_legal_docs"
USE_VECTOR = os.getenv("USE_VECTOR_RAG", "0") == "1"


# ── 내장 법령 시드 데이터 (클라우드 경량 폴백) ─────────────────────────────
_SEED_DOCS: list[dict] = [
    {
        "source": "역세권_운영기준_2026.md",
        "text": (
            "역세권 장기전세주택 건립 운영기준 (2026.3.6. 시행)\n"
            "1차 역세권(승강장 경계 250m 이내)의 법적상한 용적률은 최대 700%입니다. "
            "2차 역세권은 최대 500%입니다. "
            "제3종일반주거를 준주거로 변경 시 1차 역세권 기준용적률 210%(230%), 상한 250%, 법적상한 500~700%."
        ),
    },
    {
        "source": "역세권_운영기준_2026.md",
        "text": (
            "사전검토 신청 요건: 2026.3.6. 개정으로 동의율 요건이 40% 이상으로 완화되었습니다. "
            "추진위원회 구성은 50% 이상, 조합설립인가는 토지등소유자 3/4(75%) 이상 및 토지면적 1/2 이상 동의 필요."
        ),
    },
    {
        "source": "도시정비법.md",
        "text": (
            "서울특별시 도시 및 주거환경정비 조례: 시공자 선정 시기는 조합설립인가 이후입니다. "
            "조합설립인가 전 시공사 입찰 공고는 법 위반입니다. "
            "최초 사업시행계획인가 이후 분양공고 전에 공사비 검증을 의무적으로 신청해야 합니다."
        ),
    },
    {
        "source": "도시정비법.md",
        "text": (
            "관리처분계획: 사업비 증가 시 조합원 2/3(66.7%) 이상 동의가 필요합니다. "
            "관리처분계획 변경 인가 신청 전 한국부동산원 타당성 검토를 거쳐야 합니다. "
            "분양신청을 하지 않은 토지등소유자는 현금청산 대상입니다."
        ),
    },
    {
        "source": "역세권_운영기준_2026.md",
        "text": (
            "인센티브 항목: 전용면적 60㎡ 이하 소형주택을 용적률의 20% 이상 추가 공급 시 "
            "기준용적률의 20%를 추가 완화합니다. "
            "친환경 건축물 인센티브: 서울시 녹색건축물 설계 기준에 따라 환경·에너지 성능 중 2가지 이상 상향 시 적용."
        ),
    },
    {
        "source": "도시정비법.md",
        "text": (
            "추진위원회: 토지등소유자 50% 이상 동의로 구성. 창립총회 개최 후 운영규정 및 위원 명부 제출. "
            "조합 설립: 창립총회에서 정관 의결 후 시장·군수 인가 신청. "
            "총회 의결: 조합원 과반수 출석, 출석 조합원 과반수 찬성이 원칙."
        ),
    },
    {
        "source": "도림동239-12_사업정보.md",
        "text": (
            "도림사거리 역세권 재개발 사업 개요: 서울 영등포구 도림동 239-12 일원, "
            "구역면적 59,607.59㎡, 현재 서울시 사전검토회의 단계(정비구역 입안 초기). "
            "역세권 장기전세주택 건립 인센티브 적용 대상 구역."
        ),
    },
]


def _keyword_score(text: str, question: str) -> float:
    """단순 키워드 매칭 점수 (0.0 ~ 1.0)."""
    question_lower = question.lower()
    text_lower = text.lower()
    # 형태소 단위 분해 대신 2글자 이상 단어 추출
    words = re.findall(r"[가-힣a-z]{2,}", question_lower)
    if not words:
        return 0.0
    matched = sum(1 for w in words if w in text_lower)
    return matched / len(words)


class RagEngine:
    """벡터 RAG(로컬) 또는 키워드 검색(클라우드) 통합 인터페이스."""

    def __init__(self, docs_dir: str | None = None, db_dir: str | None = None):
        self._docs_dir = Path(docs_dir) if docs_dir else Path(__file__).parent.parent / "docs" / "legal"
        self._db_dir = str(db_dir) if db_dir else str(Path(__file__).parent.parent / "data" / "chroma_db")
        self._vector_ready = False
        self._client = None
        self._collection = None
        self._ef = None

        if USE_VECTOR:
            self._init_vector()

    def _init_vector(self) -> None:
        """벡터 DB 초기화 (USE_VECTOR_RAG=1 환경에서만 호출)."""
        try:
            import chromadb
            from chromadb.utils import embedding_functions

            self._client = chromadb.PersistentClient(path=self._db_dir)
            self._ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="paraphrase-multilingual-MiniLM-L12-v2"
            )
            self._collection = self._client.get_or_create_collection(
                name=COLLECTION_NAME,
                embedding_function=self._ef,
            )
            self._vector_ready = True
            print("[RAG] 벡터 검색 모드 활성화")
        except Exception as e:
            print(f"[RAG] 벡터 초기화 실패 → 키워드 모드로 폴백: {e}")

    def embed_all_docs(self) -> int:
        """docs/legal/*.md 파일 전체 임베딩. 반환값: 임베딩된 청크 수."""
        if not self._vector_ready:
            raise RuntimeError("USE_VECTOR_RAG=1 환경변수가 필요합니다.")
        if not self._docs_dir.exists():
            raise FileNotFoundError(f"{self._docs_dir} 없음")

        chunks, ids, metas = [], [], []
        for md_file in sorted(self._docs_dir.glob("*.md")):
            text = md_file.read_text(encoding="utf-8")
            paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 30]
            for i, para in enumerate(paragraphs):
                doc_id = f"{md_file.stem}_{i}"
                chunks.append(para)
                ids.append(doc_id)
                metas.append({"source": md_file.name, "chunk_idx": i})

        if chunks:
            self._collection.upsert(documents=chunks, ids=ids, metadatas=metas)
        return len(chunks)

    def query(self, question: str, n_results: int = 3) -> list[dict]:
        """질의에 가장 관련된 법령 조항 Top-N 반환."""
        if self._vector_ready and self._collection is not None:
            return self._vector_query(question, n_results)
        return self._keyword_query(question, n_results)

    def _vector_query(self, question: str, n_results: int) -> list[dict]:
        results = self._collection.query(
            query_texts=[question],
            n_results=n_results,
        )
        return [
            {"text": doc, "source": meta["source"], "chunk_idx": meta.get("chunk_idx", 0)}
            for doc, meta in zip(results["documents"][0], results["metadatas"][0])
        ]

    def _keyword_query(self, question: str, n_results: int) -> list[dict]:
        scored = [
            (doc, _keyword_score(doc["text"], question))
            for doc in _SEED_DOCS
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [
            {"text": doc["text"], "source": doc["source"], "chunk_idx": i}
            for i, (doc, _score) in enumerate(scored[:n_results])
        ]


# 전역 싱글턴 — 임포트 시 무거운 모델 로드 없음
rag_engine = RagEngine()
