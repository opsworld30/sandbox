# 第 29 讲：Gemini CLI Sandbox——为什么“Tool-level Sandbox”也值得学

## 1. Gemini CLI 的一个重要设计

Gemini CLI 的公开文档支持多种 Sandbox：

    macOS
      Seatbelt

    Docker
      Container

    Podman
      Container

    sandbox-exec
      macOS

    runsc
      gVisor

    LXC
      Container

这再次证明：

> Sandbox API 应该和 Sandbox Backend 解耦。

## 2. Tool-level Sandbox

Gemini CLI 还支持把 Sandbox 放在 Tool 执行层。

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

Gemini CLI 的公开设计还包含：

    sandboxed command
        ↓
    failed because restriction
        ↓
    Sandbox Expansion Request
        ↓
    user approval
        ↓
    retry with expanded capability

这是一个非常好的 UX：

> 默认严格，遇到合理需求再扩大能力。

## 5. 为什么这比默认全开放好

默认：

    network = deny

Agent：

    npm install

失败。

然后：

    Request:
    “需要访问 registry.npmjs.org”

用户批准。

最终：

    network:
      registry.npmjs.org

而不是：

    network:
      *

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

例如：

    {
      "type": "network",
      "host": "registry.npmjs.org",
      "port": 443,
      "duration": "session"
    }

审批后才更新：

    EffectivePolicy

## 8. 参考

Gemini CLI Sandbox:
https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/sandbox.md
