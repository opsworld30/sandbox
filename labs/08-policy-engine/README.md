# Lab 08：Policy Engine 与 Effective Policy

## 目标

把多层策略合成为最终策略：

- 多层 `allow_tools` 取交集；
- `deny_tools` 取并集，拒绝优先；
- `network.enabled` 采用 AND，任何一层关闭都关闭；
- `network.allowed_hosts` 取交集，不能被低优先级配置扩大。

## 运行

```bash
python3 demo.py
python3 -m unittest -v
```

## 你应该观察

System 允许的工具不代表 Project 可以全部使用；Team 或 Project 增加 deny 后，后续层不能把它重新放开。网络域名也只能收窄，不能在低信任层扩大。

## 安全边界

这是一个教学用的策略合成器，使用精确字符串集合，不是完整 Policy Language。生产实现还需要 schema 校验、路径规范化、通配符语义、租户边界、版本化、签名、能力协商和 fail-closed Enforcement。
