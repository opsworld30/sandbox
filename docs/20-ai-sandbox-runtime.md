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

Policy Engine 接收的是结构化的主体、动作、资源和上下文，而不是只靠解析命令字符串：

    subject / session
    tool
    action
    resource
    workspace
    policy version
    request context

输出：

    allow
    deny
    ask
    allow-with-scoped-capability

例如：

    subject = session-123
    action = file_write
    resource = /workspace/app.go
    tool = shell

    result = allow

而：

    subject = session-123
    action = file_read
    resource = ~/.ssh/id_rsa

    result = deny

注意：Policy Engine 在执行前可以做静态决策，但它不能仅凭 `command = npm test` 预知程序运行时会访问哪些文件或连接哪些网络。最终必须由 OS / Proxy / Firewall 等 enforcement 机制在真实访问发生时强制执行。

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
      resource
      read
      write
      execute
      create
      remove
      refer / rename

策略执行不能只依赖字符串前缀或 `realpath()`。必须考虑 symlink、hardlink、路径替换竞态、已打开 FD 和文件句柄传递。优先使用 OS 原语和基于 FD 的安全路径解析。

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
      destination
      port
      protocol
      action

其中 FQDN / domain allowlist 通常由强制 Egress Proxy 实现；DNS + Firewall 组合也必须确保解析结果与实际连接目标绑定，并防止 DNS rebinding、重定向和 direct socket 绕过。不能指望 seccomp 或 Landlock 单独做域名白名单。必须阻断绕过 Proxy 的 direct socket 路径。

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
    filesystem quota
    VM / container limits
    scheduler
    application timeout

注意磁盘容量配额不是 cgroup 的通用 disk quota 功能：cgroup v2 的 `io` 控制器主要做 I/O 资源控制，磁盘空间上限通常还需要文件系统 quota、project quota 或有容量限制的独立 volume。

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
    exec(argv=["npm", "test"])
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


## 15. Policy 与 Enforcement 必须分离

    Policy Definition
         ↓
    Effective Policy
         ↓
    Policy Compiler
         ↓
    Backend Enforcement
         ↓
    Runtime Verification

例如：

- Seatbelt profile；
- Landlock ruleset；
- seccomp filter；
- bubblewrap mount / namespace 参数；
- cgroup v2 resource controls；
- Egress Proxy / Firewall rules。

**最重要的安全要求：** 如果某个 Backend 无法强制执行关键策略（例如要求按域名限制网络，但该 Backend 只有端口级规则），必须拒绝启动、改用支持的 Backend，或明确要求用户批准降级。不能把“配置已保存”当成“限制已生效”。

## 16. API 与执行接口的安全补充

- Exec API 应接收 argv 数组，避免把不可信字符串拼成 shell command。
- Session ID 必须做身份认证和对象级授权，不能仅凭 ID 就访问其他用户 Session。
- File API 需要处理 symlink、路径穿越、FD 和并发替换问题。
- Destroy 必须清理整个进程集合、临时网络和临时凭证。
- Audit 要区分“Policy 决策事件”和“真实 OS 访问事件”；后者只有在相应审计 / tracing 能力启用时才可完整观测。

## 本讲实验代码

- [Mini AI Sandbox Runtime](../labs/17-mini-runtime/README.md)

这些是对应主题的可运行教学实验；具体操作系统要求和安全边界以各 Lab README 为准。
