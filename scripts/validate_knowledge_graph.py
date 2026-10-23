#!/usr/bin/env python3
"""Validate the curated knowledge graph against the canonical article catalog.

Usage: python3 scripts/validate_knowledge_graph.py
This check is deterministic and intentionally does not claim semantic truth.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = ROOT / "api" / "knowledge-graph.json"
CATALOG_PATH = ROOT / "api" / "catalog.json"


def main() -> int:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    try:
        graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"FAIL: cannot parse {GRAPH_PATH.relative_to(ROOT)}: {exc}")
        return 1

    try:
        catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"FAIL: cannot parse {CATALOG_PATH.relative_to(ROOT)}: {exc}")
        return 1

    nodes = graph.get("nodes")
    edges = graph.get("edges")
    catalog_items = catalog.get("items")
    check(isinstance(nodes, list), "nodes must be a list")
    check(isinstance(edges, list), "edges must be a list")
    check(isinstance(catalog_items, list), "api/catalog.json items must be a list")
    if not isinstance(nodes, list) or not isinstance(edges, list) or not isinstance(catalog_items, list):
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    article_ids = {
        item.get("id")
        for item in catalog_items
        if isinstance(item, dict) and item.get("type") in {"Articles", "Diverse Lab"}
    }
    node_ids: list[str] = []
    allowed_node_status = {"seed", "proposed", "validated", "deprecated"}
    allowed_edge_status = {"seed", "proposed", "validated", "contested", "deprecated"}

    for idx, node in enumerate(nodes):
        if not isinstance(node, dict):
            errors.append(f"nodes[{idx}] must be an object")
            continue
        node_id = node.get("id")
        check(isinstance(node_id, str) and bool(node_id.strip()), f"nodes[{idx}] missing id")
        if isinstance(node_id, str) and node_id:
            node_ids.append(node_id)
        check(bool(node.get("label")), f"node {node_id!r} missing label")
        check(node.get("status") in allowed_node_status, f"node {node_id!r} has invalid status")
        sources = node.get("source_articles", [])
        check(isinstance(sources, list), f"node {node_id!r} source_articles must be a list")
        if isinstance(sources, list):
            for source_id in sources:
                check(source_id in article_ids, f"node {node_id!r} references unknown article id {source_id!r}")

    check(len(node_ids) == len(set(node_ids)), "duplicate node ids")

    edge_ids: list[str] = []
    node_id_set = set(node_ids)
    for idx, edge in enumerate(edges):
        if not isinstance(edge, dict):
            errors.append(f"edges[{idx}] must be an object")
            continue
        edge_id = edge.get("id")
        check(isinstance(edge_id, str) and bool(edge_id.strip()), f"edges[{idx}] missing id")
        if isinstance(edge_id, str) and edge_id:
            edge_ids.append(edge_id)
        source = edge.get("source")
        target = edge.get("target")
        check(source in node_id_set, f"edge {edge_id!r} has unknown source node {source!r}")
        check(target in node_id_set, f"edge {edge_id!r} has unknown target node {target!r}")
        check(source != target, f"edge {edge_id!r} must not point to itself")
        check(bool(edge.get("relation")), f"edge {edge_id!r} missing relation")
        check(edge.get("status") in allowed_edge_status, f"edge {edge_id!r} has invalid status")
        evidence = edge.get("evidence_articles", [])
        check(isinstance(evidence, list), f"edge {edge_id!r} evidence_articles must be a list")
        if isinstance(evidence, list):
            for source_id in evidence:
                check(source_id in article_ids, f"edge {edge_id!r} references unknown evidence article id {source_id!r}")

    check(len(edge_ids) == len(set(edge_ids)), "duplicate edge ids")
    check(bool(nodes), "graph must contain at least one node")
    check(bool(edges), "graph must contain at least one edge")

    if errors:
        print(f"Knowledge graph validation FAILED ({len(errors)} issue(s))")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(
        "Knowledge graph validation OK: "
        f"{len(nodes)} nodes, {len(edges)} edges, "
        f"{len(article_ids)} catalog article/Diverse Lab IDs available for provenance."
    )
    print("Note: structural validity and provenance links do not prove semantic truth.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
