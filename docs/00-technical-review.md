# AI Sandbox 课程技术审查报告

> 审查日期：2026-11-18  
> 审查范围：第 1～44 讲、README、Lab 01（seccomp）、Lab 02（Landlock）  
> 审查目标：修正可确认的技术错误、补齐机制边界、区分产品事实与自研架构建议。

## 1. 审查结论

课程主线成立：从 Sandbox 概念、OS 原语、Agent Tool 安全，到 Runtime / Cloud / Multi-Agent 架构，顺序基本合理。

本轮发现并修订了多类容易误导读者的问题：

- 把某个产品的实现误写成所有平台的通用方案；
- 把 Landlock、seccomp、Network Namespace 的能力范围讲得过宽；
- 把 Permission / Approval / Classifier 当成 OS Sandbox 的替代品；
- 把 MCP、LSP、Browser 等工具默认当成 Agent 的子进程；
- 把 Git Worktree、HTTP_PROXY、短期 Token 等机制误认为完整安全边界；
- 把 cgroup I/O 控制误认为磁盘容量配额；
- 把 Sandbox timeout 误认为完整进程树清理；
- 把 Prewarm、Snapshot、Pool 混成同一种机制。

**结论：** 已修订已确认的问题，但这份课程不是经过独立安全认证的生产级 Sandbox 实现，也不能据此宣称“数学意义上零错误”。产品内部实现会变化；每次发布课程时应重新核对官方资料和具体版本。

## 2. 逐讲审查记录

| 讲次 | 审查结果 | 本轮处理重点 |
|---:|---|---|
| 01 | 基础概念正确 | 强调限制影响范围，不承诺绝对安全 |
| 02 | 需要补充项目架构 | 明确 OpenSandbox 是开源项目；补充 Control Plane、Data Plane、Runtime Provider、execd、Egress |
| 03 | 需要补充进程生命周期 | 说明 subprocess timeout 不保证清理所有后代进程 |
| 04 | 需要补充执行边界 | 补充 Session 级进程集合、destroy 与残留进程验证 |
| 05 | 需要限定比较结论 | 说明 OS Sandbox 不天然比 Container 安全 |
| 06 | 需要区分术语 | 区分 Seatbelt、SBPL profile、sandbox-exec；补充真实进程树范围 |
| 07 | 需要修订机制细节 | 补充 Landlock ABI 关键版本、Namespace 边界、bwrap 示例限制、seccomp cBPF |
| 08 | 需要深化底层原理 | 补充 seccomp 指针参数限制、线程级安装、继承、TSYNC、USER_NOTIF 与 LOG 边界 |
| 09 | 需要修订文件系统语义 | 补充 handled rights、REFER 例外、TRUNCATE、预打开 FD、TOCTOU、OverlayFS |
| 10 | 需要修订网络语义 | 明确 Network Namespace 不等于无条件断网；区分 IP、Proxy、DNS、Unix Socket |
| 11 | 概念正确 | 保留 Permission 与 Sandbox 的职责区分 |
| 12 | 概念正确 | 强化外部内容 / 工具输出是非可信输入的边界 |
| 13 | 需要修订凭证模型 | 区分 Broker 代理执行与 Token 下发；补充 SSH Agent / Unix Socket |
| 14 | 需要修订 MCP 范围 | 区分本地 stdio Server 与远程 HTTP Server；补充 Tool 授权和进程隔离区别 |
| 15 | 需要修订进程继承 | 明确 IDE 管理进程不一定是 Agent 的子进程；补充 cgroup / Job Object |
| 16 | 需要明确 Git 语义 | 明确 Git Worktree 不是 OS 安全边界，多个 worktree 共享部分 Git 元数据 |
| 17 | 需要修订包管理器描述 | 区分 npm lifecycle、pip source build、wheel 安装、Cargo build.rs、Go |
| 18 | 需要修订云端对象模型 | 区分 Agent Session 与 Environment；不把 Agents API Hosted Sandbox 等同 Codex Cloud |
| 19 | 需要修订比较方法 | 移除固定安全等级排序，按内核边界、威胁模型、兼容性、成本比较 |
| 20 | 需要补充 Enforcement | 区分静态 Policy 决策和运行时 OS 强制执行；补充 Backend capability negotiation / fail-closed |
| 21 | 需要区分概念 | 区分 Prewarm、Snapshot、Pool；补充跨 Session 复用前的 Reset |
| 22 | 需要限定审计能力 | 区分 Policy Event、OS Enforcement Event、Application Event；避免声称日志覆盖所有 syscall |
| 23 | 需要补充测试项 | 增加 FD、TOCTOU、Network bypass、Policy Compiler、Backend failure 测试 |
| 24 | 需要补充生产要求 | 补充 argv、路径安全、强制 Egress、cgroup、输出限制、fail-closed |
| 25 | 产品事实需要修正 | Codex Linux 公开文档描述 bwrap；区分本地、WSL2、Windows Native 与 Cloud |
| 26 | 产品范围需要修正 | 区分 Claude Code Bash Sandbox、独立 sandbox-runtime、Cloud Session；补充默认关闭和回退设置 |
| 27 | 产品行为需要修正 | 补充 Auto-review 对 Shell / MCP / Fetch 的处理、Sandbox 外重试、平台范围和默认网络 |
| 28 | 产品配置需要修正 | 补充 Copilot Harness 作用范围、默认 off、allowNetwork 默认 true、托管 MCP / LSP 和 Windows Experimental |
| 29 | 产品能力需要补充 | 补充 Windows Native、gVisor、LXC/LXD、Tool-level Sandbox 和按单次命令扩权 |
| 30 | Windows 实现需要拆分 | 区分 Codex、Gemini CLI、Anthropic sandbox-runtime、VS Code 的不同 Windows 方案 |
| 31 | 概念正确但需限定 | 固定 Policy Precedence 标为自研设计建议；区分批准一次操作和扩大 Sandbox |
| 32 | 凭证示例需要修正 | Broker 不应把 Token 返回给 Agent；短期 Token 仍是 Agent 可读取的 Secret |
| 33 | 需要补充进程清理 | 区分 process group、cgroup、Job Object 与 PTY |
| 34 | 需要修订供应链细节 | 不再笼统声称每一种 pip wheel 安装都会执行安装脚本 |
| 35 | 需要补充浏览器边界 | 区分 Browser Engine Sandbox、Profile、Agent Runtime 和远程 Browser Service |
| 36 | 概念正确但需细化 | 区分恶意用户、恶意仓库、恶意依赖、被攻陷 Tool 与非恶意错误 |
| 37 | 需要补充策略编译约束 | 增加 Backend 能力协商、Unsupported、Degraded 与 fail-closed |
| 38 | 需要补充逃逸面 | 补充 FD、FD passing、hardlink、Unix Socket、TOCTOU、进程脱离 |
| 39 | 需要修订资源控制 | 区分 cgroup I/O 与磁盘容量 quota；说明 RLIMIT_NPROC 按 real UID 计数 |
| 40 | 需要修订代理边界 | 说明 HTTPS CONNECT 看不到 TLS 内部 URL / Body；Proxy 必须阻止 direct socket 绕过 |
| 41 | 需要补充 Capability 安全 | 增加 token audience、签名、过期、重放保护；远程 Tool 需服务端 enforcement |
| 42 | 需要补充 Snapshot 安全 | 区分 Git checkpoint 与 Runtime Snapshot；补充一致性、Secret 和租户隔离 |
| 43 | 需要补充多 Agent 信任 | 明确 Agent message / artifact 也是非可信输入；增加 schema / provenance / capability 控制 |
| 44 | 需要修订云端角色 | 区分 Worker Host、Container、gVisor Runtime、MicroVM / VMM |

## 3. 已核对的关键技术事实

### 3.1 Linux seccomp

- seccomp filter 使用受限 classic BPF（cBPF），不是通用 eBPF 程序。
- 可以检查 syscall number 和原始数值参数；不能直接解引用用户态指针并读取 pathname 或 sockaddr 内容。
- Filter 默认按调用线程安装；后续子进程 / 线程继承，已存在的其他线程不会自动全部同步，需考虑 TSYNC。
- `SECCOMP_RET_LOG` 是记录后继续执行，不是拒绝。
- `USER_NOTIF` 不是安全地模拟任意 syscall 的通用机制；必须考虑指针、FD 和 TOCTOU。

### 3.2 Linux Landlock

本课程按 Kernel 文档中的 ABI 版本说明关键能力：

| ABI | 关键新增能力 |
|---:|---|
| 1 | 基础文件系统访问规则 |
| 2 | `REFER` |
| 3 | `TRUNCATE` |
| 4 | TCP bind / connect 端口规则 |
| 5 | 设备 ioctl 控制 |
| 6 | abstract Unix socket / signal scope |
| 7 | audit logging flags |
| 8 | `LANDLOCK_RESTRICT_SELF_TSYNC` |
| 9 | pathname Unix socket 控制 |
| 10 | UDP bind / connect-send 端口规则 |
| 11 | restrict_self 时设置 no_new_privs |
| 12 | namespace / capability use 限制 |

其他必须知道的事实：

- Landlock 规则只限制声明为 handled 的权限；`REFER` 有默认拒绝的特殊语义。
- 预先打开的文件 / 目录 FD 不会被新规则追溯限制。
- Landlock 网络权限是端口级，不是 FQDN 域名白名单。
- Landlock 自身并未覆盖所有文件相关 syscall。
- bind mount 与 OverlayFS 的路径语义不同。
- Landlock 是附加限制层，不能授予传统权限检查本来不允许的访问。

### 3.3 现代 AI Coding 产品

本课程不再把产品实现混成一个“统一 AI Sandbox”：

| 产品 | 当前公开资料中的实现 / 范围 |
|---|---|
| Codex | macOS Seatbelt；Linux / WSL2 bwrap；Windows Native Sandbox；Cloud 单独执行环境 |
| Claude Code | 本地 Bash Sandbox：macOS Seatbelt、Linux / WSL2 bubblewrap + proxy；File tools / MCP / hooks 不自动包含在该 Bash Sandbox 内 |
| Cursor | 本地 Shell Sandbox：macOS Seatbelt；Linux Landlock，bubblewrap fallback；Run Modes / Auto-review 是独立决策层 |
| VS Code Copilot Harness | macOS Seatbelt；glibc Linux / WSL2 bubblewrap；Windows BaseContainer Experimental；Sandbox 默认 off，outbound network 默认 allow |
| Gemini CLI | Seatbelt、Docker / Podman、Windows Native、gVisor / runsc、LXC / LXD Experimental |

产品事实核验日期：**2026-11-18**。产品版本、设置默认值、平台支持与内部实现可能变化，引用时应注明核验日期。

## 4. 实战 Lab 的验证状态

### Lab 01：seccomp

- 已做代码静态审查；
- 将目标调用改为直接执行 `syscall(SCMP_SYS(mkdirat), AT_FDCWD, ...)`，避免 libc wrapper 可能选择不同 syscall 的歧义；
- 当前审查环境没有安装 `libseccomp-dev` 头文件，因此本轮没有完成编译和运行验证；
- 需要在安装了 libseccomp 开发包、Kernel 启用 seccomp filter 的 Linux 主机上运行，并验证 EPERM / audit 日志。

### Lab 02：Landlock

- 已用 GCC 14.2 对代码进行编译检查，编译通过；
- 当前审查环境运行时返回 `ENOSYS`（Landlock syscall 不可用 / 未启用），因此无法在该环境完成运行验证；
- 需要在 Linux 5.13+ 且启用 `CONFIG_SECURITY_LANDLOCK`、并在运行时启用 Landlock LSM 的系统上执行；
- 程序会查询 ABI，并按 ABI 选择支持的 filesystem rights；
- Demo 只验证明确列入 handled 的基本文件系统权限，不应被描述成完整生产级文件系统隔离。

**重要：** 代码编译通过不等于 Sandbox 安全；单机功能测试通过也不等于完成逃逸测试。

## 5. 仍需实机验证的项目

在独立 Linux VM 中继续完成：

1. Lab 01：seccomp deny / LOG / filter inheritance；
2. Lab 02：Landlock read / write / create / symlink / REFER / TRUNCATE / pre-opened FD；
3. bubblewrap：filesystem view、PID namespace、network namespace；
4. Network Proxy：直接 socket 绕过、IPv4 / IPv6、DNS rebinding、redirect、localhost；
5. Process cleanup：后台子进程、setsid、cgroup destroy；
6. Resource limits：CPU、memory、pids、disk quota、output cap；
7. Backend failure：隔离组件初始化失败必须 fail-closed。

这些测试需要在目标 OS、Kernel、发行版和运行时版本上分别执行，不能用一台机器的结果推断所有平台。

## 6. 主要一手参考资料

### Kernel / Linux

- seccomp filter：https://www.kernel.org/doc/html/latest/userspace-api/seccomp_filter.html
- Landlock：https://www.kernel.org/doc/html/latest/userspace-api/landlock.html
- bubblewrap：https://github.com/containers/bubblewrap
- Docker seccomp：https://docs.docker.com/engine/security/seccomp/

### OpenSandbox / OpenAI

- OpenSandbox：https://github.com/opensandbox-group/OpenSandbox
- Codex Sandbox：https://developers.openai.com/codex/concepts/sandboxing
- Codex Windows Sandbox：https://openai.com/index/building-codex-windows-sandbox/
- Agents API Hosted Sandbox：https://developers.openai.com/api/docs/guides/agents-api/environments/openai-hosted

### AI Coding Products

- Claude Code Sandbox：https://code.claude.com/docs/en/sandboxing
- Anthropic sandbox-runtime：https://github.com/anthropics/sandbox-runtime
- Cursor Run Modes：https://cursor.com/docs/agent/security/run-modes
- VS Code Agent Sandboxing：https://code.visualstudio.com/docs/agents/run/agent-sandboxing
- Gemini CLI Sandbox：https://geminicli.com/docs/cli/sandbox/

## 7. 发布原则

以后新增课程内容，至少满足：

1. 产品事实必须有官方文档或源码依据，并注明核验日期；
2. OS 原语必须说明 Kernel / OS 版本和能力边界；
3. 示例命令标注“可直接运行”或“概念示意”，不能混淆；
4. Demo 必须记录编译环境和运行结果；
5. 不能验证的行为明确标注“待实机验证”；
6. Policy 配置必须对应实际 Enforcement，不能只检查配置文件；
7. 不允许 Sandbox 初始化失败后静默回退到无隔离执行；
8. 不把“没有复现问题”写成“绝对安全”。

这份报告是本轮文档技术审查记录，不替代专业安全审计、代码审计、渗透测试或目标环境验证。
