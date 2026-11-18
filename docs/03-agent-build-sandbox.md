# 第 3 讲：用 Agent 做一个简陋 Sandbox

## 1. 目标

这一讲故意先做一个“不安全”的 Runner。

目的不是上线，而是理解：

> Execution 和 Isolation 是两件事。

## 2. 最小 Runner

    import subprocess

    def run(command):
        p = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        return {
            "stdout": p.stdout,
            "stderr": p.stderr,
            "exit_code": p.returncode
        }

它可以：

    run("python --version")
    run("pytest")
    run("npm test")

## 3. 为什么它不是 Sandbox

因为：

    run("cat ~/.ssh/id_rsa")

理论上可能成功。

再比如：

    run("curl https://example.com")

也可能成功。

所以它是：

> Command Runner

不是：

> Security Sandbox

## 4. cwd 为什么不够

设置：

    cwd = /workspace/project

只改变当前目录。

程序仍然可以尝试：

    cat ../secret.txt
    cat /home/user/secret.txt

因此：

    cwd != filesystem isolation

## 5. shell=True 为什么危险

命令字符串交给 shell 解释。

生产环境更推荐明确参数：

    subprocess.run(
        ["python", "main.py"],
        ...
    )

但要注意：

> 参数数组只能解决命令解析问题，不能解决 Sandbox 问题。

即使没有 shell，程序仍然可以读取文件、创建 socket、启动子进程。

## 6. 资源问题

恶意代码可能：

    while True:
        pass

或者创建大量进程、大量输出、大量文件。

所以最终需要：

- timeout
- CPU limit
- memory limit
- disk limit
- process limit
- output limit

## 7. 本讲结论

> subprocess 解决“怎么启动程序”，Sandbox 解决“程序启动以后还能做什么”。

## 面试题

subprocess 能不能作为 Sandbox？

不能。它是进程创建接口，不会自动限制文件、网络、syscall、设备和资源。


## 安全边界补充：subprocess timeout 不等于清理整棵进程树

例如 Python：

```python
subprocess.run(["bash", "-c", "sleep 300 & wait"], timeout=5)
```

超时处理针对的是 Python 创建并等待的那个直接子进程。若 shell 又启动了子进程，不能假设它们一定全部被清理；尤其是子进程脱离进程组、重新建立 session 或被 daemonize 时。

教学实验可用 process group 做基础清理；Linux 生产环境优先考虑把 Session 的所有进程放进独立 cgroup，并在销毁时终止整个 cgroup。Windows 可研究 Job Objects。单独记录 PID 再逐个 kill 容易遇到 PID 重用和竞态。

**结论：** `timeout` 是执行接口的超时语义，不是完整的进程隔离和资源回收方案。