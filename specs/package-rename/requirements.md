# 需求文档: 包名规范化重命名

## 1. 介绍
将项目包目录从 `src/` 重命名为 `solution_memory_mcp/`，使包名符合 Python 发布规范，支持正常发布到 PyPI 供他人安装使用。

## 2. 需求与用户故事

### 需求 1: 包名规范化
**用户故事:** As a 开发者, I want 将包名从 `src` 改为 `solution_memory_mcp`, so that 用户安装后可以通过规范的包名导入和使用。

#### 验收标准
* **WHEN** 用户执行 `pip install solution-memory-mcp`, **THEN** the system **SHALL** 正确安装包并创建 `solution-memory-mcp` 命令行入口。
* **WHEN** 用户执行 `solution-memory-mcp` 命令, **THEN** the system **SHALL** 正常启动 MCP 服务器。
* **WHEN** 用户在 Python 中执行 `import solution_memory_mcp`, **THEN** the system **SHALL** 成功导入模块。

---

### 需求 2: 保持现有功能不变
**用户故事:** As a 现有用户, I want 重命名后所有 MCP 工具功能保持不变, so that 不影响现有使用。

#### 验收标准
* **WHEN** 重命名完成后, **THEN** the system **SHALL** 所有内部导入路径正确更新。
* **WHEN** 运行测试, **THEN** the system **SHALL** 所有测试通过。
