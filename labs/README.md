# Hands-on Labs：可运行实验索引

课程中的实验不再只保留流程图或伪代码。每个可执行实验都放在独立目录，包含源码、运行步骤、预期结果和安全边界说明。

> 重要：应用层 Demo 不等于 OS-level Sandbox。每个 Lab 的 README 都会标明它是策略模拟、Runner 原型，还是实际调用操作系统隔离能力。没有实机验证的 OS 实验不会标注为“已通过”。

## 实验目录

| Lab | 主题 | 主要文件 | 环境 |
|---:|---|---|---|
| 01 | seccomp syscall filter | [README](01-seccomp/README.md) · [C](01-seccomp/seccomp_demo.c) | Linux VM / C / libseccomp |
| 02 | Landlock 文件系统隔离 | [README](02-landlock/README.md) · [C](02-landlock/landlock_demo.c) | Linux Kernel / C |
| 03 | Runner、Session、超时与输出上限 | [README](03-runner-session/README.md) · [Python](03-runner-session/runner.py) | Python 3.10+ / Linux / macOS |
| 04 | bubblewrap 文件、PID、Network Namespace | [README](04-bubblewrap/README.md) · [脚本](04-bubblewrap/run.sh) | Linux VM / bwrap |
| 05 | macOS Seatbelt Profile | [README](05-macos-seatbelt/README.md) · [Profile](05-macos-seatbelt/profile.sb) | macOS / sandbox-exec |
| 06 | Network Egress Domain Policy | [README](06-network-policy/README.md) · [Python](06-network-policy/policy.py) | Python 3.10+ |
| 07 | Fake Credential Broker | [README](07-credential-broker/README.md) · [Broker](07-credential-broker/broker.py) | Python 3.10+ |
| 08 | Policy Engine / Effective Policy | [README](08-policy-engine/README.md) · [Python](08-policy-engine/policy.py) | Python 3.10+ |
| 09 | Process Tree / Process Group 清理 | [README](09-process-tree/README.md) · [Python](09-process-tree/tree_demo.py) | POSIX |
| 10 | npm Lifecycle / Supply Chain | [README](10-supply-chain/README.md) · [脚本](10-supply-chain/run.sh) | Node.js / npm |
| 11 | Git Worktree / Snapshot | [README](11-worktree-snapshot/README.md) · [脚本](11-worktree-snapshot/run.sh) | Git |
| 12 | Audit Event / Secret Redaction | [README](12-audit-events/README.md) · [Python](12-audit-events/audit.py) | Python 3.10+ |
| 13 | Multi-Agent Workspace / Artifact Broker | [README](13-multi-agent-workspaces/README.md) · [Python](13-multi-agent-workspaces/demo.py) | Python 3.10+ |
| 14 | CPU / Memory / File Size Resource Limits | [README](14-resource-limits/README.md) · [Python](14-resource-limits/resource_demo.py) | Linux VM |
| 15 | Tool Capability / Shell、Browser、MCP 分权 | [README](15-tool-capabilities/README.md) · [Python](15-tool-capabilities/policy.py) | Python 3.10+ |
| 16 | Control Plane / Worker Session API | [README](16-remote-session-api/README.md) · [Server](16-remote-session-api/server.py) | Python 3.10+ |
| 17 | Mini AI Coding Sandbox Runtime | [README](17-mini-runtime/README.md) · [Runtime](17-mini-runtime/runtime.py) | Python 3.10+ |
| 18 | Security Regression Matrix | [README](18-security-regression/README.md) · [脚本](18-security-regression/run.sh) | Python 3.10+ |
| 19 | Per-command Sandbox Expansion | [README](19-command-expansion/README.md) · [Python](19-command-expansion/expansion.py) | Python 3.10+ |
| 20 | Windows Sandbox VM 配置 | [README](20-windows-sandbox/README.md) · [WSB](20-windows-sandbox/sandbox.wsb) | Windows Sandbox |
| 21 | Prewarm / Snapshot / Pool 生命周期 | [README](21-prewarm-pool/README.md) · [Python](21-prewarm-pool/pool.py) | Python 3.10+ |
| 22 | MCP stdio / JSON-RPC 最小 Server | [README](22-mcp-stdio/README.md) · [Server](22-mcp-stdio/server.py) | Python 3.10+ |
| 23 | Shared Cache / Session Cache 完整性 | [README](23-cache-isolation/README.md) · [Python](23-cache-isolation/cache.py) | Python 3.10+ |

## 44 讲与 Lab 对照

| 课程章节 | 对应实验 |
|---|---|
| 01～04 Sandbox 基础、Runner、Session | 03、17 |
| 05～07 OS Sandbox、Seatbelt、Linux | 04、05 |
| 08 seccomp | 01 |
| 09 Filesystem Sandbox | 02、04 |
| 10 Network Sandbox | 04、06 |
| 11 Permission 与 Sandbox | 08、19 |
| 12 Prompt Injection | 06、15、18 |
| 13、32 Credential Isolation | 07 |
| 14 MCP Server | 15、22 |
| 15、33 Process Tree / LSP | 09、15 |
| 16、42 Git / Worktree / Snapshot | 11、21 |
| 17 Cache / Temp / Dependency | 10、23 |
| 18、44 Cloud / Remote Execution | 16、17、21 |
| 19 Container / MicroVM / VM / OS Sandbox 对比 | 04、05、20 |
| 20、24 AI Sandbox Runtime / Final Project | 17、18 |
| 21 Prewarm / Snapshot / Pool | 11、21 |
| 22 Audit / Observability | 12 |
| 23 Security Testing | 18 |
| 25 Codex Sandbox | 03、04、17 |
| 26 Claude Code Sandbox | 05、07 |
| 27 Cursor Sandbox | 08 |
| 28 VS Code / Copilot Sandbox | 15、22 |
| 29 Gemini CLI Sandbox Expansion | 19 |
| 30 Windows Sandbox | 20 |
| 31 Approval / Permission / Sandbox | 08、19 |
| 34 Untrusted Repository / Supply Chain | 10、23 |
| 35 Browser Agent Sandbox | 06、15 |
| 36 Threat Model | 18（测试矩阵） |
| 37 Policy Engine | 08、17 |
| 38 Sandbox Escape | 02、04、18 |
| 39 Resource Isolation | 14 |
| 40 Network Proxy | 04、06 |
| 41 Tool Capability Model | 15、22 |
| 43 Multi-Agent Isolation | 13 |

## 推荐动手顺序

1. 先跑 03、08、12、15、17：理解 Runner、Policy、Audit、Tool Capability 和 Runtime。
2. 再跑 01、02、04、05：进入真实 OS / Kernel Enforcement。
3. 再跑 06、07、09、10、11、14：网络、凭证、进程、供应链、快照和资源。
4. 最后跑 16、18、19、20、21、22、23：云端 API、回归测试、扩权、Windows、Prewarm、MCP 和 Cache。

## 验证状态约定

- **代码已提交**：源码和运行说明已进入仓库。
- **可本机运行**：依赖安装后可执行；仍需用户环境验证。
- **需要指定 OS / VM**：必须在对应系统或 disposable VM 中运行。
- **非生产实现**：策略模拟或教学原型，不可当作安全边界。

所有实验都应先阅读对应 README 的安全边界。不要在日常工作机、生产环境或含真实凭证的目录中运行逃逸、资源压力或不可信代码实验。
