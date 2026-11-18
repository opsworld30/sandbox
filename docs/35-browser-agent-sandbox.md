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

> Browser Profile 本身就是 Credential Boundary。

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
