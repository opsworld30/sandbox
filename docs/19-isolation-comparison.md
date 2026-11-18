# 第 19 讲：Container、MicroVM、VM、OS Sandbox 到底怎么选

## 1. 没有“最好”的 Sandbox

正确问题不是：

> Docker 好还是 VM 好？

而是：

> 我的威胁模型、启动延迟、兼容性和成本是什么？

## 2. Permission

特点：

    User Approval
        ↓
    Allow / Deny

优点：

- 成本低；
- 体验简单。

缺点：

- 依赖用户判断；
- Approval Fatigue；
- 不是强隔离。

适合：

    low-risk tools
    user confirmation

## 3. OS-level Sandbox

例如：

    macOS Seatbelt
    Linux Landlock
    Linux seccomp
    bubblewrap

特点：

    existing OS
        ↓
    restricted process

优点：

- 快；
- 资源成本低；
- 可以使用宿主机工具链。

缺点：

- 与 OS 强绑定；
- 配置复杂；
- Kernel / OS escape 仍然需要关注。

适合：

    local coding agent

## 4. Container

模型：

    Process
      ↓
    Container runtime
      ↓
    Shared host kernel

优点：

- 环境可复制；
- 生态成熟；
- 适合云端；
- 镜像方便。

缺点：

- 共享 Kernel；
- Linux 用户空间；
- 本地 macOS 开发体验不自然。

## 5. MicroVM

例如 Firecracker 这一类思路：

    Guest kernel
       ↓
    Virtual machine boundary
       ↓
    Host

特点：

> 比 Container 更强的隔离，同时比传统 VM 更轻量。

适合：

- 多租户；
- Untrusted code；
- Cloud execution；
- 高频 Sandbox。

## 6. Full VM

最强的通用隔离边界之一：

    Guest OS
       ↓
    Virtual hardware
       ↓
    Host

优点：

- 隔离强；
- OS 自由度高。

缺点：

- 启动慢；
- 内存大；
- 运维成本高。

## 7. 一个粗略对比

| 技术 | 隔离 | 启动 | 成本 | 兼容性 |
|---|---|---|---|---|
| Permission | 低 | 极快 | 极低 | 极高 |
| OS Sandbox | 中高 | 快 | 低 | 依赖 OS |
| Container | 高 | 快 | 中 | Linux 最自然 |
| MicroVM | 很高 | 中快 | 中高 | 较高 |
| VM | 很高 | 慢 | 高 | 高 |

这不是绝对安全等级，只是工程选择的粗略参考。

## 8. AI Coding 的实际选择

本地：

    OS Sandbox

云端：

    Container
    MicroVM
    VM

高风险多租户：

    MicroVM / VM

开发调试：

    Permission + OS Sandbox

## 9. 最重要的威胁模型

### Case A：本地可信用户

主要防：

    Prompt Injection
    accidental damage

OS Sandbox 很合适。

### Case B：陌生用户上传代码

风险更高：

    arbitrary code
    malware
    cryptomining
    data exfiltration

需要更强的远程隔离。

### Case C：多租户 SaaS

需要考虑：

    tenant A
       ≠
    tenant B

此时重点变成：

- Kernel boundary；
- resource quota；
- network；
- storage；
- credential；
- scheduler。

## 10. 面试题

### Q：什么时候优先 OS Sandbox？

本地 Agent、需要宿主机工具链、对启动延迟敏感时。

### Q：什么时候优先 MicroVM？

执行不可信代码、多租户、需要更强隔离但又要求比完整 VM 更快时。
