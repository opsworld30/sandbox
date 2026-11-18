# 第 18 讲：Cloud Sandbox——为什么云端 Agent 又会大量使用 Container

## 1. 本地和云端为什么不一样

本地 Agent：

    Mac / Linux / Windows
        ↓
    用户真实开发环境
        ↓
    OS-level Sandbox

云端 Agent：

    Agent
      ↓
    Remote Environment
      ↓
    Container / VM / MicroVM

云端不需要迁就用户本机的：

- Xcode；
- Homebrew；
- 本地 SDK；
- 本地 IDE；
- 本地文件。

所以更容易把完整执行环境隔离出去。

## 2. Cloud Sandbox 的核心价值

第一：

> Agent 不在你的电脑上执行。

第二：

> 每个 Session 可以拥有独立环境。

第三：

> 可以统一控制网络、资源、生命周期。

第四：

> 可以把运行环境和模型 Harness 分开。

## 3. Harness 和 Environment

现代 Agent Runtime 一个很重要的抽象：

    Harness
      ↓
    Agent loop
    Tool calling
    Session

    Environment
      ↓
    CPU
    Memory
    Files
    Processes
    Network

也就是说：

> 模型运行逻辑不一定和代码执行环境在同一台机器。

OpenAI 当前 Agents API 就明确把 Harness 与 Environment 分开，Environment 可以是远程 Sandbox、本地机器、Container 等。

## 4. Cloud Session

典型生命周期：

    create session
       ↓
    provision sandbox
       ↓
    clone workspace
       ↓
    agent work
       ↓
    snapshot
       ↓
    suspend / destroy

用户回来：

    resume
       ↓
    restore snapshot
       ↓
    continue

GitHub Copilot 的 Cloud Sandbox 也采用类似 Session 与远程环境分离的思路。

## 5. Cloud Sandbox 为什么不能只看 Container

因为真正的云端安全问题还有：

- multi-tenant isolation；
- resource quota；
- network egress；
- credential isolation；
- snapshot isolation；
- host kernel attack surface；
- noisy neighbor；
- scheduler。

所以 Container 只是其中一个组件。

## 6. OpenAI Hosted Sandbox 的思路

当前公开文档中，OpenAI Hosted Sandbox 提供 Linux workspace，Agent 可以在其中执行代码、修改文件、安装依赖和生成 artifact。

应用也可以选择：

    self-hosted environment

也就是说：

> Sandbox 可以是托管环境，也可以是你自己的执行环境。

## 7. Self-hosted Sandbox

Self-hosted：

    Your infrastructure
        ↓
    Executor
        ↓
    Agent Harness
        ↓
    Sandbox

好处：

- 私有网络；
- 自定义镜像；
- 自定义硬件；
- 数据合规；
- 内部工具。

代价：

- 自己维护隔离；
- 自己维护补丁；
- 自己维护资源；
- 自己维护网络和凭证。

## 8. Cloud Sandbox 的核心对象

建议抽象成：

    Environment
      ├── image / template
      ├── workspace
      ├── packages
      ├── network policy
      ├── credentials
      ├── resources
      └── lifecycle

    Session
      ├── agent config
      ├── conversation
      └── environment reference

这两个对象分开后，很多设计自然清晰。

## 9. 课堂练习

设计：

    POST /environments
    GET /environments/{id}
    POST /sessions
    POST /sessions/{id}/resume
    POST /environments/{id}/snapshot

然后思考：

> 为什么 Session 不应该等同于 Environment？

因为一个 Environment 可以在不同 Session 中复用，而 Session 保存的是 Agent 状态和对话。

## 10. 面试题

### Q：为什么云端 Agent 更容易使用 Container？

因为云端执行环境不需要保持用户本机 OS 和工具链兼容性，同时 Container 可以快速、标准化地提供隔离用户空间。

### Q：为什么还需要 MicroVM？

当 Container 的共享 Kernel 风险和多租户安全要求不能接受时，需要更强的 Kernel / VM 边界。
