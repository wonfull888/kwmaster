"""
kwmaster v7 - 第二步：AI 评分（Skill orchestration 模式）

不调外部 API。只负责：
  1. prompts: 把 cluster 分批，每批生成一个 prompt 文件给 host Claude 看
  2. collect: 读 host Claude 写的答案文件，合并成 scored.csv

输入:
  workspace/cache/clusters.csv     (prepare.py 产物)
  workspace/config.json            (product / target_user / industry_tree / golden_samples)

中间产物:
  workspace/cache/score_prompts/batch_NNNN.md     (prompts 子命令产出)
  workspace/cache/score_answers/batch_NNNN.json   (host Claude 手动产出)

输出:
  workspace/cache/scored.csv       (collect 子命令产出)

环境变量:
  KWMASTER_BATCH  可选，默认 100

用法:
  python score.py prompts <workspace>       # 第 1 步：落 prompt
  python score.py collect <workspace>       # 第 2 步：读答案合并
  python score.py status  <workspace>       # 看进度（哪些 batch 已答）
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

DEFAULT_BATCH = 100


# ---------- prompt 模板 ----------
SYSTEM_INSTRUCTIONS = """You are a senior SEO strategist. For each keyword cluster below, judge:

1. user_overlap (0.0-1.0): how much the searchers overlap with the product's target users
   - >= 0.7  searchers ARE the target users, keyword strongly relates to product
   - 0.3-0.7 searchers PARTIALLY overlap, keyword indirectly related
   - < 0.3   searchers are NOT target users, basically unrelated

2. intent: one of [informational, commercial, transactional, navigational]

3. suggested_page_hint: one of [article, product, category, landing, comparison, tool]

4. is_oot (true/false): true ONLY if keyword has NOTHING to do with the product's industry.
   Be liberal — if there is any indirect connection to the product's industry, mark false.

5. ai_reason: ONE short sentence explaining the user_overlap score.

Calibrate your scale against `golden_samples`.
"""


OUTPUT_INSTRUCTIONS = """Write your answer as a single JSON object to:
  {answer_path}

Schema:
{{
  "results": [
    {{
      "cluster_id": <int>,
      "user_overlap": <float 0-1>,
      "intent": "<informational|commercial|transactional|navigational>",
      "suggested_page_hint": "<article|product|category|landing|comparison|tool>",
      "is_oot": <true|false>,
      "ai_reason": "<one sentence>"
    }},
    ...
  ]
}}

One entry per cluster, same order as `clusters_to_score`. No markdown fences, no commentary.
"""


def _safe_str(v, default: str = "") -> str:
    """把 NaN/None/非字符串安全转为字符串。"""
    if v is None:
        return default
    if isinstance(v, float) and v != v:  # NaN
        return default
    s = str(v).strip()
    return s if s else default


def _safe_bool(v) -> bool:
    """把 NaN/None 安全转为 bool。"""
    if v is None:
        return False
    if isinstance(v, float) and v != v:  # NaN
        return False
    return bool(v)


def build_prompt(config: dict, batch: list[dict], answer_path: Path) -> str:
    """生成单批 prompt 的 markdown 文件内容。"""
    payload = {
        "product": config.get("product", ""),
        "target_user": config.get("target_user", {}),
        "industry_tree": config.get("industry_tree", {}),
        "golden_samples": config.get("golden_samples", []),
        "clusters_to_score": [
            {
                "cluster_id": int(c["cluster_id"]),
                "main_keyword": _safe_str(c.get("main_keyword")),
                "cluster_keywords": _safe_str(c.get("cluster_keywords")),
                "industry_node": _safe_str(c.get("industry_node"), "OOT"),
                "is_competitor": _safe_bool(c.get("is_competitor")),
                "competitor_brand": _safe_str(c.get("competitor_brand")),
            }
            for c in batch
        ],
    }

    return (
        "# kwmaster v7 — score batch\n\n"
        "## Instructions\n\n"
        + SYSTEM_INSTRUCTIONS
        + "\n## Output\n\n"
        + OUTPUT_INSTRUCTIONS.format(answer_path=str(answer_path))
        + "\n## Payload\n\n```json\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
        + "\n```\n"
    )


# ---------- 子命令: prompts ----------
def cmd_prompts(workspace: Path, batch_size: int) -> None:
    config = json.loads((workspace / "config.json").read_text(encoding="utf-8"))
    clusters_path = workspace / "cache" / "clusters.csv"
    if not clusters_path.exists():
        raise FileNotFoundError(f"missing {clusters_path}, run prepare.py first")

    clusters = pd.read_csv(clusters_path)
    records = clusters.to_dict(orient="records")
    batches = [records[i:i + batch_size] for i in range(0, len(records), batch_size)]

    prompt_dir = workspace / "cache" / "score_prompts"
    answer_dir = workspace / "cache" / "score_answers"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    answer_dir.mkdir(parents=True, exist_ok=True)

    for idx, batch in enumerate(batches):
        prompt_path = prompt_dir / f"batch_{idx:04d}.md"
        answer_path = answer_dir / f"batch_{idx:04d}.json"
        content = build_prompt(config, batch, answer_path)
        prompt_path.write_text(content, encoding="utf-8")

    print(f"[score:prompts] wrote {len(batches)} prompt files to {prompt_dir}")
    print(f"[score:prompts] host Claude should write answers to {answer_dir}/batch_NNNN.json")
    print(f"[score:prompts] then run: python score.py collect {workspace}")


# ---------- 子命令: status ----------
def cmd_status(workspace: Path) -> None:
    prompt_dir = workspace / "cache" / "score_prompts"
    answer_dir = workspace / "cache" / "score_answers"
    if not prompt_dir.exists():
        print("[score:status] no prompts yet")
        return
    prompts = sorted(prompt_dir.glob("batch_*.md"))
    answers = sorted(answer_dir.glob("batch_*.json")) if answer_dir.exists() else []
    answered_idx = {p.stem for p in answers}
    pending = [p.stem for p in prompts if p.stem not in answered_idx]
    print(f"[score:status] prompts: {len(prompts)}  answered: {len(answers)}  pending: {len(pending)}")
    if pending:
        print("  pending batches:")
        for s in pending[:20]:
            print(f"    {s}")
        if len(pending) > 20:
            print(f"    ... and {len(pending) - 20} more")


# ---------- 子命令: collect ----------
def cmd_collect(workspace: Path) -> Path:
    clusters = pd.read_csv(workspace / "cache" / "clusters.csv")
    answer_dir = workspace / "cache" / "score_answers"
    if not answer_dir.exists():
        raise FileNotFoundError(f"missing {answer_dir}")

    answer_files = sorted(answer_dir.glob("batch_*.json"))
    print(f"[score:collect] found {len(answer_files)} answer files")

    flat = []
    for f in answer_files:
        try:
            obj = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"  [warn] {f.name}: bad JSON ({e}), skipping", file=sys.stderr)
            continue
        if isinstance(obj, list):
            results = obj
        else:
            results = obj.get("results") or obj.get("scores") or []
        for r in results:
            try:
                cid = int(r["cluster_id"])
            except (KeyError, ValueError, TypeError):
                continue
            uo = r.get("user_overlap")
            try:
                uo = float(uo) if uo is not None else None
                if uo is not None:
                    uo = max(0.0, min(1.0, uo))
            except (ValueError, TypeError):
                uo = None
            flat.append({
                "cluster_id": cid,
                "user_overlap": uo,
                "intent": str(r.get("intent", "")).lower().strip(),
                "suggested_page_hint": str(r.get("suggested_page_hint", "")).lower().strip(),
                "ai_is_oot": bool(r.get("is_oot", False)),
                "ai_reason": str(r.get("ai_reason", "")).strip(),
            })

    if not flat:
        raise RuntimeError("no valid scored rows collected")

    scored_df = pd.DataFrame(flat).drop_duplicates(subset=["cluster_id"], keep="last")
    merged = clusters.merge(scored_df, on="cluster_id", how="left")

    # 缺失的 cluster 标 null（没答上的视为失败）
    missing = merged["user_overlap"].isna().sum()
    out_path = workspace / "cache" / "scored.csv"
    merged.to_csv(out_path, index=False)

    ai_oot = merged["ai_is_oot"].fillna(False).astype(bool).sum()
    print(f"[score:collect] wrote {out_path}")
    print(f"  total clusters: {len(merged)}")
    print(f"  scored:         {len(merged) - missing}")
    print(f"  missing/null:   {missing}")
    print(f"  AI says OOT:    {ai_oot}")
    return out_path


# ---------- 入口 ----------
USAGE = "Usage: score.py {prompts|collect|status} <workspace_dir>"


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(USAGE, file=sys.stderr)
        return 2
    cmd = argv[1]
    workspace = Path(argv[2]).expanduser().resolve()
    batch_size = int(__import__("os").environ.get("KWMASTER_BATCH", DEFAULT_BATCH))

    if cmd == "prompts":
        cmd_prompts(workspace, batch_size)
    elif cmd == "collect":
        cmd_collect(workspace)
    elif cmd == "status":
        cmd_status(workspace)
    else:
        print(USAGE, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
