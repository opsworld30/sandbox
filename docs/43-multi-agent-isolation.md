# 第 43 讲：Multi-Agent Isolation——多个 Agent 何时需要独立 Sandbox

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

对权限不同、信任等级不同或需要并行执行不可信代码的 Agent，可以使用独立安全上下文：

    Agent A
      ↓
    Sandbox A

    Agent B
      ↓
    Sandbox B

    Agent C
      ↓
    Sandbox C

然后通过受控 Message Bus / Artifact API 通信。

是否每个 Agent 都必须单独一个 Sandbox，取决于风险、资源和共享能力；关键是不能让低信任 Agent 无限制继承高权限 Agent 的文件、网络和凭证。

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


## 11. Agent Message 和 Artifact 也是不可信输入

即使消息来自同一个系统里的另一个 Agent，也可能包含被 Prompt Injection 污染的内容。下游 Agent 应把它当作数据，而不是自动执行的指令。

跨 Agent 共享建议使用：

- schema validation；
- artifact type / size / path allowlist；
- content hash / provenance；
- explicit publish / consume API；
- 独立权限和审计；
- 不能通过共享文件夹传递长期 Secret。

Multi-Agent Isolation 的核心不只是“每个 Agent 一个容器”，而是控制数据流、能力委托和跨 Agent 信任关系。

## 本讲实验代码

- [Multi-Agent Workspace / Artifact Broker](../labs/13-multi-agent-workspaces/README.md)

这些是对应主题的可运行教学实验；具体操作系统要求和安全边界以各 Lab README 为准。
