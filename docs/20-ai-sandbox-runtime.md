# 第 20 讲：设计一个 AI Sandbox Runtime

## 1. 最终目标

我们不再做：

    POST /run

而是设计：

> 一个可以被 AI Agent 调用的 Sandbox Runtime。

## 2. 总体架构

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

## 3. Policy Engine

输入：

    command
    cwd
    workspace
    network request
    tool
    credentials

输出：

    allow
    deny
    ask

例如：

    command = npm test
    cwd = /workspace

    result = allow

而：

    read = ~/.ssh/id_rsa

    result = deny

## 4. Sandbox Manager

负责：

- Session；
- lifecycle；
- backend selection；
- policy translation；
- process tree；
- audit。

## 5. Backend

定义接口：

    Create
    Exec
    ReadFile
    WriteFile
    Snapshot
    Restore
    Destroy

实现：

    LocalProcessBackend
    SeatbeltBackend
    BubblewrapBackend
    DockerBackend
    MicroVMBackend

## 6. Filesystem Policy

抽象：

    FileRule
      path
      read
      write
      execute

例如：

    /workspace
      read=true
      write=true

    /tmp
      read=true
      write=true

    /home/user/.ssh
      read=false
      write=false

## 7. Network Policy

抽象：

    NetworkRule
      domain
      port
      action

例如：

    github.com:443
      allow

    localhost
      deny

## 8. Credential Policy

不要：

    environment
      ↓
    all secrets

而是：

    credential broker
       ↓
    scoped credential
       ↓
    target

## 9. Resource Policy

至少：

    cpu
    memory
    disk
    process_count
    output_bytes
    timeout

这些限制可以在不同 Backend 映射到：

    cgroups
    VM limits
    scheduler
    application timeout

## 10. Audit Event

每次 Tool Call 记录：

    session_id
    command
    cwd
    start_time
    duration
    exit_code
    sandbox_policy
    denied_reason

网络还可以记录：

    destination
    port
    allow / deny

文件访问则根据平台能力记录必要的 policy decisions。

## 11. API

建议：

    POST /sessions
    POST /sessions/{id}/exec
    POST /sessions/{id}/files/read
    POST /sessions/{id}/files/write
    GET  /sessions/{id}/events
    POST /sessions/{id}/snapshot
    POST /sessions/{id}/restore
    DELETE /sessions/{id}

## 12. 一个请求如何走完整链路

    Agent
      ↓
    exec("npm test")
      ↓
    Policy Engine
      ↓
    workspace check
      ↓
    network policy
      ↓
    resource policy
      ↓
    Backend
      ↓
    OS Sandbox
      ↓
    process
      ↓
    stdout / stderr
      ↓
    Audit Event
      ↓
    Agent

## 13. 最重要的设计原则

### Policy 不应该只存在于 LLM Prompt

它必须在 Runtime 中有可执行的 enforcement。

### Backend 不应该泄露宿主机细节

Agent 不应该关心自己是：

    Seatbelt
    bubblewrap
    Docker
    MicroVM

### 默认拒绝

未知权限：

    deny

而不是：

    allow

## 14. 面试题

### Q：如何设计一个 AI Sandbox Runtime？

至少拆成 Policy Engine、Session Manager、Backend、Filesystem Policy、Network Policy、Credential Policy、Resource Manager 和 Audit。

### Q：为什么 Policy Engine 和 Backend 分离？

Policy 表达“想允许什么”，Backend 表达“在当前平台如何真正限制它”。
