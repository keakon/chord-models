# chord-models

[English](README.md)

为 [Chord](https://github.com/keakon/chord) 维护编程模型目录，让你选好模型就能配置，无需手工抄写 API 地址和 token 限额。
维护目标是**最近六个自然月发布的所有适合编程的前沿模型**，涵盖官方 API、第三方托管的开放权重模型和自部署模型。

## 在 Chord 中使用

```bash
chord config add
chord config add openai/gpt-6.1-sol
```

在交互终端中运行 `chord config add`，即可浏览托管 provider 及其已验证模型；也可指定完整目录 ID 直接添加。添加命令会引导你补齐接入信息、预览并确认保存。没有配置文件时，Chord 会直接创建配置、填入官方接入信息，并提示应设置哪个密钥环境变量。例如：

```bash
export OPENAI_API_KEY="你的 API key"
chord config add openai/gpt-6.1-sol
chord
```

已有 provider 会沿用原地址和凭据。OAuth 模型还会提示登录命令；需要业务空间地址或自部署地址时，用 `--url` 指定你的接口。自定义请求模型名可显式继承目录模型配方；与官方使用相同协议时，compat、thinking/reasoning 和上下文压缩策略也会自动补齐：

```bash
chord config add local/my-model \
  --url https://your-server.example/v1/chat/completions \
  --catalog cohere/north-mini-code-1-0 --api-key-env LOCAL_API_KEY
```

也可以直接添加网关上的模型，无需先查目录或拼出完整参数：

```bash
chord config add mygw/gpt-6-sol
```

Chord 会列出接近的已验证目录模型，由你按数字键立即选择，无需回车；按 `m` 可输入完整目录 ID。接着补齐新 provider 的 API 地址和密钥环境变量。选择后可选择已有模型池或创建新池，并配置推理档位和请求体压缩，确认预览后保存。已有 provider 会沿用地址与凭据。编号菜单和 `y/n` 均直接响应按键；菜单中按 Esc、`q` 或 `0`，文本中输入 `q`，或拒绝保存即可取消，配置和凭据文件保持原样。文本输入仍需回车。YAML 锚点和 `<<` 合并均可使用，编辑共享值不会改变其他引用的配置。

脚本传 `--no-interactive` 并提供完整参数；重定向 stdin 或 stdout 也会关闭交互。未匹配的模型只显示建议并返回错误，不会自动选用相似模型。

请求体压缩默认关闭。确认接口或代理支持后，可在引导中选择 `gzip` / `zstd`，传 `--compress gzip` / `--compress zstd`，或在 provider 下手动设置 `compress: gzip` / `compress: zstd`；添加模型会保留该设置。请求体压缩与上下文压缩策略相互独立。

未公布独立输入上限的模型，会从总上下文窗口中预留本次请求的输出预算。压缩阈值改用固定基线：显式记录独立输入上限时用该上限，否则在输出小于窗口时用「总窗口 − 输出」，再否则用整个窗口；它不随单次请求的计划输出浮动。价格同时记录适用范围，例如长上下文请求可能高于基础单价。Opus 5.5 配方采用官方默认推理档位 `medium`；上下文压缩阈值是 Chord 的可调起点，可按任务质量、延迟和缓存复用效果调整。模型支持的推理档位可能多于某个托管端点已验证的档位。
Qwen3.8-Max 的官方输入上限在普通模式下为 991,808 token，推理模式下为 983,616 token；目录统一采用较小的上限。

Haiku 5.5 配方面向小型编程任务和子任务，建议主代理约在 70K token 提醒、约在 87K token 压缩，为 100K 输入价格分界留出余量。这是成本优先的起点，不保证请求一定低于 100K；需要保留更多上下文时可提高模型的压缩阈值。支持统一阈值配置的 Chord 会让子代理也使用同一压缩阈值，显式用户配置优先。

用 `chord config refresh-catalog` 获取已发布的目录更新。普通查看和添加操作均可离线完成。用 `chord doctor config` 查看当前生效的目录版本及来源。模型事实、引用来源、发布日期和价格适用范围见 [models.yaml](models.yaml)，发现候选及待核实项见 [coverage.json](coverage.json) 和 [candidates/](candidates/)。
需要使用支持当前目录格式的 Chord，校验版本固定在 [validator-revision](validator-revision)。

## 覆盖情况

截至 2026-11-12，目录包含 **39 条模型事实、99 条发现候选**，发布盘点涵盖 **34 个厂商**。这是首轮覆盖盘点，**尚不能声称所有符合条件的模型均已核验**。
[coverage.json](coverage.json) 记录已纳入条目、候选、排除理由、发现来源中的发布日期以及仍待补齐的证据。许多发布日期仍缺少官方佐证，不会把第三方登记日期冒充官方发布日期。
2026-10-09 的更新仅复核部分模型的配置配方、输入上限和价格范围，没有重新盘点全部厂商。
2026-10-10 的更新调整 Haiku 5.5 的成本优先压缩建议，并将 Gemini 端点契约对齐到 API 版本根。
2026-10-13 的更新根据官方发布和编程能力资料，将 Muse Wonder 和 Muse Wonder Full 加入候选。候选说明记录接入限制、待核实的输出上限，以及持续编程任务的压缩建议：`threshold: 0.70`、`reminder: 0.60`。候选说明不会自动填充运行配置；Full 目前仅供 Muse Code 订阅用户使用。
2026-10-14 的更新将 `google/gemini-4-argon` 加入已验证模型，并记录官方 API 接入信息。输入、思考和输出共享 1,048,576 token 窗口；模型事实保留长输出可用的窗口容量，Gemini 绑定将当前流式单次请求限制为 65,536 token，更长输出需接入续传机制。价格记录每百万输入/输出 token 4/20 美元的标准费率，以及截至 2026-11-30 的 2/10 美元优惠费率。真实连接检查已到达 API，但因凭据的免费层额度为 0 返回 HTTP 429，尚未验证生成成功。
2026-10-17 的更新在每日发现筛查后，将 Meta 的 Muse Spark Open 记为候选。该开源权重模型（816B 总参/42B 激活、1M 上下文、工具调用、推理默认 xhigh）仅有登记记录：Meta 官方页面不可达，发布日期、编程适用性、硬输出上限、服务方式、价格和许可条款均未核实；登记记录中的 131072 输出沿用 Muse Spark 1.2/1.3 的实验室口径，并非 Open 的一手文档上限。
2026-10-17 的 DeepSeek 复核确认 DeepSeek-V4.1-Flash-1017 已发布，仍沿用现有 `deepseek-flash` 模型名调用，调用方式不变；该条目补录官方发布日期和公告中的 DeepSWE v1.1 编程证据。文档事实保持不变：1M 上下文、384K 硬输出上限、视觉输入，以及每百万输入/输出 token 0.3/1.2 美元的高峰未缓存价格（低谷半价，缓存命中另行计价）。登记记录中的 `deepseek-v4.1-flash` 别名与已退役的 V4-Flash 系列（`deepseek-v4-flash`、`deepseek-v4-flash-vision-exp` 及 0423/0731 日期快照）均记录明确的排除理由：旧名称仍会路由到 V4.1-Flash-1017，按 Flash 价格计费。

2026-10-24 的更新将 `moonshotai/kimi-k3.1-pro` 和 `moonshotai/kimi-k3.1-pro-highspeed` 加入已验证模型。官方发布、API 指南和定价页记录了 1M 上下文、1,048,576 token 硬输出上限、文本/图片/视频输入、low/high/max 推理档位（始终思考），以及 `https://api.moonshot.ai/v1/chat/completions` 的 Chat Completions 接入。标准价格为每百万输入/输出 token：K3.1 Pro 为 2/10 美元，速度提升 2–3 倍的 Highspeed 为 4/20 美元。使用前需至少充值 1 美元；完整开放权重计划于 2026-11-04 前释出。未验证托管绑定或真实请求。

2026-10-27 的更新将 `openai/gpt-6.1-terra` 加入已验证模型，并添加 codex 与 openai 绑定。官方公告（OpenAI 新闻索引标注 2026-10-26）、模型文档和 Codex 模型文档记录了 1,050,000 token 上下文、128,000 token 硬输出上限、文本/图片输入、none/low/medium/high/xhigh/max 推理档位（默认 medium），以及每百万输入/输出 token 1/5 美元的标准价格（缓存输入 0.05 美元；输入超过 272K 时整个请求按输入与缓存 2 倍、输出 1.5 倍计价）。编程证据为官方 Terminal-Bench 4.0 最高推理档 50.3% 的成绩，是 GPT-5.6 Terra（21.5%）的两倍以上；OpenAI 同时指出最难编码任务仍以 GPT-6.1 Sol 和 GPT-6 Astra 为宜。压缩配方沿用 gpt-6.1-sol（0.25/0.20，压在 272K 档之下）。codex 路由真实冒烟检查已到达 API，但因 OAuth 凭据过期返回 HTTP 401（现有 gpt-6.1-sol 同样失败），尚未验证生成成功；openai 路由无 API 凭据，未做真实检查。

2026-11-05 的更新是一次由修订后维护 SOP 驱动的价格与模态补全。缓存命中/写入价格已对照官方页面核实并补录：DeepSeek（deepseek-flash 命中 0.006 美元、deepseek-v4-pro 命中 0.044 美元，均无写入费）、Kimi K3（命中 0.30 美元，写入按 TTL 3/6 美元）、xAI Grok 4.6/4.7（命中 0.50/1.00 美元，Batch 八折）、GLM-5.3 及 Flash/FlashX、Qwen3.8 Max/Flash、Muse Spark 1.2/1.3（命中 0.15 美元）、Gemini 3.8 Flash 与 3.1 Pro Preview、Inception Mercury 2.5（命中 0.02 美元），以及 StepFun step-5-preview（新增 cost 块，缓存写入并入未命中价）。OpenAI GPT-5.6/6/6.1 全系补齐计价细节——三个 5.6 条目原本连 cost 块都没有，现已记录缓存输入、缓存写入与 Batch/Flex 费率。促销窗口不入库：GPT-5.6 Sol 按标准价 5/30 美元记录，官方页面当前展示的限时更低费率不作记录；Cohere north-mini-code-1-0 经核实官方口径为"限流前免费"、未公布单 token 价格，cost 块按未知定价规则继续省略。PDF 输入依据官方 PDF-support 与 PDF-files 指南补入所有 Claude 与 GPT 条目（各模型页只写"text, image"，指南层面则对具备视觉能力的模型通用支持 PDF）；Mercury 2.5 已过期的促销价修正为标准 0.20/0.75 美元。未新增模型；目录版本 2026-11-05.1。

2026-11-10 的更新将 `anthropic/claude-fable-5-2` 加入已验证模型，并在现有 anthropic 端点上添加绑定。官方发布公告、模型总览、release notes、定价、effort 与 PDF-support 页面记录了 `claude-fable-5-2` 模型名、2026-11-09 发布、官方编程基准（FrontierCode 2.0 xhigh 档 49.1%，对比 Fable 5.1 的 32.4%；FrontierSWE v2 69.9%）、1M token 上下文、128,000 token 硬输出上限、文本/图片/PDF 输入、始终开启的自适应思考与全部五档 effort（默认 `high`），以及每百万输入/输出 token 8/40 美元（缓存读取 0.20 美元；5m/1h 缓存写入 10/16 美元；fast mode `speed: "fast"` 为 16/80 美元；仅美国推理 1.1 倍；Batch API 五折）。压缩配方沿用 Fable 5.1 的 0.70/0.60 家族建议：官方未记录 5.2 专属的可靠窗口或计价档位边界（完整 1M 窗口按标准价计费），省略则会让后继模型回落到全局 0.8 默认值。与 Fable 5.2 同日发布、仅向通过 Anthropic 验证计划的组织开放的 Claude Mythos 5.2 记为候选：官方页面写明规格与定价与 Fable 5.2 相同，但没有可核验的通用服务路由。未运行真实端点检查；目录版本 2026-11-10.1。

2026-11-11 的更新将 `google/gemini-4-carbon` 和 `tencent/hy4` 加入已验证模型。Carbon 依据官方公告（2026-10-28）、上线公告、API 模型页、latest-model 指南和定价页核实：`gemini-4-carbon` 模型名、2026-11-10 起 API 全面开放、官方编程基准（CursorBench 4.0、WANDR、AutomationBench 第一；SEC-bench Pro 88.2%、CWE-bench 71.0%、ExploitGym 54.8%）、输入/思考/输出共享 1,048,576 token 窗口（同步输出 65,536，long decode 可至窗口上限）、文本/图片/视频/音频/PDF 输入、low/medium/high 思考档位（默认 `medium`），以及 2026-12-01 起每百万输入/输出 token 4/20 美元（11 月 30 日前为 2/10 美元；隐式缓存命中同期 0.10/0.20 美元）。压缩配方有意省略：官方未记录 Carbon 专属的可靠窗口或计价档位边界，与 Argon 一样沿用全局默认。真实 gemini 冒烟检查已带密钥到达 API，但免费层配额为 0 返回 HTTP 429，尚未验证生成。腾讯 Hy4（混元家族正式版，2026-11-04 发布）依据腾讯发布公告、Hy 研究页、Hy API 指南、TokenHub 价格页和深度思考文档核实：长程软件工程与 GameDev/GameLogic 编程证据、API 指南的 1M/960k/64k 规格（按二进制口径记为 1048576/983040/65536，这是唯一能让输入加输出等于上下文窗口的读法）、文本/图片输入、思考默认开启（`high` 默认档，`no_think` 关闭），以及新加坡 TokenHub 每百万 token 0.834/2.501 美元、缓存命中 0.042 美元（广州为 ¥6/¥18/¥0.3；12 月 31 日前的五折促销不作记录价）。Hy4 记录了 OpenAI Chat Completions 接入信息，但未添加托管绑定，也未运行 TokenHub 真实检查。同一批页面为 hy4-preview 候选补齐官方规格（纯文本输入、相同规格与价格），因其将于 2026-12-07 下线（公告 2559）继续保留候选身份不提升；hy3 候选补录文档规格与价格。目录版本 2026-11-11.1。

2026-11-12 的更新对照官方 Model Studio 模型页与发布盘点，将阿里的 Qwen4-Max-Preview 记为候选。预览版旗舰（`qwen4-max-preview`，2026-11-11 发布）记录了 1M 上下文、思考与最终回答共享的 393,216 token 输出预算、文本/图片/视频输入、默认开启思考的 `low`/`medium`/`xhigh` 档位（默认 `xhigh`），以及经 Token Plan 专用 Base URL 的 OpenAI Chat Completions、Responses 与 Anthropic Messages 兼容接入。继续保留候选不提升：预览版仅支持 Token Plan（无按量计价）、2026-11-25 24:00（UTC+8）下线，且官方尚未公布编程评测。候选说明不会自动填充运行配置；正式版预计以新的模型 ID 发布，持续关注。

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

不传路径时，脚本通过 Go module proxy 解析固定提交的 Chord 校验器。CI 使用同一套校验，检查数据改动是否递增版本、发布标签是否与数据版本一致。
每日发现任务产出待核实遗漏和日期缺口报告，供维护者对照官方发布资料处理；不会自动把第三方登记信息升级为默认配置。发现通知名单中尚未记录审查结论的新模型时，工作流会失败以提醒维护者；不按盘点距今天数触发失败。

范围、证据、价格和发布流程见 [CONTRIBUTING.md](CONTRIBUTING.md)。本地校验通过不代表线上 CI、远端标签发布或真实模型请求已通过。
