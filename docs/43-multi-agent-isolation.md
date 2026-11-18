# 第 43 讲：Multi-Agent Isolation——多个 Agent 为什么不能共享一个 Sandbox

## 1. Multi-Agent 是什么

例如：

    Planner
       ↓
    Coder
       ↓
    Tester
       ↓
    Reviewer

每个 Agent 负责不同任务。

问题：

> 它们是否共享同一个权限？

## 2. 最危险的设计

    Agent A
               Shared Sandbox
       /
    Agent B

如果：

    Agent A 被攻击

它可能影响：

    Agent B
    Agent B 的 files
    Agent B 的 credentials

## 3. 更合理的模型

    Agent A
      ↓
    Sandbox A

    Agent B
      ↓
    Sandbox B

    Agent C
      ↓
    Sandbox C

然后通过：

    Message Bus

进行通信。

## 4. Agent 间通信也需要 Policy

例如：

    A → B
      allow result

但：

    A → B
      credential

应该：

    deny

因为：

> Agent-to-Agent message 本身也是数据流。

## 5. Shared Workspace 的风险

如果：

    /workspace

所有 Agent 都可写：

    Agent A
      ↓
    malicious file
      ↓
    Agent B
      ↓
    executes it

这就是：

> Cross-Agent Contamination

## 6. 推荐模型

    shared/
      read-only

    agent-a/
      read-write

    agent-b/
      read-write

然后：

    artifact exchange

通过显式 API：

    publish_artifact()
    consume_artifact()

而不是：

    random shared filesystem

## 7. Credential Isolation

不同 Agent：

    Planner
      no credential

    Coder
      git scoped credential

    Deploy Agent
      deployment scoped credential

这就是：

> Per-agent capability

## 8. 为什么 Multi-Agent 会放大风险

单 Agent：

    1 个 trust boundary

Multi-Agent：

    A
    B
    C
    MCP
    Browser
    Tool

边界数量增加。

而且：

    Agent A output
       ↓
    Agent B context

可能出现：

    indirect prompt injection

## 9. 实验

创建：

    agent-a/
    agent-b/

规则：

    A:
      write agent-a
      read shared

    B:
      write agent-b
      read shared

测试：

    A creates shared/malicious.md

B 读取后：

    不应该自动执行其中指令。

这就是：

> Data != Instruction

## 10. 核心结论

Multi-Agent Sandbox 不只是：

    N 个 Docker

而是：

    N 个 Security Context
      +
    Controlled Communication
      +
    Capability Isolation
      +
    Artifact Boundary
