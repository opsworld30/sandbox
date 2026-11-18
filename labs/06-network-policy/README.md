# Lab 06：Network Egress Policy 与 Domain Allowlist

## 目标

用一段可运行的 Python 代码理解：

- exact hostname allowlist；
- 不把 `example.com.evil.test` 当成 `example.com`；
- 不把子域名自动视为允许；
- 默认拒绝未列入的域名和本地地址。

## 环境与运行

Python 3.10+，无第三方依赖：

```bash
python3 demo.py
python3 -m unittest -v
```

## 重要边界

这个 Lab 只实现**策略判断函数**，不是强制网络隔离。它不能阻止程序绕过函数直接创建 Socket，也不能单独解决 DNS Rebinding。真正的 Egress Control 还需要 Network Namespace / Firewall 阻断 direct egress，并由强制 Proxy 处理域名策略；Proxy 应将解析结果与实际连接目标绑定。
