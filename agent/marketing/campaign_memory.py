"""F2b Campaign Vector Memory — Chroma persistent store with SQL degrade."""

from __future__ import annotations

import hashlib
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

COLLECTION_NAME = "mb_campaign_memory"
DEFAULT_PERSIST_DIR = "data/chroma/marketing"
TOP_K_DEFAULT = 5
EMBED_DIMS = 64


def memory_persist_path() -> Path:
    raw = (os.getenv("MB_CHROMA_PATH") or DEFAULT_PERSIST_DIR).strip()
    path = Path(raw)
    if not path.is_absolute():
        path = Path.cwd() / path
    return path


def _hash_embed(texts: List[str], dims: int = EMBED_DIMS) -> List[List[float]]:
    """Deterministic local embedding — no onnx / network (VPS-safe)."""
    out: List[List[float]] = []
    for text in texts:
        vec = [0.0] * dims
        tokens = (text or "").lower().split()
        if not tokens:
            tokens = ["_empty_"]
        for tok in tokens:
            h = hashlib.sha256(tok.encode("utf-8")).digest()
            for i in range(dims):
                vec[i] += (h[i % len(h)] / 255.0) - 0.5
        norm = sum(v * v for v in vec) ** 0.5 or 1.0
        out.append([v / norm for v in vec])
    return out


def _chroma_available() -> bool:
    try:
        import chromadb  # noqa: F401

        return True
    except Exception:
        return False


def _get_collection():
    """Return (collection, None) or (None, reason)."""
    if not _chroma_available():
        return None, "chromadb_not_installed"
    try:
        import chromadb

        path = memory_persist_path()
        path.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=str(path))
        # Embeddings supplied explicitly — no DefaultEmbeddingFunction / onnx
        coll = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        return coll, None
    except Exception as exc:
        logger.warning("[mb.memory] chroma init failed: %s", exc)
        return None, str(exc)


def _doc_text(row: Dict[str, Any]) -> str:
    payload = row.get("payload") or {}
    if isinstance(payload, str):
        payload = {}
    return " | ".join(
        [
            str(row.get("heuristic_rule_id") or ""),
            str(row.get("proposed_action") or ""),
            str(row.get("llm_rationale_nl") or row.get("rationale_nl") or ""),
            str(payload.get("severity") or ""),
            str(row.get("governance_result") or ""),
            str(row.get("hitl_status") or ""),
        ]
    )


def _outcome_from_row(row: Dict[str, Any]) -> str:
    """negative|positive|unknown — from hitl/governance/hypothesis."""
    hitl = (row.get("hitl_status") or "").lower()
    gov = (row.get("governance_result") or "").lower()
    outcome = (row.get("outcome") or "").lower()
    if outcome in ("negative", "positive"):
        return outcome
    if hitl in ("denied", "deny") or gov == "deny":
        return "negative"
    if hitl in ("approved", "approve") or gov == "allow":
        return "positive"
    return "unknown"


def upsert_decision(row: Dict[str, Any]) -> Dict[str, Any]:
    """Index one shadow/decision row into Chroma (no-op on degrade)."""
    action_id = row.get("action_id")
    if not action_id:
        return {"ok": False, "error": "missing_action_id"}
    coll, err = _get_collection()
    if coll is None:
        return {"ok": False, "memory_source": "sql_fallback", "error": err}
    doc = _doc_text(row)
    outcome = _outcome_from_row(row)
    meta = {
        "action_id": str(action_id),
        "heuristic_rule_id": str(row.get("heuristic_rule_id") or ""),
        "proposed_action": str(row.get("proposed_action") or ""),
        "outcome": outcome,
        "governance_result": str(row.get("governance_result") or ""),
        "hitl_status": str(row.get("hitl_status") or ""),
    }
    try:
        emb = _hash_embed([doc])[0]
        coll.upsert(
            ids=[str(action_id)],
            documents=[doc],
            embeddings=[emb],
            metadatas=[meta],
        )
        return {"ok": True, "memory_source": "chroma", "action_id": action_id}
    except Exception as exc:
        logger.warning("[mb.memory] upsert failed: %s", exc)
        return {"ok": False, "memory_source": "sql_fallback", "error": str(exc)}


def query_similar(
    decision_text: str,
    *,
    top_k: int = TOP_K_DEFAULT,
    prefer_negative: bool = True,
) -> Dict[str, Any]:
    """
    Top-k similar past decisions.
    Returns memory_source chroma|sql_fallback and hits[].
    """
    coll, err = _get_collection()
    if coll is not None:
        try:
            q_emb = _hash_embed([decision_text or "hold"])[0]
            raw = coll.query(
                query_embeddings=[q_emb],
                n_results=max(top_k * 2, top_k),
                include=["documents", "metadatas", "distances"],
            )
            hits: List[Dict[str, Any]] = []
            ids = (raw.get("ids") or [[]])[0]
            docs = (raw.get("documents") or [[]])[0]
            metas = (raw.get("metadatas") or [[]])[0]
            dists = (raw.get("distances") or [[]])[0]
            for i, aid in enumerate(ids):
                meta = metas[i] if i < len(metas) else {}
                hits.append(
                    {
                        "action_id": aid,
                        "document": docs[i] if i < len(docs) else "",
                        "outcome": (meta or {}).get("outcome", "unknown"),
                        "heuristic_rule_id": (meta or {}).get("heuristic_rule_id"),
                        "proposed_action": (meta or {}).get("proposed_action"),
                        "distance": dists[i] if i < len(dists) else None,
                    }
                )
            if prefer_negative:
                neg = [h for h in hits if h.get("outcome") == "negative"]
                rest = [h for h in hits if h.get("outcome") != "negative"]
                hits = (neg + rest)[:top_k]
            else:
                hits = hits[:top_k]
            return {
                "ok": True,
                "memory_source": "chroma",
                "hits": hits,
                "negative_hits": sum(1 for h in hits if h.get("outcome") == "negative"),
            }
        except Exception as exc:
            logger.warning("[mb.memory] query failed, SQL fallback: %s", exc)
            err = str(exc)

    return _sql_fallback_query(decision_text, top_k=top_k, error=err)


def _sql_fallback_query(
    decision_text: str,
    *,
    top_k: int,
    error: Optional[str] = None,
) -> Dict[str, Any]:
    from agent.db import db_list_marketing_shadow

    rows = db_list_marketing_shadow(limit=max(top_k * 5, 20))
    needle = set((decision_text or "").lower().split())
    scored: List[Dict[str, Any]] = []
    for row in rows:
        doc = _doc_text(row)
        tokens = set(doc.lower().split())
        overlap = len(needle & tokens) if needle else 0
        outcome = _outcome_from_row(row)
        scored.append(
            {
                "action_id": row.get("action_id"),
                "document": doc,
                "outcome": outcome,
                "heuristic_rule_id": row.get("heuristic_rule_id"),
                "proposed_action": row.get("proposed_action"),
                "distance": 1.0 / (1.0 + overlap),
                "_overlap": overlap,
            }
        )
    scored.sort(key=lambda h: (-(1 if h["outcome"] == "negative" else 0), -h["_overlap"]))
    hits = [{k: v for k, v in h.items() if k != "_overlap"} for h in scored[:top_k]]
    return {
        "ok": True,
        "memory_source": "sql_fallback",
        "hits": hits,
        "negative_hits": sum(1 for h in hits if h.get("outcome") == "negative"),
        "degrade_reason": error,
    }


def sync_from_shadow(limit: int = 100) -> Dict[str, Any]:
    """Batch index recent shadow rows into Chroma."""
    from agent.db import db_list_marketing_shadow

    rows = db_list_marketing_shadow(limit=limit)
    upserted = 0
    failed = 0
    last_source = "chroma"
    for row in rows:
        res = upsert_decision(row)
        last_source = res.get("memory_source") or last_source
        if res.get("ok"):
            upserted += 1
        else:
            failed += 1
    return {
        "ok": True,
        "synced": upserted,
        "failed": failed,
        "total": len(rows),
        "memory_source": last_source if upserted else "sql_fallback",
    }


def enrich_decision_with_memory(decision: Any) -> Dict[str, Any]:
    """
    Query memory for a Decision dataclass; return enrichment dict.
    Does not mutate North Star — only rationale/dims hints.
    """
    text = (
        f"{getattr(decision, 'heuristic_rule_id', '')} "
        f"{getattr(decision, 'proposed_action', '')} "
        f"{getattr(decision, 'rationale_nl', '')}"
    )
    result = query_similar(text, top_k=TOP_K_DEFAULT, prefer_negative=True)
    neg = int(result.get("negative_hits") or 0)
    warning = ""
    if neg > 0:
        ids = [
            h.get("action_id")
            for h in (result.get("hits") or [])
            if h.get("outcome") == "negative"
        ]
        warning = (
            f" MEMORY WARNING: {neg} similar past decision(s) negative/denied "
            f"({', '.join(str(i) for i in ids[:3])})."
        )
    return {
        "memory_source": result.get("memory_source"),
        "memory_hits": len(result.get("hits") or []),
        "memory_negative_hits": neg,
        "memory_warning": warning,
        "hits": result.get("hits") or [],
    }


def memory_status() -> Dict[str, Any]:
    path = memory_persist_path()
    coll, err = _get_collection()
    count = 0
    source = "sql_fallback"
    if coll is not None:
        try:
            count = int(coll.count())
            source = "chroma"
            err = None
        except Exception as exc:
            err = str(exc)
            source = "sql_fallback"
    return {
        "ok": True,
        "memory_source": source,
        "collection": COLLECTION_NAME,
        "persist_path": str(path),
        "count": count,
        "chroma_installed": _chroma_available(),
        "degrade_reason": err,
    }
