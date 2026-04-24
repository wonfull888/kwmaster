# kwmaster v7

把一堆 DataForSEO 关键词 CSV 变成一张「哪个页面先做、做什么类型」的优先级清单。输入产品上下文，输出 4 档分档 + 1 张趋势横切表。整个流程只调一次 AI。

---

## 它解决什么问题

你从 DataForSEO 拉回来几百上千个关键词，不知道：

- 哪些值得做页面，哪些直接丢掉
- 该做 comparison 页、blog 文章，还是工具页
- 哪些词正在爆发，哪些已经在死

kwmaster 把这三个问题合并成一个命令跑完，输出可以直接交给 SEO/内容团队排期的 CSV。

---

## 输出

| 文件 | 内容 | 行动 |
|---|---|---|
| `P0_priority.csv` | 高相关 + 低竞争 + 足量搜索 | 立即建页面 |
| `P1_priority.csv` | 次优先 | P0 跑完后排期 |
| `P2_priority.csv` | 内容补充型 | 博客 / FAQ |
| `EXCLUDED.csv` | 不在行业内 / 低相关 / 流量太小 | 不做 |
| `TRENDING.csv` | 横切：rising / declining 信号 | 复审 EXCLUDED 里的 rising 词；警惕 P0/P1 里的 declining 词 |

每行包含：主词、cluster 大小、月搜量、搜量总和、KD、CPC、搜索意图、user_overlap、综合得分、页面建议（comparison / article / tool / landing）、趋势（YoY %）、竞品命中、行业节点、AI 评分理由。

---

## 评分逻辑

```
final_score = user_overlap × 0.40
            + kd_score    × 0.25
            + vol_score   × 0.25
            + intent_score× 0.10
```

| 指标 | 规则 |
|---|---|
| KD 分 | <20 → 1.0 / 20-40 → 0.7 / 40-60 → 0.4 / >60 → 0.1 |
| 搜量分 | >10k → 1.0 / 1k-10k → 0.7 / 100-1k → 0.4 / <100 → 直接 EXCLUDED |
| 意图分 | transactional 1.0 / commercial 0.9 / navigational 0.7 / informational 0.5 |
| 分档 | ≥0.75 P0 / 0.55-0.75 P1 / 0.35-0.55 P2 / <0.35 EXCLUDED |
| 强制 P0 | user_overlap ≥ 0.9 AND 月搜 ≥ 1000 AND 非双判 OOT |

---

## 三步流程

```
# 第一步：去重、聚类、打标签、算趋势
python src/main.py prepare <workspace>

# 第二步a：生成 AI 评分 prompts
python src/main.py prompts <workspace>

# 第二步b：你（Claude）逐 batch 读取 score_prompts/batch_NNNN.md，
#           写评分结果到 score_answers/batch_NNNN.json
#           用 status 查进度：
python src/main.py status <workspace>

# 第三步：分档输出 + TRENDING 横切
python src/main.py rank <workspace>
```

跑完后 `output/` 下有 5 个 CSV，3 条断言自动校验（唯一性 + OOT 守约 + 总数守恒）。

---

## Workspace 结构

```
<workspace>/
  config.json               产品描述 + target_user + 行业树 + competitor_brands + golden_samples
  input/
    core/*.csv              DataForSEO related_keywords 输出
    competitor/*.csv        DataForSEO ranked_keywords 输出
  cache/                    中间产物，断点可续跑
  output/
    P0_priority.csv
    P1_priority.csv
    P2_priority.csv
    EXCLUDED.csv
    TRENDING.csv
```

---

## 安装

需要 Python ≥ 3.10，唯一依赖 pandas。

```bash
bash install.sh
```

---

## 性能参考

833 个 cluster → 9 batch → 整体约 30-60 分钟（AI 评分占大头）。

---

## 常见坑

- **JSON 严格**：cluster_id 是 int，user_overlap 是 float，is_oot 是 bool，错一个就被跳过
- **别漏 cluster**：100 个进去 100 个出来，缺的直接进 EXCLUDED
- **OOT 双判**：`is_oot=true` 不立即排除，要 `industry_node=OOT AND is_oot=true` 同时成立才进 EXCLUDED
- **断点续跑**：cache/ 有就跳过，删掉就重跑

---

## 这是一个 Claude Code / OpenCode Skill

安装到 skill 目录后，直接对 Claude 说「帮我跑 kwmaster，workspace 在 ~/Downloads/foo」即可。Claude 会自动调用三步流程并全程反馈进度。

```bash
# Claude Code
cp -r . ~/.claude/skills/kwmaster/

# OpenCode
cp -r . ~/.config/opencode/skills/kwmaster/
```
