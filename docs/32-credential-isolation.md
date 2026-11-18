# 第 32 讲：Credential Isolation——为什么不要把 Token 塞进 Sandbox

## 1. 这是 Agent Sandbox 最容易漏掉的地方

你可能已经做到：

    filesystem sandbox
    network sandbox

但环境变量里还有：

    OPENAI_API_KEY
    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY
    GITHUB_TOKEN

那么：

    Agent
      ↓
    printenv
      ↓
    SECRET

网络一旦被打开：

    SECRET
      ↓
    attacker.com

前面的 Sandbox 可能全部失效。

## 2. Credential Boundary

真正安全的模型：

    Agent Sandbox
       |
       | operation request only
       |
       ↓
    Credential Broker / Proxy
       ↓
    attach secret server-side
       ↓
    target service
       |
       ↓
    return operation result (not secret)

## 3. 为什么 Proxy 是好办法

例如：

    Agent
      ↓
    git push
      ↓
    Git Proxy
      ↓
    validate repo
      ↓
    validate branch
      ↓
    attach credential
      ↓
    GitHub

Agent 根本不知道真实 token。

## 4. 环境变量为什么危险

环境变量会被很多程序读取：

    printenv
    /proc
    crash dump
    child process
    debug logs

所以：

    SECRET = environment variable

并不等于：

    SECRET = protected secret

## 5. SSH Agent 也需要考虑

很多开发机有：

    SSH_AUTH_SOCK

如果 Sandbox 可以访问这个 Unix socket：

    Agent
      ↓
    SSH Agent
      ↓
    request signature with loaded key

它可能获得比你预期更大的能力。实际可签名范围取决于 Key 的确认要求、有效期和 destination constraints；Socket 本身仍然是一种能力入口。

因此：

> Unix socket 也属于 Credential Boundary。

## 6. Docker Socket 同样危险

    /var/run/docker.sock

一旦暴露：

    Agent
      ↓
    Docker API
      ↓
    privileged container control

因此自研 Sandbox Policy 可以有类似：

    denyUnixSockets

但这不是所有 OS / Backend 都提供的统一开关；实际需要通过 mount namespace、文件系统可见性、Socket ACL、代理架构或平台专属机制限制具体 Unix Socket。

## 7. Credential Broker 的 API

例如：

    POST /credentials/github/push

请求：

    repo
    branch
    commit

Broker 验证：

    session
    repo
    branch
    policy

成功后：

    perform push

而不是返回：

    GITHUB_TOKEN=xxxxx

## 8. 实验

做一个 Fake Credential Broker。

不要使用真实 token。

流程：

    sandbox
       ↓
    requestGitOperation("push", repo, branch)
       ↓
    broker
       ↓
    validate(session + repo + branch)
       ↓
    broker performs fake operation
       ↓
    return { ok: true }

测试：

    sandbox 能不能 print the fake token？

目标：

    sandbox 从未收到 token，因此无 token 可打印。

## 9. 核心结论

> 最安全的 Credential 是 Agent 根本拿不到的 Credential。

这句话对：

    API Key
    Cloud Credential
    Git Credential
    SSH Agent
    Database Credential

全部成立。


## 10. 一个容易混淆的安全结论

- **Broker 返回短期 Token**：降低泄露后的权限和时间窗口，但 Token 已经进入不可信执行环境。
- **Broker / Proxy 代为执行操作**：可以让真实凭证始终留在可信服务端，只向 Agent 返回操作结果。

如果设计目标是“Agent 根本拿不到真实凭证”，必须使用第二种模式，或确保凭证只被可信 helper 消费、且 Agent 无法读取其进程内存、FD 或 IPC payload。
