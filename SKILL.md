---
name: kwmaster
description: Keyword planning master for SEO + GEO. Use when the user provides a website + DataForSEO keyword CSVs (core + competitor) and wants a prioritized P0/P1/P2/EXCLUDED page-layout plan. Runs a 3-step pipeline (prepare → AI score → rank) and outputs 4 priority CSVs + 1 横切 TRENDING CSV.
---

# kwmaster v7

输入产品上下文 + 一堆 DataForSEO 关键词 CSV，输出 4 个分档 CSV（P0 立刻做 / P1 排队做 / P2 内容补充 / EXCLUDED 不做）+ 1 个横切 TRENDING CSV（rising / declining 信号）。

整个 skill 只在第二步调一次 AI（就是你，host Claude）。第一步、第三步都是程序。

## 何时使用

用户提供：
1. 一个 workspace 目录，含 `config.json`、`input/core/*.csv`、`input/competitor/*.csv`
2. 想要"按页面优先级排好序的关键词列表"
3. 关键词来自 DataForSEO（related_keywords API + ranked_keywords API）

## 工作目录约定

```
<workspace>/
  config.json                      产品 + 用户 + 行业树 + competitor_brands + golden_samples
  input/
    core/*.csv                     DataForSEO related_keywords 输出
    competitor/*.csv               DataForSEO ranked_keywords 输出
  cache/
    clusters.csv                   prepare 产物
    score_prompts/batch_NNNN.md    score prompts 产物
    score_answers/batch_NNNN.json  你（host Claude）写的答案
    scored.csv                     score collect 产物
  output/
    P0_priority.csv
    P1_priority.csv
    P2_priority.csv
    EXCLUDED.csv
    TRENDING.csv                   横切表（rising/declining 信号）
```

## 三步流程

### 第一步：数据准备（程序）

```
python src/main.py prepare <workspace>
```

跑完产出 `cache/clusters.csv`：去重 + 聚类 + 贴 industry_node 和 competitor_brand 标签 + 算 trend 三列（yoy_pct / slope_3mo_norm / trend_label，从 DataForSEO `search_volume_trend.yearly` 与 `monthly_searches` 直接计算）。

### 第二步：AI 评分（你来做）

#### 2a. 生成 prompts

```
python src/main.py prompts <workspace>
```

跑完产出 9 个左右的 `cache/score_prompts/batch_NNNN.md`，每个含 100 个 cluster。

#### 2b. 你（host Claude）逐批回答

**对每个 batch_NNNN.md 文件，做以下事**：

1. 用 Read 工具读取 `cache/score_prompts/batch_NNNN.md`
2. 文件里包含完整的 instructions、payload、和**输出路径**（写在 `## Output` 段）
3. 严格按 schema 给每个 cluster 评分：
   - `user_overlap` (0.0-1.0)
   - `intent`: informational / commercial / transactional / navigational
   - `suggested_page_hint`: article / product / category / landing / comparison / tool
   - `is_oot`: true / false
   - `ai_reason`: 一句话
4. 用 Write 工具把答案写到 `cache/score_answers/batch_NNNN.json`，格式：
   ```json
   {"results": [{"cluster_id": 0, "user_overlap": 0.9, "intent": "commercial", "suggested_page_hint": "comparison", "is_oot": false, "ai_reason": "..."}, ...]}
   ```
5. **不要 markdown 代码块包裹，不要解释，纯 JSON**

**评分标准（必读）**：
- `user_overlap >= 0.7`：搜索者就是 target_user，词跟产品强相关
- `0.3 <= user_overlap < 0.7`：搜索者部分重合，词间接相关
- `user_overlap < 0.3`：搜索者不是 target_user，基本无关
- `is_oot = true` 只在词跟产品行业**完全无关**时才用。有任何间接关联 → false。
- 用 `golden_samples` 校准你的尺子。

**进度查询**：
```
python src/main.py status <workspace>
```
显示哪些 batch 已答、哪些还 pending。

#### 2c. 答完所有 batch

继续到第三步。

### 第三步：分档输出（程序）

```
python src/main.py rank <workspace>
```

跑完产出 `output/{P0,P1,P2}_priority.csv` + `output/EXCLUDED.csv` + `output/TRENDING.csv`。

会自动跑 3 条业务断言，任一失败立刻报错：
1. 唯一性：每个 cluster 只出现在一个 4 档 CSV（TRENDING 是横切，不参与守恒）
2. OOT 守约：P0/P1 不允许双判 OOT 的词
3. 总数守恒：四档 CSV 行数之和 = 输入 cluster 数

## TRENDING 横切表

`output/TRENDING.csv` 是 4 档之外的第 5 个输出，**横切关系，不影响 4 档守恒**。

**入选规则**：
- `rising`：YoY ≥ +100% **或** 3 月归一化斜率 ≥ +0.20
- `declining`：YoY ≤ -50% **或** 斜率 ≤ -0.20
- 硬过滤：search_volume ≥ 50；非双判 OOT；monthly_searches 数据完整（缺数跳过）

**数据来源**：
- `yoy_pct` 直接用 DataForSEO `keyword_info.search_volume_trend.yearly`（百分比，已算好）
- `slope_3mo_norm` 从 `keyword_info.monthly_searches` 数组算最近 3 月归一化斜率

**怎么用**：
- 看 TRENDING ∩ EXCLUDED 的 rising 词 → 主公式漏掉的早期机会，建议手动复审
- 看 TRENDING ∩ P0/P1 的 declining 词 → 已规划但流量在死，建议降权或转向

## 一次性走完的对话样板

用户：「我把 workspace 放在 ~/Downloads/foo，跑一下」

你：
1. `Bash: python src/main.py prepare ~/Downloads/foo` → 看 cluster 数
2. `Bash: python src/main.py prompts ~/Downloads/foo` → 看 batch 数（如 9 个）
3. `Bash: ls ~/Downloads/foo/cache/score_prompts/` → 列出所有 batch
4. **循环 N 次**：Read `batch_0000.md` → 在脑子里评分 → Write `batch_0000.json`
   - 一定要逐 batch 完整答完，不要省略 cluster
   - 一个 batch 大概 100 个 cluster，预算 1500-3000 token 输出
5. `Bash: python src/main.py status ~/Downloads/foo` → 确认 0 pending
6. `Bash: python src/main.py rank ~/Downloads/foo` → 看四档统计 + 断言通过
7. 给用户报：P0/P1/P2/EXCLUDED 各多少条，文件在哪

## 性能预期

- 833 cluster ≈ 9 batch × 100/batch
- 单 batch 评分大约 2-5 分钟（含 Read、思考、Write）
- 整体 30-60 分钟跑完

## 常见坑

- **JSON 必须严格**：cluster_id 是 int，user_overlap 是 float，is_oot 是 bool。错一个就被 collect 跳过
- **batch 内别漏 cluster**：100 个进去 100 个出来，缺的会被标 null 进 EXCLUDED
- **不要改 cluster_id**：评分按 cluster_id 对齐，乱了就废
- **OOT 双判规则**：你判 `is_oot=true` 不会立即排除；只有 `industry_node==OOT && is_oot==true` 才进 EXCLUDED 闸门
- **断点续跑**：cache/ 下有就跳过；删了重跑

## 安装依赖

第一次用之前：
```
bash install.sh
```
建 .venv 装 pandas（唯一依赖）。

## PRD 参考

完整规则见仓库根目录 `keyword_analysis_rules_v7.md`。

PRD 是唯一真相，Skill 跟 PRD 不一致以 PRD 为准。
