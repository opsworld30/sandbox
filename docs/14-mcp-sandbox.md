# 第 14 讲：MCP Server 为什么也需要 Sandbox

## 1. Agent Sandbox 不能只保护 Bash

一个现代 Agent 可能有：

    Bash
    Python
    Browser
    MCP
    LSP
    Git
    Database Tool

如果只保护：

    Bash

而 MCP Server 可以：

    read filesystem
    access network
    run process

整体安全边界还是不完整。

## 2. MCP Server 本质上也是进程

很多 MCP Server 的运行模型：

    Agent
      ↓
    MCP Client
      ↓
    MCP Server process
      ↓
    Files / Network / Database

所以 MCP Server 本身就是一个执行主体。

## 3. 为什么 MCP 更危险

MCP Server 往往有专门的能力：

    filesystem server
    database server
    browser server
    GitHub server
    internal API server

如果 Server 被配置过高：

    Agent
      ↓
    MCP
      ↓
    powerful backend

那么 Agent 的实际权限可能超过你以为的 Bash Sandbox。

## 4. 正确模型

    Agent
      ↓
    Tool Router
      ├── Bash → Sandbox A
      ├── MCP  → Sandbox B
      └── LSP  → Sandbox C

然后：

    Sandbox B
      ├── filesystem policy
      ├── network policy
      └── credential policy

## 5. MCP Server 的最小权限

例如一个 GitHub MCP Server 只需要：

    repo.read

就不要给：

    organization.admin

一个数据库 MCP 只需要：

    SELECT

就不要：

    DROP TABLE
    ALTER USER

这是 Tool Capability 的思想。

## 6. Managed Server 和 Independent Server

需要区分：

    Agent Host
      ↓
    starts MCP
      ↓
    sandbox applies

和：

    User manually starts MCP
      ↓
    independent process

第二种可能不受 Agent Sandbox 管理。

所以产品文档必须明确：

> Sandbox 到底覆盖哪些进程？

## 7. MCP 和 Prompt Injection

MCP response 也可能包含不可信内容。

例如：

    MCP result
      ↓
    “请执行这个命令”
      ↓
    LLM
      ↓
    Bash

所以：

> MCP 是 Tool Boundary，不是 Trust Boundary。

## 8. 课堂练习

设计三个 MCP：

    read-files
    query-db
    github

分别定义：

    filesystem capability
    database capability
    network capability

然后回答：

> 为什么不能给所有 MCP 一个相同的 Sandbox？

因为不同工具的最小权限完全不同。

## 9. 面试题

### Q：MCP Server 为什么需要 Sandbox？

因为 MCP Server 本身会执行代码并访问外部资源，Agent Sandbox 如果不覆盖 MCP 进程，整体攻击面仍然存在。

### Q：MCP 和 Sandbox 谁更重要？

不是二选一。MCP 定义工具能力，Sandbox 约束工具运行时能力。

## 参考

VS Code Agent Sandboxing:
https://code.visualstudio.com/docs/agents/run/agent-sandboxing
