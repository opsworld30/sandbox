# 第 44 讲：Remote Execution——代码到底应该在哪台机器运行

## 1. AI Coding Agent 的执行位置

可能有：

    Local
    Remote SSH
    Dev Container
    Cloud VM
    Cloud Container
    MicroVM

所以第一问题不是：

> “用什么 Sandbox？”

而是：

> “代码在哪里执行？”

## 2. Local

    Agent
      ↓
    User Machine
      ↓
    OS Sandbox

目标：

> 保护用户机器。

## 3. Remote Host

    Local UI
      ↓
    SSH
      ↓
    Remote Agent
      ↓
    Remote Sandbox

安全边界必须：

    Remote Host

本地 UI 做的：

    approval

不等于：

    remote enforcement

## 4. SSH 本身不是 Sandbox

SSH 解决：

    secure transport
    authentication
    remote shell

它不天然解决：

    filesystem restriction
    network restriction
    process restriction
    resource quota

所以：

    SSH
      +
    Remote Sandbox

才是完整方案。

## 5. Cloud Agent

典型：

    User
      ↓
    API
      ↓
    Scheduler
      ↓
    Worker Host / VM
      ↓
    Sandbox Runtime
      ↓
    workload process

Worker Host 可以是 VM、物理机或集群节点；它承载具体的 workload。需要区分 Host 类型和 workload 隔离运行时：

    VM / MicroVM
      └── guest OS / workload

    Container
      └── OCI container runtime

    gVisor
      └── runsc：容器运行时接口 + 用户态 Kernel sandbox

gVisor 不是 Worker Host 的机器类型；MicroVM 则由 VMM / Hypervisor 提供虚拟机边界。
## 6. Multi-tenancy

云端最大的变化：

本地：

    protect user machine

云端：

    protect tenant A from tenant B
    protect tenant from platform
    protect platform from agent

所以需要更多层：

    Tenant Isolation
       ↓
    Worker Isolation
       ↓
    Sandbox
       ↓
    Process

## 7. Control Plane / Data Plane

非常重要。

Control Plane：

    Session API
    Policy
    Scheduler
    Audit

Data Plane：

    actual code execution

正确模型：

    Control Plane
         ↓
    Worker
         ↓
    Sandbox

不要让：

    sandboxed code

直接访问：

    control plane credentials

## 8. Session Token 与 Credential Broker

例如：

    session_id
    audience
    capability scope
    expiry

Session 可以拿到范围受限的会话凭证，但如果 Token 对 Agent 进程可读，它仍然是 Agent 可外传的 Secret。若目标是让 Agent 根本拿不到真实云凭证，应由可信 Broker / Proxy 验证 Session capability 并代为执行操作，而不是把云平台主凭证或可直接调用云 API 的长期 Token 注入 Sandbox。

## 9. Remote Artifact

Agent 产生：

    build.zip

应该：

    Sandbox
      ↓
    Artifact Store
      ↓
    signed metadata
      ↓
    User

而不是：

    Sandbox
      ↓
    direct access to internal storage

## 10. Remote Sandbox 的完整链路

    User
      ↓
    Agent API
      ↓
    Policy Engine
      ↓
    Scheduler
      ↓
    Worker
      ↓
    Sandbox Runtime
      ↓
    OS / Kernel
      ↓
    Code

旁边还有：

    Audit
    Artifact Store
    Egress Gateway
    Credential Broker

## 11. 实验

先做单机模拟：

    Control Plane
       ↓
    Local Worker
       ↓
    Sandbox

然后把：

    Worker

换成：

    Remote Worker

你的 API 不应该变化。

这就是：

> Execution Backend Abstraction

## 12. 面试题

为什么 Remote Worker 还需要 Sandbox？

因为 Worker 本身可能运行多个 Session；Remote Host 是共享基础设施，不能因为用了远程机器就认为代码天然隔离。


## 13. Remote Execution 还需要明确的控制面边界

Control Plane 管理 Session、Policy、调度和凭证发放；Data Plane 执行不可信代码。Sandbox 内的进程不应拿到 Control Plane 的主凭证，也不应直接访问 Scheduler、Metadata DB 或宿主机管理 Socket。

Remote Worker 不是天然安全边界：同一 Worker Host 可能承载多个 Session，仍需要 cgroup / container / MicroVM / VM 隔离、网络策略和清理机制。
