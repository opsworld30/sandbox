# 第 2 讲：OpenSandbox 与自建难度

> 本讲的 OpenSandbox 指开源项目 [opensandbox-group/OpenSandbox](https://github.com/opensandbox-group/OpenSandbox)，不是 Linux Kernel 的某个 Sandbox API，也不是所有沙箱的统称。以下架构以项目当前公开文档为准，项目会持续演进。

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

## 5. OpenSandbox 当前架构应该怎么看

不要把它想成“一个 Docker 命令的 HTTP 包装”。

项目公开架构可以拆成：

    Client SDK / CLI / MCP
              |
              v
    Lifecycle Control Plane
      - 鉴权
      - 参数校验
      - Session / Sandbox 生命周期
      - 元数据与调度
              |
              v
    Runtime Backend
      - Docker：本地 / 单机容器
      - Kubernetes：容器型 Sandbox Provider
      - FastSandbox 集成：模板化 MicroVM 路径
              |
              v
    Sandbox Data Plane
      - workload container / guest
      - execd：命令、文件、PTY 等执行接口
      - 可选 Code Interpreter / Jupyter
              |
              v
    OS / Container Runtime / Hypervisor

网络和安全是旁路但关键的层：

    Sandbox
       |
       +--> Egress Sidecar / Egress Process
       |       - 域名 / IP 策略
       |       - DNS / nftables（依后端而定）
       |       - 可选 Credential Vault / Proxy
       |
       +--> Ingress / Endpoint Access
       |
       +--> Resource Limits / Audit / Metrics

需要特别理解两条数据路径：

1. 生命周期请求由 Control Plane 处理；
2. 命令、文件、PTY 等执行流量可能通过解析后的 endpoint 直连数据面，也可能经过代理或网关；不要假设所有执行字节都穿过 Lifecycle Server。

Runtime-neutral API 也不代表每个 Backend 的能力完全相同。Volume、egress、snapshot、MicroVM 等能力必须按实际 Backend 的能力矩阵核对。

## 6. 自建难度应该怎么评估

真正的难点不是写出 `POST /run`，而是把下面这些责任做完整：

- 身份认证与 Session 授权；
- 生命周期与资源回收；
- 工作区挂载和文件权限；
- 进程树终止；
- 网络 egress 强制执行；
- 凭证不下发到不可信进程；
- CPU / Memory / PID / Disk 配额；
- 日志、指标和安全审计；
- 后端能力差异与降级策略；
- Sandbox 失败时 fail-closed，而不是自动无隔离重试。

## 7. OpenSandbox 应该学什么

重点不是复制某个项目的实现，而是学习：

- Control Plane / Data Plane 分离；
- Runtime Provider 抽象；
- Session 生命周期；
- Execution / File / PTY API；
- Workspace 与 Volume；
- Egress / Credential Broker；
- Resource / Audit / Observability；
- Backend capability matrix。

## 8. 本讲实验

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

## 参考资料

- OpenSandbox 仓库：https://github.com/opensandbox-group/OpenSandbox
- Architecture：https://github.com/opensandbox-group/OpenSandbox/blob/main/docs/architecture/index.md
- Quick Start：https://github.com/opensandbox-group/OpenSandbox/blob/main/docs/getting-started/index.md

**版本提示：** OpenSandbox 的 runtime provider、FastSandbox / MicroVM 集成和各语言 SDK 的能力会变化。部署前必须以仓库当前版本的架构文档、配置和 SDK capability matrix 为准。
