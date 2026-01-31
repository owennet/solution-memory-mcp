# Solution Memory MCP Server

跨项目问题解决方案记忆系统 - 为 Windsurf/Cascade 设计的 MCP Server。

## 功能特性

- 🧠 **自动捕获** - 保存问题解决方案，包含问题描述、根因分析、解决步骤
- 🔍 **混合搜索** - 结合关键词精确匹配 (FTS5) 和语义相似度 (向量) 搜索
- 🏷️ **智能标签** - 自动分类：技术栈、问题类型、错误代码
- 📦 **完全离线** - 所有数据存储在本地，保护隐私
- 🌍 **跨项目共享** - 全局注册，所有项目可用，统一存储

## 安装

### 前置要求

- Python >= 3.11
- Windsurf IDE

### 安装步骤

```bash
# 1. 克隆或下载项目
cd solution-memory-mcp

# 2. 使用 Python 3.11+ 安装
python3.11 -m pip install -e .

# 或使用 Homebrew 安装的 Python
/opt/homebrew/bin/python3.11 -m pip install -e .
```

## Windsurf 配置

MCP 配置文件路径：`~/.codeium/windsurf/mcp_config.json`

添加以下配置：

```json
{
  "mcpServers": {
    "solution-memory": {
      "command": "/opt/homebrew/bin/python3.11",
      "args": ["-m", "solution_memory_mcp"],
      "cwd": "/path/to/solution-memory-mcp",
      "env": {
        "SOLUTION_MEMORY_PATH": "~/.solution-memory"
      }
    }
  }
}
```

> **注意**：请将 `command` 替换为你系统上 Python 3.11+ 的实际路径

配置完成后**重启 Windsurf** 使配置生效。

## Cascade 自动化配置

为了让 Cascade 在工作过程中自动保存和检索解决方案，需要在 Windsurf 的 **Memories** 或 **Global Rules** 中添加使用规则：

```markdown
# Solution Memory 使用规则

1. **遇到问题时** - 先调用 `search_solutions` 搜索是否有类似解决方案
2. **成功解决问题后** - 调用 `save_solution` 保存解决方案
3. **触发条件**：修复 bug、解决配置问题、处理依赖冲突
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
└── chroma/         # Chroma 向量数据库 (语义嵌入)
```

### 数据特点

- **全局存储** - 数据存储在用户 home 目录，不绑定特定项目
- **跨项目共享** - 所有项目的解决方案统一管理
- **双重索引** - FTS5 关键词搜索 + 向量语义搜索

## 搜索模式

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| `hybrid` (默认) | 关键词 + 语义混合 | 通用搜索 |
| `keyword` | 纯关键词 FTS5 | 精确匹配错误信息 |
| `semantic` | 纯语义向量 | 模糊描述、不同表述 |

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/

# 手动测试服务
python -m solution_memory_mcp
```

## 常见问题

### 服务状态显示黄色

首次启动时需要下载 embedding 模型（~90MB），可能需要几十秒。完成后变为绿色。

### 语义搜索分数为 0

确保通过 MCP 工具 `save_solution` 保存，会自动同步到向量库。直接操作数据库不会触发同步。

## License

MIT
