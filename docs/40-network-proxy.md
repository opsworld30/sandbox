# 第 40 讲：Network Proxy——为什么“禁止联网”和“允许指定域名”是两个完全不同的问题

## 1. 最简单的 Network Sandbox

    network = disabled

优点：

    简单
    安全边界清晰

缺点：

    npm install
    pip install
    git clone
    package download

都不能做。

所以 Coding Agent 通常需要：

> Restricted Network

## 2. 两种模型

### Model A：Direct Egress

    Agent
      ↓
    Internet

然后由 OS / firewall 限制。

### Model B：Proxy Egress

    Agent
      ↓
    Proxy
      ↓
    Policy
      ↓
    Internet

Proxy 模式更容易：

    audit
    allowlist
    credential mediation
    domain policy

## 3. HTTP 和 HTTPS

HTTP：

    Agent
      ↓
    Proxy
      ↓
    GET example.com

HTTPS 常见：

    CONNECT example.com:443
      ↓
    Proxy
      ↓
    TCP tunnel

如果只需要控制：

    destination host
    destination port

不一定需要解密 HTTPS。

## 4. Domain Allowlist

例如：

    github.com
    pypi.org
    registry.npmjs.org

但实际工程要考虑：

    subdomain
    redirect
    CDN
    IPv4
    IPv6
    DNS

例如：

    pypi.org
       ↓
    CDN
       ↓
    another domain

所以“只允许一个域名”在真实系统里不是一个简单字符串比较。

## 5. DNS Policy

如果：

    Agent
      ↓
    DNS
      ↓
    attacker.example
      ↓
    10.0.0.5

那么仅检查 hostname 可能不够。

需要考虑：

    hostname
    resolved IP
    redirect target
    connection target

## 6. localhost

最重要的测试：

    127.0.0.1
    localhost
    ::1

因为：

    localhost
       ↓
    IDE
    DB
    Redis
    Admin API

所以：

    Internet allow
    !=
    Local network allow

## 7. Private IP

典型：

    10.0.0.0/8
    172.16.0.0/12
    192.168.0.0/16

还要注意：

    link-local
    IPv6 private/local ranges

生产环境不能只写三个 IPv4 CIDR 就认为内网完全封住。

## 8. Unix Socket

网络安全也包括：

    Unix domain socket

例如：

    docker.sock

所以：

    TCP Network Policy
      +
    Unix Socket Policy

才比较完整。

## 9. Egress Gateway

云端 AI Sandbox 可以设计：

    Sandbox
      ↓
    Egress Gateway
      ↓
    Policy
      ↓
    Internet

Gateway 可以记录：

    session_id
    destination
    port
    bytes
    decision
    timestamp

这就把：

    Network Security

和：

    Observability

连接起来。

## 10. Credential Injection

更高级：

    Sandbox
      ↓
    proxy
      ↓
    inject scoped credential
      ↓
    GitHub

这样：

    Agent

不需要直接拿：

    GitHub Token

这就是：

> Network Proxy + Credential Broker

组合。

## 11. 实验

设计：

    NetworkPolicy {
      mode: allowlist
      domains:
        - github.com
        - pypi.org
      deny_private_network: true
      deny_localhost: true
    }

测试：

    github.com       → allow
    pypi.org         → allow
    example.com      → deny
    127.0.0.1        → deny
    10.0.0.1         → deny

## 12. 最终网络模型

    Agent
      ↓
    Network Policy
      ↓
    Sandbox
      ↓
    Egress Proxy
      ↓
    DNS / Firewall
      ↓
    Internet

不要把：

    HTTP_PROXY

当成完整安全边界。

真正安全的边界必须能够阻止：

    direct socket

绕过 Proxy。

## 13. 面试题

为什么 HTTP Proxy 不能单独作为 Sandbox？

因为程序可以直接创建 socket 绕过 HTTP_PROXY。因此需要 OS/network enforcement 保证流量不能绕过代理或防火墙。
