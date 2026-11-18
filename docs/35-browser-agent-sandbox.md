# 第 35 讲：Browser Agent 为什么需要另一层 Sandbox

## 1. Coding Agent 和 Browser Agent 不一样

Coding Agent：

    shell
    filesystem
    compiler
    git

Browser Agent：

    browser
    JavaScript
    DOM
    cookies
    downloads
    network

Browser Agent 的核心资产是：

    Cookie
    Session
    LocalStorage
    Browser Profile
    Credentials

## 2. 为什么不能把浏览器直接放进普通 Agent

如果：

    Agent
      ↓
    Browser
      ↓
    user's real Chrome profile

那么 Agent 可能间接接触：

    login sessions
    cookies
    local data

所以：

> Browser Profile 是 Credential Boundary 的一部分。

必须使用独立、受控的 Profile；不要把用户日常 Chrome Profile、真实 Cookie、密码库或扩展配置直接挂载给 Agent。若确实需要登录态，应通过专用账号、短期会话或受控凭证代理提供，并限定可访问的站点和操作。

## 3. 正确模型

    Agent
      ↓
    Browser Tool
      ↓
    isolated browser profile
      ↓
    browser process sandbox
      ↓
    network policy

而不是：

    Agent
      ↓
    personal Chrome

## 4. Downloads 也是文件系统边界

浏览器下载：

    /Downloads/file

如果 Sandbox 只允许：

    /workspace

那么下载必须：

    /workspace/downloads

否则：

    Browser
      ↓
    Download
      ↓
    Host filesystem

## 5. Browser Network 和 Agent Network

有时需要：

    Agent network = deny
    Browser network = allow

这意味着：

> 不同 Tool 可以拥有不同 Network Policy。

例如：

    Shell
      network = deny

    Browser
      network = allow-list

这也是 Tool-level Sandbox 的典型场景。

## 6. Browser → localhost

浏览器访问：

    http://localhost:3000

可能连接：

    dev server
    local admin
    database UI
    internal tool

所以 Browser Agent 也必须考虑：

    localhost
    private IP
    loopback
    IPv6

## 7. 实验

建立两个 Tool：

    shell
    browser

配置：

    shell:
      network = deny

    browser:
      network = allow example.com

然后问：

> Browser 能不能替 Shell 访问任意网络？

答案应该是：

    No

因为 Browser 自己也有独立的 Network Policy。

## 8. 核心结论

Browser Sandbox 是：

    Browser Process
      +
    Browser Profile
      +
    Filesystem
      +
    Network
      +
    Credential

不是简单：

    “浏览器放进 Docker”。


## 9. Browser 的三个边界要分开

1. **Browser Engine Sandbox**：Chromium / browser process 自身的 renderer / utility process 隔离。
2. **Browser Profile Isolation**：Cookie、LocalStorage、登录态、下载目录和扩展配置是否与用户真实 Profile 分开。
3. **Agent Runtime Sandbox**：Browser Tool 进程或远程 Browser Service 能访问哪些文件、网络和凭证。

浏览器引擎有自己的 Sandbox，不代表 Agent 的文件和网络策略已经正确；使用独立 Profile，也不代表 Browser 能访问的站点已经受到网络 allowlist 限制。

## 10. Browser 可能是远程服务

有些 Agent 的 Browser Tool 运行在远程 Browser Service，而不是本机 Chrome 进程。此时本地 Shell Sandbox 不会自动约束远程 Browser；文件下载、浏览器凭证、网络 egress 和日志都必须在 Browser Service 所在环境实施控制。

## 11. 浏览器访问 localhost 的风险

Browser Tool 与 Shell Tool 可能使用不同网络路径。即使 Shell Sandbox 禁止访问本机网络，也不能推断 Browser 一定被同一策略限制。必须分别测试：

- 127.0.0.1 / ::1；
- RFC1918 私有 IPv4；
- IPv6 ULA / link-local；
- 重定向后的目标；
- DNS 解析后 IP；
- 下载和上传路径。
