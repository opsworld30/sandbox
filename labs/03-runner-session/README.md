# Lab 03：Runner、Session 工作目录与进程清理

## 目标

运行一个最小 POSIX Runner，观察：

- 参数使用 argv 数组传递，不拼接 Shell 字符串；
- 命令只能把工作目录解析到指定 workspace 内；
- 设置超时；
- stdout / stderr 合并后限制输出字节数；
- 每次执行创建独立 process group，超时或超出输出限制时终止整组进程。

## 环境

Python 3.10+；Linux 或 macOS。这个实验不需要第三方依赖。

## 运行

```bash
python3 demo.py
```

预期看到 workspace 文件内容、退出码，以及 `cwd=../` 被拒绝。

## 进一步实验

把 demo 中的命令替换成：

```python
["python3", "-c", "import time; time.sleep(10)"]
```

将 timeout 设为 1 秒，观察 `timed_out=True`。

再尝试大量输出：

```python
["python3", "-c", "print('X' * 1000000)"]
```

观察 `output_limited=True`。

## 安全边界

这是 Runner 教学实现，不是生产 Sandbox。路径检查存在 TOCTOU 风险；同 UID 进程仍共享宿主机 Kernel 和其他可访问资源。生产环境还要叠加 bubblewrap / Landlock、seccomp、cgroup、网络隔离和凭证代理。输出限制是 Runner 层的字节上限，不替代 cgroup 的内存限制。
