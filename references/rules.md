# Rules

## Clustering Rules

### Merge These Together

- spelling variants
- singular and plural variants
- light verb variants: `convert`, `converter`, `conversion`
- phrase-order variants with same SERP intent
- long-tail modifiers that belong in on-page sections or FAQ

Examples:

- `timestamp to date`
- `convert timestamp to date`
- `timestamp date converter`

Usually map to one tool page.

### Split These Apart

- tool intent vs informational intent
- comparison intent vs definition intent
- code-language intent vs general consumer intent
- niche audience intent that deserves dedicated examples

Examples:

- `unix timestamp converter` -> tool page
- `what is unix timestamp` -> definition page
- `python epoch to datetime` -> developer guide
- `discord timestamp generator` -> dedicated tool page

## Page-Type Rules

## Site-Type Priority Map

Use this map before assigning keywords.

| Site type | Default high-priority pages | Typical keyword destinations |
|---|---|---|
| Tool site | home, tool, use-case, blog, glossary | utility, converter, calculator, workflow, developer questions |
| SaaS | home, solution, feature, comparison, blog | category, audience, use case, feature, alternative |
| Content site | home, pillar/landing, blog, glossary, comparison | how-to, definition, topic cluster, comparison |
| E-commerce | home, category/landing, solution, comparison, blog | category, use case, buying, comparison |
| Local service site | home, service landing, location landing, solution, blog | service, service+location, audience, local questions |
| Docs/developer site | home, feature, integration/language landing, blog, glossary | API capability, framework, code example, troubleshooting |

## Routing Logic

- First choose the site type.
- Then limit page recommendations to that type's page system.
- Then route each keyword into the best-fitting page type.
- Then decide whether it belongs on an existing URL, a new URL, a support section, or nowhere.
- If there is no keyword data yet, stop before final routing and only recommend research directions.

## CSV Handling Rules

- Process each CSV independently first.
- Do not merge files before you understand each file's dominant theme.
- After per-file cleaning, merge themes only where the intent is clearly shared.
- Preserve file-level context in your notes so you know which seed topic generated which cluster.

## Noise Rules

Treat these as likely noise or low-priority unless they clearly matter to the site:

- brand names of unrelated competitors or utilities
- broken spellings or malformed tokens
- domain-like keyword garbage
- weak word-order variants with no strategy impact
- highly fragmented terms with no traffic and no conversion role

## Blog Strategy Rules

- Blog is a growth channel, not a leftovers bucket.
- Search broadly for article-worthy keywords inside every CSV.
- Classify article keywords by funnel before assigning priority.
- Use topic hubs when a keyword is too broad or too difficult for a single article.

## Execution Rules

- Every recommendation should be actionable by a human or another AI without additional interpretation.
- Prefer explicit next steps over vague suggestions.
- Include concrete implementation notes whenever you recommend a page or article.

### Home Page

Best for the broadest brand-aligned head term when the site has one dominant offer.

Use for:

- primary category or flagship utility
- strongest branded or semi-branded keyword target

### Solution Page

Best for audience, workflow, or business-problem intent.

Use for patterns like:

- `[product] for [audience]`
- `[solution] for [use case]`
- operational or team workflow queries

Include:

- audience pain point
- workflow framing
- feature proof
- CTA tied to that use case

### Feature Page

Best for capability-specific intent tied to product evaluation.

Use for patterns like:

- `[product feature]`
- `how [feature] works`
- capability comparisons

Include:

- feature explanation
- benefits
- screenshots/examples
- links to relevant solution pages

### Tool Page

Best for high-intent utility queries.

Include:

- direct input/output area near top
- one-sentence explanation
- examples
- FAQ
- links to adjacent tools

### Blog Guide

Best for `how to`, `why`, troubleshooting, workflow, and platform-specific questions.

Include:

- direct answer first
- steps
- screenshots or code if relevant
- common mistakes
- link back to the tool page

### Glossary Or Definition Page

Best for `what is`, `meaning`, `definition`, `difference between`.

Include:

- concise definition
- comparison table
- real examples
- follow-up FAQ

### Comparison Page

Best for `vs`, `alternative`, `difference between`, and high-consideration product queries.

Include:

- comparison summary at top
- structured table
- winner by use case

## GEO Patterns

Strong GEO pages tend to include:

- a direct answer within the first 60 words
- headings that mirror user questions
- structured lists and tables
- short examples with labeled outputs
- plain-language definitions before nuance
- explicit statements of limits or assumptions

## Tool-Site Playbook

For utility sites like converters, calculators, and generators:

1. Defend core tool terms with the strongest existing tool pages.
2. Expand with scenario pages for languages, platforms, and workflows.
3. Add concept pages only where they support tool discovery or GEO citation.
4. Use internal links from guides and glossaries back into the tool pages.
5. Prefer fewer, stronger pages over many thin keyword pages.

## Suggested Response Pattern For Uploaded Exports

When the user uploads or pastes an export, respond with:

1. `What the export says overall`
2. `Which keywords map to existing pages`
3. `Which new pages to create and what type they should be`
4. `Which keywords should become blog posts`
5. `What to merge`
6. `What to ignore`
7. `What to publish first`

## Suggested Response Pattern For Site-Only Requests

When the user shares only a website, respond with:

1. `网站类型`
2. `推荐页面体系`
3. `建议研究的核心主题`
4. `建议导出的 seed topics`
5. `哪些结论必须等待关键词数据`

## Confidence Notes

Use these only when needed:

- `High confidence`: intent and page type are clear
- `Medium confidence`: keyword likely fits, but SERP check would confirm split vs merge
- `Low confidence`: missing data or ambiguous wording; recommend default path anyway
