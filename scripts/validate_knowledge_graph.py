#!/usr/bin/env python3
"""Validate the curated knowledge graph against the existing catalog."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    try:
        graph = json.loads((ROOT / "api/knowledge-graph.json").read_text(encoding="utf-8"))
        catalog = json.loads((ROOT / "api/catalog.json").read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"FAIL unable to load graph/catalog: {exc}")
        return 1

    errors = []
    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if graph.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        print("FAIL nodes and edges must be arrays")
        return 1

    node_by_id = {}
    for i, node in enumerate(nodes):
        node_id = node.get("id") if isinstance(node, dict) else None
        if not node_id:
            errors.append(f"nodes[{i}] missing id")
            continue
        if node_id in node_by_id:
            errors.append(f"duplicate node id: {node_id}")
        node_by_id[node_id] = node
        if node.get("type") not in {"concept", "article", "project", "system"}:
            errors.append(f"node {node_id}: unsupported type {node.get('type')!r}")
        if not node.get("label"):
            errors.append(f"node {node_id}: missing label")

    catalog_ids = {item.get("id") for item in catalog.get("items", []) if item.get("id")}
    for node_id, node in node_by_id.items():
        article_id = node.get("article_id")
        if node.get("type") == "article" and not article_id:
            errors.append(f"article node {node_id}: missing article_id")
        if article_id and article_id not in catalog_ids:
            errors.append(f"node {node_id}: article_id absent from api/catalog.json: {article_id}")

    edge_ids = set()
    for i, edge in enumerate(edges):
        edge_id = edge.get("id") if isinstance(edge, dict) else None
        if not edge_id:
            errors.append(f"edges[{i}] missing id")
            continue
        if edge_id in edge_ids:
            errors.append(f"duplicate edge id: {edge_id}")
        edge_ids.add(edge_id)
        if edge.get("source") not in node_by_id:
            errors.append(f"edge {edge_id}: unknown source {edge.get('source')!r}")
        if edge.get("target") not in node_by_id:
            errors.append(f"edge {edge_id}: unknown target {edge.get('target')!r}")
        if not edge.get("type"):
            errors.append(f"edge {edge_id}: missing relation type")
        if edge.get("confidence") not in {"low", "medium", "high"}:
            errors.append(f"edge {edge_id}: confidence must be low, medium or high")
        for evidence_id in edge.get("evidence", []):
            if evidence_id not in catalog_ids:
                errors.append(f"edge {edge_id}: evidence id absent from api/catalog.json: {evidence_id}")

    if errors:
        for error in errors:
            print(f"FAIL {error}")
        print(f"Knowledge graph validation failed: {len(errors)} issue(s)")
        return 1
    print(f"OK knowledge graph: {len(nodes)} nodes, {len(edges)} edges; article references resolve")
    return 0

if __name__ == "__main__":
    sys.exit(main())
