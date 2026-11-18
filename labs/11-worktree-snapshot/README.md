# Lab 11：Git Worktree 与 Snapshot

## 环境

Git 2.20+；Linux / macOS / WSL。

## 运行

```bash
chmod +x run.sh
./run.sh
```

脚本会创建临时 Git 仓库、提交基线、创建独立 Agent Worktree、在 Worktree 修改文件并提交，然后通过 `git archive` 导出一个不可变代码快照。

## 观察

- Worktree 是独立 checkout，不是完整 Runtime Snapshot；
- Git commit 记录版本化代码，不包含进程、临时目录和运行时状态；
- `git archive` 导出的是提交中的跟踪文件，不包含未跟踪文件。

实验结束后自动删除临时目录。
