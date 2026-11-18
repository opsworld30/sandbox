# Lab 09：Process Tree 与整组进程清理

## 环境

Python 3.10+；Linux 或 macOS。

## 运行

```bash
python3 tree_demo.py
```

程序会创建 parent → child → grandchild 三层进程，全部加入同一个 process group，然后通过一次 `killpg` 终止整组。

## 观察

- 只 kill root PID 不一定会结束所有后代；
- process group 能覆盖正常继承该组的子进程；
- 如果子进程主动调用 `setsid()` 脱离进程组，process group 就不再足够；
- Linux 多租户 Runtime 应进一步使用 cgroup v2 管理整个 Session 的进程集合。

本实验演示进程组，不是 cgroup，也不是完整 Sandbox。
