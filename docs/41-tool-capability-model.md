# 第 41 讲：Tool Capability Model——为什么不同 Tool 不应该拥有同样的 Sandbox

## 1. Agent 不是只有 Shell

一个现代 AI Coding Agent 可能有：

    Shell
    File
    Git
    MCP
    Browser
    LSP
    Database
    Cloud CLI

如果所有 Tool 都共享：

    full filesystem
    full network
    full credentials

那么最弱的 Tool 会成为整个系统的突破口。

## 2. Capability 是什么

Capability 可以理解成：

> 某个 Tool 被允许拥有的一种具体能力。

例如：

    Shell:
      workspace.read
      workspace.write
      process.spawn

    Browser:
      network.example.com
      browser.dom
      browser.download

    Git:
      repo.read
      branch.write

    Database:
      db.read

## 3. 为什么不能只设计一个 Sandbox

错误：

    Agent
      ↓
    One Sandbox
      ↓
    Shell
    MCP
    Browser
    LSP

因为不同 Tool 的能力完全不同。

更合理：

    Agent
      ↓
    Tool Policy
      ├── Shell Sandbox
      ├── MCP Sandbox
      ├── Browser Sandbox
      ├── LSP Sandbox
      └── Git Policy

## 4. Capability 应该尽可能细

例如：

    network

太粗。

可以拆：

    network.connect
    network.resolve
    network.github
    network.package_registry

Filesystem：

    file.read.workspace
    file.write.workspace
    file.read.shared

Credential：

    credential.git.read
    credential.git.push
    credential.aws.read

## 5. Capability Delegation

Agent 可以调用：

    Git Tool

但不应该直接得到：

    GITHUB_TOKEN

Git Tool 自己拥有：

    git.push(repo-A, branch-B)

这就是：

> Capability Delegation

Tool 拥有能力，但 Agent 不直接拥有底层 Credential。

## 6. MCP 是一个典型案例

假设 MCP：

    filesystem-server

它可能拥有：

    read /
    write /

如果 Agent 能调用它：

    Shell Sandbox

可能被 MCP 绕过。

所以 MCP Server 本身应该有：

    MCP Policy

例如：

    filesystem:
      root = /workspace

## 7. LSP 同样需要 Capability

LSP 需要：

    workspace.read

可能还需要：

    process.spawn

但通常不应该需要：

    arbitrary network

所以可以设计：

    LSP:
      read workspace
      process limited
      network deny

## 8. Browser 可以拥有独立网络

例如：

    Browser:
      example.com
      github.com

但：

    Shell:
      network deny

这就是：

> Per-tool Network Policy

## 9. Capability Token

进一步可以设计：

    capability_token

例如：

    {
      "session": "s1",
      "tool": "git",
      "capabilities": [
        "repo.read",
        "branch.write"
      ],
      "expires_at": "..."
    }

Tool 每次请求都必须验证。

## 10. 为什么这比“大一统 Sandbox”高级

因为它把：

    Agent Security

变成：

    Capability Security

核心问题从：

> “Agent 能不能运行？”

变成：

> “Agent 当前这一步到底拿到了哪些能力？”

## 11. 实验

定义：

    ToolPolicy

    shell:
      filesystem: workspace-rw
      network: deny

    browser:
      filesystem: downloads
      network: allowlist

    git:
      filesystem: workspace
      credential: git-scoped

然后写：

    effectivePolicy(tool)

## 12. 核心结论

> 最小权限不是只对用户做的，也要对 Tool 做。

现代 Agent Runtime 越来越像：

    Agent
      ↓
    Tool
      ↓
    Capability
      ↓
    Sandbox
      ↓
    OS
