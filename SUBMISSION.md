# 0.8.0 publication checkpoint / 发布检查点

本人已确认版本0.8.0、新仓库pantry-steward及发布者名称：leoniaodo、zix、
power胖丸、Roooy。本人随后授权提交发布修复、推送新分支和创建PR；没有授权
合并PR、推送版本标签、创建公开Release或修改App Hub Issue。

## Source / 源码

- 基线：c814a7d0d8659cebfabcd2dcb4711e6f27b5308d；业务main.splash不改。
- 发布包：bundle/；宿主：woshuoduijiushidui/OctoSense，宿主改动不在应用包内。
- 官方工具：386359153ed6377b5f047bd9ed2767a6a2ac2bc7。
- 工作流采用当前App Flow官方模板，只替换工具提交占位符。
- 检查见review/LOCAL-CHECKS.md，审核回答见REVIEW-ANSWERS.md。
- 提交正文草稿：review/APP-HUB-ISSUE.md。

## Identity and request / 身份及申请

GitHub API确认公开repository ID为1399970684，owner ID为327475236；旧URL
重定向到本仓库且ID相同，是改名而非另建。官方catalog-v2签名验证通过，
sequence16尚无pantry-steward条目。因此按首次正式准入准备，不更新既有目录身份。

原App Hub #166仍Open且保留比赛评审记录；比赛入围不是目录上架。
首次上架前在该Issue补新版评论并更新标题／版本，不重复开申请。
不得修改catalog.json、catalog-v2.json、index/或artifacts/。发布前重查当前目录。

## Human checkpoints / 待本人确认

1. 审阅修改、四张新截图、PRIVACY.md与Windows有限验证范围。图片／语音依赖
   实际宿主；配套改版宿主测试不等于官方发布版或真实模型验收。
2. 提交发布修复、推送分支与创建PR已获授权；不覆盖队友的新main提交。
3. PR合并并复核后，另行确认精确v0.8.0标签和公开Release。推标签触发工作流，
   不移动或覆盖历史标签；不需要开发者签名私钥。
4. 工作流成功后下载app.bundle.pack.json、规范manifest和release-receipt.json，
   核对SHA256、最终摘要及publisher-unpack／publisher-verify（用当前认证目录）。
   不给封存包重盖章。
5. 修改原Issue正文前先评论拟修改内容和理由；下载验证完成后再更新标题／正文，
   添加最终提交与发布链接。当前申请草稿仍标pending。
6. App Hub审批与目录publication由维护者负责，不保证结果或时间。

English: local preparation and branch/PR publication are authorized. Review
source/screenshots/privacy and host limits; separately authorize merging and the immutable v0.8.0 tag.
Verify final downloaded artifacts before updating existing request #166.
No publisher private key is needed. Competition review and workflow success
are not catalog admission. Recheck catalog identity before release.
