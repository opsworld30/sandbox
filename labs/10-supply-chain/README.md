# Lab 10：依赖安装脚本为什么属于执行风险

## 环境

Node.js 18+ / npm 9+。无需下载第三方依赖。

## 运行

```bash
chmod +x run.sh
./run.sh
```

脚本在临时目录中执行两次安装：

1. `npm install --ignore-scripts`：不运行 lifecycle script，marker 不应出现；
2. `npm install --ignore-scripts=false`：允许执行 `postinstall`，marker 会出现。

## 你要理解

依赖安装不只是“下载文件”。npm lifecycle script 可以在安装阶段执行代码。真实项目中应优先在隔离环境中安装，并根据依赖审查结果决定是否允许脚本执行。

本实验只演示 npm lifecycle，不代表所有包管理器有相同机制。临时目录不包含真实项目或凭证。
