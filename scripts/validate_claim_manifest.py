#!/usr/bin/env python3
"""Validate resume claim provenance and consistency across delivery views.

This is intentionally a small structural lint. It does not decide whether a
claim is true; it checks that the evidence and view metadata needed for a
human review are present and that derived views do not rewrite facts.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


STATUSES = {"verified", "historical", "proposed", "unknown"}
PUBLISHABILITY = {"public", "public_with_qualifier", "internal_only", "blocked"}
PUBLIC_VIEWS = {"compact", "standard", "technical", "ats"}
RISK_RE = re.compile(
    r"实现|负责|主导|上线|生产|分布式|多.?Agent|审批|恢复|用户|提效|提升|覆盖|审计|密级|权限|"
    r"100%|/|P95|Recall|MRR|Precision|通过"
)
DATE_RE = re.compile(r"20\d{2}(?:[./-]\d{1,2}){0,2}")


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("根节点必须是 JSON object")
    return value


def claim_map(data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    claims = data.get("claims", [])
    if isinstance(claims, dict):
        items = list(claims.values())
    elif isinstance(claims, list):
        items = claims
    else:
        raise ValueError("claims 必须是 list 或 object")
    result: Dict[str, Dict[str, Any]] = {}
    for claim in items:
        if not isinstance(claim, dict):
            raise ValueError("claims 中的每一项必须是 object")
        claim_id = claim.get("claim_id")
        if not isinstance(claim_id, str) or not claim_id.strip():
            raise ValueError("每条 claim 必须有非空 claim_id")
        if claim_id in result:
            raise ValueError(f"重复 claim_id: {claim_id}")
        result[claim_id] = claim
    return result


def required_text_list(value: Any) -> List[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError("限定词字段必须是字符串数组")
    return value


def text_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    raise ValueError("文本字段必须是字符串或字符串数组")


def normalized(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def normalized_text(value: str) -> str:
    return re.sub(r"\s+", "", value)


def validate_claims(claims: Dict[str, Dict[str, Any]], label: str) -> List[str]:
    errors: List[str] = []
    for claim_id, claim in claims.items():
        prefix = f"{label}:{claim_id}"
        for field in ("canonical_fact", "status", "publishability", "ownership", "scope"):
            if not claim.get(field):
                errors.append(f"{prefix} 缺少 {field}")

        status = claim.get("status")
        publishability = claim.get("publishability")
        if status not in STATUSES:
            errors.append(f"{prefix} status 无效: {status!r}")
        if publishability not in PUBLISHABILITY:
            errors.append(f"{prefix} publishability 无效: {publishability!r}")
        if status == "historical" and publishability == "public":
            errors.append(f"{prefix} historical 必须带限定词，不能直接 public")
        if status in {"proposed", "unknown"} and publishability in {
            "public",
            "public_with_qualifier",
        }:
            errors.append(f"{prefix} {status} 不得公开投递")

        source_refs = claim.get("source_refs")
        if not isinstance(source_refs, list) or not source_refs:
            errors.append(f"{prefix} 缺少 source_refs")
        else:
            for index, source in enumerate(source_refs):
                if not isinstance(source, dict) or not source.get("path"):
                    errors.append(f"{prefix} source_refs[{index}] 缺少 path")
                if isinstance(source, dict) and not source.get("evidence_type"):
                    errors.append(f"{prefix} source_refs[{index}] 缺少 evidence_type")

        fact_text = str(claim.get("canonical_fact", ""))
        if claim.get("metric") or RISK_RE.search(fact_text):
            if not claim.get("verification"):
                errors.append(f"{prefix} 高风险/量化主张缺少 verification")
            if not claim.get("ownership") or not claim.get("scope"):
                errors.append(f"{prefix} 高风险主张缺少 ownership 或 scope")

        for field in ("mandatory_qualifiers", "required_qualifiers"):
            try:
                required_text_list(claim.get(field))
            except ValueError as exc:
                errors.append(f"{prefix} {field}: {exc}")

    return errors


def view_refs(data: Dict[str, Any]) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    manifest = data.get("view_manifest")
    if not isinstance(manifest, dict):
        return None, []
    name = str(manifest.get("name", ""))
    refs = manifest.get("claim_refs", [])
    if not isinstance(refs, list):
        raise ValueError("view_manifest.claim_refs 必须是 list")
    if not all(isinstance(item, dict) for item in refs):
        raise ValueError("view_manifest.claim_refs 中的每一项必须是 object")
    return name, refs


def render_tokens(claim: Dict[str, Any]) -> List[str]:
    explicit = text_list(claim.get("render_tokens"))
    if explicit:
        return list(dict.fromkeys(token for token in explicit if token))

    tokens: List[str] = []
    metric = claim.get("metric")
    if isinstance(metric, dict):
        for key in ("value", "baseline"):
            value = metric.get(key)
            if value is not None and str(value).strip():
                tokens.append(str(value))
    tokens.extend(DATE_RE.findall(str(claim.get("canonical_fact", ""))))
    scope = str(claim.get("scope", ""))
    scope_parts = [part.strip() for part in re.split(r"[/；;,，]+", scope)]
    tokens.extend(part for part in scope_parts if len(part) >= 2)
    return list(dict.fromkeys(token for token in tokens if token))


def validate_view(
    data: Dict[str, Any],
    label: str,
    claims: Dict[str, Dict[str, Any]],
    *,
    require_manifest: bool = False,
) -> List[str]:
    errors: List[str] = []
    view_name, refs = view_refs(data)
    if not view_name:
        if require_manifest:
            errors.append(f"{label}:缺少 view_manifest，不能校验最终投递文本")
        return errors
    if view_name not in PUBLIC_VIEWS:
        errors.append(f"{label}:未知投递视图 {view_name!r}")

    seen: Dict[str, Dict[str, Any]] = {}
    for ref in refs:
        if ref.get("profile_claim") is True:
            if not str(ref.get("text", "")).strip():
                errors.append(f"{label}:profile_claim 缺少渲染文本")
            continue
        claim_id = ref.get("claim_id")
        if not isinstance(claim_id, str) or claim_id not in claims:
            errors.append(f"{label}:{claim_id} 引用了不存在的 claim_id")
            continue
        if claim_id in seen:
            errors.append(f"{label}:{claim_id} 在 view_manifest 中重复")
        seen[claim_id] = ref
        claim = claims[claim_id]
        omitted = bool(ref.get("omitted", False))
        policy = claim.get("view_policy", {})
        if not isinstance(policy, dict):
            policy = {}
        expected = policy.get(view_name)
        if expected == "required" and omitted:
            errors.append(f"{label}:{claim_id} 是 required，但被省略")
        if expected == "forbidden" and not omitted:
            errors.append(f"{label}:{claim_id} 是 forbidden，但被引用")
        if omitted:
            if not ref.get("omit_reason"):
                errors.append(f"{label}:{claim_id} 省略时必须填写 omit_reason")
            continue
        text = str(ref.get("text", ""))
        if not text.strip():
            errors.append(f"{label}:{claim_id} 被引用但缺少渲染文本")
        normalized_rendered = normalized_text(text)
        qualifiers = required_text_list(claim.get("mandatory_qualifiers", [])) + required_text_list(
            claim.get("required_qualifiers", [])
        )
        for qualifier in dict.fromkeys(qualifiers):
            if qualifier and normalized_text(qualifier) not in normalized_rendered:
                errors.append(f"{label}:{claim_id} 缺少限定词: {qualifier}")
        for token in render_tokens(claim):
            if normalized_text(token) not in normalized_rendered:
                errors.append(f"{label}:{claim_id} 缺少事实 token: {token}")
        allowed_by_view = claim.get("allowed_phrasing_by_view", {})
        if isinstance(allowed_by_view, dict) and allowed_by_view.get(view_name):
            options = text_list(allowed_by_view[view_name])
            if not any(
                normalized_text(option) in normalized_rendered for option in options
            ):
                errors.append(f"{label}:{claim_id} 不符合 {view_name} 的 approved phrasing")
        for forbidden in text_list(claim.get("forbidden_phrasing")):
            if forbidden and normalized_text(forbidden) in normalized_rendered:
                errors.append(f"{label}:{claim_id} 命中 forbidden phrasing: {forbidden}")
        allowed_views = claim.get("allowed_views")
        if isinstance(allowed_views, list) and view_name not in allowed_views:
            errors.append(f"{label}:{claim_id} 不允许出现在 {view_name} 视图")
        if claim.get("publishability") in {"internal_only", "blocked"}:
            errors.append(f"{label}:{claim_id} 为 {claim['publishability']}，不得进入公开视图")
        if claim.get("status") in {"proposed", "unknown"}:
            errors.append(f"{label}:{claim_id} 为 {claim['status']}，不得进入公开视图")

    for claim_id, claim in claims.items():
        policy = claim.get("view_policy", {})
        if not isinstance(policy, dict):
            policy = {}
        expected = policy.get(view_name)
        if expected == "required" and claim_id not in seen:
            errors.append(f"{label}:{claim_id} 是 required，但未出现在 view_manifest")
        if expected == "forbidden" and claim_id in seen and not seen[claim_id].get("omitted", False):
            errors.append(f"{label}:{claim_id} 是 forbidden，但被引用")
    return errors


def compare_views(
    view_paths: Iterable[Path], canonical: Dict[str, Dict[str, Any]]
) -> List[str]:
    loaded: List[Tuple[str, Dict[str, Dict[str, Any]]]] = [
        ("<canonical>", canonical)
    ]
    errors: List[str] = []
    for path in view_paths:
        try:
            data = load_json(path)
            view_claims = claim_map(data) if "claims" in data else {}
            extra_claims = sorted(set(view_claims) - set(canonical))
            for claim_id in extra_claims:
                errors.append(f"{path}: view-only claim 不在 canonical manifest: {claim_id}")
            loaded.append((str(path), view_claims))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: 无法读取视图 claims: {exc}")
    fields = (
        "canonical_fact",
        "status",
        "publishability",
        "scope",
        "ownership",
        "metric",
        "forbidden_phrasing",
    )
    for index, (left_path, left) in enumerate(loaded):
        for right_path, right in loaded[index + 1 :]:
            for claim_id in sorted(set(left) & set(right)):
                for field in fields:
                    if normalized(left[claim_id].get(field)) != normalized(right[claim_id].get(field)):
                        errors.append(
                            f"视图事实漂移 {claim_id}.{field}: {Path(left_path).name} != {Path(right_path).name}"
                        )
    return errors


def read_artifact(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise ValueError("PDF 文本校验需要 pypdf，或先传入 PDF 的纯文本提取文件") from exc
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return path.read_text(encoding="utf-8", errors="ignore")


def validate_artifacts(
    view_items: List[Tuple[Path, Dict[str, Any]]], artifact_paths: Iterable[Path]
) -> List[str]:
    artifacts = list(artifact_paths)
    if not artifacts:
        return []
    if not view_items:
        return ["--artifacts 需要至少一个 --views 文件"]
    if len(view_items) == 1:
        pairs = [(view_items[0], artifact) for artifact in artifacts]
    elif len(view_items) == len(artifacts):
        pairs = list(zip(view_items, artifacts))
    else:
        return ["多视图 artifact 校验要求 --artifacts 与 --views 数量一致，且顺序对应"]

    errors: List[str] = []
    for (view_path, view_data), artifact_path in pairs:
        try:
            artifact_text = normalized_text(read_artifact(artifact_path))
        except (OSError, ValueError) as exc:
            errors.append(f"{artifact_path}: 无法提取最终文本: {exc}")
            continue
        _, refs = view_refs(view_data)
        for ref in refs:
            if ref.get("omitted") or ref.get("profile_claim") is True:
                continue
            rendered = str(ref.get("text", ""))
            if rendered and normalized_text(rendered) not in artifact_text:
                errors.append(
                    f"{artifact_path}: 缺少 {ref.get('claim_id', 'profile_claim')} 的 rendered_text"
                )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path, help="canonical claims JSON")
    parser.add_argument(
        "--views",
        nargs="*",
        type=Path,
        default=[],
        help="optional derived view JSON files; each may include claims and view_manifest",
    )
    parser.add_argument(
        "--artifacts",
        nargs="*",
        type=Path,
        default=[],
        help="final Markdown/TXT/PDF text artifacts; order corresponds to --views",
    )
    args = parser.parse_args()

    errors: List[str] = []
    loaded_views: List[Tuple[Path, Dict[str, Any]]] = []
    try:
        manifest = load_json(args.manifest)
        claims = claim_map(manifest)
        errors.extend(validate_claims(claims, args.manifest.name))
        errors.extend(validate_view(manifest, args.manifest.name, claims))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"{args.manifest}: 无法读取 canonical manifest: {exc}")
        claims = {}

    for path in args.views:
        try:
            data = load_json(path)
            view_claims = claim_map(data) if "claims" in data else {}
            errors.extend(validate_claims(view_claims, path.name))
            extra_claims = sorted(set(view_claims) - set(claims))
            for claim_id in extra_claims:
                errors.append(f"{path}: view-only claim 不在 canonical manifest: {claim_id}")
            errors.extend(validate_view(data, path.name, claims, require_manifest=True))
            loaded_views.append((path, data))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: 无法读取视图 manifest: {exc}")
    if args.views:
        errors.extend(compare_views(args.views, claims))
    errors.extend(validate_artifacts(loaded_views, args.artifacts))

    if errors:
        print(f"FAIL: {len(errors)} 个问题")
        for error in errors:
            print(f"- {error}")
        return 1
    print("OK: claim provenance、发布权限和视图事实一致性检查通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
