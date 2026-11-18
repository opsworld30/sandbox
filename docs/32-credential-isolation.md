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
       | no long-lived secret
       |
       ↓
    Credential Broker
       ↓
    short-lived credential
       ↓
    target service

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
    sign arbitrary challenge

它可能获得比你预期更大的能力。

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

所以 Sandbox 要有：

    denyUnixSockets

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
    requestCredential("github")
       ↓
    broker
       ↓
    validate(session)
       ↓
    return fake scoped token

测试：

    sandbox 能不能 print token？

目标：

    NO

## 9. 核心结论

> 最安全的 Credential 是 Agent 根本拿不到的 Credential。

这句话对：

    API Key
    Cloud Credential
    Git Credential
    SSH Agent
    Database Credential

全部成立。
