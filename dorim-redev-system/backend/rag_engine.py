# dorim-redev-system/backend/rag_engine.py
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

COLLECTION_NAME = "dorim_legal_docs"


class RagEngine:
    def __init__(
        self,
        docs_dir: str = None,
        db_dir: str = None,
    ):
        if docs_dir is None:
            docs_dir = str(Path(__file__).parent.parent / "docs" / "legal")
        if db_dir is None:
            db_dir = str(Path(__file__).parent.parent / "data" / "chroma_db")

        self.docs_dir = Path(docs_dir)
        self.client = chromadb.PersistentClient(path=db_dir)
        self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="paraphrase-multilingual-MiniLM-L12-v2"
        )
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.ef,
        )

    def embed_all_docs(self) -> int:
        """docs/legal/*.md 파일 전체 임베딩. 반환값: 임베딩된 청크 수."""
        if not self.docs_dir.exists():
            raise FileNotFoundError(f"{self.docs_dir} 없음")

        chunks, ids, metas = [], [], []
        for md_file in sorted(self.docs_dir.glob("*.md")):
            text = md_file.read_text(encoding="utf-8")
            paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 30]
            for i, para in enumerate(paragraphs):
                doc_id = f"{md_file.stem}_{i}"
                chunks.append(para)
                ids.append(doc_id)
                metas.append({"source": md_file.name, "chunk_idx": i})

        if chunks:
            self.collection.upsert(documents=chunks, ids=ids, metadatas=metas)
        return len(chunks)

    def query(self, question: str, n_results: int = 3) -> list[dict]:
        """질의에 가장 관련된 법령 조항 Top-N 반환."""
        results = self.collection.query(
            query_texts=[question],
            n_results=n_results,
        )
        return [
            {
                "text": doc,
                "source": meta["source"],
                "chunk_idx": meta["chunk_idx"],
            }
            for doc, meta in zip(
                results["documents"][0], results["metadatas"][0]
            )
        ]


# 전역 싱글턴
rag_engine = RagEngine()
