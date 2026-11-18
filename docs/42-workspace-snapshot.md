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

Git 主要记录版本化的仓库内容；Agent 还可能创建：

    node_modules
    .cache
    build/
    temp/
    generated files

这些不一定进入 Git。

而 Git Worktree 还会共享部分 common Git metadata / object database，所以它也不是完整的状态隔离。

因此：

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


## 12. Snapshot 的一致性和敏感数据问题

创建 Snapshot 前要决定是否停止进程、flush 文件缓冲、冻结写入或使用文件系统 / VM 提供的一致性快照。否则 Snapshot 可能包含不一致状态。

恢复时还要特别注意：

- 不应无意恢复旧的凭证、Cookie、SSH Agent 状态；
- 不应把 Tenant A 的 Snapshot 恢复到 Tenant B；
- Snapshot 应加密、做访问控制、保留期限和删除策略；
- Snapshot 恢复不能降低当前 Session 的安全策略版本；
- 不要把旧的网络连接和临时 Socket 当成可安全复用状态。

Snapshot 记录的是状态，不是安全授权。恢复时应重新应用当前有效 Policy。


## 参考

- Git Worktree：https://git-scm.com/docs/git-worktree
- Linux OverlayFS：https://docs.kernel.org/filesystems/overlayfs.html
- Linux cgroup v2：https://docs.kernel.org/admin-guide/cgroup-v2.html
