# 第 19 讲：Container、MicroVM、VM、OS Sandbox 到底怎么选

## 1. 没有固定的“安全等级排行榜”

正确问题不是：

> Docker 好还是 VM 好？

而是：

> 我的威胁模型、攻击者能力、内核共享方式、启动延迟、兼容性和成本是什么？

下面比较的是典型架构特征，不是对所有实现的绝对安全排名。配置错误的 MicroVM 可能比正确配置的 Container 更危险；OS Sandbox 也可能因为开放过多路径和 Socket 而失去价值。

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

例如 Firecracker 这一类 VMM：

    Guest kernel
       ↓
    virtual CPU / memory / device model
       ↓
    host KVM / hypervisor boundary
       ↓
    Host

MicroVM 通常使用精简设备模型和专用 VMM，目标是在提供 VM 级硬件虚拟化边界的同时降低启动和资源开销。

但“MicroVM 一定比传统 VM 安全”不是严谨结论。安全性取决于 Hypervisor / VMM、设备模型、Host Kernel、配置和运维。

适合：

- 多租户；
- Untrusted code；
- Cloud execution；
- 高频 Sandbox。

## 6. Full VM

VM 提供 Guest Kernel 与 Host 之间的虚拟化边界，是强隔离方案之一，但不能笼统说“最强”。Hypervisor、虚拟设备、共享目录、剪贴板、网络和 Guest Agent 都可能形成跨边界通道。

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

## 7. 比较时应该看哪些维度

| 方案 | 主要边界 | 是否共享 Host Kernel | 典型优势 | 典型代价 |
|---|---|---|---|---|
| Permission / Approval | 用户或策略决策 | 是 | 易集成、低开销 | 不是 OS 隔离，依赖审批流程 |
| OS Sandbox | OS 对进程施加的访问限制 | 是 | 启动快、可用宿主机工具链 | 平台相关，策略难写，仍共享 Kernel |
| Container | namespaces / cgroups / LSM 等组合 | 通常共享 | 环境封装、生态成熟 | Host Kernel 共享，需加固配置 |
| MicroVM | 虚拟机 / VMM 边界 | Guest 有独立 Kernel | 适合不可信多租户执行 | VMM / Hypervisor 复杂度与资源成本 |
| Full VM | 虚拟化硬件边界 | Guest 有独立 Kernel | OS 兼容性高、边界清晰 | 启动、内存和运维成本可能较高 |

不要把 Permission 当成和 Container 同级的 Sandbox 技术。它是决策控制层，通常需要和 OS enforcement 组合。

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


## 11. 选择时必须先问的六个问题

1. 代码是否来自不可信用户或第三方仓库？
2. 攻击者是否可能主动尝试 Sandbox Escape？
3. 是否允许访问宿主机凭证、Unix Socket 或内网？
4. 需要兼容哪些 OS、语言和开发工具？
5. 每秒创建多少 Sandbox，启动延迟和内存预算是多少？
6. 失败时是否 fail-closed，还是允许绕过到宿主机执行？

只有回答这些问题，才能有依据地选择 OS Sandbox、Container、MicroVM 或 VM。
