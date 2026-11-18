# Lab 04：用 bubblewrap 建立最小 Linux 文件与网络视图

## 环境

仅限 Linux 测试 VM。需要安装 bubblewrap（命令名 `bwrap`）。不同发行版的 User Namespace、mount 权限和 bwrap 编译选项不同；如果启动失败，先检查本机发行版的 bwrap 文档，不要直接关闭隔离选项。

Ubuntu / Debian：

```bash
sudo apt-get update
sudo apt-get install bubblewrap
```

## 准备

```bash
mkdir -p workspace
echo "visible workspace file" > workspace/hello.txt
echo "host secret should not be mounted" > host-secret.txt
```

## 运行

```bash
chmod +x run.sh
./run.sh
```

脚本只把必要的系统目录以只读方式映射进 Sandbox，把当前 workspace 以可写方式映射到 `/workspace`，并创建独立 PID、IPC、UTS、Network Namespace。

预期：

- `/workspace/hello.txt` 可读；
- 可以在 `/workspace` 创建文件；
- 宿主机的 `host-secret.txt` 不会出现在 Sandbox；
- Sandbox 内没有默认外网路由。

## 检查

```bash
./run.sh --check
```

## 注意

这是一个最小教学命令，不是通用生产配置。系统动态库、DNS、证书、GPU、开发工具和包管理器可能还需要额外挂载。不要随意添加整个 `$HOME`、Docker Socket 或宿主机凭证目录。
