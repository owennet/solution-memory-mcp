# Solution Memory MCP Server

跨项目问题解决方案记忆系统 - 为 Windsurf/Cascade 设计的 MCP Server。

## 功能特性

- 🧠 **自动捕获** - 保存问题解决方案，包含问题描述、根因分析、解决步骤
- 🔍 **混合搜索** - 结合关键词精确匹配 (FTS5) 和语义相似度 (向量) 搜索
- 🏷️ **智能标签** - 自动分类：技术栈、问题类型、错误代码
- 📦 **完全离线** - 所有数据存储在本地，保护隐私

## 安装

```bash
cd solution-memory-mcp
pip install -e .
```

## Windsurf 配置

在 Windsurf 的 MCP 配置文件中添加：

```json
{
  "mcpServers": {
    "solution-memory": {
      "command": "python",
      "args": ["-m", "solution_memory_mcp"],
      "cwd": "/path/to/solution-memory-mcp",
      "env": {
        "SOLUTION_MEMORY_PATH": "~/.solution-memory"
      }
    }
  }
}
```

## MCP 工具

### save_solution

保存新的解决方案。

```json
{
  "title": "Docker 容器网络连接失败",
  "problem": "API 请求报错 ECONNREFUSED...",
  "solution": "检查 Docker 网络配置...",
  "root_cause": "容器使用了 bridge 网络但未正确配置端口映射",
  "error_messages": ["ECONNREFUSED 127.0.0.1:3000"],
  "tags": ["Docker", "networking", "bug"],
  "project_name": "my-project"
}
```

### search_solutions

搜索相似解决方案。

```json
{
  "query": "ECONNREFUSED 连接被拒绝",
  "limit": 5,
  "tags": ["Docker"],
  "search_mode": "hybrid"
}
```

### get_solution

获取解决方案完整详情。

```json
{
  "id": "uuid-of-solution"
}
```

### list_tags

列出所有标签。

```json
{
  "category": "tech_stack"
}
```

## 数据存储

默认存储位置：`~/.solution-memory/`

```
~/.solution-memory/
├── solutions.db    # SQLite 数据库 (元数据 + FTS5 索引)
└── chroma/         # Chroma 向量数据库
```

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/
```

## License

MIT
