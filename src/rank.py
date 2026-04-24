"""
kwmaster v7 - 第三步：分档输出（程序，不调 AI）

输入:
  workspace/cache/scored.csv     (score.py collect 产物)

输出:
  workspace/output/P0_priority.csv
  workspace/output/P1_priority.csv
  workspace/output/P2_priority.csv
  workspace/output/EXCLUDED.csv

规则见 PRD 第 8 章。
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

# ---------- 评分映射 ----------
W_USER_OVERLAP = 0.40
W_KD = 0.25
W_SEARCH_VOLUME = 0.25
W_INTENT = 0.10

P0_THRESHOLD = 0.75
P1_THRESHOLD = 0.55
P2_THRESHOLD = 0.35

# 强制 P0 规则：核心定位词哪怕被 KD/vol 压档也必须 P0
# user_overlap >= 0.9 AND search_volume >= 1000 AND 非双判 OOT
FORCE_P0_USER_OVERLAP = 0.9
FORCE_P0_MIN_VOLUME = 1000

# TRENDING 输出规则（横切，不影响 4 档）
TRENDING_MIN_VOLUME = 50  # 当前搜索量门槛，避免小样本噪音

INTENT_SCORES = {
    "transactional": 1.0,
    "commercial": 0.9,
    "navigational": 0.7,
    "informational": 0.5,
}


def kd_score(kd) -> float:
    """KD 越低越好。空值按最难处理（最低分）。"""
    if pd.isna(kd):
        return 0.1
    if kd < 20:
        return 1.0
    if kd < 40:
        return 0.7
    if kd < 60:
        return 0.4
    return 0.1


def sv_score(sv) -> float | None:
    """搜索量分值。<100 返回 None 表示直接排除。"""
    if pd.isna(sv):
        return None
    if sv < 100:
        return None
    if sv < 1000:
        return 0.4
    if sv <= 10000:
        return 0.7
    return 1.0


def intent_score(intent) -> float:
    if not isinstance(intent, str):
        return 0.5
    return INTENT_SCORES.get(intent.lower().strip(), 0.5)


# ---------- 主流程 ----------
def run(workspace: Path) -> dict[str, Path]:
    scored_path = workspace / "cache" / "scored.csv"
    if not scored_path.exists():
        raise FileNotFoundError(f"missing {scored_path}, run score.py collect first")

    df = pd.read_csv(scored_path)
    print(f"[rank] loaded {len(df)} scored clusters")

    # 合入趋势字段（从 clusters.csv，scored.csv 不含）
    clusters_path = workspace / "cache" / "clusters.csv"
    if clusters_path.exists():
        cdf = pd.read_csv(clusters_path)
        trend_cols = [c for c in ["yoy_pct", "slope_3mo_norm", "trend_label"] if c in cdf.columns]
        if trend_cols:
            df = df.merge(
                cdf[["cluster_id"] + trend_cols], on="cluster_id", how="left"
            )
            print(f"[rank] merged trend columns: {trend_cols}")
    if "trend_label" not in df.columns:
        df["trend_label"] = "none"

    # 计算各维度分值
    df["_kd_s"] = df["kd"].apply(kd_score)
    df["_sv_s"] = df["search_volume"].apply(sv_score)
    df["_intent_s"] = df["intent"].apply(intent_score)
    df["_uo"] = pd.to_numeric(df["user_overlap"], errors="coerce")

    # final_score
    def calc_score(r) -> float | None:
        if pd.isna(r["_uo"]) or r["_sv_s"] is None:
            return None
        return (
            r["_uo"] * W_USER_OVERLAP
            + r["_kd_s"] * W_KD
            + r["_sv_s"] * W_SEARCH_VOLUME
            + r["_intent_s"] * W_INTENT
        )

    df["final_score"] = df.apply(calc_score, axis=1)

    # OOT 双判
    df["ai_is_oot"] = df["ai_is_oot"].fillna(False).astype(bool) if "ai_is_oot" in df.columns else False
    df["_double_oot"] = (df["industry_node"] == "OOT") & df["ai_is_oot"]

    # 排除原因
    def bucket(r) -> str:
        if r["_sv_s"] is None:
            return "EXCLUDED"  # 搜索量 < 100 或缺失
        if pd.isna(r["_uo"]):
            return "EXCLUDED"  # AI 评分失败
        if r["_double_oot"]:
            return "EXCLUDED"  # 双判 OOT
        s = r["final_score"]
        if s is None:
            return "EXCLUDED"
        # 强制 P0：核心定位词（高 user_overlap + 有量 + 非 OOT）
        if (
            r["_uo"] >= FORCE_P0_USER_OVERLAP
            and pd.notna(r["search_volume"])
            and r["search_volume"] >= FORCE_P0_MIN_VOLUME
        ):
            return "P0"
        if s >= P0_THRESHOLD:
            return "P0"
        if s >= P1_THRESHOLD:
            return "P1"
        if s >= P2_THRESHOLD:
            return "P2"
        return "EXCLUDED"  # final_score < 0.35

    def excluded_reason(r) -> str:
        if r["_sv_s"] is None:
            sv = r["search_volume"]
            return f"search_volume<100 ({int(sv) if pd.notna(sv) else 'NA'})"
        if pd.isna(r["_uo"]):
            return "AI scoring failed (null user_overlap)"
        if r["_double_oot"]:
            return "OOT double-judged (industry_node=OOT AND ai_is_oot=true)"
        if r["final_score"] is None or r["final_score"] < P2_THRESHOLD:
            return f"final_score<{P2_THRESHOLD}"
        return ""

    df["bucket"] = df.apply(bucket, axis=1)
    df["excluded_reason"] = df.apply(
        lambda r: excluded_reason(r) if r["bucket"] == "EXCLUDED" else "", axis=1
    )

    # 输出列：保留 PRD 要求的字段 + 关键打分明细
    keep_cols = [
        "cluster_id",
        "main_keyword",
        "cluster_keywords",
        "cluster_size",
        "search_volume",
        "search_volume_sum",
        "kd",
        "competition",
        "competition_level",
        "cpc",
        "main_intent_dataforseo",
        "intent",
        "user_overlap",
        "industry_node",
        "competitor_brand",
        "ai_is_oot",
        "is_competitor",
        "competitor_count",
        "competitor_domains",
        "competitor_urls",
        "competitor_best_position",
        "suggested_page_hint",
        "final_score",
        "yoy_pct",
        "slope_3mo_norm",
        "trend_label",
        "ai_reason",
        "excluded_reason",
    ]
    keep_cols = [c for c in keep_cols if c in df.columns]
    out_df = df[keep_cols + ["bucket"]].copy()

    output_dir = workspace / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    out_paths: dict[str, Path] = {}

    counts = {}
    for tag in ["P0", "P1", "P2", "EXCLUDED"]:
        sub = out_df[out_df["bucket"] == tag].drop(columns=["bucket"])
        # 排序：P0/P1/P2 按 final_score 降序；EXCLUDED 按搜索量降序
        if tag == "EXCLUDED":
            sub = sub.sort_values("search_volume", ascending=False, na_position="last")
        else:
            sub = sub.sort_values("final_score", ascending=False)
        if tag == "EXCLUDED":
            fname = "EXCLUDED.csv"
        else:
            fname = f"{tag}_priority.csv"
        path = output_dir / fname
        sub.to_csv(path, index=False)
        out_paths[tag] = path
        counts[tag] = len(sub)

    # ---------- TRENDING（横切输出，不影响 4 档守恒断言） ----------
    trending_df = out_df.copy()
    # 筛选规则:
    # 1. trend_label in {rising, declining}（label_trend 已做过 OOT-无关的判断，此处再过 OOT）
    # 2. 当前 search_volume >= TRENDING_MIN_VOLUME
    # 3. 非双判 OOT（OOT 词再涨也不看）
    trending_df = trending_df.merge(df[["cluster_id", "_double_oot"]], on="cluster_id", how="left")
    trending_mask = (
        trending_df["trend_label"].isin(["rising", "declining"])
        & (pd.to_numeric(trending_df["search_volume"], errors="coerce") >= TRENDING_MIN_VOLUME)
        & (~trending_df["_double_oot"].fillna(False).astype(bool))
    )
    trending_out = trending_df[trending_mask].drop(columns=["_double_oot"]).copy()
    # 排序：先 rising 后 declining；rising 按 yoy_pct 降序，declining 按 yoy_pct 升序（最跌在前）
    trending_out["_trend_order"] = trending_out["trend_label"].map({"rising": 0, "declining": 1})
    trending_out["_yoy_sort"] = pd.to_numeric(trending_out["yoy_pct"], errors="coerce").fillna(0)
    rising = trending_out[trending_out["trend_label"] == "rising"].sort_values("_yoy_sort", ascending=False)
    decl = trending_out[trending_out["trend_label"] == "declining"].sort_values("_yoy_sort", ascending=True)
    trending_out = pd.concat([rising, decl], ignore_index=True).drop(columns=["_trend_order", "_yoy_sort"])
    trending_path = output_dir / "TRENDING.csv"
    trending_out.to_csv(trending_path, index=False)
    out_paths["TRENDING"] = trending_path
    n_rise = (trending_out["trend_label"] == "rising").sum()
    n_decl = (trending_out["trend_label"] == "declining").sum()
    print(f"[rank] TRENDING: {len(trending_out)} ({n_rise} rising, {n_decl} declining)")

    # ---------- 三条业务断言（PRD 第 8 章） ----------
    print("[rank] running self-check assertions")
    # 1. 唯一性
    bucket_counts_per_id = out_df.groupby("cluster_id")["bucket"].nunique()
    dup = bucket_counts_per_id[bucket_counts_per_id > 1]
    assert dup.empty, f"FAIL uniqueness: cluster_id appearing in multiple buckets: {dup.head().to_dict()}"

    # 2. OOT 守约：P0/P1 不允许双判 OOT
    p0p1 = out_df[out_df["bucket"].isin(["P0", "P1"])]
    oot_in_p0p1 = p0p1.merge(df[["cluster_id", "_double_oot"]], on="cluster_id")
    leak = oot_in_p0p1[oot_in_p0p1["_double_oot"]]
    assert leak.empty, f"FAIL OOT守约: {len(leak)} OOT clusters leaked into P0/P1"

    # 3. 总数守恒
    total_out = sum(counts.values())
    assert total_out == len(df), f"FAIL 守恒: out={total_out} vs in={len(df)}"

    print(f"[rank] OK  P0={counts['P0']}  P1={counts['P1']}  P2={counts['P2']}  EXCLUDED={counts['EXCLUDED']}  total={total_out}")
    for tag, p in out_paths.items():
        print(f"  {tag} -> {p}")
    return out_paths


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: rank.py <workspace_dir>", file=sys.stderr)
        sys.exit(2)
    run(Path(sys.argv[1]).expanduser().resolve())
