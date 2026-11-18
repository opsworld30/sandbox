# AI Sandbox 沙箱入门

这套课程从传统 Sandbox 一直讲到现代 AI Coding Agent Runtime。目标不是记住 Docker、Seatbelt、seccomp 这些名词，而是理解它们分别解决什么问题、为什么要组合，以及如何自己设计一个 AI Sandbox。

## 核心问题

AI Agent 最终会执行：

    Shell
    Python
    Node
    Git
    MCP
    LSP
    Browser
    自定义工具

因此真正的问题不是“模型会不会犯错”，而是：

> 即使模型犯错，程序最多能影响什么？

核心安全链：

    LLM
      ↓
    Agent
      ↓
    Tool Calling
      ↓
    Policy
      ↓
    Sandbox Runtime
      ↓
    OS / Kernel

## 课程结构

### 第一阶段：基础
1. 什么是 Sandbox
2. OpenSandbox 与自建难度
3. 用 Agent 做简陋 Sandbox
4. 自研简陋 Sandbox

### 第二阶段：现代 AI Coding Sandbox
5. 为什么 AI Coding 不一定使用 Docker
6. macOS Seatbelt
7. Linux Namespace / Landlock / bubblewrap
8. seccomp
9. Filesystem Sandbox
10. Network Sandbox
11. Permission 与 Sandbox

### 第三阶段：Agent Security
12. Prompt Injection
13. Secret / Credential
14. MCP Sandbox
15. LSP / Tool / Process Tree
16. Git / Worktree / Checkpoint
17. Cache / Temp / Dependency

### 第四阶段：Cloud Runtime
18. Cloud Sandbox
19. Container / MicroVM / VM / OS Sandbox
20. AI Sandbox Runtime 架构
21. Prewarm / Snapshot / Pool
22. Audit / Observability
23. Security Testing
24. Final Project



### 第五阶段：主流 AI Coding Sandbox 实战拆解
25. Codex Sandbox：Permission → Sandbox Manager → OS Backend
26. Claude Code 本地命令 Sandbox：Bash / PowerShell / Monitor 与工具覆盖边界
27. Cursor Sandbox：Permission / Sandbox / Classifier 分层
28. VS Code Agent Sandbox：Terminal 与托管 MCP / LSP 的隔离范围
29. Gemini CLI Sandbox：Tool-level Sandbox 与动态扩权
30. Windows Sandbox：为什么需要自己组合 OS 能力

### 第六阶段：高级 Agent Runtime 安全
31. Approval / Permission / Sandbox / Classifier
32. Credential Isolation：Token、SSH Agent、Socket
33. Process Tree / PTY / Background Process
34. Untrusted Repository / Supply Chain
35. Browser Agent Sandbox
36. Threat Model：从“防攻击”推导 Sandbox Policy

### 第七阶段：Sandbox Runtime 深入
37. Policy Engine：规则语言与 Effective Policy
38. Sandbox Escape：常见绕过面与防御
39. Resource Isolation：cgroups、rlimit、IO、fork bomb
40. Network Proxy：HTTP CONNECT、DNS、Egress Gateway

### 第八阶段：Runtime Architecture
41. Tool Capability Model：Shell / MCP / Browser / LSP 分权
42. Workspace Snapshot：Checkpoint、Rollback、Copy-on-write
43. Multi-Agent Isolation：Agent-to-Agent 边界
44. Remote Execution：SSH / Remote Host / Cloud Worker

### 第九阶段：隔离技术深入
45. MicroVM 深入：Firecracker、KVM、启动成本
46. gVisor：用户态 Kernel 与 syscall interception
47. WASI / WebAssembly Sandbox
48. Windows Native Sandbox 深入

### 第十阶段：生产化与安全验证
49. Sandbox Observability：事件模型、Trace、Forensics
50. Sandbox Benchmark：启动速度、吞吐、安全性、兼容性
51. Escape Challenge：构建自己的 Sandbox CTF
52. Production Architecture：多租户 AI Sandbox 平台

> 目前课程正文已经推进到第 44 讲：从 Sandbox 基础、Linux/macOS 原语，到 Codex / Claude Code / Cursor / VS Code / Gemini CLI 的设计，再到 Policy、Escape、Resource、Network、Capability、Snapshot、Multi-Agent、Remote Runtime。

## 主流 AI Coding 产品的学习地图

### Codex

    Local
      ├── macOS → Seatbelt
      ├── Linux / WSL2 → bubblewrap（bwrap）
      └── Windows → native Windows sandbox

    Cloud
      └── separate remote execution environment

    Note:
      Codex local Linux implementation should not be
      described as Landlock + seccomp by default.

### Claude Code

    Local Claude Code command Sandbox
      ├── macOS → Seatbelt
      ├── Linux / WSL2 → bubblewrap + network proxy
      └── Native Windows → use WSL2 / container

    Scope:
      Bash / PowerShell / Monitor commands and child processes
      are sandboxed; File / Web tools, MCP, hooks, LSP,
      plugin monitors, helpers and Mods are outside by default.

    Cloud Session:
      isolated VM per Anthropic-hosted session
      + server-side GitHub / credential proxy

    Independent sandbox-runtime:
      separate project; Windows srt-win is Alpha
      (optional experimental MXC BaseContainer backend).

### Cursor

    Local Agent
      ↓
    Run Mode / Permission / Auto-review
      ↓
    Shell Sandbox
      ├── macOS → Seatbelt
      └── Linux → Landlock, bubblewrap fallback

    Auto-review:
      may review non-sandboxed Shell / MCP / Fetch calls.
      Classifier is not a security boundary.
      Cloud Agents use a different execution model.

### VS Code / Copilot

    Copilot Harness Session
      ├── Terminal + child processes
      ├── managed MCP Server
      └── managed Language Server
              ↓
          Sandbox

    Defaults:
      Sandbox off
      outbound network allowNetwork = true

    Windows BaseContainer:
      Experimental

### Gemini CLI

    Gemini CLI
      ↓
    Sandbox Provider
      ├── macOS → Seatbelt
      ├── Docker / Podman → Container
      ├── Windows → Windows Native Sandbox
      ├── Linux → gVisor / runsc
      └── Linux → LXC / LXD (Experimental)

    Additional:
      Tool-level Sandbox + per-command Sandbox Expansion

## 最重要的认知

不要问：

> “哪个产品用了 Docker？”

应该问：

> “它把安全边界放在哪里？”

以及：

> “这个边界最终由谁 enforce？”

答案通常应该一路追到：

    Policy
      ↓
    Runtime
      ↓
    OS
      ↓
    Kernel


## 技术审查记录

本轮第 1～44 讲及 Lab 01 / Lab 02 的技术审查和修订记录：

- [课程技术审查报告](docs/00-technical-review.md)

**产品实现核验日期：2026-11-18。** Codex、Claude Code、Cursor、VS Code、Gemini CLI 的 Sandbox 能力会随版本变化，阅读时应同时查看对应官方文档。

## 学习标准

每一讲都必须回答：

1. 它是什么？
2. 为什么需要？
3. 底层发生了什么？
4. 怎么使用？
5. 不使用会有什么风险？
6. 它和其他 Sandbox 技术怎么组合？
7. 在 AI Coding Agent 中具体放在哪里？

## 参考资料

Linux seccomp:
https://www.kernel.org/doc/html/latest/userspace-api/seccomp_filter.html

Linux Landlock:
https://docs.kernel.org/userspace-api/landlock.html

bubblewrap:
https://github.com/containers/bubblewrap

Docker seccomp:
https://docs.docker.com/engine/security/seccomp/

OpenAI Codex Sandbox:
https://developers.openai.com/codex/concepts/sandboxing

OpenAI Codex Windows Sandbox:
https://openai.com/index/building-codex-windows-sandbox/

Claude Code Sandbox:
https://code.claude.com/docs/en/sandboxing

Anthropic sandbox-runtime:
https://github.com/anthropics/sandbox-runtime

Cursor Run Modes:
https://cursor.com/docs/agent/security/run-modes

Gemini CLI Sandbox:
https://geminicli.com/docs/cli/sandbox/

OpenSandbox:
https://github.com/opensandbox-group/OpenSandbox

OpenAI Agents API Hosted Sandbox:
https://developers.openai.com/api/docs/guides/agents-api/environments/openai-hosted

VS Code Agent Sandboxing:
https://code.visualstudio.com/docs/agents/run/agent-sandboxing


## Hands-on Labs

本课程目前提供 **23 个独立实验目录**，不再只保留实验思路或伪代码。每个 Lab 都包含源码或配置、运行步骤、预期结果与安全边界说明。

- [完整实验目录与 44 讲映射](labs/README.md)
- [Lab 01：seccomp](labs/01-seccomp/README.md)
- [Lab 02：Landlock](labs/02-landlock/README.md)
- [Lab 03：Runner / Session](labs/03-runner-session/README.md)
- [Lab 04：bubblewrap](labs/04-bubblewrap/README.md)
- [Lab 05：macOS Seatbelt](labs/05-macos-seatbelt/README.md)
- [Lab 06：Network Egress Policy](labs/06-network-policy/README.md)
- [Lab 07：Credential Broker](labs/07-credential-broker/README.md)
- [Lab 08：Policy Engine](labs/08-policy-engine/README.md)
- [Lab 09：Process Tree](labs/09-process-tree/README.md)
- [Lab 10：Supply Chain](labs/10-supply-chain/README.md)
- [Lab 11：Git Worktree / Snapshot](labs/11-worktree-snapshot/README.md)
- [Lab 12：Audit / Redaction](labs/12-audit-events/README.md)
- [Lab 13：Multi-Agent Workspace](labs/13-multi-agent-workspaces/README.md)
- [Lab 14：Resource Limits](labs/14-resource-limits/README.md)
- [Lab 15：Tool Capabilities](labs/15-tool-capabilities/README.md)
- [Lab 16：Remote Session API](labs/16-remote-session-api/README.md)
- [Lab 17：Mini AI Sandbox Runtime](labs/17-mini-runtime/README.md)
- [Lab 18：Security Regression](labs/18-security-regression/README.md)
- [Lab 19：Command-scoped Expansion](labs/19-command-expansion/README.md)
- [Lab 20：Windows Sandbox](labs/20-windows-sandbox/README.md)
- [Lab 21：Prewarm / Pool](labs/21-prewarm-pool/README.md)
- [Lab 22：MCP stdio Server](labs/22-mcp-stdio/README.md)
- [Lab 23：Cache Isolation](labs/23-cache-isolation/README.md)

注意：策略模拟、应用层原型和真正调用 OS / Kernel 的实验会明确区分；代码已提交不等于已经在所有操作系统和 Kernel 版本上完成实机验证。
