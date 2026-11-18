# 第 31 讲：Approval、Permission、Sandbox、Classifier 到底是什么关系

这是 AI Agent 安全里最容易混淆的一讲。

## 1. 四个东西分别解决什么

### Approval

> 用户要不要批准这次动作？

### Permission Policy

> 什么动作默认允许、拒绝、询问？

### Classifier

> 一个动作看起来风险高不高？

### Sandbox

> 即使执行，技术上最多能访问什么？

## 2. 一个真实例子

Agent 想执行：

    curl https://attacker.example

流程可以是：

    Agent
      ↓
    Permission Policy
      ↓
    Network = denied
      ↓
    Sandbox
      ↓
    connect()
      ↓
    DENY

如果 Network 是允许的：

    Agent
      ↓
    Permission
      ↓
    Classifier
      ↓
    User Approval
      ↓
    Sandbox
      ↓
    Network Policy
      ↓
    allow / deny

## 3. 为什么审批不是 Sandbox

审批：

    “你确定吗？”

Sandbox：

    “就算你确定，系统也不允许访问这个文件。”

这两个完全不同。

## 4. 为什么 Classifier 不是 Sandbox

Classifier：

    probability = 0.97 safe

这只是：

    Decision Support

Classifier 可以是规则、统计模型或 LLM；在 Cursor Auto-review 等产品里，它可能是模型辅助的风险判断。不要把所有产品的 Classifier 都假设成同一个模型。

Sandbox：

    open("/home/user/.ssh/id_rsa")
       ↓
    Kernel / OS Policy
       ↓
    EPERM

这是：

    Enforcement

## 5. 最好的设计

    Agent
      ↓
    Intent
      ↓
    Policy Engine
      ↓
    ┌───────────────┐
    │ Allow         │
    │ Ask           │
    │ Deny          │
    └───────────────┘
      ↓
    Sandbox
      ↓
    OS Enforcement

## 6. 为什么需要多层

攻击者可能：

    Prompt Injection
          ↓
    Model
          ↓
    malicious command
          ↓
    Classifier miss
          ↓
    Permission miss
          ↓
    Sandbox catches

所以：

> 安全设计的目标不是“模型永远正确”，而是让模型错误时仍然被边界兜住。

## 7. Policy Precedence

不同产品会有不同的策略合并规则。下面只是一个可用于自研 Runtime 的设计示例，不是行业统一标准：

    Mandatory System Guardrails
       >
    Organization / Team Policy
       >
    Project Policy
       >
    User Preference
       >
    Agent Request

关键不是死记这个排序，而是定义清楚：

- 哪些规则是不可覆盖的 mandatory deny；
- 冲突时采用 deny-overrides 还是明确优先级；
- 谁可以扩大权限；
- Agent 是否能修改自己的策略（默认不可以）；
- Policy 变更是否需要重新审批和记录版本。

例如 Team 禁止访问 `~/.ssh`，Project 不应该通过普通 allow 规则覆盖它。

## 8. 面试题

为什么需要 Permission 和 Sandbox 两层？

因为 Permission 控制“是否执行”，Sandbox 控制“执行后能做什么”，二者是不同维度的安全控制。


## 9. 还要区分“审批”和“扩大 Sandbox”

用户批准一个命令，可能只代表允许执行该动作；也可能代表允许一次 Sandbox 外执行，或允许扩大某个 capability。UI 和 Runtime 必须明确告诉用户本次批准的范围、持续时间和是否移除 OS 限制。

**安全原则：** 不要把“用户点了 Allow”自动等同于“永久关闭 Sandbox”。
