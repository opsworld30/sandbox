# 第 27 讲：拆解 Cursor Sandbox——Sandbox、Permissions、Classifier 为什么要分开

## 1. Cursor 当前 Run Modes 与 Sandbox 的关系

截至 2026-11-18，Cursor 当前公开 Run Modes 为：

    Auto-review
    Allowlist
    Run Everything

Run Modes 决定工具调用如何自动执行、何时需要用户确认；Sandbox 则是叠加在 Shell / Terminal 命令上的 OS 访问限制。它们不是同一个开关。

Auto-review 适用于 Shell、MCP 和 Fetch 调用；但 OS Sandbox 主要用于受支持的本地 Shell 命令。Cursor Cloud Agents 使用独立的专用机器执行，不使用本地 Run Modes 的审批流程。

产品模式会随版本变化，以下按当前公开文档描述。

## 2. 三个问题

### 问题 A：Agent 能不能自动执行？

这是：

    Permission / Run Mode

### 问题 B：执行以后能访问什么？

这是：

    Sandbox

### 问题 C：这个动作是不是看起来危险？

可以由：

    Classifier

辅助判断。

所以：

    Classifier
       ↓
    Policy Decision
       ↓
    Sandbox Enforcement

而不是：

    LLM Classifier
       ↓
    “安全”
       ↓
    直接放行

## 3. Cursor Auto-review Classifier 不是 Security Boundary

Cursor 当前 Auto-review 使用后端 LLM Classifier 审查某些不在 Sandbox 内执行的动作，以及 Sandbox 失败后申请在 Sandbox 外重试的动作。

Classifier 在 Cursor 当前 Auto-review 中运行于 Cursor 后端，使用 Cursor 管理的小型模型；当前文档列出 Gemini 3.5 Flash Lite，并以 Haiku 作为 fallback。审查时它还可以对本机文件执行只读的 ReadFile、Grep、Glob、ListDir 等操作，以查看待执行脚本或相关上下文。

Classifier 仍可能误判：

    false positive
    false negative

因此：

    “Classifier 认为安全”

不等于：

    OS enforcement 已允许

反过来，Sandbox 也不能只依赖 Classifier 的结论。真正的文件和网络边界仍由 Sandbox policy 与 OS enforcement 实现。

## 4. Cursor 当前 Sandbox 覆盖什么

Cursor 文档明确把 Sandbox 描述为对**受支持的 Terminal / Shell 命令**施加约束，主要涉及：

- workspace 文件；
- protected paths；
- network allowlist；
- temporary directories；
- extra read / write paths。

平台实现：

    macOS
      → Seatbelt via sandbox-exec

    Linux
      → native sandbox with Landlock
      → bubblewrap fallback

Linux 环境还可能在 Sandbox 内看到 user namespace 映射后的 UID（例如 UID 0），不能把容器内的 UID 直接理解成宿主机真实 UID。

这说明：Sandbox 不是要求“所有命令都必须成功”，而是优先让安全范围内的命令自动运行。

## 5. Cursor 的 Auto-review 流程很值得研究

当前文档描述的顺序大致是：

    Agent Tool Call
       ↓
    allowlisted call?
       ├── yes → run outside sandbox
       └── no
            ↓
    shell command supported by sandbox?
       ├── yes → run in sandbox
       └── no → Auto-review classifier
                    ↓
                 allow / block / ask

如果 Sandbox 内命令因权限限制失败，也可以进入 Classifier review，再决定是否允许 Sandbox 外重试。

因此必须修正一个常见误解：

> Cursor 并不是“永远不允许 Sandbox 外执行”；它可以经过 Auto-review / approval 流程放行某些外部执行。

这也意味着用户必须理解：批准 Sandbox 外执行会移除该次操作的文件系统和网络限制。

## 6. Sandbox JSON 和 Permission JSON 为什么应该分开

假设：

    permissions.json

表达：

    “什么动作需要审批？”

而：

    sandbox.json

表达：

    “Sandbox 里面能访问什么？”

这是两个维度。

错误设计：

    allow = true
    → everything allowed

正确设计：

    permission decision
       +
    sandbox capability

## 7. 为什么项目级配置很重要

AI Coding Agent 通常有：

    User Policy
    Project Policy
    Team Policy
    Hard-coded Safety Policy

最终可能：

    Effective Policy
       =
    merge(User, Project, Team, System)

但必须注意：

> 下层配置不能随意削弱上层安全边界。

例如 Team：

    deny ~/.ssh

Project：

    allow ~/.ssh

最终应该：

    DENY

## 8. Cursor 的关键安全提醒

Cursor 当前 Auto-review 允许 Sandbox 失败的命令进入 Classifier review；Classifier 可能允许它在 Sandbox 外执行，也可能阻止并要求 Agent 换方案或向用户请求批准。

因此教学重点不是“产品绝不降级”，而是：

1. 区分 Sandbox 内执行与 Sandbox 外执行；
2. 理解 classifier 只是决策辅助，不是强制隔离；
3. 观察用户是否会被明确告知外部执行；
4. 设计自己的 Runtime 时，避免静默、自动、无审批地从 Sandbox 降级到 unrestricted。

## 9. 实验：自己实现 Effective Policy

输入：

    system:
      deny ~/.ssh

    team:
      allow github.com

    project:
      allow workspace write

    user:
      allow pypi.org

输出：

    EffectivePolicy

    filesystem:
      workspace write
      ~/.ssh deny

    network:
      github.com
      pypi.org

## 10. 面试题

为什么 Classifier 不能代替 Sandbox？

因为 Classifier 是概率模型，可能误判；Sandbox 是在进程实际执行时强制限制文件、网络等能力。前者是风险判断，后者是技术 enforcement。

## 参考

Cursor Run Modes:
https://cursor.com/docs/agent/security/run-modes

Cursor sandbox engineering deep dive:
https://cursor.com/blog/secure-sandbox

**核验日期：2026-11-18。** Run Modes、Classifier 模型和平台实现会随 Cursor 版本变化。


## 11. 配置文件各自负责什么

当前 Cursor 文档区分：

- `permissions.json`：定义 allow / deny 规则；Auto-review 先应用这些规则，再对未覆盖的动作使用 Classifier；
- `sandbox.json`：配置 Sandbox 能访问的路径、网络域名、临时目录等。

这两个文件不是一个总开关。即使 Permission 允许某个动作，也不代表 Sandbox 自动授予该动作需要的文件或网络能力。


## 12. Auto-review 不只审查 Shell

当前 Cursor Auto-review 也适用于 MCP 和 Fetch 工具调用：

    allowlisted shell / MCP / Fetch
       → run outside Sandbox

    other shell commands
       → Sandbox when supported

    shell cannot use Sandbox / sandboxed command fails
       → LLM Classifier review

    other MCP / Fetch calls
       → LLM Classifier review

    classifier allows
       → action can run outside Sandbox

因此不要把 Cursor Auto-review 画成“Shell Sandbox 的一层 Kernel 防护”。它是跨工具调用的审批 / 风险判断流程，真正的 OS Sandbox 当前主要用于受支持的 Terminal Shell 命令。

## 13. Cursor 网络默认行为

Cursor 的 Sandbox 默认阻止任意网络访问；网络模式可选择仅使用 `sandbox.json` allowlist、allowlist 加 Cursor 内置默认域名，或允许全部网络。当前默认网络模式是 allowlist + 内置默认域名。

这和 VS Code Copilot Harness 的 `allowNetwork=true` 默认值不同，不能把不同产品的默认配置混成一套。


## 14. Read Access 默认值也会影响实际边界

Cursor 当前 Read Access 的默认模式是 `System`，Agent 可以读取 Workspace 外的文件而无需先请求批准。若要把读取范围收窄到项目，需要选择 `Workspace` 并配置 Read Allowlist。

因此要分开理解：

- Shell Sandbox 的执行限制；
- Agent 文件读取权限；
- Auto-review 的审批策略。

不能只开启 Shell Sandbox，就推断 Agent 的所有文件读取都只限于当前 Workspace。

当前公开的本地 Sandbox 平台选项为 macOS 与 Linux；不要把这套实现直接推断到 Windows。
