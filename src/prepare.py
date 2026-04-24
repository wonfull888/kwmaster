"""
kwmaster v7 - 第一步：数据准备（程序，不调 AI）

输入:
  workspace/input/core/*.csv         (DataForSEO related_keywords API 输出)
  workspace/input/competitor/*.csv   (DataForSEO ranked_keywords API 输出)
  workspace/config.json              (产品/用户/行业树/golden_samples)

输出:
  workspace/cache/clusters.csv       (去重 + 聚类 + 贴竞品/行业标签)

不调 AI，全程序。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Iterable

import pandas as pd

# ---------- 字段映射 ----------
# DataForSEO 列名超长，统一映射到短名
COL_KEYWORD = "keyword_data.keyword"
COL_SEARCH_VOLUME = "keyword_data.keyword_info.search_volume"
COL_COMPETITION = "keyword_data.keyword_info.competition"
COL_COMPETITION_LEVEL = "keyword_data.keyword_info.competition_level"
COL_CPC = "keyword_data.keyword_info.cpc"
COL_KD = "keyword_data.keyword_properties.keyword_difficulty"
COL_MAIN_INTENT = "keyword_data.search_intent_info.main_intent"
COL_MONTHLY_SEARCHES = "keyword_data.keyword_info.monthly_searches"
COL_TREND_YEARLY = "keyword_data.keyword_info.search_volume_trend.yearly"
# competitor 专属
COL_RANKED_DOMAIN = "ranked_serp_element.serp_item.domain"
COL_RANKED_URL = "ranked_serp_element.serp_item.url"
COL_RANKED_POSITION = "ranked_serp_element.serp_item.rank_absolute"


# ---------- 工具函数 ----------
def normalize_keyword(kw: str) -> str:
    """规范化：小写、去标点、压缩空格"""
    if not isinstance(kw, str):
        return ""
    s = kw.lower().strip()
    s = re.sub(r"[^\w\s\-]", " ", s)  # 留字母数字下划线和连字符
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def tokens(kw: str) -> set[str]:
    """切词成 token 集合（用于 Jaccard）"""
    return set(t for t in kw.split() if len(t) > 1)


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def edit_distance(a: str, b: str, cap: int = 4) -> int:
    """编辑距离，超过 cap 提前返回"""
    if abs(len(a) - len(b)) > cap:
        return cap + 1
    if a == b:
        return 0
    # 标准 DP
    m, n = len(a), len(b)
    if m == 0:
        return n
    if n == 0:
        return m
    prev = list(range(n + 1))
    for i in range(1, m + 1):
        cur = [i] + [0] * n
        row_min = cur[0]
        for j in range(1, n + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
            if cur[j] < row_min:
                row_min = cur[j]
        if row_min > cap:
            return cap + 1
        prev = cur
    return prev[n]


# ---------- 趋势计算 ----------
def parse_monthly_searches(raw) -> list[int]:
    """解析 monthly_searches JSON，返回最新月在前的 search_volume 列表。
    缺失 / 解析失败 / 长度不足 → 返回空列表（调用方应跳过）。
    """
    if not isinstance(raw, str) or not raw.strip():
        return []
    try:
        arr = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return []
    if not isinstance(arr, list) or not arr:
        return []
    # 按 (year, month) 倒序排（最新在前）
    try:
        arr_sorted = sorted(
            arr,
            key=lambda x: (x.get("year", 0), x.get("month", 0)),
            reverse=True,
        )
        return [int(x.get("search_volume") or 0) for x in arr_sorted]
    except (TypeError, ValueError):
        return []


def slope_3mo(volumes: list[int]) -> float | None:
    """最近 3 个月线性斜率 / 均值 = 月均增长率。
    返回 None 表示数据不足。
    例: [400, 200, 100] → 斜率 +150/月，均值 233 → +0.64 (月增 64%)
    """
    if len(volumes) < 3:
        return None
    recent = volumes[:3]  # [m_now, m-1, m-2]
    mean = sum(recent) / 3
    if mean <= 0:
        return None
    # x = [0,1,2] 对应 m-2, m-1, m_now（按时间正序）
    # y = recent[::-1]
    y = recent[::-1]
    n = 3
    x_mean = 1.0  # (0+1+2)/3
    num = sum((i - x_mean) * (y[i] - mean) for i in range(n))
    den = sum((i - x_mean) ** 2 for i in range(n))  # = 2.0
    slope_per_month = num / den if den else 0.0
    return slope_per_month / mean  # 归一化为月增长率


def label_trend(yoy_pct: float | None, slope_norm: float | None,
                yoy_thresh: float = 100.0,
                slope_thresh: float = 0.20) -> str:
    """根据 YoY 和归一化斜率打标签。
    rising: YoY ≥ +100% 或月增 ≥ +20%
    declining: YoY ≤ -50% 或月降 ≤ -20%
    flat: 其它
    none: 数据不足（两个都 None）
    """
    has_yoy = yoy_pct is not None
    has_slope = slope_norm is not None
    if not has_yoy and not has_slope:
        return "none"

    rising = (has_yoy and yoy_pct >= yoy_thresh) or (has_slope and slope_norm >= slope_thresh)
    declining = (has_yoy and yoy_pct <= -50.0) or (has_slope and slope_norm <= -slope_thresh)

    if rising and not declining:
        return "rising"
    if declining and not rising:
        return "declining"
    return "flat"


# ---------- 加载 + 字段对齐 ----------
def load_csvs(folder: Path, source_label: str) -> pd.DataFrame:
    """加载某个目录下所有 CSV，做字段对齐"""
    files = sorted(folder.glob("*.csv"))
    if not files:
        return pd.DataFrame()
    frames = []
    for f in files:
        df = pd.read_csv(f, low_memory=False)
        df["__source_file"] = f.name
        df["__source"] = source_label
        frames.append(df)
    out = pd.concat(frames, ignore_index=True)
    return out


def select_fields(df: pd.DataFrame, source: str) -> pd.DataFrame:
    """从原始 DataForSEO 列里挑出需要的字段，统一命名"""
    if df.empty:
        return df
    rec = pd.DataFrame()
    rec["keyword_raw"] = df.get(COL_KEYWORD, "")
    rec["search_volume"] = pd.to_numeric(df.get(COL_SEARCH_VOLUME), errors="coerce")
    rec["kd"] = pd.to_numeric(df.get(COL_KD), errors="coerce")
    rec["competition"] = pd.to_numeric(df.get(COL_COMPETITION), errors="coerce")
    rec["competition_level"] = df.get(COL_COMPETITION_LEVEL, "")
    rec["cpc"] = pd.to_numeric(df.get(COL_CPC), errors="coerce")
    rec["main_intent"] = df.get(COL_MAIN_INTENT, "")
    rec["monthly_searches_raw"] = df.get(COL_MONTHLY_SEARCHES, "").astype(str) if COL_MONTHLY_SEARCHES in df.columns else ""
    rec["yoy_pct"] = pd.to_numeric(df.get(COL_TREND_YEARLY), errors="coerce")
    rec["source"] = source
    rec["source_file"] = df["__source_file"].values
    if source == "competitor":
        rec["ranked_domain"] = df.get(COL_RANKED_DOMAIN, "")
        rec["ranked_url"] = df.get(COL_RANKED_URL, "")
        rec["ranked_position"] = pd.to_numeric(df.get(COL_RANKED_POSITION), errors="coerce")
    else:
        rec["ranked_domain"] = ""
        rec["ranked_url"] = ""
        rec["ranked_position"] = pd.NA
    return rec


# ---------- 去重 ----------
def dedupe(df: pd.DataFrame) -> pd.DataFrame:
    """完全相同的 keyword 合并:
    - search_volume / kd / competition / cpc 取 max
    - 其它字段 core 优先（source='core' 排前面后取 first）
    - competitor 信息保留为 list
    """
    if df.empty:
        return df
    df = df.copy()
    df["keyword"] = df["keyword_raw"].map(normalize_keyword)
    df = df[df["keyword"].str.len() > 0].copy()

    # 排序保证 core 在前
    df["__src_order"] = (df["source"] != "core").astype(int)
    df = df.sort_values(["keyword", "__src_order", "search_volume"], ascending=[True, True, False])

    def agg(g: pd.DataFrame) -> pd.Series:
        comp_rows = g[g["source"] == "competitor"]
        # 月度数据：优先 core 第一行，否则 competitor 第一行
        monthly_raw = ""
        for _, row in g.iterrows():
            v = row.get("monthly_searches_raw", "")
            if isinstance(v, str) and v.strip() and v.strip().lower() != "nan":
                monthly_raw = v
                break
        return pd.Series({
            "keyword": g["keyword"].iloc[0],
            "search_volume": g["search_volume"].max(skipna=True),
            "kd": g["kd"].max(skipna=True),
            "competition": g["competition"].max(skipna=True),
            "competition_level": g["competition_level"].dropna().astype(str).iloc[0] if g["competition_level"].notna().any() else "",
            "cpc": g["cpc"].max(skipna=True),
            "main_intent": g["main_intent"].dropna().astype(str).iloc[0] if g["main_intent"].notna().any() else "",
            "yoy_pct": g["yoy_pct"].dropna().iloc[0] if g["yoy_pct"].notna().any() else pd.NA,
            "monthly_searches_raw": monthly_raw,
            "is_competitor": len(comp_rows) > 0,
            "competitor_domains": ";".join(sorted(set(comp_rows["ranked_domain"].dropna().astype(str)))) if len(comp_rows) else "",
            "competitor_urls": ";".join(sorted(set(comp_rows["ranked_url"].dropna().astype(str)))) if len(comp_rows) else "",
            "competitor_best_position": int(comp_rows["ranked_position"].min()) if (len(comp_rows) and comp_rows["ranked_position"].notna().any()) else 0,
            "source_files": ";".join(sorted(set(g["source_file"].dropna().astype(str)))),
        })

    out = df.groupby("keyword", sort=False, group_keys=False).apply(agg).reset_index(drop=True)
    return out


# ---------- 聚类 ----------
def cluster_keywords(df: pd.DataFrame, jaccard_thresh: float = 0.6, edit_cap: int = 3) -> pd.DataFrame:
    """聚类:
    两词同 cluster 的条件 (任一满足):
      - token Jaccard >= jaccard_thresh
      - 编辑距离 <= edit_cap (短词容易满足)

    实现: 按搜索量倒序遍历, 已分配的跳过, 未分配的开新 cluster, 然后扫剩余词找近邻。
    复杂度 O(n^2) — 1200 词以内秒级, 上万行以下能接受。
    """
    if df.empty:
        df["cluster_id"] = []
        return df
    df = df.copy()
    df["search_volume_filled"] = df["search_volume"].fillna(0)
    df = df.sort_values("search_volume_filled", ascending=False).reset_index(drop=True)
    df["cluster_id"] = -1

    keywords = df["keyword"].tolist()
    token_sets = [tokens(k) for k in keywords]
    cluster_id = 0
    assigned = df["cluster_id"].values

    for i in range(len(df)):
        if assigned[i] != -1:
            continue
        assigned[i] = cluster_id
        ti = token_sets[i]
        ki = keywords[i]
        for j in range(i + 1, len(df)):
            if assigned[j] != -1:
                continue
            tj = token_sets[j]
            kj = keywords[j]
            # 先 Jaccard, 不够再编辑距离
            if jaccard(ti, tj) >= jaccard_thresh:
                assigned[j] = cluster_id
                continue
            # 编辑距离只对短词有效（避免长词偶然相似）
            if max(len(ki), len(kj)) <= 25 and edit_distance(ki, kj, cap=edit_cap) <= edit_cap:
                assigned[j] = cluster_id
        cluster_id += 1

    df["cluster_id"] = assigned
    return df


def aggregate_clusters(df: pd.DataFrame) -> pd.DataFrame:
    """每个 cluster 聚合成一行:
    - main_keyword: cluster 内搜索量最高的词
    - cluster_keywords: cluster 内所有词分号分隔
    - search_volume: 取 max（代表 cluster 的整体潜力）
    - kd / competition / cpc: 取 main_keyword 的值
    - is_competitor: cluster 内有任一词是竞品则为 true
    """
    if df.empty:
        return pd.DataFrame()
    df = df.copy()
    df = df.sort_values(["cluster_id", "search_volume_filled"], ascending=[True, False])

    def agg(g: pd.DataFrame) -> pd.Series:
        head = g.iloc[0]
        comp_rows = g[g["is_competitor"]]
        # 趋势：用 main_keyword (head) 的数据
        yoy = head.get("yoy_pct")
        yoy_val = float(yoy) if pd.notna(yoy) else None
        volumes = parse_monthly_searches(head.get("monthly_searches_raw", ""))
        slope = slope_3mo(volumes)
        trend = label_trend(yoy_val, slope)
        return pd.Series({
            "cluster_id": int(head["cluster_id"]),
            "main_keyword": head["keyword"],
            "cluster_keywords": ";".join(g["keyword"].tolist()),
            "cluster_size": len(g),
            "search_volume": int(g["search_volume_filled"].max()),
            "search_volume_sum": int(g["search_volume_filled"].sum()),
            "kd": float(head["kd"]) if pd.notna(head["kd"]) else None,
            "competition": float(head["competition"]) if pd.notna(head["competition"]) else None,
            "competition_level": head["competition_level"],
            "cpc": float(head["cpc"]) if pd.notna(head["cpc"]) else None,
            "main_intent_dataforseo": head["main_intent"],
            "yoy_pct": yoy_val if yoy_val is not None else pd.NA,
            "slope_3mo_norm": round(slope, 4) if slope is not None else pd.NA,
            "trend_label": trend,
            "is_competitor": bool(comp_rows.shape[0] > 0),
            "competitor_count": int(comp_rows.shape[0]),
            "competitor_domains": ";".join(sorted(set(d for d in ";".join(comp_rows["competitor_domains"].astype(str)).split(";") if d))),
            "competitor_urls": ";".join(sorted(set(u for u in ";".join(comp_rows["competitor_urls"].astype(str)).split(";") if u))),
            "competitor_best_position": int(comp_rows["competitor_best_position"].replace(0, pd.NA).min()) if (comp_rows.shape[0] and comp_rows["competitor_best_position"].replace(0, pd.NA).notna().any()) else 0,
        })

    return df.groupby("cluster_id", sort=True, group_keys=False).apply(agg).reset_index(drop=True)


# ---------- 行业节点匹配 ----------
def collect_node_keywords(industry_tree: dict) -> list[tuple[str, str]]:
    """从 industry_tree 抽出 (节点路径, 匹配关键词) 列表

    industry_tree 结构:
      { "SEO": { "Keyword Research Tools": ["Keyword Planner", ...], ... }, ... }

    匹配关键词来源:
      - 叶子节点名 (如 "Keyword Planner")
      - 二级节点名 (如 "Keyword Research Tools")
      - 一级节点名 (如 "SEO")
    """
    nodes: list[tuple[str, str]] = []
    for top, sub_dict in industry_tree.items():
        if not isinstance(sub_dict, dict):
            continue
        for sub, leaves in sub_dict.items():
            path = f"{top} > {sub}"
            # 叶子优先（最具体）
            if isinstance(leaves, list):
                for leaf in leaves:
                    nodes.append((f"{path} > {leaf}", normalize_keyword(leaf)))
            # 二级节点本身
            nodes.append((path, normalize_keyword(sub)))
        # 一级节点本身（最宽泛）
        nodes.append((top, normalize_keyword(top)))
    return nodes


def match_competitor_brand(keyword: str, cluster_keywords: str, brands: list[str]) -> str:
    """命中任一竞品品牌词 → 返回品牌名；不命中返回空串。

    匹配规则:
      - 含空格/点的品牌（如 "copy.ai"、"copy ai"）→ 子串匹配
      - 单词品牌（如 "jasper"）→ 整词匹配，避免误伤（"jasperware" 不算）
    """
    haystack = (keyword + " " + cluster_keywords.replace(";", " ")).lower()
    haystack_tokens = set(haystack.split())
    for brand in brands:
        b = brand.lower().strip()
        if not b:
            continue
        if " " in b or "." in b:
            if b in haystack:
                return brand
        else:
            if b in haystack_tokens:
                return brand
    return ""


def match_industry_node(keyword: str, cluster_keywords: str, nodes: list[tuple[str, str]]) -> str:
    """关键词匹配: 看 main_keyword 或 cluster 内任一词是否包含节点名

    匹配优先级: 叶子 > 二级 > 一级。collect_node_keywords 已按这个顺序追加，遍历时第一个匹配即返回。
    全部不命中返回 'OOT'。
    """
    haystack = (keyword + " " + cluster_keywords.replace(";", " ")).lower()
    haystack_tokens = set(haystack.split())
    for path, needle in nodes:
        if not needle:
            continue
        # 词组匹配 (子串)
        if " " in needle:
            if needle in haystack:
                return path
        else:
            # 单词匹配 (整词)
            if needle in haystack_tokens:
                return path
    return "OOT"


# ---------- 主流程 ----------
def run(workspace: Path) -> Path:
    config_path = workspace / "config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"config.json not found at {config_path}")
    config = json.loads(config_path.read_text(encoding="utf-8"))

    industry_tree = config.get("industry_tree", {})
    if not industry_tree:
        raise ValueError("config.json missing 'industry_tree'")

    core_dir = workspace / "input" / "core"
    comp_dir = workspace / "input" / "competitor"
    if not core_dir.exists():
        raise FileNotFoundError(f"missing {core_dir}")

    print(f"[prepare] loading core/  from {core_dir}")
    core_raw = load_csvs(core_dir, "core")
    print(f"  core rows: {len(core_raw)}")

    print(f"[prepare] loading competitor/ from {comp_dir}")
    comp_raw = load_csvs(comp_dir, "competitor") if comp_dir.exists() else pd.DataFrame()
    print(f"  competitor rows: {len(comp_raw)}")

    core = select_fields(core_raw, "core")
    comp = select_fields(comp_raw, "competitor")
    merged = pd.concat([core, comp], ignore_index=True)
    print(f"[prepare] merged rows: {len(merged)}")

    print("[prepare] dedupe + normalize")
    deduped = dedupe(merged)
    print(f"  unique keywords: {len(deduped)}")

    print("[prepare] clustering (jaccard>=0.6 or edit<=3)")
    clustered = cluster_keywords(deduped)
    print(f"  cluster_id range: 0..{clustered['cluster_id'].max()}")

    print("[prepare] aggregating clusters")
    clusters = aggregate_clusters(clustered)
    print(f"  cluster count: {len(clusters)}")

    print("[prepare] tagging industry nodes + competitor brands")
    nodes = collect_node_keywords(industry_tree)
    brands = config.get("competitor_brands", [])
    print(f"  industry node patterns: {len(nodes)}")
    print(f"  competitor brand patterns: {len(brands)}")

    def tag_row(r):
        brand = match_competitor_brand(r["main_keyword"], r["cluster_keywords"], brands)
        if brand:
            return pd.Series({"industry_node": "Competitor", "competitor_brand": brand})
        node = match_industry_node(r["main_keyword"], r["cluster_keywords"], nodes)
        return pd.Series({"industry_node": node, "competitor_brand": ""})

    tags = clusters.apply(tag_row, axis=1)
    clusters["industry_node"] = tags["industry_node"]
    clusters["competitor_brand"] = tags["competitor_brand"]

    oot_count = (clusters["industry_node"] == "OOT").sum()
    comp_brand_count = (clusters["industry_node"] == "Competitor").sum()
    in_tree_count = len(clusters) - oot_count - comp_brand_count
    print(f"  in-tree clusters:    {in_tree_count} ({in_tree_count/len(clusters)*100:.1f}%)")
    print(f"  competitor clusters: {comp_brand_count} ({comp_brand_count/len(clusters)*100:.1f}%)")
    print(f"  OOT clusters:        {oot_count} ({oot_count/len(clusters)*100:.1f}%)")
    print(f"  competitor-source clusters (from competitor CSV): {clusters['is_competitor'].sum()}")

    # 趋势分布
    trend_counts = clusters["trend_label"].value_counts().to_dict()
    print(f"[prepare] trend distribution: {trend_counts}")

    cache_dir = workspace / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    out_path = cache_dir / "clusters.csv"
    clusters.to_csv(out_path, index=False)
    print(f"[prepare] wrote {out_path} ({len(clusters)} clusters)")
    return out_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: prepare.py <workspace_dir>", file=sys.stderr)
        sys.exit(2)
    run(Path(sys.argv[1]).expanduser().resolve())
