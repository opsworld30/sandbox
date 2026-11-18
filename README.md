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
26. Claude Code Bash Sandbox：Filesystem + Network，以及工具覆盖边界
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
      File tools / MCP / hooks are not automatically
      covered by the Bash Sandbox.

    Cloud Session:
      isolated VM per Anthropic-hosted session
      + server-side GitHub / credential proxy

    Independent sandbox-runtime:
      separate project; Windows support is Alpha.

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

- Lab 01：seccomp 最小实验
  - [实验说明](labs/01-seccomp/README.md)
  - [C 代码](labs/01-seccomp/seccomp_demo.c)
  - [Makefile](labs/01-seccomp/Makefile)

- Lab 02：Landlock 文件系统隔离
  - [实验说明](labs/02-landlock/README.md)
  - [C 代码](labs/02-landlock/landlock_demo.c)
  - [Makefile](labs/02-landlock/Makefile)

下一轮待补充的实战：

- bubblewrap 最小可运行实验；
- Network Namespace + forced proxy 实验；
- Workspace / symlink / inherited FD 边界实验；
- Credential Broker fake service；
- Process Tree + cgroup v2 清理实验；
- Prompt Injection + Sandbox 验证；
- Mini AI Sandbox Runtime 综合项目。
