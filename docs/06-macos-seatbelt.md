# 第 6 讲：macOS Seatbelt

## 1. Seatbelt 到底是什么

可以先把它理解成：

> macOS 提供的一套进程级 Sandbox 机制，应用通过 Sandbox Profile 描述允许和禁止的操作，系统据此限制进程。

概念：

    Agent
      ↓
    sandbox-exec / Seatbelt
      ↓
    Sandbox Profile
      ↓
    macOS security enforcement

关键点：

> Agent 仍然是 macOS 原生进程，不需要变成 Linux Container。

## 2. Profile 是什么

Profile 可以理解成 Policy Language。

概念规则：

    allow read /workspace
    allow write /workspace
    allow write /tmp

    deny read ~/.ssh
    deny write /System

真实 Profile 会复杂得多，因为 Python、Node、Java 等运行时需要动态库、TTY、IPC、系统服务等能力。

## 3. 为什么默认拒绝很重要

如果：

    allow everything
    deny ~/.ssh
    deny ~/.aws

未来出现新的敏感目录，可能仍然能被读取。

更安全的模型：

    deny by default
    ↓
    allow minimum required

这就是 Least Privilege。

## 4. 子进程继承

AI Agent 会不断启动：

    Agent
      ├── bash
      ├── python
      ├── npm
      └── git

如果 Sandbox 只保护 Agent 自己，而不保护 child process，安全边界就很容易失效。

因此真正需要关注：

> Process Tree

现代 Agent Sandbox 通常会让被启动的命令及其子进程继续处在 Sandbox 边界内。

## 5. 为什么 Profile 很难写

你不能简单说：

    只允许 workspace

因为程序还需要：

- /usr 下的 runtime；
- 动态库；
- 临时目录；
- TTY；
- DNS / TLS 相关能力；
- IPC；
- 系统信息。

因此 Sandbox 工程的真实难点是：

> 安全性和兼容性的平衡。

## 6. 实验

创建：

    sandbox-demo/
      workspace/
        allowed.txt
      outside/
        secret.txt

设计目标：

    allowed.txt  → allow read
    secret.txt   → deny read

测试：

    cat workspace/allowed.txt
    cat outside/secret.txt

然后再启动 Python：

    python -c "open('outside/secret.txt').read()"

观察：

> Sandbox 保护的不是“cat 命令”，而是运行中的进程。

## 7. 不要把 Seatbelt 当万能药

安全强度取决于：

- profile；
- OS 版本；
- 允许的 IPC；
- inherited FD；
- network policy；
- credentials；
- sandbox escape vulnerabilities。

所以现代设计仍然需要：

    Seatbelt
    +
    Permission
    +
    Network Policy
    +
    Credential Isolation
    +
    Audit

## 参考

OpenAI Codex Seatbelt policy:
https://github.com/openai/codex/blob/main/codex-rs/sandboxing/src/seatbelt_base_policy.sbpl

OpenAI Codex Seatbelt implementation:
https://github.com/openai/codex/blob/main/codex-rs/sandboxing/src/seatbelt.rs
