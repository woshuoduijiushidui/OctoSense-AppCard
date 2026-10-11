# 0.8.0 本地提交准备 / Publication checkpoint

当前 `bundle/` 是 Issue #2 的 **0.8.0 未发布源码候选**，仅面向 Windows。固定版本 App Hub 包检查、19 项 Python 测试、隔离完整宿主的本地测试签名安装，以及官方宿主手动回退检查已通过。本地改版宿主已验证能力探测、共用选择界面及取消不写库；用户报告真实 MiniMax 图片、摄像头及重试前台验收通过，但未留存逐步独立日志。四张原截图及现有视频属于先前 0.7.0 手动流程；新版合成数据界面截图仅说明界面变化。新视频不属于本次 PR。详见 [VALIDATION.md](VALIDATION.md)。这些本地检查不等于正式封存包、上架或比赛资格。

发布前仍须完成：

1. 正式发布前复核用户报告的真实图片提供方、相机、已有图片、取消与重启前台验收，以及当前截图的适用范围；本地测试签名身份已获本人许可并用于隔离安装。新录屏由其他任务处理。
2. 审核工作流、发布者身份、签名／封存流程、当前公开支持与隐私链接。现有 `publisher-toolchain.json` 和发布工作流仍固定早期 0.6.2 的 App Hub 提交 `655114c4943cd2490daaefa2173e7b5aaa20669f`，与本次源码检查使用的宿主固定提交不同，不能直接作为 0.8.0 发布证明；listing 隐私链接也仍指向 `main/PRIVACY.md`，远端页面须与最终候选一致。
3. 取得本人对提交、推送、`v0.8.0` 标签、发布、App Hub 新 Issue 的分别适用授权；运行最新版发布流程并核对产物 SHA256、publisher-unpack／publisher-verify 和实际工作流／Release URL。
4. 单独确认比赛截止后的改进版本是否被接受；源码完成不自动改变比赛规则。旧版 [0.6.1 / #99](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/99) 的标签及审核记录不变。

当前没有创建标签、Release、新 Issue 或提交到 App Hub，也没有使用正式签名身份。

## 早期 0.6.2 历史清单

这是早期 0.6.2 本地候选的历史清单，不是已发布证明或合格评分。此记录写成时，Issue #2 功能分支尚未确定新版本；当前版本已改为上文的 0.8.0 候选，但发布核验仍未完成。下文的 v0.6.2 发布步骤不适用于此分支，不能据此推送标签或提交。

- 版本：pantry-steward 0.6.2；包路径：bundle/。
- 旧提交：[0.6.1 / #99](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/99)，其标签及审核记录不变。
- 发布者姓名、Windows-only 声明及向宿主模型提供方发送规划输入的隐私说明：用户已确认。
- 背景图 sunlit-pantry-bg.png：作者于 2026-10-08 确认是本人原创，已记录 NOTICE；不声称独立权属鉴定。
- 支持：https://github.com/woshuoduijiushidui/OctoSense-AppCard/issues
- 隐私：https://github.com/woshuoduijiushidui/OctoSense-AppCard/blob/main/PRIVACY.md
- 源码检查、单元测试及尚未验证项见 [VALIDATION.md](VALIDATION.md)。

## 发布前仍须本人确认

1. 审阅 .github/workflows/publish-app.yml；它只在推送 v* 标签时运行，发布作业获得 contents、id-token、attestations 写权限。没有开发者签名 secret。
2. 允许提交、推送并创建新的 v0.6.2 标签。当前任务只获准本地修复，尚未做这些外部动作。
3. 老师是否接受截止后的改进版本；源码修改不自动改变比赛截止规则。

## 授权后按最新版规则完成

依照[官方提交说明](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md)：

- 用当前工具链完成源包检查、原生测试和 hub scan，所有问题逐项回答。
- 发布经审阅的源码与工作流，使用新的精确版本标签，不移动 v0.6.1。
- GitHub 工作流成功后下载 app.bundle.pack.json、规范 manifest 和 release-receipt.json；核对 SHA256，并用 publisher-unpack / publisher-verify 校验，不能对封存包重新 stamp。
- 为 **0.6.2 创建新 Issue**，关联 #99，填写实际标签、完整 SHA、bundle/ 路径、工作流 URL、Release 与 pack URL、校验输出、截图、隐私与支持链接。
- 未运行的项目标记 pending；不要用旧版 PASSED 冒充新发布证明。

GitHub 工作流成功、比赛评分、维护者审批、目录发布及兼容宿主安装是不同环节。目前不保证任何审批结果。
