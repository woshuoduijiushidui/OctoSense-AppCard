# 0.8.0 publication checkpoint / 发布检查点

本人已确认版本0.8.0、新仓库pantry-steward及发布者名称：leoniaodo、zix、
power胖丸、Roooy。本人先授权提交发布修复、推送新分支和创建PR；PR #48合并后，
本人另行授权创建精确的v0.8.0标签并公开发布Release。历史标签未被移动。

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

## Completed / 已完成（2026-10-14）

1. 审阅修改、四张新截图、PRIVACY.md与Windows有限验证范围。
2. 提交发布修复、推送分支与创建PR；PR #48已合并，未覆盖队友的新main提交。
3. 已创建并推送精确注释标签v0.8.0（main HEAD 5b273b00d5eebe4b5c6d11afbb93090a926d37cb），
   未移动v0.6.1／v0.6.2；不需要开发者签名私钥。
4. 发布工作流运行38452092377成功，公开Release
   <https://github.com/woshuoduijiushidui/pantry-steward/releases/tag/v0.8.0>
   含app.bundle.pack.json、octosense-app-manifest.json、release-receipt.json。
   已下载并核对：包SHA256 0737f960d5f6848b6b38b0433454665965d0b30ac70c32aad37bdc22ab03eb45
   与回执一致，封存manifest摘要041be3b30945a23cc4788a357c156bb693a7d879169ac2618973c8863e2d61f6
   与源码摘要一致。记录见VALIDATION.md。

## Human checkpoints / 待本人确认

1. 用当前认证目录对下载的封存包执行publisher-unpack／publisher-verify；不给封存包重盖章。
2. 在官方发布版宿主上安装封存包；当前未验证。
3. 修改原Issue #166正文前先评论拟修改内容和理由；下载验证完成后再更新标题／正文，
   添加最终提交与发布链接。当前申请草稿仍标pending。
4. App Hub审批与目录publication由维护者负责，不保证结果或时间。

English: local preparation, branch/PR publication, the immutable v0.8.0 tag and
the public release are authorized and done on 2026-10-14; the workflow run
38452092377 succeeded and the downloaded pack matches its receipt. Remaining
human steps: publisher-unpack/publisher-verify against the current
authenticated catalog, sealed-pack install on an official released host, a
comment before editing request #166, and maintainer admission. No publisher
private key is needed. Competition review and workflow success are not
catalog admission.
