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

一次 Agent Turn：

    LLM
      ↓
    Tool Call
      ↓
    Policy
      ↓
    Sandbox
      ↓
    Process
      ↓
    Network

最好能够通过 trace_id 串起来。

这样可以回答：

> 哪一次模型决策最终导致哪个系统调用被拒绝？

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
