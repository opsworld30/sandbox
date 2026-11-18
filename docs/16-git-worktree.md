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

Checkpoint 可以建立在：

- Git commit；
- Git worktree；
- filesystem snapshot；
- overlay filesystem；
- VM snapshot。

## 6. 为什么 Snapshot 和 Git 不完全一样

Git：

> 记录代码版本。

Snapshot：

> 记录运行环境状态。

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
