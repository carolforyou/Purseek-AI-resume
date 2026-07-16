"""Knowledge base service using FAISS + TF-IDF embeddings.

Document storage (pickles): data/vector_store/
FAISS index (ASCII path required): TEMP/codex_kb/
"""

import os
import pickle
from pathlib import Path
from typing import List, Optional, Tuple

import faiss
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sklearn.feature_extraction.text import TfidfVectorizer

PROJECT_DATA = Path(__file__).resolve().parents[3] / "data"
DOCS_DIR = PROJECT_DATA / "vector_store"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

# FAISS can't handle non-ASCII paths (Chinese chars), use TEMP
FAISS_DIR = Path(os.environ.get("TEMP", "/tmp")) / "codex_kb"
FAISS_DIR.mkdir(parents=True, exist_ok=True)

INDEX_PATH = FAISS_DIR / "faiss.index"
DOCS_PATH = DOCS_DIR / "documents.pkl"
VECTORIZER_PATH = DOCS_DIR / "vectorizer.pkl"


class KnowledgeBase:
    """FAISS-backed knowledge base with TF-IDF embeddings."""

    def __init__(self) -> None:
        self.dimension: int = 512
        self.index: Optional[faiss.IndexFlatIP] = None
        self.documents: List[str] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=80,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        self._load_if_exists()

    def _load_if_exists(self) -> None:
        if INDEX_PATH.exists() and DOCS_PATH.exists() and VECTORIZER_PATH.exists():
            try:
                self.index = faiss.read_index(str(INDEX_PATH))
                with open(str(DOCS_PATH), "rb") as f:
                    self.documents = pickle.load(f)
                with open(str(VECTORIZER_PATH), "rb") as f:
                    self.vectorizer = pickle.load(f)
                self.dimension = self.index.d
            except Exception:
                self._init_empty()

    def _init_empty(self) -> None:
        self.vectorizer = TfidfVectorizer(
            max_features=self.dimension, analyzer="char_wb", ngram_range=(2, 4),
        )
        self.index = None
        self.documents = []

    def _save(self) -> None:
        FAISS_DIR.mkdir(parents=True, exist_ok=True)
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        if self.index is not None:
            faiss.write_index(self.index, str(INDEX_PATH))
        with open(str(DOCS_PATH), "wb") as f:
            pickle.dump(self.documents, f)
        if self.vectorizer is not None:
            with open(str(VECTORIZER_PATH), "wb") as f:
                pickle.dump(self.vectorizer, f)

    def add_documents(self, texts: List[str], source: str = "") -> int:
        all_chunks: List[str] = []
        for text in texts:
            if not text.strip():
                continue
            chunks = self.text_splitter.split_text(text)
            all_chunks.extend(chunks)

        if not all_chunks:
            return 0

        if self.vectorizer is None:
            self.vectorizer = TfidfVectorizer(
                max_features=self.dimension, analyzer="char_wb", ngram_range=(2, 4),
            )

        all_docs = self.documents + all_chunks
        vectors = self.vectorizer.fit_transform(all_docs).toarray().astype(np.float32)
        faiss.normalize_L2(vectors)

        actual_dim = vectors.shape[1]
        self.dimension = actual_dim
        self.index = faiss.IndexFlatIP(actual_dim)
        self.index.add(vectors)
        self.documents = all_docs
        self._save()
        return len(all_chunks)

    def search(self, query: str, k: int = 5) -> List[Tuple[str, float]]:
        if self.index is None or not self.documents or self.vectorizer is None:
            return []
        query_vector = self.vectorizer.transform([query]).toarray().astype(np.float32)
        faiss.normalize_L2(query_vector)
        scores, indices = self.index.search(query_vector, min(k, len(self.documents)))
        results: List[Tuple[str, float]] = []
        for score, idx in zip(scores[0], indices[0]):
            if 0 <= idx < len(self.documents):
                results.append((self.documents[idx], float(score)))
        return results

    def delete_all(self) -> None:
        self.documents = []
        self.index = None
        self.vectorizer = TfidfVectorizer(
            max_features=self.dimension, analyzer="char_wb", ngram_range=(2, 4),
        )
        for p in [INDEX_PATH, DOCS_PATH, VECTORIZER_PATH]:
            if p.exists():
                p.unlink()

    def get_stats(self) -> dict:
        return {
            "document_count": len(self.documents),
            "vector_dimension": self.dimension,
            "index_type": type(self.index).__name__ if self.index else "None",
        }


_kb_instance: Optional[KnowledgeBase] = None


def get_knowledge_base() -> KnowledgeBase:
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = KnowledgeBase()
    return _kb_instance
