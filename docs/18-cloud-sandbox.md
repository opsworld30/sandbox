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

现代 Agent Runtime 一个重要的架构抽象是把 Agent 会话和执行环境分开：

    Agent Session
      - agent configuration
      - conversation / turn state
      - tool routing

    Execution Environment
      - CPU / Memory
      - workspace / files
      - processes
      - network policy

也就是说：

> 模型推理、Agent 编排和代码执行不一定发生在同一台机器。

以 OpenAI Agents API 为例，公开接口把 Session 与 Environment 分开建模，Environment 可以选择 OpenAI-hosted sandbox 或 self-hosted sandbox。注意这是 API 的对象模型，不应把它误写成所有产品都使用同一种 Harness 内部实现。

## 4. Cloud Session

一种常见的生命周期设计：

    create environment
       ↓
    provision sandbox
       ↓
    prepare workspace
       ↓
    attach / create Agent Session
       ↓
    agent work
       ↓
    persist required artifacts
       ↓
    suspend / destroy

是否支持 snapshot、resume、memory restore，取决于具体平台。不要把“Session 可继续”直接等同于“底层 VM 内存快照恢复”。

其他产品也会提供远程执行会话，但不同产品的“Cloud Session”“Cloud Agent”“Sandbox”概念和隔离边界并不完全相同。应按各自官方文档区分，不能只凭名称推断内部实现。

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


## 11. OpenAI Hosted Sandbox 的事实边界

截至 2026-11-18，OpenAI Agents API 的 OpenAI-hosted sandbox 文档描述的是一个 Linux workspace，采用 container 资源规格（small / medium / large），每个 Session 有独立 workspace，文件在 Sandbox 存续期间跨 turns 保留；还可以设置 network access（enabled / disabled / restricted）。

这属于 Agents API 的 OpenAI-hosted sandbox，不能和 Codex Cloud 的所有内部实现简单画等号。产品、API 和不同执行面需要分开描述。

参考：
- OpenAI-hosted sandboxes：https://developers.openai.com/api/docs/guides/agents-api/environments/openai-hosted
- Self-hosted sandboxes：https://developers.openai.com/api/docs/guides/agents-api/environments/self-hosted
- Sandbox lifecycle：https://developers.openai.com/api/docs/guides/agents-api/environments/lifecycle
