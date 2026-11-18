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

## 2. MCP Server 是协议端点，不一定是本地进程

常见的两种部署：

    Local stdio MCP
    Agent Host
      ↓
    MCP Client
      ↓
    local MCP Server process
      ↓
    Files / local tools

    Remote HTTP MCP
    Agent Host
      ↓
    HTTPS / Streamable HTTP
      ↓
    remote MCP service
      ↓
    remote data / API

本地 stdio MCP Server 是本机执行进程，需要在启动它的主机上做进程和资源隔离。远程 MCP Server 不在本机运行，本地 Shell Sandbox 不会自动保护远程服务；它需要在服务端部署自己的身份验证、授权、网络和运行时边界。

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
    starts / manages MCP process
      ↓
    configured sandbox applies

和：

    User / another service starts MCP
      ↓
    independent process

第二种通常不自动受当前 Agent Host 的 Sandbox 管理。即使产品文档说“支持 MCP Sandbox”，也要核对它具体覆盖哪些启动方式、哪些传输协议、哪些平台，以及是否只覆盖由 Agent Host 管理的 Server。

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


## 10. MCP Tool 的授权与 MCP Server 的进程隔离是两回事

- MCP protocol / tool schema：描述客户端可以调用哪些工具、参数是什么。
- Tool authorization：决定当前用户 / Session 能不能调用某个工具。
- Server process sandbox：限制本地 MCP Server 进程能读写什么、联网到哪里、消耗多少资源。
- Remote service isolation：限制远端 MCP 服务及其后端资源。

给 MCP 工具加一个 `read_file` 权限，不代表服务器进程只能读取某个目录；反过来，把本地 MCP Server 放进进程 Sandbox，也不代表其远端 API token 只有最小权限。

## 参考补充

MCP 官方规范：https://modelcontextprotocol.io/specification
VS Code Agent Sandboxing：https://code.visualstudio.com/docs/agents/run/agent-sandboxing

## 本讲实验代码

- [MCP Tool Capability](../labs/15-tool-capabilities/README.md)
- [最小 MCP stdio Server](../labs/22-mcp-stdio/README.md)

这些是对应主题的可运行教学实验；具体操作系统要求和安全边界以各 Lab README 为准。
