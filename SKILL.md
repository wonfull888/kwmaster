---
name: kwmaster
description: Keyword planning master for SEO and GEO, especially for newer websites that need traffic through low-competition keyword targeting, page planning, topic clusters, blog content, and GEO-friendly content systems. Start from a real website or business, infer the site's core topics and likely core keywords, then turn KWFinder exports or keyword lists into page-level execution plans for existing pages, new pages, blog articles, topic hubs, and supporting content. Use when the user shares a website and asks what core keywords to research, or shares keyword exports and asks which keywords should map to existing pages, new pages, tool pages, landing pages, glossary pages, comparison pages, topic pages, or blog articles. Trigger on requests like KWFinder, keyword export, keyword list, core keywords, page mapping, content mapping, search intent, blog planning, topic cluster planning, GEO planning, SEO planning, 内容营销, 专题规划, and 关键词规划.
---

# KWMaster

Turn websites and keyword lists into a practical page plan for SEO and GEO growth. Focus on what should be built or optimized, where each keyword belongs, which content clusters should be created, and why.

## Positioning

This skill is optimized for newer sites that need to win traffic by:

- targeting lower-difficulty opportunities before broader head terms
- using keyword analysis to decide page layout and content structure
- building topic clusters and content marketing systems, not just isolated pages
- prioritizing faster traffic paths over broad but unrealistic targets

## Core Modules

Treat the skill as a modular workflow. Run the modules in order and keep their outputs separate in your thinking and in the final report.

1. `website analysis overview module`
2. `keyword analysis for page layout module`
3. `keyword analysis for content marketing module`
4. `external-link guidance module`

Reporting totals remain required, but they are treated as a required footer block, not a standalone numbered module.

## Rule Priority And Filtering

To reduce ambiguity in long instructions, apply this priority order:

1. `Tier A (hard requirements)`
   - module order and module headings
   - required table schemas and required columns
   - required enums (`disposition`, `reason_codes`, `priority`)
   - required count metrics and coverage totals
   - required output-language rules
2. `Tier B (default strategy rules)`
   - new-site prioritization logic
   - clustering and canonicalization defaults
   - topic-hub and internal-linking defaults
3. `Tier C (optional depth rules)`
   - extra narrative elaboration
   - extended examples when not needed for execution

If Tier B or Tier C conflicts with Tier A, Tier A always wins.

## Execution Profiles

Use one of two execution profiles:

- `strict` (default): enforce Tier A completely and keep Tier B decisions minimal.
- `full`: enforce Tier A + Tier B + Tier C for maximum strategic depth.

Unless the user explicitly asks for expanded strategy depth, use `strict`.

## Core Rules

- Start with the website when possible. Infer the site's core offerings, page types, audience, and monetization path before judging keywords.
- Treat the keyword list as input for page planning.
- Do not just restate volume and KD. Decide what page should exist, what page should absorb the keyword, and whether the keyword is worth pursuing now.
- Keep the analysis process mostly invisible. Show clear decisions, rationale, and page actions.
- Do not give final keyword-to-page mapping without keyword data. Before export analysis, only suggest core themes, seed topics, and candidate page directions.
- Keep outputs concise and decision-oriented. Avoid long speculative sections.
- When the user shares multiple CSV files, process them file by file first, then merge cross-file conclusions.
- Blog strategy is not optional. For content-led growth and GEO, explicitly search for keywords that belong in educational, mid-funnel, and conversion-supporting blog content.
- Default to a new-site strategy unless the user clearly says the site already has strong authority.
- Prefer lower-difficulty keywords before broader, harder keywords when choosing what a new site should pursue first.
- Treat low-volume and zero-volume keywords as valid opportunities when intent is clear, the need is real, and the page can convert or support a strong cluster.
- Content marketing is a core output, not a leftover section.
- Topic clusters should be preferred over isolated blog posts when a subject can support a pillar or专题 plus supporting articles.
- Keep distribution advice light. Suggest channels, but do not build a heavy distribution plan.
- Do not pretend to know SERP authority, DA, or competitive weakness when that data is not available.
- Do not pretend to know whether a content angle is truly additive versus current SERP leaders unless such SERP analysis was actually performed.

## Inputs To Accept

- A website or a list of URLs
- A brief description of the business, product, or site type
- Plain keyword lists pasted in chat
- CSV or spreadsheet exports from KWFinder
- Partial exports with columns like `keyword`, `volume`, `kd`, `cpc`, `trend`, `serp`
- Existing site URLs plus target market or language

If the user shares incomplete exports, proceed with what is available. Missing volume or KD lowers confidence but should not block planning.

## Batch Processing For Large CSV Exports

The skill must support chunked processing for large single-file exports.

Trigger chunked mode when either condition is true:

- single CSV file size is greater than `1 MB`
- single CSV row count is greater than `50,000`

Chunking defaults:

- split into chunks of `20,000` rows per chunk
- if memory pressure appears, reduce chunk size to `10,000` rows
- process chunks sequentially for one file, then merge at file level

Chunk-processing requirements:

1. Preserve row traceability using `source_file` and stable `source_row`.
2. Apply cleaning and normalization within each chunk.
3. Build temporary canonical groups per chunk.
4. Merge canonical groups across chunks before final routing.
5. Only after cross-chunk merge, produce final disposition and target mapping.

Cross-chunk merge priority (deterministic):

1. stronger intent and page-fit
2. known KD over unknown KD (`kd=0` stays review-sensitive)
3. lower KD when intent/fit are similar
4. higher volume when difficulty and intent are similar

Reporting requirements in chunked mode:

- files processed in chunked mode
- chunk count per file
- raw rows per file and per chunk total
- dedup / merge count within chunks
- dedup / merge count across chunks
- effective keyword pool after final cross-chunk merge

## New-Site Strategy Defaults

Use these defaults unless the user explicitly wants another strategy:

1. Prioritize keywords by realistic entry potential, not by volume alone.
2. Prefer low-KD opportunities first.
3. Within low-KD opportunities, prefer keywords with clearer commercial, conversion, comparison, alternative, and selection intent.
4. Include zero-volume or near-zero keywords when they represent real, concrete user problems.
5. Use page layout plus content marketing together.
6. Build clusters around narrow areas where the site can become the most complete result.

## Recommended Workflow

### Site First, Export Second

Prefer this order when the user has a live site:

1. Review the site and infer core keyword themes.
2. Recommend the seed topics or core keywords to export from KWFinder.
3. Analyze the exported keyword list.
4. Return a page-level action plan.

If the user skips step 1 and only gives keywords, still proceed.

## Two Output Modes

### Mode 1: Website Assessment Only

Use when the user gives a site but has not yet shared keyword data.

Allowed output:

- site type
- recommended page system
- core keyword themes to research
- seed topics to export from KWFinder
- caution notes about where data is still needed

Do not output:

- final keyword mapping to pages
- final page creation priority based on keywords
- definitive keyword layout recommendations

### Mode 2: Export-Based Planning

Use when the user shares KWFinder exports or keyword rows with usable data.

Allowed output:

- keyword-to-page mapping
- new page recommendations
- blog assignments
- merge / ignore decisions
- priority decisions based on volume, difficulty, and intent

## Module 1: Website Analysis Overview

This module stays concise. It establishes what kind of site this is and what page system fits it.

### Goal

- identify the site's primary type
- identify the site's secondary type when relevant
- identify the site's main acquisition path
- recommend the right page system before keyword routing begins

### Output Of This Module

- site type
- secondary site type if needed
- core themes
- recommended page system
- why this system fits

## Module 2: Keyword Analysis For Page Layout

This module replaces the old generic routing output with a clearer page-layout report.

### Goal

- clean and normalize the keyword exports
- decide which keywords should map to existing pages
- decide which keywords justify new pages
- prioritize faster traffic opportunities for a newer site

### Rules

- Start with CSV cleaning inside this module.
- Process CSV files one by one first, then merge cross-file conclusions.
- For oversized single files, process chunk by chunk first, then merge cross-chunk conclusions before cross-file merge.
- Keep one decision row centered on one primary keyword or decision keyword cluster.
- Add a separate related-keywords field rather than exploding every tiny variant into its own main row.
- Prefer optimizing high-fit existing pages before proposing too many new pages.
- Treat weak variants as supporting keywords, not as separate page decisions.

### Cleaning Requirements

For each CSV file:

1. Remove blank rows and malformed keywords.
2. Remove obvious off-topic noise.
3. Normalize casing, punctuation, and simple format variants.
4. Normalize equivalent terms where appropriate, such as:
   - `jpeg` -> `jpg`
   - `photo`, `picture`, `pic` -> keep as user language in related-keyword fields when useful, but treat them as intent variants during routing
   - `compress`, `reduce`, `shrink`, `minimize`, `lower` -> treat as likely same task family unless intent clearly differs
5. Identify exact duplicates and near-duplicates.
6. Mark weak variants as support-only instead of decision keywords.

### Output Of This Module

- files analyzed count
- total raw keywords
- total removed as invalid or noise
- total merged or normalized
- effective keyword pool
- keywords mapped to existing pages
- keywords mapped to new pages
- support-only / ignored keywords summary

## Module 3: Keyword Analysis For Content Marketing

This is a core module. Do not treat content marketing as a leftover after page planning.

### Goal

- identify all keywords that should be won through content marketing
- organize them into TOFU, MOFU, and BOFU
- identify topic hubs /专题
- identify which cluster articles should sit under each topic page
- identify other supporting content pages beyond standard blog posts

### Funnel Layers

- `TOFU`: educational and discovery keywords
- `MOFU`: comparison, use-case, workflow, and decision-support keywords
- `BOFU`: high-intent tutorial keywords that should push users into tools or products
- `DEV`: optional additional category when technical implementation content clearly exists

### Content-Marketing Rules

- Try hard to find content-marketing opportunities, especially for newer sites.
- Prefer topic clusters over isolated articles when a theme supports a pillar or专题 plus supporting articles.
- Every recommended topic page must include `required_cluster_articles`.
- Every cluster article must belong to one primary topic page.
- Cluster articles should prioritize lower-difficulty keywords before harder standalone targets.
- Topic pages and cluster articles must link to each other.
- Topic pages and cluster articles must also link to the relevant tool pages or conversion pages.
- New-site content systems should not rely only on isolated articles when a coherent topic cluster can be formed.
- Include other content-led page types when useful, such as glossary, comparison, FAQ-heavy support pages, and resource pages.
- Reserve external-link quantity guidance for Module 4 to avoid duplicated placement.
- Treat the article pool as a production queue, not as a raw keyword dump.
- Only keep an article row when it is worth becoming a standalone piece of content.
- Merge wording variants into one canonical article and move the rest into related keywords.
- Downgrade weak article candidates into support content when they are better suited for FAQ blocks, glossary support, comparison sections, or topic-page subsections.
- Filter out capability-mismatch keywords, brand-noise keywords, URL-like keywords, and obvious competitor-navigation keywords unless the user explicitly wants competitor content.
- Give each canonical article one primary topic owner. Do not keep the same article in multiple topic clusters unless the user explicitly wants duplicate ownership.

### Topic Hub Rule

Prefer `topic hub / 专题` when:

- the keyword is broad and supports multiple subtopics
- one article cannot satisfy the topic deeply enough
- several lower-difficulty cluster articles can strengthen the main topic page
- the topic can connect educational, comparative, and conversion-supporting content

Hard rules:

- Do not recommend a topic page without cluster articles.
- Do not leave cluster articles unattached to a primary topic page when a topic structure exists.
- Use internal links to express the hub-and-spoke relationship, not duplicated standalone planning.

### Output Of This Module

- blog article opportunities by funnel stage
- topic page opportunities by funnel stage
- required cluster articles under each topic page
- other content-marketing page opportunities by funnel stage
- content-system linking guidance between topic pages, articles, and tool pages

## Reporting And Totals (Required Footer Block)

Every final report should clearly show the scope of analysis so the user knows the work covered the full dataset.

### Goal

- make the report auditable
- show how much data was analyzed and kept
- show how many keyword decisions were made across page layout and content marketing

### At Minimum Report

- number of files analyzed
- number of files processed in chunked mode
- total chunk count
- total raw keywords
- number removed as noise or invalid
- number merged or normalized
- effective keyword pool after cleaning
- number mapped to existing pages
- number mapped to new pages
- number mapped to blog articles
- number mapped to topic pages
- number mapped to other content-marketing pages
- number ignored or marked support-only

This totals block must appear after Module 4 in the final report.

## First Pass

1. Identify the site type and core monetization path.
2. Choose the page system that fits that site type.
3. Identify the main topic clusters and content-marketing clusters.
4. Classify each keyword intent as one of: `tool`, `definition`, `how-to`, `comparison`, `use-case`, `transactional`, `navigational`.
5. Decide the best page type inside that site's page system.
6. Group near-duplicates and variants under one canonical page target.
7. Separate page-layout decisions from content-marketing decisions.

## Site-Type Routing (Condensed)

Choose one primary site type before routing. If mixed, name one secondary type.

Use the detailed routing matrix in `references/rules.md` (Site-Type Priority Map).

Minimum routing behavior:

- choose site type first
- constrain page types to that site type
- route each keyword cluster to one canonical page target
- decide action as one of: `optimize existing`, `create new`, `merge into existing`, `defer`
- split only when dominant intent differs materially

Default for this skill when uncertain: `tool site` with page types
`home`, `tool`, `use-case/landing`, `blog`, `glossary`, `comparison`.

## Page-System Rule

- Do not assign keywords to page types the site does not really need.
- Start from the site type's core page system, then map keywords into that system.
- Only recommend new page types when the site's growth path clearly requires them.

## Decision Rules

### One Primary Intent Per Page

- Merge keywords that express the same job to be done.
- Split keywords when the SERP intent is materially different.
- Do not create separate pages just because wording differs.

Examples:

- Merge: `epoch to date`, `convert epoch to date`, `epoch converter`
- Split: `unix timestamp converter` and `what is unix timestamp`
- Split: `discord timestamp generator` and `timezone meeting planner`

### Priority Scoring

Use a practical priority instead of a rigid formula:

- `P1`: Best chance to win earlier traffic or conversions for a newer site; usually lower difficulty, strong fit, and clear intent
- `P2`: Good supporting opportunity, useful cluster support, medium effort, or medium difficulty
- `P3`: Worth doing later for authority, topical coverage, or GEO support
- `Ignore`: Weak fit, duplicate intent, or low strategic value

Score using these signals in order:

1. Intent match with the site
2. Likelihood of being a realistic near-term target for a newer site
3. Business value or user value
4. Difficulty
5. Support value for GEO, clusters, and internal linking

### New-Site Keyword Rules

- Prefer lower KD before higher volume when the site is still new.
- Prefer clearer commercial, comparison, selection, and conversion-supporting intent inside low-KD sets.
- Do not auto-reject zero-volume or near-zero-volume keywords when the intent is concrete and page fit is strong.
- Use higher-difficulty keywords more often as topic-page or longer-term targets, not as immediate first-wave priorities.

### GEO Filters

Mark keywords as strong GEO targets when they naturally lead to:

- direct definitions
- step-by-step answers
- code snippets
- checklists
- tables
- comparisons
- FAQs

These often include patterns like:

- `what is ...`
- `how to ...`
- `... vs ...`
- `best ... for ...`
- `why does ...`
- `examples of ...`

## Output Workflow (Canonical)

### Raw Export Mode

Return in this order:

1. Module 1: website analysis overview
2. Module 2: keyword analysis for page layout
3. Module 3: keyword analysis for content marketing
4. Module 4: external-link guidance
5. Reporting and totals footer block

### Website-Only Mode

Return in this order:

1. Site type
2. Recommended page system
3. Core keyword themes to research
4. Seed topics to export from KWFinder
5. Short note on decisions blocked by missing keyword data

### Template Compliance Gate (Required)

Before final output, run a strict template check. If any item fails, revise before sending.

Required checks:

1. 模块标题按中文规范且仅出现一次，顺序固定：
   - `模块1：网站分析总览`
   - `模块2：页面布局关键词分析`
   - `模块3：内容营销关键词分析`
   - `模块4：外链数量建议`
2. Reporting and totals footer block exists and includes all minimum count fields.
3. Module 2 includes both required tables:
   - `keywords mapped to current pages`
   - `keywords mapped to new pages`
4. Module 3 includes all required subsections:
   - `blog article pages`
   - `blog topic pages`
   - `other content-marketing pages`
5. Priority legend includes `P1`, `P2`, `P3`, `HOLD`.
6. Topic-linking explanation is explicit (hub-and-spoke relationship).
7. Supporting CSV filename(s) are listed after each relevant module/subsection.
8. If report language is Chinese, all narrative text is Chinese while keyword strings remain in original source language.
9. Module-level CSV references must point to cleaned, module-specific output CSV files (not the same raw source file set repeated across modules).
10. Each module that cites CSV files must also show the directory path where those CSV files are located.
11. 除关键词值及其字段/属性外，报告中的标题、说明、项目符号、模块名、小节名、提示语必须为中文。

### Minimum Required Fields By Module (Strict Profile)

Module 1 requires:

- site type
- secondary site type when relevant
- core themes
- recommended page system
- input keyword coverage scope

Module 2 requires:

- files analyzed count
- cleaning totals (raw, removed, merged, effective)
- `keywords mapped to current pages` table
- `keywords mapped to new pages` table

Module 3 requires:

- article total count + top 10 representative rows
- topic total count + top 10 representative rows
- other-content total count + representative rows
- priority legend (`P1`, `P2`, `P3`, `HOLD`)
- topic-linking explanation

Module 4 requires:

- external-link quantity guidance by page type

Footer block requires:

- all required totals listed in `At Minimum Report`
- language lock: Chinese narrative + original-language keywords (no keyword translation)
- cleaned CSV artifact list with directory path

### Required CSV Artifacts

For substantial datasets, generate these files:

1. `master-keyword-routing.csv`
2. `page-layout.csv`
3. `content-articles.csv`
4. `content-topics.csv`
5. `content-other-pages.csv`
6. `reporting-totals.csv`

### Output Directory Rule

Use a single output directory for every report run.

Default directory:

- `<skill_root>/output`

Override behavior:

1. If the user specifies an output directory, use that directory for this and future outputs in the same project/session.
2. After user override, echo the active output directory in the report and keep using it unless the user changes it again.
3. Create the directory if it does not exist.

All generated artifacts must be written to the active output directory:

- Markdown report
- `master-keyword-routing.csv`
- `page-layout.csv`
- `content-articles.csv`
- `content-topics.csv`
- `content-other-pages.csv`
- `reporting-totals.csv`

### File Naming Rule

Use this naming convention for every generated file:

- `<website-name>-<YYYY-MM-DD>-<file-name>`

Examples:

- `geowriter-ai-2026-03-30-report.md`
- `geowriter-ai-2026-03-30-master-keyword-routing.csv`
- `geowriter-ai-2026-03-30-page-layout.csv`

Website-name normalization:

- use domain-derived lowercase slug
- replace `.` with `-`
- remove protocol and path

`master-keyword-routing.csv` is mandatory for auditable row coverage.

Use this minimum schema:

`source_file,source_row,keyword_raw,keyword_norm,search_volume,kd,kd_status,intent_raw,cpc,relevance,disposition,target_type,target_id,target_url,funnel_stage,priority,reason_codes,notes`

Use only approved `disposition` enums:

- `ignore_noise`
- `ignore_offscope`
- `merge_variant`
- `map_existing_page`
- `map_new_page`
- `map_article`
- `map_topic`
- `map_faq_support`
- `map_glossary`
- `map_comparison`
- `map_resource`
- `hold_needs_review`

### Display Constraints

- Module 2: show all page-layout rows in Markdown.
- Module 3 article/topic: show top 10 rows each in Markdown.
- Module 3 other-content: concise representative rows.
- Always reference supporting CSV filenames after relevant sections.
- For each module's supporting CSV list, include `Directory: <path>` on a separate line.

Top-10 selection rule (Module 2 and Module 3):

- Do NOT rank top 10 by pure search volume.
- Rank by `Priority first`, then by `expected traffic opportunity` within the same priority tier.
- This means `P1` candidates should appear before `P2`, even when some `P2` rows have larger volume.
- Within each priority tier, prefer rows with stronger realistic traffic potential for the current site stage (new-site default).

Recommended tie-break order for top-10 ranking:

1. `Priority` (`P1` > `P2` > `P3` > `HOLD`)
2. better site-intent fit (direct page fit and conversion usefulness)
3. lower difficulty (`KD`) when fit is similar
4. higher `Search volume` when KD and fit are similar

For transparency, briefly state this ranking logic before each top-10 table in Module 2/3.

### Expected Traffic Opportunity Score (Standard Formula)

Use this normalized score to rank candidates within the same reporting run.

```text
opportunity_score = priority_weight + intent_fit_weight + kd_weight + volume_weight
```

Scoring components:

- `priority_weight`
  - `P1 = 40`
  - `P2 = 25`
  - `P3 = 10`
  - `HOLD = 0`
- `intent_fit_weight`
  - `high = 25`
  - `medium = 15`
  - `low = 5`
- `kd_weight`
  - `max(0, 25 - KD/2)`
  - if KD is missing, use `0` and keep review-sensitive behavior
- `volume_weight`
  - `min(10, log10(SearchVolume + 1) * 2.5)`

Ranking rule with this score:

1. sort by `Priority` tier (`P1 > P2 > P3 > HOLD`)
2. within the same tier, sort by `opportunity_score` descending
3. if still tied, prefer lower `KD`, then higher `Search volume`

Reporting requirement:

- In Module 2/3 top-10 sections, state that ranking uses `Priority-first + opportunity_score`.
- If any manual override is applied, state the override reason in one line.

Module-level CSV reference mapping (required):

- 模块1 -> `master-keyword-routing.csv`（可补充 `reporting-totals.csv`）
- 模块2 -> `page-layout.csv`（可补充 `master-keyword-routing.csv`）
- 模块3A（blog article pages）-> `content-articles.csv`
- 模块3B（blog topic pages）-> `content-topics.csv`
- 模块3C（other content-marketing pages）-> `content-other-pages.csv`
- 报告汇总模块 -> `reporting-totals.csv`

In the footer block, also list all cleaned CSV artifacts and the shared output directory.

Do not reference only the raw source CSV set in module outputs.

### FastMD Publishing (If Installed)

If local `fastmd` is available, publish the generated Markdown report automatically.

Detection rule:

- check with `command -v fastmd`

Publishing rule:

1. Save report as a local `.md` file first.
2. Run `fastmd push <report-file>`.
3. Capture and return the document ID or URL in the final response.

Failure behavior:

- if `fastmd` is not installed or push fails, still return the local report path.
- never block report delivery on FastMD publishing.

### Redundancy Policy

- satisfy repeated requirements once in the designated module
- treat duplicated reminders as non-authoritative echoes
- do not duplicate Module 2 or Module 3 decisions in Module 1

For full examples and optional extended schemas, use:

- `references/templates.md`
- `references/rules.md`

## Cannibalization Rules

- Flag cannibalization when two planned pages would target the same dominant intent.
- Recommend one canonical page unless the SERP clearly separates tool intent from informational intent.
- Prefer folding small variants into one strong page with FAQ support.

## Existing Site Review

When the user provides a site:

1. Map clusters to existing URLs first.
2. Identify gaps where no suitable URL exists.
3. Prefer optimizing high-fit existing pages before proposing many new ones.
4. Note internal linking paths between tool pages and supporting content.
5. Infer missing core keyword themes and tell the user what to export next if needed.
6. State the site's primary and secondary site type if mixed.
7. Separate existing-page recommendations from new-page recommendations.
8. Separate page-layout recommendations from content-marketing recommendations.

## Multi-Language Rule

- Plan the English information architecture first unless the user asks for another market first.
- Reuse cluster logic across languages, but do not assume the same query patterns or priority in every locale.

## Output Language Rule

- Default report language for this skill is Chinese for report title, module headings, and narrative explanations.
- Only switch narrative language if the user explicitly asks for another language.
- Keep keywords in source language without translation.
- Keep keyword attributes and field names in their original/source language in tables and CSV outputs.
- Keep structured enum values and code fields (`disposition`, `reason_codes`, `priority`) in stable machine-readable English.
- Do not translate or paraphrase keywords into Chinese in tables, labels, notes, or examples when the report is referring to the keyword itself. Use the original keyword string.

Additional enforcement:

- Chinese-only zones: report title, module headings, subsection headings, bullets, narrative explanations, guidance text, and summary sentences.
- Non-Chinese allowed zones: keyword values and original field/attribute labels (e.g., `Primary keyword`, `Search volume`, `KD`, `Intent`, `CPC`, `Priority`).
- If English narrative text appears outside allowed zones, revise before final output.

### Language Lock Examples

- correct: `关键词: jpg to png` + `说明: 该词应映射到工具页`
- incorrect: `关键词: JPG 转 PNG` (translated keyword string)

If any translated keyword string appears, revise before final output.

## Output Style

- Be decisive.
- Use short explanations focused on why.
- When confidence is low because data is incomplete, say so briefly and still recommend the best default.
- Avoid filler like "this keyword appears relevant". Say whether to target, merge, defer, or ignore.
- Prefer action verbs like `map`, `create`, `merge`, `support`, `ignore`, `defer`.
- Keep reports compact. Prefer the minimum structure needed to move the work forward.
- Make the report useful for execution by developers or AI systems, not just for strategy discussion.
- Put priority in the last column of the page-layout and content-marketing tables.
- Prefer structured tables over long prose once keyword data exists.
- When content opportunities become too numerous for readable Markdown, summarize in Markdown and move the larger pool into CSV files.
- Keep the Markdown report aligned with the formal module structure requested by the user; do not replace it with a processing log or pipeline summary.
- Do not add extra addendum-style sections like `附` or `补充说明` in the final formal report. Put only required information into the formal modules.

## Reusable Templates

- Read `references/templates.md` for the default cluster table, page-mapping table, and publishing-plan template.
- Read `references/rules.md` for clustering rules, page-type rules, GEO patterns, and a tool-site playbook.
