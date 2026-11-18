# 第 42 讲：Workspace Snapshot——为什么 Agent 需要“后悔药”

## 1. AI Agent 的一个天然问题

Agent 会修改很多文件：

    edit
    edit
    edit
    test
    edit
    edit

如果某一步把项目改坏：

    怎么恢复？

传统 Git 可以：

    git checkout

但 Agent Runtime 还需要处理：

    untracked files
    generated files
    dependency state
    temp state
    process state

所以需要：

> Workspace Snapshot

## 2. Snapshot 是什么

最简单理解：

    Snapshot 1
       ↓
    Agent modifies
       ↓
    Snapshot 2

如果出问题：

    rollback → Snapshot 1

## 3. 为什么 Git 不完全够

Git 主要记录：

    tracked source

但 Agent 可能创建：

    node_modules
    .cache
    build/
    temp/
    generated files

这些不一定进入 Git。

所以：

    Git Checkpoint
      !=
    Runtime Snapshot

## 4. Copy-on-write

如果每次：

    copy 10GB workspace

成本很高。

可以使用：

    Base
      ↓
    Copy-on-write layer

只有修改的 blocks / files 才产生新数据。

概念：

    Base Workspace
         |
      Snapshot
         |
      Overlay
         |
      Agent writes

## 5. Snapshot 和 Sandbox 的关系

Sandbox：

> 防止越界。

Snapshot：

> 越界前的变化可恢复。

所以：

    Sandbox
      +
    Snapshot

形成：

    Prevention
      +
    Recovery

## 6. Session Checkpoint

可以设计：

    checkpoint(session)

记录：

    filesystem snapshot
    policy version
    git revision
    environment metadata

然后：

    rollback(session, checkpoint_id)

## 7. 为什么 Process 也要考虑

如果 Agent：

    starts server

然后 Snapshot：

    filesystem only

rollback 后：

    server
    仍然运行

所以完整 Runtime 可能需要：

    filesystem state
    process state
    network state

不过生产环境通常不会轻易做完整 process snapshot，而是：

    stop process
    restore filesystem
    recreate session

## 8. Snapshot 和 Security

Snapshot 还有一个安全价值：

如果恶意代码：

    modifies workspace
    creates persistence file

rollback 可以清理：

    persistence

例如：

    modified .git/hooks
    modified scripts
    generated malicious config

## 9. 实验

最简单版本：

    tar snapshot

然后：

    agent changes

最后：

    restore

虽然性能差，但非常适合理解：

> Checkpoint → Mutate → Rollback

## 10. 进阶

继续研究：

    overlayfs
    btrfs snapshot
    ZFS snapshot
    reflink
    copy-on-write
    VM snapshot
    MicroVM snapshot

最终会连接到：

    Prewarm
    Snapshot
    Pool

这些是 Cloud Sandbox 的核心性能优化技术。

## 11. 核心结论

Sandbox 是：

    “不让它出去”

Snapshot 是：

    “即使它改坏了，也能回来”

两者应该一起设计。
