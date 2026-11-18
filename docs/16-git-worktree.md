# 第 16 讲：Git、Worktree 与 Checkpoint

## 1. AI Coding 的第二个问题：代码状态隔离

Sandbox 解决：

> Agent 能访问什么。

Git / Worktree 解决：

> Agent 修改了什么。

两者应该组合。

## 2. 一个 Agent 改代码的风险

如果多个 Agent 都直接修改：

    main working tree

就可能：

    Agent A
      ↓
    modify auth

    Agent B
      ↓
    modify payment

最终互相覆盖。

## 3. Worktree

更好的模型：

    repository
       ├── worktree-A
       ├── worktree-B
       └── worktree-C

每个 Agent：

    Agent A → worktree-A
    Agent B → worktree-B
    Agent C → worktree-C

## 4. Sandbox + Worktree

真正的多 Agent：

    Agent A
      ↓
    Sandbox A
      ↓
    Worktree A

    Agent B
      ↓
    Sandbox B
      ↓
    Worktree B

这样：

- 文件隔离；
- Git 状态隔离；
- 进程隔离；
- 网络策略可以不同。

## 5. Checkpoint

Agent 经常：

    修改 10 个文件
       ↓
    测试失败

用户希望：

> 回到刚才状态。

因此 Runtime 可以做：

    checkpoint
       ↓
    changes
       ↓
    rollback

Checkpoint / Rollback 可以建立在：

- Git commit / tag；
- filesystem snapshot；
- overlay filesystem；
- VM / MicroVM snapshot。

Git Worktree 是独立 checkout / 并行工作区机制，不是状态快照本身；它可以和 commit 或 filesystem snapshot 组合，用来隔离多个 Agent 的代码修改。

## 6. 为什么 Snapshot 和 Git 不完全一样

Git：

> 记录版本化的代码状态。

Runtime Snapshot：

> 按具体实现保存 workspace、磁盘或 VM 状态；并不一定包含完整进程内存和所有外部状态。

环境里可能还有：

    node_modules
    virtualenv
    cache
    generated files
    running state

所以云 Sandbox 常常需要比 Git 更完整的状态保存。

## 7. 多 Agent 的进一步问题

当 Agent A 和 B 同时运行：

    CPU
    Memory
    Disk
    Network

还会共享。

所以最终要进入：

    Tenant Isolation
    Resource Quota
    Scheduler

## 8. 课堂设计

设计：

    repo/
      worktree-A/
      worktree-B/

然后：

    Agent A → 修改 A
    Agent B → 修改 B

最后：

    review
      ↓
    merge

## 9. 面试题

### Q：为什么 AI Coding Sandbox 需要 Git Worktree？

Sandbox 解决运行时访问边界，Worktree 解决代码状态隔离。多 Agent 并行开发时，两者需要结合。

### Q：Snapshot 和 Git commit 有什么区别？

Git 主要保存版本化代码；Snapshot 可以保存完整执行环境和 workspace 状态。


## 10. 非常重要：Git Worktree 不是安全边界

Git Worktree 隔离的是多个工作目录的 checkout 状态，便于并行开发；它不是 OS Sandbox。

多个 linked worktree 通常共享同一个 Git common directory / object database，部分 refs 和仓库级元数据也可能共享。拥有足够文件访问权限的 Agent 仍可能影响共享 Git 元数据、hooks、config 或其他工作区。

因此：

    Worktree
      = code-state / checkout isolation

    Sandbox
      = process / filesystem / network / credential boundary

多 Agent 场景应当同时使用独立 worktree 和独立 Sandbox，并明确共享的 Git 元数据由谁写入。

## 本讲实验代码

- [Git Worktree 与 Snapshot](../labs/11-worktree-snapshot/README.md)

这些是对应主题的可运行教学实验；具体操作系统要求和安全边界以各 Lab README 为准。
