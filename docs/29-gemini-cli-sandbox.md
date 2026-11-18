# 第 29 讲：Gemini CLI Sandbox——为什么“Tool-level Sandbox”也值得学

## 1. Gemini CLI 的一个重要设计

截至 2026-11-18，Gemini CLI 官方 Sandbox 文档列出的方式包括：

    macOS
      → Seatbelt / sandbox-exec

    Docker / Podman
      → Container

    Windows
      → Windows Native Sandbox

    Linux
      → gVisor / runsc

    Linux
      → LXC / LXD（Experimental）

注意：`sandbox-exec` 是 Gemini CLI 选择 macOS Seatbelt 的配置入口，不是和 Seatbelt 并列的另一种隔离技术。

这再次证明：

> Sandbox API 应该和 Sandbox Backend 解耦。

## 2. Tool-level Sandbox

Gemini CLI 文档明确支持 Tool-level sandboxing：对单次工具执行（例如 `shell_exec`、`write_file`）做隔离，而不是把整个 CLI 进程都放进 Sandbox。

例如：

    Gemini CLI
       ↓
    Shell Tool
       ↓
    Sandbox

而不是：

    整个 Gemini CLI
       ↓
    Sandbox

为什么有价值？

因为 CLI 自己可能需要：

    UI
    config
    model API
    history

但真正危险的是：

    shell_exec
    write_file
    tool server

所以可以做到：

> 只把高风险 Tool 放进 Sandbox。

## 3. 这是一个非常重要的架构选择

方案 A：

    Whole-process sandbox

    Agent
      ↓
    Sandbox
      ↓
    everything

优点：

- 简单；
- 边界清晰。

缺点：

- 兼容性差；
- Agent 自己也被限制。

方案 B：

    Tool sandbox

    Agent
      ├── UI / model / config
      │      ↓
      │    normal
      │
      └── Shell
             ↓
          Sandbox

优点：

- 更灵活；
- 本地工具更容易兼容。

缺点：

- Tool 边界设计复杂；
- 容易出现绕过路径。

## 4. Sandbox Expansion

Gemini CLI 当前文档明确提供 Sandbox Expansion：

    sandboxed command
        ↓
    failed because restriction
        ↓
    Sandbox Expansion Request
        ↓
    user approval
        ↓
    run this command with expanded capability

这是一个非常好的 UX：

> 默认严格，遇到合理需求再扩大能力。

## 5. 为什么这比默认全开放好

当所选 Provider / Profile 将网络设为受限时，例如：

    network = deny

Agent：

    npm install

可能因网络权限不足而触发 Sandbox Expansion Request：

    Request:
    “本次命令需要访问 registry.npmjs.org”

用户批准后，只为本次命令执行扩展相应能力，而不是永久修改整个 Session 的基础策略。

注意：Gemini CLI 的默认网络行为取决于 Provider 和 Profile。macOS 默认 `permissive-open` profile 允许网络；不能把“默认断网”概括成所有 Gemini CLI Sandbox 的统一默认值。

## 6. 这其实是 Capability Expansion

可以抽象成：

    BaseCapability
       ↓
    AddCapability
       ↓
    Session Policy

例如：

    filesystem:
      workspace rw

扩展：

    + ~/shared readonly

网络：

    + registry.npmjs.org:443

## 7. 实验

实现：

    SandboxExpansionRequest

数据：

    reason
    requested_capability
    scope
    duration

以下是**自研 Runtime 的概念数据结构，不是 Gemini CLI 的实际 API schema**：

    {
      "type": "network",
      "host": "registry.npmjs.org",
      "port": 443,
      "duration": "single_command"
    }

Gemini CLI 的扩权针对本次命令执行；不应把它描述成永久修改整个 Session 的策略。审批后才更新：

    EffectivePolicy

## 8. 参考

Gemini CLI Sandbox:
https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/sandbox.md


## 9. Windows Native Sandbox 的边界

Gemini CLI 的 Windows Native Sandbox 使用 Windows Mandatory Integrity Control 的 Low Mandatory Level，并通过 `icacls` 设置相关文件 / 目录的完整性级别。官方文档提醒这些完整性级别变化可能留在文件系统中，Sandbox 会话结束后不一定自动恢复。

这与 Codex 的 restricted token + ACL + Windows Firewall 设计不同，也与 Anthropic sandbox-runtime 的 WFP + dedicated local user Alpha 实现不同。不要把它们统称成一个“Windows Sandbox 方案”。

## 10. 默认配置不等于默认断网

Gemini CLI 的 macOS 默认 Seatbelt profile（例如 permissive-open）会限制项目目录外写入，但仍允许较广泛的读取和网络访问。具体权限取决于所选 profile 和 Sandbox provider，不能只看到 `-s` 就认为网络默认 deny。

## 11. 参考

Gemini CLI Sandbox:
https://geminicli.com/docs/cli/sandbox/

GitHub source:
https://github.com/google-gemini/gemini-cli

**核验日期：2026-11-18。** Windows Native、LXC/LXD 等支持状态和配置名称应以当前官方文档为准。


## 12. Gemini CLI 自身运行在 Docker 里时的一个坑

如果 Gemini CLI 本身已经运行在一个 Docker 容器里，而你又选择 Docker Sandbox，CLI 可能需要访问宿主机 Docker Socket 来创建 sibling sandbox container，并且 workspace 的绝对路径必须与宿主机看到的路径一致。

这意味着 `/var/run/docker.sock` 是高权限能力：不要为了让 Sandbox 正常工作，就无条件把 Docker Socket 暴露给不可信 Agent 进程。应把创建 Sandbox 的职责放在可信 Host / Broker 一侧。
