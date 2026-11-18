# Lab 17：Mini AI Coding Sandbox Runtime（综合项目）

这是课程第 3、4、20、24、25、37、41、44 讲的综合实验。

## 环境

Python 3.10+，Linux / macOS；无第三方依赖。

## 运行 Demo

```bash
python3 demo.py
```

## 运行测试

```bash
python3 -m unittest -v
```

## 本项目包含

- Session Manager：创建、查询和销毁临时 Session；
- Workspace：每个 Session 有独立目录；
- Policy：命令 allowlist、文件路径检查；
- Exec：argv 数组、无 Shell、超时、输出上限；
- Audit：JSONL 记录执行结果，不记录命令输出；
- Lifecycle：Session 销毁时删除 Workspace。

## 重要边界

这是一个**应用层教学 Runtime**，不是安全 Sandbox。它没有调用 Landlock、seccomp、bubblewrap、cgroup 或 Network Namespace。同 UID 的恶意进程仍可能绕过应用层检查。真正生产化时，应将这个 Runtime 的 Backend 替换为 OS-level Enforcement，并加入网络与凭证隔离。
