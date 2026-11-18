# 第 11 讲：Permission ≠ Sandbox

## 1. 为什么这两个概念经常被混淆

AI Coding Agent 经常出现：

    Allow
    Deny
    Ask
    Auto

很多人会把它们理解成 Sandbox。

其实不是。

Permission 是：

> 是否允许 Agent 发起这一次操作。

Sandbox 是：

> 即使允许，这个进程的系统能力仍然被限制在什么范围。

## 2. 一个具体例子

Agent 想执行：

    rm project/test.log

Permission：

    user → Allow

然后 Sandbox 检查：

    project/test.log
      ↓
    workspace?
      ↓
    yes
      ↓
    execute

如果 Agent 想：

    rm ~/.ssh/id_rsa

即使 Permission 层发生错误：

    user → Allow

Sandbox 仍然应该：

    ~/.ssh/id_rsa
      ↓
    outside workspace
      ↓
    DENY

所以两者是两层。

## 3. 为什么只依赖 Permission 不够

假设一个 Agent 每执行一个命令都弹窗：

    npm install?
    allow

    python test?
    allow

    rm file?
    allow

一天几百次之后，用户会出现：

> Approval Fatigue

最后可能无脑点 Allow。

所以现代 Agent 开始把“常见安全操作”放到 Sandbox 内自动执行，把真正越界的操作留给用户。

Anthropic 公开资料把这一变化描述为从频繁 approval 向 OS-level sandbox 转移。

## 4. Sandbox 的意义

如果定义：

    workspace
      READ + WRITE

那么：

    cat workspace/a.txt
    echo hi > workspace/b.txt

可以自动执行。

但：

    cat ~/.ssh/id_rsa
    curl internal-service
    write /System/...

直接被 Sandbox 阻止。

这就减少了用户必须审批的次数。

## 5. 三种典型模式

### 模式 A：Ask Every Time

    Tool
      ↓
    Approval
      ↓
    User

优点：控制强。

缺点：慢，容易疲劳。

### 模式 B：Sandbox + Auto

    Tool
      ↓
    Sandbox
      ↓
    within policy → auto
    outside policy → ask

这是现代 Agent 很重要的模式。

### 模式 C：Full Access

    Tool
      ↓
    User Account
      ↓
    OS

风险最高。

## 6. Approval 和 Sandbox 应该独立

理想设计：

    approval_policy
        +
    sandbox_policy

可以组合：

    approval = never
    sandbox = workspace-write

也可以：

    approval = on-request
    sandbox = workspace-write

这两个参数回答不同问题。

## 7. 为什么 AI Coding 特别适合这种设计

Coding Agent 经常执行：

    ls
    git diff
    pytest
    npm test
    go test

这些动作如果都要求用户确认：

> Agent 的效率会非常低。

但如果它们全部在：

    workspace
    + restricted network
    + restricted credentials

内执行：

> 就可以自动化。

## 8. 一个非常重要的安全结论

不要设计：

    “用户点了 Allow → 完全放开”

更好的设计：

    Allow
      ↓
    仍然受 Sandbox 约束

只有明确的：

    Bypass Sandbox

才意味着离开安全边界，而且应该是显式、高风险操作。

## 9. 面试题

### Q：Permission 和 Sandbox 谁更底层？

通常 Sandbox 更接近运行时和 OS enforcement；Permission 更偏策略与交互。

### Q：为什么 Sandbox 可以减少 Approval？

因为在一个已经定义好的安全边界内，很多操作不需要逐次人工确认。

## 参考

Anthropic:
https://www.anthropic.com/research/claude-code-sandboxing

VS Code:
https://code.visualstudio.com/docs/agents/run/agent-sandboxing

## 本讲实验代码

- [Effective Policy 合成](../labs/08-policy-engine/README.md)
- [单次命令扩权](../labs/19-command-expansion/README.md)

这些是对应主题的可运行教学实验；具体操作系统要求和安全边界以各 Lab README 为准。
