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

后续会继续补充：

- Landlock 实验；
- bubblewrap 实验；
- network proxy 实验；
- workspace boundary 实验；
- Prompt Injection + Sandbox 实验；
- Sandbox Runtime 综合项目。
