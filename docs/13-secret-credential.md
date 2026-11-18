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

优先考虑代理式访问：

    Agent
      ↓
    request GitHub operation
      ↓
    Credential Broker / Git Proxy
      ↓
    validate session + repository + operation
      ↓
    attach credential server-side
      ↓
    GitHub

这种模式下，真实 Token 留在 Broker 一侧，不返回给 Agent。

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

如果必须向执行环境发放 Token，至少应限制：

    scope = minimum required
    repository = specific repository
    permission = read-only / selected write
    TTL = short
    audience = expected service

短期 Token 可以缩短泄露窗口，但**只要 Token 被交给 Agent 进程，Agent 就可能读取、打印或外传它**。短期凭证是风险降低措施，不等于“秘密从未暴露”。

如果要求 Agent 本身拿不到真实凭证，应使用 Proxy / Broker 代为执行操作，而不是把 Token 返回给 Agent。

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

创建 Fake Broker：

    Agent
      ↓
    POST /git/push
      { repo, branch, commit }
      ↓
    Broker checks policy
      ↓
    Broker performs fake push
      ↓
    returns { ok: true }

实验要求：响应中只返回操作结果，不返回 `FAKE_GITHUB_TOKEN`。然后尝试从 Agent 的环境变量、文件系统和进程参数中搜索 Token，确认它根本没有进入执行环境。

如果要演示“短期 Token 下发”，必须明确标注：它仍然是 Agent 可读取的 Secret，只是 scope 和有效期更小。

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


## 12. SSH Agent 与 Unix Socket 也是 Credential

`SSH_AUTH_SOCK` 不一定暴露私钥文件，但允许进程向 SSH Agent 请求签名。它本身就是一种被委托的身份能力；如果 Sandbox 能访问该 socket，Agent 可能以你的身份完成认证操作。

同样，`/var/run/docker.sock`、云凭证代理 socket、数据库 socket 都可能把高权限能力带进 Sandbox。应按 Capability 设计是否允许访问，而不是只检查有没有密钥文件。

## 13. 参考资料补充

Claude Code 本地 Sandbox 的 credential masking / proxy 行为：https://code.claude.com/docs/en/sandboxing
Anthropic sandbox-runtime：https://github.com/anthropics/sandbox-runtime
OpenAI Agents API Sandbox Security：https://developers.openai.com/api/docs/guides/agents-api/environments/security
