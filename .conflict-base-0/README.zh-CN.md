# 冰箱管家 · Pantry Steward

简体中文 | [English](README.md)

把确认过的库存，变成可以复核并执行的一顿饭。

## 版本与验证范围

此功能分支是尚未发布的 Issue #2 **0.8.0 源码候选**，并包含 Issue #8–#11 的功能（六周期候选、组合计划、未来阶段编辑与总览页）。除手动库存、周期和菜单外，它在具备图片能力的本地改版宿主上提供拍照／导入图片识别草稿；官方宿主回退手动录入。源码包通过当前固定版本 App Hub 门禁。[Issue #99](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/99) 请求审核的是 **0.6.1**，不是此候选；不声称已发布或获 App Hub 审批。

目标平台仅为 Windows。2026-10-11，0.8.0 包通过固定版本 App Hub 检查，19 项 Python 测试通过；未修改的官方完整宿主在隔离档案完成 26 项 UI／数据检查和重启检查，两种图片入口都显示手动回退。本地改版宿主通过图片能力探测、共用选择界面及取消不写库检查；任务专用模拟结果验证了两类可编辑草稿和多行一次入库。用户报告剩余的 MiniMax 图片、摄像头、重试和重启前台验收通过；没有逐步独立日志。正式 Store 发布仍未验证。见[验证记录](VALIDATION.md)。

## 功能闭环

确认饮食档案及 1／3／7／15／21／30 天周期（每周期 3 份候选，可单独重新生成；1 天用于短周期体验）；可直接确认单选，也可按顺序组合不同周期（允许重复，如 7+7），确认前可调整顺序、移除或用其它候选替换，组合页显示总天数与各阶段起止日期和目标，单个计划最多 12 个阶段。已确认阶段在起止日期开始时锁定；尚未开始的阶段仍可在「档案」页调整顺序、替换、移除或改目标，重算其后阶段的日期与计划总天数，已确认的进度与用餐记录不受影响。然后预览库存批次 → 生成本地规则或官方 model.complete 候选 → 查看做法和用量 → 接受方案 → 单独确认实际食用量，才扣库存和累计摄入。每个已确认阶段都是所属方案的快照，之后改候选不影响它。总览页展示长期计划、当前阶段、当天每餐进度，以及当前阶段热量、蛋白质目标与实际值的对比；进度只按已完成餐次 ÷（周期天数 × 3）累计，仅生成或确认菜单不改变进度，只有确认实际食用才增加；目标随日期覆盖今天的阶段自动切换。

此工作分支把过敏、忌口和饮食偏好分开；录入先生成可编辑草稿，再由用户确认入库。支持 g/kg、ml/L、个，以及由用户确认换算量的简单包装单位。同名食材按组展示，每批仍可分别编辑或移除。图片识别仅在本地改版宿主报告 `model.vision_capability` 时启用；结果中不确定的字段由用户补齐。

今日和阶段数值为原型估算。存档旧计划保留库存与计划历史。默认手动生成；可在设置中主动开启自动生成，但接受菜单和扣减仍须确认。删除菜谱不回滚库存或删除摄入记录。详见[周期说明](CYCLE-PLANS.md)。

## 演示

[历史手动流程录屏](video/演示视频.mp4)

![先前 Windows card-host 首页截图](bundle/screenshots/01-main.png)

[菜单候选](bundle/screenshots/02-plan.png) · [食用确认](bundle/screenshots/03-confirm.png) · [库存](bundle/screenshots/04-updated.png)

现有录屏及四张截图来自先前 0.7.0 候选在隔离的官方 Windows card-host 中使用合成数据的手动流程；其中图片按钮状态不代表当前 0.8.0 界面。当前版合成数据截图包括[首页](docs/qa/issue-2-home-after.png)、[修改用户画像](docs/qa/issue-2-profile-edit-after.png)、[库存](docs/qa/issue-2-inventory-after.png)、[改版宿主图片选择](docs/qa/issue-2-image-chooser-after.png)、[官方宿主手动提示](docs/qa/issue-2-official-fallback-after.png)、[菜谱](docs/qa/issue-2-recipe-after.png)和[食用前核对](docs/qa/issue-2-consumption-after.png)。新版截图只说明界面，不能证明真实图片识别、Store 发布或真实模型响应。新录屏不属于本次 PR。

## Windows 源码运行

本仓库只含应用，不是完整宿主或安装包。入口是根目录 run.cmd，不是 apps/pantry-steward/run.cmd。

需要 Git、Python 3.11+、Rust、Windows C++ 工具和 Windows SDK。按[官方 Quickstart](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/QUICKSTART.md)准备当前原生工作区。0.8.0 的摄像头授权声明要求完整 OctoSense shell；独立 card-host 不实现该授权代理。

早期 0.6.2 发布工作流固定 App Hub 655114c4943cd2490daaefa2173e7b5aaa20669f；当前 OctoSense 宿主固定的是 App Hub 8347a489141c0e24cab564883db7c4592935a8b2。验证此编辑后的 bundle 须使用当前宿主固定版本。

固定版本工具在同级 OctoSense 仓库中构建后，从本应用目录用全新测试档案执行。第二条命令使用该仓库的当前分支；它是未修改官方宿主还是本地改版宿主，取决于检出版本。第二条命令保持运行，第三条在另一个终端执行：

```cmd
run.cmd --hub ..\OctoSense\target\release\hub.exe --check
run.cmd --host-workspace ..\OctoSense --hidden --remote 18442 --app-data target\qa-d2
python -X utf8 tools\smoke.py --port 18442 --profile target\qa-d2
```

`--hub --check` 不需要宿主工程或密钥。完整宿主的隔离安装需要此前经本人许可生成的本地测试密钥；原生冒烟脚本需要全新、隔离的 `--app-data` 目录。重启相同档案后可加 `--restart` 核对持久化。

启动器只校验现有摘要，不自动修复。当前 0.8.0 候选已用固定版本 App Hub 重新盖章并通过包检查；修改 bundle 后须再次盖章。

本机 D2 已用本地测试签名在完整宿主的隔离档案中安装；这不是正式 Store 发布。`--prepare-local-test` 会在 Git 之外创建本地测试密钥，必须取得本人同意。测试不能使用他人的现有库存。

图片 AI 必须在本地改版 OctoSense 宿主中测试，并在宿主 AI providers 页配置提供方。未修改的官方完整宿主已单独通过手动回退检查；不能仅凭上面的命令认定宿主为官方版本。用户报告 MiniMax 图片识别前台验收通过。正式封存包还要求 publisher-github-v1 支持；本地测试签名安装不等于正式发布。

## AI、隐私和边界

- storage 保存应用自己的库存、档案、方案、历史、备份和用户选择的图片。
- model 经官方宿主将目标、填写的档案（包括过敏、忌口和偏好）、合格批次的名称与原生单位／数量发送到用户配置的模型提供方。数值规划另发送估算克数、营养参考和周期余额；未核算菜谱仅标注营养参考是否完整。密钥留在宿主；应用不读取 ai.env 或收集密钥。
- 在宿主的 AI providers 页面配置模型。预算查询成功不代表模型已配置。失败时手动选择本地规则。停止等待不保证撤销已发送或计费的请求。
- 图片识别需相机／文件权限。Windows 本地改版宿主只接受一张应用内 JPEG、PNG 或 WebP 图片，最大 10 MiB；仅支持 `minimax`／`minimax-cn` 的 `MiniMax-M3` 或 `moonshot` 的 `kimi-k2.5`，将图片及识别提示词送至用户配置的提供方，返回可编辑草稿。官方宿主不支持时显示手动录入提示。没有直接联网主机、麦克风权限或独立应用 Agent 工具；语音不可用，宿主关闭后不后台执行。
- 营养数值为原型估算，不是医疗建议，不保证过敏或食品安全。生成时优先使用具备完整营养参考的食材；缺少参考时可生成标为“营养未核算”的菜谱，按原单位扣减库存，但不计入周期热量与营养数值。未知食材若要参与数值规划，须补齐每 100g 营养参考。

用户报告本候选的在线菜谱和图片识别前台检查通过；未留存完整的独立提供方逐步日志。参见发布者已确认的[隐私说明](PRIVACY.md)、[支持说明](SUPPORT.md)和[审核回答](REVIEW-ANSWERS.md)。

## 发布

只分发 bundle/；工具、视频、审核包和本地状态留在包外。Git 属性保护 Windows 下的原始包字节。

[App Hub 提交指南](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md)说明发布路线。0.8.0 候选尚需正式发布证据复核、公开链接核对及另行取得本人发布授权。不声称已运行发布工作流、推标签、发布、创建新 Issue 或获批。

待本人确认的环节见[提交准备](SUBMISSION.md)。源码检查或工作流成功不等于比赛合格或 Hub 审核通过。

## 许可证与来源

[Apache License 2.0](LICENSE)，参见 [NOTICE](NOTICE)。依赖和第三方素材保留各自许可证。作者于 2026-10-08 确认 sunlit-pantry-bg.png 为本人原创，已在 NOTICE 记录；这是作者声明，不是独立权属鉴定或 Hub 审批。

作者：leoniaodo、zix、power胖丸、Roooy。

[OctoSense](https://github.com/OctoSense-org/OctoSense) · [Design Flow](https://github.com/OctoSense-org/OctoScript-App-Design-Flow) · [App Hub](https://github.com/OctoSense-org/OctoSense-App-Hub)
