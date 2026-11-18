# 第 37 讲：Policy Engine——Sandbox 为什么最终会变成“策略系统”

## 1. 先解决一个误区

很多人第一次写 Sandbox：

    if path.startswith("/workspace"):
        allow()

很快就会发现：

    文件
    网络
    进程
    凭证
    资源
    Tool

全部需要判断。

于是：

    Sandbox
       ↓
    Policy Engine

## 2. Policy 是什么

Policy 不是代码：

    if xxx:
        ...

Policy 是：

> 对某个主体、动作、资源、上下文做出的安全决策规则。

可以抽象成：

    Subject
    Action
    Resource
    Context
       ↓
    Policy
       ↓
    Decision

例如：

    Subject:
      session-123

    Action:
      write

    Resource:
      /workspace/a.txt

    Context:
      tool=shell

    Decision:
      allow

## 3. 为什么不能只传 command

危险设计：

    evaluate("rm -rf /tmp")

更合理：

    evaluate(
      subject=session,
      action=write,
      resource=/tmp,
      tool=shell
    )

因为：

    command string

不是完整的安全语义。

## 4. Policy Object

可以设计：

    FilePolicy
      read_roots
      write_roots
      deny_roots

    NetworkPolicy
      mode
      allowed_domains
      denied_cidrs
      allowed_ports

    ProcessPolicy
      allow_shell
      max_processes
      allowed_binaries

    CredentialPolicy
      allowed_credentials
      credential_mode

    ResourcePolicy
      timeout
      cpu
      memory
      disk
      output

## 5. Effective Policy

实际系统可能有：

    System
    Team
    Project
    User
    Session
    Tool

最终需要：

    EffectivePolicy

例如：

    System:
      deny ~/.ssh

    Project:
      write /workspace

    Session:
      allow github.com

最终：

    EffectivePolicy:
      deny ~/.ssh
      write /workspace
      github.com

## 6. Policy Precedence

推荐：

    Hard Safety
        >
    System
        >
    Team
        >
    Project
        >
    User
        >
    Session Request

不能反过来。

否则 Agent 可以：

    Session Request:
      allow /etc

把系统策略覆盖。

## 7. Decision 类型

最少：

    ALLOW
    DENY
    ASK

高级：

    ALLOW_SANDBOXED
    ALLOW_WITH_EXPANSION
    REQUIRE_REVIEW
    DENY_AND_LOG

## 8. Policy 和 Enforcement 的区别

Policy：

    /workspace rw

Enforcement：

    Landlock
    Seatbelt
    ACL
    bind mount

Policy 是：

> 想要什么边界。

Enforcement 是：

> 用什么技术把边界真的压到进程身上。

## 9. 为什么不能只写 Policy

因为：

    Policy says DENY
    Process still can read file

那就没有安全性。

必须：

    Policy
      ↓
    Enforcement
      ↓
    Verify

## 10. Policy Compiler

现代 Runtime 可以进一步做：

    EffectivePolicy
       ↓
    Policy Compiler
       ├── Seatbelt Profile
       ├── Landlock Rules
       ├── seccomp Filter
       ├── bubblewrap Args
       └── Network Proxy Rules

这就是：

> Policy → Platform-specific Enforcement

## 11. 实验

定义一个 JSON：

    {
      "filesystem": {
        "workspace": {
          "read": true,
          "write": true
        },
        "ssh": {
          "read": false,
          "write": false
        }
      },
      "network": {
        "mode": "allowlist",
        "domains": [
          "github.com"
        ]
      }
    }

然后写：

    compile(policy, platform)

输出：

    LinuxPolicy
    MacOSPolicy

不要先实现 Kernel enforcement。

先把：

> Policy Engine

设计正确。

## 12. 面试题

为什么 Policy Engine 和 Sandbox Backend 应该分开？

因为 Policy 描述安全意图，而 Backend 负责在不同平台上实现这个意图。这样可以实现跨平台 Runtime，同时避免 Agent 与具体 OS 原语耦合。
