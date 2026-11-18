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
    Worker
      ↓
    Sandbox

Worker 可以：

    VM
    MicroVM
    Container
    gVisor

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

## 8. Session Token

例如：

    session_id
    capability
    expiry

Sandbox：

    only receives scoped token

而不是：

    cloud master credential

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
