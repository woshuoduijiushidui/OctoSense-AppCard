# Draft: Submit pantry-steward 0.8.0

待本人授权后补原App Hub #166；本文件不是已提交或获批的Issue。
修改正文前先评论拟修改内容和理由。不沿用0.6.2发布证明。

### Release status

Request opened; release evidence pending

### App id

pantry-steward

### Version

0.8.0

### Repository URL

https://github.com/woshuoduijiushidui/pantry-steward

### Requested capabilities and app behavior

应用：冰箱管家。发布者：leoniaodo、zix、power胖丸、Roooy。

storage：本应用的档案、过敏／忌口、方案阶段、库存、菜单、摄入快照、进度、
模拟订单、对话、选择的图片和临时音频。
model：宿主菜单、营养估算、问管家对话，以及兼容提供方的图片／转写。
密钥留在宿主，不读取ai.env、不收集密钥。
camera、files：主动拍照／导入图片，识别后核对草稿，确认才入库。
microphone：可选前台录音；先发现能力并取得设备许可。转写文字先填入输入框，
另点发送才对话。能力缺失时保留手动／文字路径；声明能力不提供宿主接口。

整合个人建档、分批库存与单位换算；1／3／7／15／21／30天候选及最多12阶段
组合、未来阶段调整与总览；库存三餐日菜单、派生缺菜清单；应用内模拟商品、
购物车、订单、收货确认；独立实际食用记录、1天体验和复盘；问管家多轮对话、
软记忆及可选图片／语音。

健康方向不是具体执行方案。菜单只用生成时合格库存，之后库存变化才形成
缺口。生成／接受不扣库存；模拟下单无真实支付／配送，不接美团API。只有
确认收货才入库，只有确认实际食用才追加摄入、扣库存、增加进度。修改未来
阶段不覆盖真实记录；1天体验只用库存、不补菜。无模型时不伪造本地替代菜单。
营养含估算，仅供参考，不保证医疗效果、营养或过敏／食品安全。

问管家通过model.complete实现，不配置独立后台octos应用Agent，包内没有
tools.json、AGENT.md或运行时技能；应用不直接访问远程主机，退出宿主后不后台
运行。当前Windows图片／语音来自配套改版宿主：
https://github.com/woshuoduijiushidui/OctoSense 。应用包不含宿主改动。

### Tag

Pending: v0.8.0，未推送。

### Full commit SHA

Pending: 最终发布提交，不用准备基线冒充。

### Bundle path

bundle/

### GitHub workflow run URL

Pending: 本次新标签的成功工作流。

### Release and pack URL

Pending: 最终Release及app.bundle.pack.json、release-receipt.json。

### Release pack SHA256

Pending: 下载最终包后计算并核对回执。

### Bundle BLAKE3 digest

Pending: 最终封存包清单为准；源包检查见review/GATE.json。

### Privacy policy URL

https://github.com/woshuoduijiushidui/pantry-steward/blob/main/PRIVACY.md

本次隐私修订未推送，公开页面与候选一致性待再次核对。

### Support contact

https://github.com/woshuoduijiushidui/pantry-steward/issues

### Platforms tested

Windows：配套改版宿主源码e5f8a820e858e8828695c903344c1756752bf67f的现有二进制；
相同业务脚本的已有TEST签名样本、隔离合成档案，19项原生检查及2项重启检查
通过。36项自动测试通过，包括Script VM生产helper。不是官方发布版、真实
模型或最终封存包安装证明。其他平台未验证。

### App Hub revision the gate ran on

386359153ed6377b5f047bd9ed2767a6a2ac2bc7

### Gate and publisher verification output

源包通过，只有unsigned警告，完整结果见review/GATE.json；scan有7项问题，
未执行外部审核器。本次publisher-unpack／publisher-verify待发布后下载验证。

### Scan answers

REVIEW-ANSWERS.md回答全部7项问题，并指出源文件、宿主和验证限制。

### Screenshots

bundle/screenshots/05-current-home.png
bundle/screenshots/06-current-inventory.png
bundle/screenshots/07-current-chat-draft.png
bundle/screenshots/08-current-settings.png

真实Windows运行、合成库存、在线AI关闭、未发送文字；不是模型／相机／录音
成功证据。正式提交需补不可变源码链接。

### What is not verified

本次真实模型／ASR／图片提供方、硬件相机／录音、完整新功能回归、官方发布
宿主封存包安装和升级、新电脑冷启动及Android／iOS／macOS／Linux。
新版工作流、下载摘要和发布证明仍待完成；本地TEST签名不是正式发布身份。
模拟采购不产生真实交易。

GitHub API确认公开repository ID1399970684、owner ID327475236，是旧仓库改名；
认证目录sequence16尚无pantry-steward，发布前需重查。首次上架前沿用#166，
保留历史比赛评分记录。

### Optional legacy authentication

Not applicable: GitHub publishing.

### Confirmations

- [ ] 发布者复核：包和Issue无密码、私钥、API Key或Token。
- [ ] 不移动、删除或重建已经推送的标签。
- [ ] 已列待验证项，理解Release成功不是Hub审批或上架。
