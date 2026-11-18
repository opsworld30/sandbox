# 第 13 讲：Secret / Credential 隔离

## 1. 最危险的一个误区

很多人认为：

    Sandbox
      +
    ~/.ssh 不可读

就安全了。

如果环境变量里还有：

    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY
    GITHUB_TOKEN
    DATABASE_PASSWORD

Agent 仍然可能直接：

    env

所以：

> Credential Isolation 是 Sandbox 的独立安全层。

## 2. 最差的设计

    Agent
      ↓
    process environment
      ↓
    real secret

这样 Agent 进程本身就拥有秘密。

如果 Agent 被 Prompt Injection：

    read env
       ↓
    secret
       ↓
    exfiltrate

## 3. 更好的设计：Credential Broker

    Agent
      ↓
    request GitHub
      ↓
    Credential Broker
      ↓
    short-lived credential
      ↓
    GitHub

真实 Token 不直接暴露给 Agent。

## 4. Scoped Credential

不要：

    GITHUB_TOKEN = full admin

而应该：

    repo = read-only
    duration = 10 min
    repository = specific repo

这就是：

> Least Privilege Credential

## 5. 为什么短期 Token 更好

如果：

    Token TTL = 10 min

泄露后的窗口更小。

如果：

    Token TTL = 1 year

那么一次 Prompt Injection 可能造成长期风险。

## 6. Credential Proxy

另一种模式：

    Agent
      ↓
    HTTPS Proxy
      ↓
    approved.github.com
      ↓
    Proxy injects real credential

Agent 看到的不是：

    Authorization: real-token

而是一个受控的 placeholder / scoped credential。

现代 Agent Sandbox 已经开始使用类似的 Credential Proxy 思路。

## 7. 环境变量 Masking

例如：

    API_TOKEN = real-secret

Agent 工具内部只看到：

    API_TOKEN = MASKED

当访问：

    api.example.com

Proxy 才注入真正的认证信息。

因此：

    Secret
      ↓
    outside sandbox
      ↓
    proxy
      ↓
    approved destination

## 8. 为什么 Git 特别适合这种设计

Agent 经常需要：

    git clone
    git fetch
    git push

但你不希望：

    Agent
      ↓
    GITHUB_TOKEN
      ↓
    arbitrary API

所以可以：

    Agent
      ↓
    Git Credential Proxy
      ↓
    verify repo / branch / operation
      ↓
    GitHub

## 9. 一个完整模型

    Agent
       │
       ├── filesystem sandbox
       │
       ├── network sandbox
       │
       └── credential broker
                    ↓
               real secret

这样即使 Agent 被攻破，攻击面仍然受到限制。

## 10. 课堂练习

不要使用真实 Token。

创建：

    FAKE_GITHUB_TOKEN=demo-token

然后比较：

    process environment
       vs
    broker-based access

重点不是实现真正 GitHub 登录，而是理解：

> Agent 为什么不应该直接持有高价值 credential。

## 11. 面试题

### Q：为什么 Sandbox 不能解决 Credential 问题？

因为如果秘密本身就在 Sandbox 可读的环境变量、文件或 FD 中，那么 Sandbox 已经无法阻止“合法读取”。

### Q：为什么要使用短期、最小权限 credential？

降低泄露后的 Blast Radius。

## 参考

Anthropic Claude Code on the web:
https://www.anthropic.com/research/claude-code-sandboxing

OpenAI sandbox security:
https://developers.openai.com/api/docs/guides/agents-api/environments/security
