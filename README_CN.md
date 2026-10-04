# chord-models

[English](README.md)

为 [Chord](https://github.com/keakon/chord) 维护编程模型目录，让你选好模型就能配置，无需手工抄写 API 地址和 token 限额。
维护目标是**最近六个自然月发布的所有适合编程的前沿模型**，涵盖官方 API、第三方托管的开放权重模型和自部署模型。

## 在 Chord 中使用

```bash
chord config show --catalog
chord config add openai/gpt-6.1-sol
```

查看目录，复制模型对应的添加命令即可。没有配置文件时，Chord 会直接创建配置、填入官方接入信息，并提示应设置哪个密钥环境变量。例如：

```bash
export OPENAI_API_KEY="你的 API key"
chord config add openai/gpt-6.1-sol
chord
```

已有 provider 会沿用原地址和凭据。OAuth 模型还会提示登录命令；需要业务空间地址或自部署地址时，用 `--url` 指定你的接口。自定义请求模型名可显式借用目录事实：

```bash
chord config add local/my-model \
  --url https://your-server.example/v1/chat/completions \
  --catalog cohere/north-mini-code-1-0 --api-key-env LOCAL_API_KEY
```

用 `chord config refresh-catalog` 获取已发布的目录更新。普通查看和添加操作均可离线完成。完整来源、发布日期、价格适用范围和刷新得到的候选见 `chord config show --catalog --json`。
需要使用支持当前目录格式的 Chord，校验版本固定在 [validator-revision](validator-revision)。

## 覆盖情况

截至 2026-10-05，目录包含 **31 条模型事实、98 条发现候选**，发布盘点涵盖 **33 个厂商**。这是首轮覆盖盘点，**尚不能声称所有符合条件的模型均已核验**。
[coverage.json](coverage.json) 记录已纳入条目、候选、排除理由、发现来源中的发布日期以及仍待补齐的证据。许多发布日期仍缺少官方佐证，不会把第三方登记日期冒充官方发布日期。

- **模型事实**：来自已引用的文档；可以没有托管端点绑定，未知信息保持缺省。
- **官方接入信息**：只在你明确选择目录模型后提供地址、请求模型名和密钥环境变量；不表示已完成真实请求验证，也不提供端点专用的发送规则。
- **托管端点绑定**：保存该端点专属的参数和行为；新增或修改需提交相应证据及真实请求检查记录。
- **发现候选**：保留部分事实和待核实项，不会自动填充运行配置。最大输出、权限要求、发布日期或编程适用性不明确时，继续留在候选区。

窗口按六个自然月计算，不按 180 天计算。较旧事实可继续服务已有配置；退役、重复和不适用型号记录明确处理理由。
阿里云等需要业务空间和地域信息的接口由用户提供地址，避免目录替你选错地域或填写不存在的空间。

## 维护

```bash
# 使用本地 Chord 校验；不会改写 Chord 的内嵌目录。
./scripts/validate.sh ../chord
```

不传路径时，脚本下载固定提交的 Chord 校验器。CI 使用同一套校验，检查数据改动是否递增版本、发布标签是否与数据版本一致。
每周发现任务产出待核实遗漏和日期缺口报告，供维护者对照官方发布资料处理；不会自动把第三方登记信息升级为默认配置。盘点超过七天未更新时，每周检查会失败。

范围、证据、价格和发布流程见 [CONTRIBUTING.md](CONTRIBUTING.md)。本地校验通过不代表线上 CI、远端标签发布或真实模型请求已通过。
