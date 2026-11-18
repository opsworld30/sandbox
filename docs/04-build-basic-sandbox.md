# 第 4 讲：自研简陋 Sandbox——从 Runner 到 Runtime

## 1. 第一步：Session

    class SandboxSession:
        id
        workspace
        created_at
        timeout

Runtime：

    create()
    exec()
    destroy()

## 2. 为什么必须有生命周期

Agent 不是执行一次命令。

它可能：

    create
      ↓
    install
      ↓
    test
      ↓
    edit
      ↓
    test
      ↓
    package
      ↓
    destroy

如果没有 destroy：

- 后台进程可能残留；
- 临时文件可能残留；
- socket 可能残留；
- cache 可能泄露；
- 资源可能一直占用。

## 3. Manager 和 Backend

Manager：

- Session；
- 生命周期；
- policy；
- audit；
- quota。

Backend：

- 创建执行环境；
- 启动进程；
- 收集结果；
- 销毁环境。

结构：

    SandboxManager
          ↓
    SandboxBackend
          ↓
    OS / Container / VM

## 4. 常见错误

### 错误一：命令黑名单

    if "rm" in command:
        deny()

问题是 shell、解释器、脚本、别名和子进程都可以绕开字符串判断。

### 错误二：只限制 cwd

不能阻止绝对路径和 symlink。

### 错误三：只限制网络

文件泄露仍然存在。

### 错误四：只使用 Docker

Docker 是一种执行后端，不等于完整安全策略。

### 错误五：没有审计

出问题后你不知道：

- Agent 执行了什么；
- 访问了什么文件；
- 连接了什么网络；
- 为什么被拒绝。

## 5. 本阶段最重要的转折

从：

    Application
       ↓
    subprocess

升级到：

    Policy
       ↓
    Sandbox Runtime
       ↓
    OS
       ↓
    Kernel

下一讲开始进入现代 AI Coding Agent 的真实实现思路。

## 本讲必须补上的一个边界

如果示例只执行：

```python
subprocess.run(argv, timeout=10)
```

它不能证明整棵子进程树都能被可靠终止。请把下面三个问题分开：

1. 命令本身是否超时；
2. 命令启动的后代进程是否全部退出；
3. Session 销毁后是否还残留后台进程、端口或文件句柄。

生产 Runtime 应给每个 Session 建立可整体清理的进程边界（例如 Linux cgroup v2 / Windows Job Object），并在 destroy 后验证没有残留进程。

## 本讲实验代码

- [Runner 与 Session 生命周期](../labs/03-runner-session/README.md)
- [Mini Runtime](../labs/17-mini-runtime/README.md)

这些是对应主题的可运行教学实验；具体操作系统要求和安全边界以各 Lab README 为准。
