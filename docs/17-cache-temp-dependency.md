# 第 17 讲：Cache、Temp 与 Dependency 隔离

## 1. 为什么 Cache 也是安全边界

为了性能，Sandbox 不可能每次都：

    npm install
    pip install
    cargo fetch

所以会使用：

    npm cache
    pip cache
    cargo registry
    Go module cache

这会带来两个问题：

1. 性能；
2. 信息泄露 / 污染。

## 2. Shared Cache 的问题

Agent A：

    install dependency

Agent B：

    reuse cache

如果 Cache 中存在：

- 私有 package；
- token；
- 用户路径；
- 恶意 artifact；

就可能出现 cross-session leakage。

## 3. Cache 隔离模型

可以分成：

    Global immutable cache
    Per-user cache
    Per-project cache
    Per-session cache

安全等级通常：

    shared
      ↓
    user
      ↓
    project
      ↓
    session

越靠后隔离越强，成本也越高。

## 4. Cache Poisoning

例如：

    Agent A
      ↓
    writes malicious cache artifact

Agent B：

    reuse cache
      ↓
    execute artifact

因此：

> Cache 不是单纯性能组件，也是 Supply Chain Boundary。

## 5. Temp Directory

很多程序会使用：

    /tmp

如果多个 Session 共享：

    Session A
      ↓
    /tmp/file

    Session B
      ↓
    read /tmp/file

就可能发生信息泄露。

所以云 Sandbox 通常需要：

    per-session temp

## 6. Dependency 安全

AI Agent 经常执行：

    npm install
    pip install
    cargo add

这些命令会下载并执行第三方代码。

因此：

    Network Sandbox
       +
    Filesystem Sandbox
       +
    Dependency policy

需要一起考虑。

## 7. postinstall 风险

某些包安装时可能运行：

    install script

所以：

    npm install
       ↓
    arbitrary code execution

本质上就是 Sandbox 要保护的场景。

## 8. 推荐架构

    Sandbox
       ├── workspace
       ├── private temp
       ├── read-only base cache
       └── writable session cache

这样既能复用大部分依赖，又减少跨 Session 污染。

## 9. 课堂练习

设计：

    cache/
    session-A/
    session-B/

定义：

    base cache → read only
    session cache → read/write

然后讨论：

> 为什么不应该让 Agent 任意修改共享基础 Cache？

## 10. 面试题

### Q：Cache 为什么属于 Sandbox 设计？

因为 Cache 可能包含文件、依赖、凭证或用户数据，而且跨 Session 共享会形成新的信息流和执行边界。

### Q：为什么依赖安装是高风险操作？

因为安装过程可能执行第三方脚本，并获得当前 Sandbox 的文件、网络和进程权限。
