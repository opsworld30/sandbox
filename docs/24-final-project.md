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

    exec(argv, cwd, timeout, output_limit)

请求必须使用 argv 数组，不要把不可信输入拼接成 shell 字符串。若确实需要 shell，应把 shell 本身视为被执行程序，并由 Sandbox 限制它及其后代进程。

返回：

    stdout
    stderr
    exit_code
    duration
    timed_out
    output_truncated

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

注意：`allowedDomains` 必须由强制 Egress Proxy / DNS + Firewall 等网络层机制执行；仅设置 HTTP_PROXY 环境变量不够，因为程序可以直接创建 socket。

### 7. Audit

记录：

    session
    tool
    argv_hash / redacted_argv
    decision
    duration
    exit_code
    policy_version
    backend
    enforcement_status

不要把完整环境变量、Token、密码或可能包含 Secret 的命令参数原样写入日志。

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


## 13. 关键安全要求补充

### API 安全

- 每个 Session API 都必须做认证和对象级授权；
- Session ID 不是授权凭证；
- Exec 请求不能允许调用方覆盖宿主机路径或 Backend 内部参数；
- 文件操作不能只靠字符串检查；
- 错误响应不要泄露宿主机绝对路径、环境变量或 Secret。

### 资源 enforcement

- Linux CPU / Memory / PIDs：使用 cgroup v2 等 OS 资源控制；
- 磁盘容量：使用文件系统 quota / 独立受限 volume；cgroup `io` 主要控制 I/O 资源，不等同磁盘空间配额；
- stdout / stderr：在流式收集时计数并截断或终止，不能先完整缓存在内存再检查；
- timeout / destroy：终止整个 Session 进程集合，而不是只 kill 父 PID。

### Fail-closed

如果关键隔离初始化失败，例如无法创建所需 namespace、加载 seccomp、设置网络出口规则或资源限制：

    sandbox setup failed
        ↓
    do not execute

不要自动回退到宿主机无隔离执行。若产品提供 Sandbox 外执行，必须作为独立审批动作，清楚显示风险并记录审计。

## 14. 本项目不应宣称的内容

完成这个 Mini Runtime 不代表已经实现生产级多租户安全。至少还需要独立的安全评估、逃逸测试、Kernel / VMM 攻击面审查、镜像供应链验证、并发和租户隔离测试，以及持续补丁管理。
