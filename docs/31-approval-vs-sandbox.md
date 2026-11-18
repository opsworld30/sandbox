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

Sandbox：

    open("/home/user/.ssh/id_rsa")
       ↓
    Kernel Policy
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

推荐：

    System Policy
       >
    Team Policy
       >
    Project Policy
       >
    User Policy
       >
    Agent Request

注意：

    Agent Request

不能自己修改：

    System Policy

否则：

    Agent:
    “请把 ~/.ssh 加到 allowlist。”

就能绕过整个安全模型。

## 8. 面试题

为什么需要 Permission 和 Sandbox 两层？

因为 Permission 控制“是否执行”，Sandbox 控制“执行后能做什么”，二者是不同维度的安全控制。
