# Templates

## Minimal Cluster Table

Use when the user wants a concise plan.

| Cluster | Core intent | Representative keywords | Recommended page | Page type | Priority |
|---|---|---|---|---|---|
| Unix timestamp conversion | Convert value to readable date or back | unix timestamp converter, epoch to date, timestamp to date | /timestamp-converter | tool page | P1 |

## Website Assessment Template

Use when no keyword export has been shared yet.

- `网站类型`：工具站
- `推荐页面体系`：首页、工具页、分类页、场景页、Blog、术语页
- `建议研究的核心主题`：压缩、转换、尺寸、EXIF、去水印
- `建议导出的 seed topics`：compress image, resize image, exif viewer
- `暂不下结论的部分`：关键词布局、优先级、新建页面决策，需等待 KWFinder 数据

## Report Totals Template

Use at the end of export-based reports.

- `分析文件数`：3
- `原始关键词总数`：5421
- `删除噪音/无效关键词`：612
- `归并/标准化处理关键词`：1380
- `有效关键词池`：442809
- `用于现有页面优化的关键词数`：120
- `用于新页面规划的关键词数`：94
- `用于 Blog 的关键词数`：210
- `用于专题/Hub 的关键词数`：37
- `忽略或仅作支持覆盖的关键词数`：剩余部分

Note: `有效关键词池` means keywords remaining after noise removal and normalization, not the count of visible examples in the report.

## Blog Funnel Template

Use when blog strategy is central.

| Funnel | Keyword | Volume | KD | Why it belongs here | Recommended content |
|---|---|---:|---:|---|---|
| TOFU | what is exif data | 590 | 18 | educational discovery intent | glossary/article |
| MOFU | optimize images for web | 3300 | 38 | decision support and workflow intent | topic article |
| BOFU | compress image to 100kb without losing quality | 180 | 26 | high-intent tutorial near conversion | tutorial article |

## Execution Block Template

Use under each major recommendation.

- `页面类型`：tool page
- `URL`：`/compress-image-to-100kb`
- `主关键词`：`compress image to 100kb`
- `标题方向`：How to Compress an Image to 100KB Online
- `H1 方向`：Compress Image to 100KB
- `建议模块`：tool, quick answer, tips, faq, related pages
- `内链目标`：`/compress-image`, `/compress-jpg`
- `CTA`：use the tool now

## Detailed Page Mapping Table

Use when the user wants implementation detail.

| Recommended URL | Primary keyword | Secondary keywords | Intent | Page type | Action | GEO blocks | Notes |
|---|---|---|---|---|---|---|---|
| /timestamp-converter | unix timestamp converter | epoch converter; timestamp to date; date to timestamp | tool | tool page | optimize existing | quick answer; examples; FAQ | strongest commercial fit |

## Site Type And Page System Template

Use at the top of substantial outputs.

- `Site type`: tool site
- `Secondary type`: docs/developer site
- `Why`: most high-value queries seek a utility first, with supporting developer explanations second
- `Recommended page system`: home page, tool pages, use-case pages, blog guides, glossary pages, comparison pages

`Action` should be one of:

- `optimize existing`
- `create new`
- `merge into existing`
- `defer`

## Publishing Plan

Use this when turning clusters into an execution queue.

| Sprint | Page | Main goal | Reason now | Priority |
|---|---|---|---|---|
| Week 1 | /timestamp-converter | Capture highest-intent head term | strongest fit and likely top traffic page | P1 |

## GEO Notes Template

For top pages, add a short block like this:

- `Page`: `/timestamp-converter`
- `Quick answer`: define unix timestamp in one sentence
- `Examples`: 3 sample timestamps with human-readable output
- `FAQ`: seconds vs milliseconds, negative timestamps, 2038 problem
- `Why it helps GEO`: gives AI systems short quotable answers plus examples

## Keyword Triage Template

Use when reviewing pasted keyword rows one by one.

| Keyword | Decision | Canonical target | Why |
|---|---|---|---|
| epoch to date | target | /epoch-to-date-converter | exact tool intent |
| what is unix timestamp | target | /blog/what-is-unix-timestamp | informational intent differs from converter page |
| free online time app | ignore | - | weak fit and unclear intent |

## Existing Site Mapping Template

Use when the site already has pages.

| Keyword cluster | Recommended page | Action | Why this page | Notes |
|---|---|---|---|---|
| unix timestamp converter | /timestamp-converter | optimize existing | strongest tool intent match | add seconds vs milliseconds FAQ |

## New Page Planning Template

Use when the export reveals gaps.

| Keyword cluster | New page type | Recommended URL | Why create it | Priority |
|---|---|---|---|---|
| what is unix timestamp | glossary page | /blog/what-is-unix-timestamp | informational intent differs from tool page | P1 |
| timestamp for remote teams | solution page | /solutions/remote-team-timezone-coordination | workflow intent, not just utility intent | P2 |

## Blog Planning Template

Use when the user wants clear editorial assignments.

| Blog keyword | Recommended article | Why blog, not landing page | Internal link target |
|---|---|---|---|
| is unix timestamp always utc | Is Unix Timestamp Always UTC? | best answered with explanation and FAQ | /timestamp-converter |

## Page System Planning Template

Use when the user needs the architecture before keyword mapping.

| Site type | Page type | Role | Typical keyword pattern |
|---|---|---|---|
| SaaS | solution page | capture audience or workflow intent | crm for startups |
| SaaS | feature page | capture capability-specific intent | pipeline automation |
| Tool site | tool page | capture utility intent | unix timestamp converter |
