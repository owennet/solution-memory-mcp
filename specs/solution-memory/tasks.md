# 实施计划: 跨项目问题解决方案记忆系统 (Solution Memory)

## 阶段 1: 项目初始化

- [x] **任务 1.1:** 创建项目目录结构和 `pyproject.toml`
  - _关联需求: 基础架构_

- [x] **任务 1.2:** 创建数据模型定义 (`src/models/solution.py`)
  - _关联需求: #1, #3_

## 阶段 2: 存储层实现

- [x] **任务 2.1:** 实现 SQLite 存储层 (`src/storage/sqlite_store.py`)
  - 创建数据库表 (solutions, tags, solution_tags)
  - 创建 FTS5 虚拟表和同步触发器
  - 实现 CRUD 操作
  - _关联需求: #1, #2_

- [x] **任务 2.2:** 实现 Chroma 向量存储层 (`src/storage/chroma_store.py`)
  - 初始化 Chroma 客户端和 Collection
  - 实现向量的添加、搜索、删除
  - _关联需求: #2_

- [x] **任务 2.3:** 实现混合搜索引擎 (`src/search/hybrid_search.py`)
  - FTS5 关键词搜索
  - Chroma 语义搜索
  - 分数融合算法
  - _关联需求: #2_

## 阶段 3: MCP 工具实现

- [x] **任务 3.1:** 实现 `save_solution` 工具 (`src/tools/save_solution.py`)
  - 输入验证
  - 保存到 SQLite + Chroma
  - 自动标签提取
  - _关联需求: #1, #3, #5_

- [x] **任务 3.2:** 实现 `search_solutions` 工具 (`src/tools/search_solutions.py`)
  - 调用混合搜索引擎
  - 支持标签过滤
  - 返回轻量级结果
  - _关联需求: #2, #4, #5_

- [x] **任务 3.3:** 实现 `get_solution` 工具 (`src/tools/get_solution.py`)
  - 按 ID 获取完整详情
  - _关联需求: #4, #5_

- [x] **任务 3.4:** 实现 `list_tags` 工具 (`src/tools/list_tags.py`)
  - 按类别列出标签
  - 返回关联数量
  - _关联需求: #3, #5_

## 阶段 4: MCP Server 集成

- [x] **任务 4.1:** 创建 MCP Server 入口 (`src/server.py`)
  - 注册所有工具
  - 配置 stdio 传输
  - _关联需求: #5_

- [x] **任务 4.2:** 创建 `__main__.py` 入口点
  - 支持 `python -m src` 启动
  - _关联需求: #5_

## 阶段 5: 测试与文档

- [x] **任务 5.1:** 编写单元测试
  - 存储层测试
  - _关联需求: 质量保证_

- [x] **任务 5.2:** 创建 README.md
  - 安装说明
  - Windsurf 配置示例
  - 使用示例
  - _关联需求: 文档_

- [ ] **任务 5.3:** 端到端测试
  - 完整流程验证
  - _关联需求: 质量保证_
