# 第 2 讲：OpenSandbox 与自建难度

## 1. “能执行代码”不等于 Sandbox

最简单的执行服务：

    POST /run
    command = python main.py

它解决的是 Execution。

真正 Sandbox 还要解决：

    Execution
    Isolation
    Filesystem Policy
    Network Policy
    Resource Limit
    Lifecycle
    Audit

## 2. 为什么难度会迅速增加

假设 Agent 执行：

    npm install

你马上会遇到：

- npm 从哪里下载？
- 能不能访问公司内网？
- package 是否可以执行 install script？
- node_modules 写在哪里？
- 运行时间多久？
- 子进程多少？
- stdout 多大？
- 失败后 Session 是否保留？
- 下一次执行是否共享文件？

因此 Sandbox 本质上是一个 Runtime，而不是一个 subprocess 函数。

## 3. Session 为什么重要

AI Coding 通常是多步过程：

    create session
       ↓
    write files
       ↓
    run tests
       ↓
    modify code
       ↓
    run again
       ↓
    destroy

所以需要：

    Session
      ├── workspace
      ├── process tree
      ├── policies
      ├── resources
      └── audit events

## 4. Backend 抽象

推荐：

    SandboxManager
          ↓
    SandboxBackend
      ├── LocalProcess
      ├── Seatbelt
      ├── Bubblewrap
      ├── Docker
      └── MicroVM

上层只知道：

    create
    exec
    read_file
    write_file
    destroy

这样以后换隔离技术，不需要改 Agent。

## 5. OpenSandbox 应该学什么

重点不是复制某个项目的实现，而是学习：

- Runtime 抽象；
- Session 生命周期；
- Execution API；
- Workspace；
- Backend；
- Resource；
- Network；
- File API。

## 6. 本讲实验

画出自己的 Sandbox API：

    POST /sessions
    POST /sessions/{id}/exec
    GET  /sessions/{id}/events
    DELETE /sessions/{id}

然后回答：

> 哪一层负责安全策略？哪一层负责真正执行？

## 面试题

为什么 Sandbox 要做 Backend 抽象？

因为不同平台和不同安全等级需要不同执行后端。Agent 不应该和 Docker、Seatbelt、bubblewrap 等具体实现耦合。
