# 第 27 讲：拆解 Cursor Sandbox——Sandbox、Permissions、Classifier 为什么要分开

## 1. Cursor 的设计值得研究什么

Cursor 的公开文档把：

    Run Mode
    Permission
    Sandbox
    Classifier

分成不同层。

这非常适合用来理解现代 Agent Security。

## 2. 三个问题

### 问题 A：Agent 能不能自动执行？

这是：

    Permission / Run Mode

### 问题 B：执行以后能访问什么？

这是：

    Sandbox

### 问题 C：这个动作是不是看起来危险？

可以由：

    Classifier

辅助判断。

所以：

    Classifier
       ↓
    Policy Decision
       ↓
    Sandbox Enforcement

而不是：

    LLM Classifier
       ↓
    “安全”
       ↓
    直接放行

## 3. 为什么 Classifier 不是 Security Boundary

Classifier 是模型。

模型会：

    false positive
    false negative

因此：

    “模型认为安全”

不能替代：

    OS enforcement

例如：

    Classifier:
    “curl example.com 应该没问题”

但真正 Sandbox：

    network = deny

最终还是：

    DENIED

## 4. Cursor 的一个重要思想

公开文档中，sandboxed terminal 可以限制：

- workspace；
- protected paths；
- network；
- temporary directories；
- extra read/write paths。

某些需要完整系统权限的命令可能不能在 Sandbox 中执行。

这说明：

> Sandbox 不是要求“所有命令都必须成功”，而是优先让安全范围内的命令自动运行。

## 5. 为什么允许“不进入 Sandbox”的命令

例如：

    xcodebuild
    docker
    privileged system operation

可能依赖宿主机能力。

因此真实产品通常需要：

    Command
       ↓
    Can sandbox?
       ├── YES → sandbox
       └── NO  → permission / review

这是一种：

> Capability-aware execution

## 6. Sandbox JSON 和 Permission JSON 为什么应该分开

假设：

    permissions.json

表达：

    “什么动作需要审批？”

而：

    sandbox.json

表达：

    “Sandbox 里面能访问什么？”

这是两个维度。

错误设计：

    allow = true
    → everything allowed

正确设计：

    permission decision
       +
    sandbox capability

## 7. 为什么项目级配置很重要

AI Coding Agent 通常有：

    User Policy
    Project Policy
    Team Policy
    Hard-coded Safety Policy

最终可能：

    Effective Policy
       =
    merge(User, Project, Team, System)

但必须注意：

> 下层配置不能随意削弱上层安全边界。

例如 Team：

    deny ~/.ssh

Project：

    allow ~/.ssh

最终应该：

    DENY

## 8. Cursor 的一个关键安全思想

如果一个 sandboxed command 失败：

    permission denied

不能简单认为：

    “Sandbox 太麻烦了”

然后自动：

    run unrestricted

更合理：

    Sandbox failure
       ↓
    understand reason
       ↓
    classify
       ↓
    ask user / alternative

## 9. 实验：自己实现 Effective Policy

输入：

    system:
      deny ~/.ssh

    team:
      allow github.com

    project:
      allow workspace write

    user:
      allow pypi.org

输出：

    EffectivePolicy

    filesystem:
      workspace write
      ~/.ssh deny

    network:
      github.com
      pypi.org

## 10. 面试题

为什么 Classifier 不能代替 Sandbox？

因为 Classifier 是概率模型，Sandbox 是技术强制边界。前者可以判断，后者负责最终 enforcement。

## 参考

Cursor Run Modes:
https://cursor.com/docs/agent/security/run-modes

Cursor sandbox:
https://cursor.com/docs/agent/security/run-modes
