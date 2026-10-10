# 冰箱管家 · Pantry Steward

简体中文 | [English](README.md)

把确认过的库存，变成可以复核并执行的一顿饭。

## 版本与验证范围

本目录为 **0.6.2 可编辑候选**。工作区另含 Issue #8 的六周期候选；版本号由发布检查点决定，不随每个功能分支递增。[Issue #99](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/99) 请求审核的是 **0.6.1**，不是此候选；不声称任何版本已获准上架。

仅声明 Windows：当前固定工具链已通过源码检查和有限原生冒烟测试。本候选的完整在线模型回归、新电脑安装、全功能回归和封存包安装仍未验证，见[验证记录](VALIDATION.md)。

## 功能闭环

确认饮食档案及 1／3／7／15／21／30 天周期（每周期 3 份候选，可单独重新生成；1 天用于短周期体验）；可直接确认单选，也可按顺序组合不同周期（允许重复，如 7+7），确认前可调整顺序、移除或用其它候选替换，组合页显示总天数与各阶段起止日期和目标，单个计划最多 12 个阶段。已确认阶段在起止日期开始时锁定；尚未开始的阶段仍可在「档案」页调整顺序、替换、移除或改目标，重算其后阶段的日期与计划总天数，已确认的进度与用餐记录不受影响。然后预览库存批次 → 生成本地规则或官方 model.complete 候选 → 查看做法和用量 → 接受方案 → 单独确认实际食用量，才扣库存和累计摄入。每个已确认阶段都是所属方案的快照，之后改候选不影响它。

今日和阶段数值为原型估算。存档旧计划保留库存与计划历史。默认手动生成；可在设置中主动开启自动生成，但接受菜单和扣减仍须确认。删除菜谱不回滚库存或删除摄入记录。详见[周期说明](CYCLE-PLANS.md)。

## 演示

[查看录屏](video/演示视频.mp4)

![历史 Windows 截图](bundle/screenshots/01-main.png)

[菜单候选](bundle/screenshots/02-plan.png) · [食用确认](bundle/screenshots/03-confirm.png) · [库存](bundle/screenshots/04-updated.png)

截图来自历史 Windows 原生运行，不是手机截图或 0.6.2 在线模型完整证据。视频不放进分发包。

## Windows 源码运行

本仓库只含应用，不是完整宿主或安装包。入口是根目录 run.cmd，不是 apps/pantry-steward/run.cmd。

需要 Git、Python 3.11+、Rust、Windows C++ 工具和 Windows SDK。按[官方 Quickstart](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/QUICKSTART.md)准备当前原生工作区，构建 hub 与 card-host；复用共享框架，但必须核对官方固定版本，不能只用旧缓存程序代替。

此候选的发布工作流固定 App Hub 655114c4943cd2490daaefa2173e7b5aaa20669f。本地已使用该版本、未修改的源代码和锁文件编译检查器。完整新电脑下载/构建仍未验证。

假设工具仓库位于同级 OctoSense-App-Hub，在本应用目录执行：

```cmd
run.cmd --hub ..\OctoSense-App-Hub\target\release\hub.exe --check
run.cmd --hub ..\OctoSense-App-Hub\target\release\hub.exe --card-host ..\OctoSense-App-Hub\target\release\card-host.exe --standalone
```

--hub --check 不需要宿主工程或密钥；--standalone 使用官方 card-host，仅验证本地规则，没有模型服务，也不是商店安装。--app-data 可指定独立测试目录，默认预览数据在 .local-state/standalone。删除数据前请备份。

启动器只校验现有摘要，不自动修复。当前工具的源码摘要已记录在 VALIDATION.md；旧版 Windows hub 会产生不同的路径摘要，并可能误拒绝许可证的网址。遇到拒绝应更新工具，不得删除法律声明、改权限绕过门禁，或对封存包重新 stamp。

旧 --host-workspace / --prepare-local-test 路线仅保留给历史 0.6.1 的隔离兼容演练，不推荐用它运行此候选。后者涉及仓库外本机测试密钥，必须本人另行同意；本次没有生成密钥。原来的工程和库存未更改。

在线 AI 必须在提供官方 model 服务的兼容 OctoSense 宿主中测试，在宿主 AI providers 页配置提供方。此处的 card-host 命令不能验证它。正式封存包还要求 publisher-github-v1 支持，兼容正式宿主尚待官方发布；不声称已验证安装或在线完整流程。

## AI、隐私和边界

- storage 只保存应用自己的库存、档案、方案、历史和备份。
- model 经官方宿主将目标、档案、库存成分与周期余额发送到用户配置的模型提供方。密钥留在宿主；应用不读取 ai.env 或收集密钥。
- 在宿主的 AI providers 页面配置模型。预算查询成功不代表模型已配置。失败时手动选择本地规则。停止等待不保证撤销已发送或计费的请求。
- 没有直接联网主机、麦克风权限或独立应用 Agent 工具。不录音，语音不可用；没有 OCR、照片识别或宿主关闭后的后台执行。
- 营养数值为原型估算，不是医疗建议，不保证过敏或食品安全。未知食材参与数值规划前须补齐包装标签。

用户曾报告旧版在线生成成功；本候选完整在线回归未验证。参见发布者已确认的[隐私说明](PRIVACY.md)、[支持说明](SUPPORT.md)和[审核回答](REVIEW-ANSWERS.md)。

## 发布

只分发 bundle/；工具、视频、审核包和本地状态留在包外。Git 属性保护 Windows 下的原始包字节。

[最新默认路线](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md)使用准备好的 GitHub 标签工作流及不可变工具链，无需开发者签名密钥。本人审阅工作流并授权发布后，推新的 v0.6.2 标签、校验封存 Release 包，再创建关联 #99 的新版 Issue。不要移动 v0.6.1。目前只在本地准备；不声称已运行工作流、推标签、发布、创建新 Issue 或获批。封存包需支持 publisher-github-v1 的宿主；所引官方指南说明兼容正式宿主仍待发布。

待本人确认的环节见[提交准备](SUBMISSION.md)。源码检查或工作流成功不等于比赛合格或 Hub 审核通过。

## 许可证与来源

[Apache License 2.0](LICENSE)，参见 [NOTICE](NOTICE)。依赖和第三方素材保留各自许可证。作者于 2026-10-08 确认 sunlit-pantry-bg.png 为本人原创，已在 NOTICE 记录；这是作者声明，不是独立权属鉴定或 Hub 审批。

作者：leoniaodo、zix、power胖丸、Roooy。

[OctoSense](https://github.com/OctoSense-org/OctoSense) · [Design Flow](https://github.com/OctoSense-org/OctoScript-App-Design-Flow) · [App Hub](https://github.com/OctoSense-org/OctoSense-App-Hub)
