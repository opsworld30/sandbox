# 第 24 讲：最终项目——Mini AI Coding Sandbox

## 1. 项目目标

最终不要做：

    POST /run

而要做：

> 一个可以给 AI Coding Agent 使用的简化 Sandbox Runtime。

## 2. 最终架构

    AI Agent
       ↓
    Tool Router
       ↓
    Policy Engine
       ↓
    Sandbox Manager
       ↓
    Sandbox Backend
       ↓
    OS / Container / MicroVM

## 3. 核心模块

### 1. Session Manager

负责：

    create
    resume
    destroy

### 2. Policy Engine

负责：

    file policy
    network policy
    process policy
    credential policy
    resource policy

### 3. Backend

至少实现一个：

    Linux Bubblewrap Backend

可选：

    Docker Backend
    macOS Seatbelt Backend

### 4. Exec Service

提供：

    exec(argv, cwd, timeout)

返回：

    stdout
    stderr
    exit_code
    duration

### 5. File Service

提供：

    read_file
    write_file

所有路径必须经过 policy。

### 6. Network Policy

至少支持：

    allowNetwork
    allowedDomains
    allowLocalNetwork

### 7. Audit

记录：

    session
    tool
    command
    decision
    duration
    exit_code
    policy_version

## 4. API 设计

    POST /sessions

    POST /sessions/{id}/exec

    POST /sessions/{id}/files/read

    POST /sessions/{id}/files/write

    GET /sessions/{id}/events

    POST /sessions/{id}/snapshot

    POST /sessions/{id}/restore

    DELETE /sessions/{id}

## 5. Session 数据结构

    Session
      id
      workspace
      backend
      policy_version
      status
      created_at
      last_active_at

## 6. Policy 数据结构

    FileRule
      path
      read
      write
      execute

    NetworkRule
      domain
      port
      action

    ResourcePolicy
      cpu
      memory
      timeout
      process_count
      output_bytes

## 7. 执行链

一个 exec 请求：

    Agent
      ↓
    POST /sessions/{id}/exec
      ↓
    authenticate
      ↓
    load session
      ↓
    evaluate policy
      ↓
    prepare sandbox
      ↓
    launch process
      ↓
    collect output
      ↓
    audit
      ↓
    return result

## 8. Linux Backend

第一版建议：

    bubblewrap
       +
    filesystem policy
       +
    network namespace / proxy
       +
    no_new_privs
       +
    seccomp / Landlock where appropriate

不要第一版就同时实现所有 Kernel 原语。

先：

    M0 execution
    M1 workspace
    M2 filesystem
    M3 network
    M4 resource
    M5 audit
    M6 security tests

## 9. 最终安全目标

Agent 可以：

    read/write workspace
    run tests
    install dependencies
    use allowed network

Agent 不可以：

    read SSH keys
    access unrelated projects
    access private network by default
    access host-level sockets
    bypass resource limits
    retain state after destroy

## 10. 最终测试

至少通过：

### Functional

    python test
    npm test
    go test

### Filesystem

    outside read → deny
    outside write → deny
    symlink escape → deny

### Network

    allowed domain → allow
    localhost → deny
    private network → deny

### Process

    child process → sandboxed
    background process → cleanup

### Resource

    timeout → terminate
    output limit → truncate / terminate

### Credential

    fake secret → unavailable

### Injection

    malicious instruction → bounded

## 11. 最终你真正学会了什么

不是：

    Docker
    Seatbelt
    seccomp

而是：

    Threat Model
       ↓
    Policy
       ↓
    Runtime
       ↓
    OS Enforcement
       ↓
    Audit
       ↓
    Security Testing

这套思维可以迁移到：

- AI Coding Agent；
- Code Interpreter；
- MCP；
- Browser Agent；
- Workflow Agent；
- Cloud Agent；
- Multi-Agent Runtime。

## 12. 最终面试题

### Q1：如果让你设计一个 AI Coding Sandbox，你怎么设计？

从 Threat Model 开始，拆成 Policy Engine、Session Manager、Backend、Filesystem、Network、Credential、Resource 和 Audit。根据部署场景选择 OS Sandbox、Container、MicroVM 或 VM。

### Q2：为什么不能只用 Docker？

因为本地 Coding Agent 需要宿主机工具链；同时 Container 本身也需要额外的 filesystem、network、credential 和 resource policy。

### Q3：为什么不能只依赖 LLM 的安全 Prompt？

因为 Prompt Injection 和模型误判都可能让 Agent 产生危险 Tool Call。真正的安全边界必须在 Runtime / OS 层。

### Q4：为什么要做 Defense in Depth？

因为单一机制总有覆盖不到的边界。Filesystem、Network、Credential、Process、Syscall、Resource 等控制互相补充。

## 最终学习地图

    LLM
      ↓
    Agent
      ↓
    Tool Calling
      ↓
    Permission
      ↓
    Sandbox Policy
      ↓
    Sandbox Runtime
      ↓
    ┌─────────────────────┐
    │ Filesystem          │
    │ Network             │
    │ Process             │
    │ Credential          │
    │ Resource            │
    │ Syscall             │
    └─────────────────────┘
      ↓
    OS / Kernel
      ↓
    Container / MicroVM / VM

这就是完整的 AI Sandbox 知识体系。
