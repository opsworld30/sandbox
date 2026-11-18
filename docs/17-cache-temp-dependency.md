# 第 17 讲：Cache、Temp 与 Dependency 隔离

## 1. 为什么 Cache 也是安全边界

为了性能，Sandbox 不可能每次都：

    npm install
    pip install
    cargo fetch

所以会使用：

    npm cache
    pip cache
    cargo registry
    Go module cache

这会带来两个问题：

1. 性能；
2. 信息泄露 / 污染。

## 2. Shared Cache 的问题

Agent A：

    install dependency

Agent B：

    reuse cache

如果 Cache 中存在：

- 私有 package；
- token；
- 用户路径；
- 恶意 artifact；

就可能出现 cross-session leakage。

## 3. Cache 隔离模型

可以分成：

    Global immutable cache
    Per-user cache
    Per-project cache
    Per-session cache

这不是固定的安全等级排序。真正决定风险的是：

- 谁可以读取和写入；
- 是否跨 Tenant 共享；
- 基础 Cache 是否不可变；
- 写入能否影响其他 Session 后续执行；
- artifact 是否做来源、完整性和版本校验。

通常可以把**共享只读基础 Cache**与**Session 可写 Cache**分开；但不能只凭 Global / User / Project / Session 的名字判断安全强弱。

## 4. Cache Poisoning

例如：

    Agent A
      ↓
    writes malicious cache artifact

Agent B：

    reuse cache
      ↓
    execute artifact

因此：

> Cache 不是单纯性能组件，也是 Supply Chain Boundary。

## 5. Temp Directory

很多程序会使用：

    /tmp

如果多个 Session 共享：

    Session A
      ↓
    /tmp/file

    Session B
      ↓
    read /tmp/file

就可能发生信息泄露。

所以云 Sandbox 通常需要：

    per-session temp

## 6. Dependency 安全

AI Agent 经常执行：

    npm install
    pip install
    cargo build

这些命令可能下载、构建或在安装阶段执行第三方代码，但不同生态的行为不完全一样。

因此：

    Network Sandbox
       +
    Filesystem Sandbox
       +
    Dependency policy

需要一起考虑。

## 7. 不同生态的安装脚本不能一概而论

- **npm**：依赖包可以声明 `preinstall`、`install`、`postinstall` 等 lifecycle scripts，安装时可能执行代码。
- **Python / pip**：从 source distribution 构建时，PEP 517 build backend 会运行构建代码；安装预构建 wheel 与构建 source distribution 的执行路径不同，不能说每个 wheel 安装都会运行任意安装脚本。
- **Rust / Cargo**：`cargo build` 可能执行依赖包的 `build.rs`；`cargo fetch` 与 build 的执行语义不同。
- **Go**：模块下载通常不执行模块包里的构建脚本，但使用 VCS 源拉取时可能调用 Git 等外部客户端；Go 编译通常是编译而非运行包代码，但 `go test`、`go generate`、cgo 工具链以及显式调用的生成器 / 构建工具可能执行程序或脚本。

正确结论不是“所有 install 都必然执行任意脚本”，而是：依赖获取、构建和测试链路中存在不可信代码执行点，应在 Sandbox 中运行，并限制网络、文件、凭证和资源。

## 8. 推荐架构

    Sandbox
       ├── workspace
       ├── private temp
       ├── read-only base cache
       └── writable session cache

这样既能复用大部分依赖，又减少跨 Session 污染。

## 9. 课堂练习

设计：

    cache/
    session-A/
    session-B/

定义：

    base cache → read only
    session cache → read/write

然后讨论：

> 为什么不应该让 Agent 任意修改共享基础 Cache？

## 10. 面试题

### Q：Cache 为什么属于 Sandbox 设计？

因为 Cache 可能包含文件、依赖、凭证或用户数据，而且跨 Session 共享会形成新的信息流和执行边界。

### Q：为什么依赖安装是高风险操作？

因为安装过程可能执行第三方脚本，并获得当前 Sandbox 的文件、网络和进程权限。


## 11. Cache 是数据边界，也是供应链边界

只读共享 Cache 能降低跨 Session 写入污染，但不能自动保证内容可信。仍要考虑：

- Cache artifact 的来源、完整性和校验；
- 私有 Registry token 是否写入配置文件或日志；
- 不同租户能否观察到 package 名称、路径或元数据；
- 可写 cache 是否能投毒其他 Session；
- Cache 清理、过期和版本隔离。

推荐把**共享只读基础 Cache**和**Session 可写 Cache**分开，并且不要让不可信 Session 写入其他 Session 将直接执行的共享缓存。


## 参考资料

- npm lifecycle scripts：https://docs.npmjs.com/cli/using-npm/scripts
- Python build isolation / PEP 517：https://packaging.python.org/en/latest/specifications/pyproject-toml/
- Cargo build scripts：https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Go test：https://pkg.go.dev/cmd/go#hdr-Test_packages
- Go generate：https://pkg.go.dev/cmd/go#hdr-Generate_Go_files_by_processing_source
