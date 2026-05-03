# Human Control Layer Starter

Copy/adapt these pages when a wiki grows beyond what the human can personally know page-by-page.

## `maps.md`

```markdown
---
title: "Knowledge Maps"
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: query
tags: [knowledge-management]
sources: []
---

# Knowledge Maps

> Human control entry: fast recovery of the wiki's topic structure. This is not the full index.

## 一级主题地图

- **主题 A**：范围、核心入口。
- **主题 B**：范围、核心入口。

## 主题之间的关系

- **A ↔ B**：关系说明。

## 核心枢纽页面

- [[overview]]
- [[questions]]
- [[principles]]
- [[decisions]]
- [[queries/inbox]]
- [[index]]
- [[log]]

## 待完善地图

- Identify 5-10 hub pages per theme.
```

## `questions.md`

```markdown
---
title: "Long-term Questions"
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: query
tags: [knowledge-management]
sources: []
---

# Long-term Questions

> Only recurring, judgment-changing, action-relevant questions live here. Candidate questions go to [[queries/inbox]].

## 进行中问题

### Q1：...

- 状态：进行中
- 相关页面：[[overview]]、[[maps]]、[[principles]]、[[queries/inbox]]
- 当前最佳回答：
- 下一步需要验证：

## 已部分解决的问题

## 反复出现的问题

## 暂时搁置的问题
```

## `principles.md`

```markdown
---
title: "Principles"
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: query
tags: [knowledge-management]
sources: []
---

# Principles

> Few, hard, reusable judgment rules — not quotes or summaries.

## 知识管理原则

### 原则 1：LLM 负责规模，人负责方向

- 含义：
- 适用场景：
- 反例：
- 相关页面：[[overview]]、[[maps]]、[[questions]]、[[queries/inbox]]
```

## `decisions.md`

```markdown
---
title: "Decisions"
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: query
tags: [knowledge-management]
sources: []
---

# Decisions

> Records choices made with wiki support. If the wiki does not affect decisions, it is only a library.

## YYYY-MM-DD｜Decision title

- 背景：
- 参考页面：
- 决策：
- 理由：
- 保留疑问：
- 后续复盘时间：
```

## `queries/inbox.md`

```markdown
---
title: "Query Inbox"
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: query
tags: [knowledge-management]
sources: []
---

# Query Inbox

> Candidate questions captured by AI. Candidate does not mean final knowledge.

## YYYY-MM-DD｜Question title

- 原始问题：
- 价值判据：
  - 反复出现 / 改变判断 / 连接多个主题 / 未来会复用 / 暴露认知缺口 / 产生原则
- 当前摘要：
- 建议去向：[[questions]] / [[principles]] / [[overview]] / [[decisions]] / formal query page
- 状态：candidate / promoted / rejected / merged
```
