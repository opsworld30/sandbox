# 第 22 讲：Sandbox 监控、审计与可观测性

## 1. 为什么 Sandbox 需要 Audit

出现事故时你需要回答：

    Agent 做了什么？
    什么被允许？
    什么被拒绝？
    为什么？
    访问了什么网络？
    哪个 Session？
    哪个 Tool？

如果没有 Audit：

> 你只有“出事了”，没有证据。

## 2. 一个 Exec Event

建议至少记录：

    session_id
    command
    cwd
    start_time
    end_time
    duration
    exit_code
    sandbox_mode
    policy_version

## 3. Network Event

可以记录：

    session_id
    destination
    port
    protocol
    decision
    reason

例如：

    github.com:443
      allow

    10.0.0.12:5432
      deny
      reason = local-network-disabled

## 4. Policy Event

非常重要：

    action
    resource
    decision
    policy
    reason

例如：

    action = file_read
    resource = ~/.ssh/id_rsa
    decision = deny
    reason = outside_workspace

## 5. 为什么需要 Policy Version

如果今天 policy 是：

    v1

明天：

    v2

发生事故后：

    “为什么这个 Session 当时允许访问？”

必须知道当时使用的是哪个 Policy。

所以：

    policy_version
       ↓
    audit event

## 6. Denial Logging

被拒绝本身也是有价值的数据。

例如：

    1000 次 denied file read
      ↓
    发现 Agent 经常需要某个合法目录
      ↓
    调整 policy

因此 Audit 不只是安全工具，也是产品优化工具。

## 7. Metrics

建议：

    sandbox_create_latency
    sandbox_start_latency
    exec_duration
    sandbox_denied_count
    network_denied_count
    session_count
    snapshot_latency
    pool_hit_rate

## 8. Trace

一次 Agent Turn 可以尝试关联：

    Agent Turn
      ↓
    Tool Call
      ↓
    Policy Decision
      ↓
    Sandbox Session
      ↓
    Process / Network Event

通过 trace_id、session_id、tool_call_id 和 process identity 建立关联。

但要注意：普通的应用 Trace 不会自动知道 Kernel 拒绝了哪个 syscall。要观测 syscall 级别的拒绝，需要额外启用 seccomp logging、audit、eBPF / tracepoint 或其他 OS 级观测机制，并考虑权限、性能和日志完整性。

## 9. 安全和隐私

Audit 本身不能变成新的数据泄露源。

不要默认记录：

    password
    API token
    full file content
    private prompt

应该记录：

    metadata
    hash
    decision
    reason

## 10. 面试题

### Q：Sandbox 为什么需要 Observability？

因为安全边界不仅需要 enforcement，还需要验证、调试、审计和事故调查。

### Q：Audit 应该记录什么？

记录决策和元数据，不应无脑记录敏感数据本身。


## 11. Policy Decision 与 OS Audit Event 不要混淆

- Policy Decision：Runtime 在执行前或工具调用阶段做出的 allow / deny / ask。
- Enforcement Event：OS / Proxy / cgroup 实际阻止或限制了某个动作。
- Application Event：命令退出码、超时、stdout / stderr 等应用层结果。

这三类事件的粒度和可信度不同。没有启用文件审计或 syscall tracing 时，不要声称 Audit 已记录“所有文件读写”或“每一个系统调用”。

## 12. 日志本身也要防泄露

命令行参数、环境变量、URL query、HTTP header 和异常堆栈都可能带有 Secret。审计系统应做字段级脱敏、访问控制、保留期限和防篡改设计。

## 本讲实验代码

- [Audit Event 与 Secret Redaction](../labs/12-audit-events/README.md)

这些是对应主题的可运行教学实验；具体操作系统要求和安全边界以各 Lab README 为准。
