# 需求文档: 跨项目问题解决方案记忆系统 (Solution Memory)

## 1. 介绍

一个为 Windsurf/Cascade 设计的智能记忆系统，自动捕获和索引问题解决方案，使相同问题在不同项目中无需重复解决。系统通过 MCP Server 实现，结合 AI 压缩和语义搜索，在遇到类似问题时自动提供历史解决方案。

## 2. 需求与用户故事

### 需求 1: 自动捕获问题解决方案

**用户故事:** As a 开发者, I want Cascade 自动识别并保存我解决的问题, so that 我不需要手动记录每个解决方案。

#### 验收标准
* **WHEN** Cascade 帮助用户解决了一个 bug、配置问题或技术难题, **THEN** the system **SHALL** 自动提取问题描述、根因分析和解决方案。
* **WHEN** 解决方案被捕获时, **THEN** the system **SHALL** 使用 AI 生成结构化摘要，包含：问题标签、技术栈、错误信息、解决步骤。
* **IF** 用户使用 `<private>` 标签包裹内容, **THEN** the system **SHALL NOT** 存储该内容。

---

### 需求 2: 跨项目语义搜索

**用户故事:** As a 开发者, I want 在遇到问题时自动获得历史解决方案建议, so that 我可以快速复用之前的经验。

#### 验收标准
* **WHEN** 用户描述一个问题或错误信息, **THEN** the system **SHALL** 自动搜索语义相似的历史解决方案。
* **WHEN** 找到相关解决方案时, **THEN** the system **SHALL** 返回匹配度排序的结果列表，包含：问题摘要、解决方案、原始项目、时间。
* **IF** 搜索结果为空, **THEN** the system **SHALL** 静默处理，不打扰用户。

---

### 需求 3: 智能分类与标签

**用户故事:** As a 开发者, I want 解决方案被自动分类, so that 我可以按技术栈或问题类型浏览历史记录。

#### 验收标准
* **WHEN** 保存解决方案时, **THEN** the system **SHALL** 自动提取并分配标签：
  - **技术栈**: React, Node.js, Python, Docker, etc.
  - **问题类型**: bug, configuration, performance, security, dependency, etc.
  - **错误代码**: HTTP 状态码、编译错误代码等
* **WHEN** 用户请求按类别浏览时, **THEN** the system **SHALL** 支持按标签过滤。

---

### 需求 4: 渐进式上下文注入

**用户故事:** As a 开发者, I want 系统智能控制注入的上下文量, so that 不会因为过多历史信息而影响当前对话质量。

#### 验收标准
* **WHEN** 新会话开始时, **THEN** the system **SHALL** 仅注入轻量级索引（标题 + ID），而非完整内容。
* **WHEN** 用户或 Cascade 需要详情时, **THEN** the system **SHALL** 按需获取完整解决方案。
* **IF** 上下文 token 超过配置阈值, **THEN** the system **SHALL** 优先显示最相关的结果。

---

### 需求 5: MCP 工具接口

**用户故事:** As a Cascade AI, I want 通过 MCP 工具与记忆系统交互, so that 我可以自动保存和检索解决方案。

#### 验收标准
* **WHEN** 需要保存解决方案时, **THEN** the system **SHALL** 提供 `save_solution` 工具。
* **WHEN** 需要搜索历史时, **THEN** the system **SHALL** 提供 `search_solutions` 工具。
* **WHEN** 需要获取详情时, **THEN** the system **SHALL** 提供 `get_solution` 工具。
* **WHEN** 需要列出所有标签时, **THEN** the system **SHALL** 提供 `list_tags` 工具。

---

## 3. 非功能性需求

| 类别 | 要求 |
|------|------|
| **性能** | 搜索响应时间 < 500ms |
| **存储** | 本地 SQLite + 向量数据库，数据完全离线 |
| **隐私** | 所有数据存储在本地，不上传云端 |
| **可扩展性** | 支持 10,000+ 解决方案记录 |

---

## 4. 用户交互流程示例

```
场景: 用户在新项目中遇到 "ECONNREFUSED" 错误

1. 用户: "我的 API 请求报错 ECONNREFUSED"

2. Cascade 自动调用 search_solutions:
   → 找到 3 个相关历史解决方案

3. Cascade 响应:
   "我在你的历史记录中找到了类似问题的解决方案：
    - #142: Docker 容器网络配置问题 (2024-01)
    - #89: 本地代理端口冲突 (2023-11)
    
    最相关的是 #142，当时的解决方案是..."

4. 问题解决后，Cascade 自动调用 save_solution:
   → 保存新的解决方案变体（如果有新信息）
```

---

## 5. 设计决策

| 问题 | 决策 | 理由 |
|------|------|------|
| **AI 模型** | Cascade 自身生成摘要 | MCP Server 只负责存储，由 Cascade 在调用 `save_solution` 时传入结构化摘要，零额外成本 |
| **向量数据库** | Chroma | 成熟的本地向量数据库，支持持久化，Python 生态友好 |
| **自动化程度** | 自动保存 | 无需用户确认，Cascade 自动判断何时保存 |
