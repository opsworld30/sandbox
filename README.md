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
26. Claude Code Sandbox：Filesystem + Network 双边界
27. Cursor Sandbox：Permission / Sandbox / Classifier 分层
28. VS Code Agent Sandbox：Terminal / MCP / LSP 一起保护
29. Gemini CLI Sandbox：Tool-level Sandbox 与动态扩权
30. Windows Sandbox：为什么需要自己组合 OS 能力

### 第六阶段：高级 Agent Runtime 安全
31. Approval / Permission / Sandbox / Classifier
32. Credential Isolation：Token、SSH Agent、Socket
33. Process Tree / PTY / Background Process
34. Untrusted Repository / Supply Chain
35. Browser Agent Sandbox
36. Threat Model：从“防攻击”推导 Sandbox Policy

### 第七阶段：建议继续扩展
37. Policy Engine：规则语言与 Effective Policy
38. Sandbox Escape：常见绕过面与防御
39. Resource Isolation：cgroups、rlimit、IO、fork bomb
40. Network Proxy：HTTP CONNECT、DNS、Egress Gateway
41. Tool Capability Model：Shell / MCP / Browser / LSP 分权
42. Workspace Snapshot：Checkpoint、Rollback、Copy-on-write
43. Multi-Agent Isolation：Agent-to-Agent 边界
44. Remote Execution：SSH / Remote Host / Cloud Worker
45. MicroVM 深入：Firecracker、KVM、启动成本
46. gVisor：用户态 Kernel 与 syscall interception
47. WASI / WebAssembly Sandbox
48. Windows Native Sandbox 深入
49. Sandbox Observability：事件模型、Trace、Forensics
50. Sandbox Benchmark：启动速度、吞吐、安全性、兼容性
51. Escape Challenge：构建自己的 Sandbox CTF
52. Production Architecture：多租户 AI Sandbox 平台

> 37-52 是下一阶段扩展路线。目标是把课程从“认识 Sandbox”推进到“能够设计和实现一个生产级 AI Agent Runtime”。

## 主流 AI Coding 产品的学习地图

### Codex

    Local
      ├── macOS → Seatbelt
      ├── Linux → Landlock / seccomp
      └── Windows → native sandbox / WSL path

    Cloud
      └── isolated container

### Claude Code

    Local
      ├── macOS → Seatbelt
      └── Linux → bubblewrap

    Cloud
      └── isolated environment + proxy / credential mediation

### Cursor

    Local Agent
      ↓
    Run Mode / Permission
      ↓
    Sandbox
      ↓
    macOS Seatbelt / Linux native sandbox

### VS Code / Copilot

    Agent Host
      ├── Terminal
      ├── MCP
      └── Language Server
              ↓
          Sandbox

### Gemini CLI

    Tool
      ↓
    Sandbox Backend
      ├── Seatbelt
      ├── Docker
      ├── Podman
      ├── runsc
      └── LXC

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
https://kernel.org/doc/html/latest/userspace-api/seccomp_filter.html

Linux Landlock:
https://docs.kernel.org/userspace-api/landlock.html

bubblewrap:
https://github.com/containers/bubblewrap

Docker seccomp:
https://docs.docker.com/engine/security/seccomp/

OpenAI Codex sandbox:
https://github.com/openai/codex/tree/main/codex-rs/sandboxing

Anthropic Sandbox Runtime:
https://github.com/anthropic-experimental/sandbox-runtime

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

后续会继续补充：

- Landlock 实验；
- bubblewrap 实验；
- network proxy 实验；
- workspace boundary 实验；
- Prompt Injection + Sandbox 实验；
- Sandbox Runtime 综合项目。
