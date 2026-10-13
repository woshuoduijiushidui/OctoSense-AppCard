# Migration validation

## Issue #3 PR baseline sync — 2026-10-13

The Issue #3 branch merged `origin/main` at `900c0c3`, retaining the current
`model.complete@2` image discovery/import contract and the optional local-host
microphone/transcription contract in the same bundle. The restamped 0.8.0
bundle digest is `9cce08f308fdfbe9d3f124c36ac93fb54e8dd4ad53be752b68c57c59b6edac5e`.
The pinned Hub's offline bundle gate passed with only the expected unsigned
warning; the launcher check passed; all 36 Python tests passed. A synthetic
Agent-panel screenshot from the pre-sync candidate is in
`docs/qa/issue-3-agent-panel.png`; the panel code had no text merge conflict.
Real model, camera and microphone calls have not been replayed on the merged
digest. Earlier foreground evidence remains tied to its recorded digest.
The standalone `card-host` rejected this digest at admission because it does
not implement `app_policy.device_consent@1`; its offline smoke did not reach
the app. That path requires the full desktop host, so it is not counted as a
passed native regression for this digest.

## Issue #3 chat follow-up — 2026-10-13

The bundle digest before the PR baseline sync was `e223fff9ac368106af591be2346df5e4289a20750bc6136883fd92579d24a308`.
The chat panel now keeps the latest message visible and offers older/newer pages;
opening it again keeps the selected history page. Message bubbles have horizontal
and bottom insets. A two-step `清空` action deletes only today's visible messages
and context summary; inventory, menu and confirmed soft preferences remain.
Successful Agent replies also clear the native text field, while a failed model
call retains the draft for retry.

The screenshot's `18262` is an internal day count for 2020-01-01. Both isolated
test profiles had a synthetic egg batch with that expired date. Agent input now
uses a calendar date and expiry status; the app does not silently edit stored
inventory. The model receives the formatted date, expiry status and quantity
label, while previous assistant messages and the summary are sanitized before
normal replies and context compaction. The model task now explicitly requires readable dates,
units and nutrition explanations. User-facing replies and old assistant bubbles
also filter repeated internal field names, numeric IDs and `piece`;
actual-consumption review text and the stock picker use the same readable terms.

- Production Script VM cases passed, including session clearing without business
  writes, history paging after an incoming message, repeated internal-field
  filtering in model context, expiry display and clearing the native text field
  on success.
  Full Python suite passed 36/36 in a task-owned Windows temporary directory.
- Pinned Hub stamp/check and `tools/launch.py --check --offline` passed with the
  expected unsigned warning. Isolated official native offline smoke passed 19
  checks; quit/relaunch restart checks passed 2.
- In an isolated official native profile with synthetic chat history, the panel
  opened on the latest item, older/newer navigation returned to it, and `清空`
  showed a separate confirmation. After confirmation, messages and summary were
  empty and the business-state file SHA-256 was unchanged. A persisted old
  assistant reply containing repeated `18262`, `piece`, `menu_candidates`,
  `nutrition_kcal`, `uses` and `food_id` rendered without those raw tokens.
  The native bubble inset and scrollbar were inspected from a real screenshot.
- This follow-up did not call a real model or microphone. The successful-send
  input clear was verified in the production Script VM; a real-provider repeat
  remains unverified because the configured host reached its model budget.

## Issue #3 M6 end-to-end checkpoint — 2026-10-13

The Issue #3 candidate uses one Pantry bundle in two isolated Windows host
profiles. Final source digest: `ee11ba0571780a3351473261c5e0a590f2cc6f74d18441d529d88c878737cb81`.
The pinned Hub stamp/check passed with the expected unsigned warning. The
production Agent still uses the host model service and the existing inventory,
three-meal menu and intake confirmation paths. M6 tightened durable preference
filtering, current-state precedence in compressed conversations, user-readable
proposal cards and reply text, and a deterministic fallback when a model
incorrectly describes an unconfirmed proposal as already recorded. Settings
now describe the local voice capability and official text fallback accurately.

- **Unit/fixture:** `python -X utf8 -m unittest discover -s tools -p 'test_*.py'`
  passed 36/36 with a task-owned Windows temporary directory. The production
  Script VM cases include durable preference versus a one-off meal request and
  a false `已记录` model reply while an intake proposal remains unconfirmed.
  `python -X utf8 tools/launch.py --host-workspace ..\OctoSense --check --offline`
  passed. The final bundle version remains 0.8.0.
- **Official native, isolated, AI disabled:** `tools/smoke.py --m6-offline`
  passed 19 checks on a fresh profile: six-cycle onboarding, camera/import
  fallback, manual stock entry, separate batches, edit/remove, settings and
  no fabricated menu when online AI is disabled. After host quit/relaunch,
  `--restart` passed 2 exact-state and home checks. The historical
  `--legacy-flow` path still assumes a removed local-rule menu switch and was not used
  as evidence for menu or intake; those paths were exercised separately.
- **Menu shortage and simulated market, isolated fixture:** a copy of the
  accepted synthetic three-meal state had spinach reduced to 100 g in a
  task-owned profile. The Menu page derived `还差 100 克` from 200 g planned
  use, with no intake record or stock deduction. `一键补齐` carried that gap
  into one spinach cart line and one pack; submitting a confirmed simulated
  order left stock revision 10, spinach 100 g and execution count zero.
  Restart kept an identical `pantry.json` SHA-256. Confirmed receipt then
  created a separate 300 g spinach batch, set the order to `已收货`, and left
  execution count zero. The Menu page re-derived `库存够，不用买`; a second
  restart again preserved the exact state. The order/receipt check used a
  synthetic stock mutation, not a real purchase or a model response.
- **Official native, real provider:** on the prior M6 build, the same-day Agent
  continued across Home, Inventory and Menu; 11 messages survived an official
  host restart with the same session digest. The unsupported microphone path
  showed the exact text fallback and created no WAV. A two-egg proposal wrote
  nothing before review and one inventory event after final confirmation; an
  ambiguous egg-batch edit asked which batch without a proposal. At 17
  messages, context compaction advanced its summary cursor while the visible
  conversation remained. A complete three-meal proposal wrote no stock before
  confirmation; acceptance saved the menu without deducting inventory. A
  separately requested `偏好清淡` was saved as soft memory only after accepting
  its menu, and the next real answer saw it. Task-owned synthetic spinach,
  mushrooms and tofu were seeded only inside that isolated app-data to make a
  three-meal menu feasible. The final-digest official text probe received the
  host `rate`/budget error, retained the unsent draft and made no business
  write; a final-digest real-provider reply is therefore unverified.
- **Local native, real provider and device:** an earlier M6 build used a real
  Windows microphone and configured MiniMax ASR. The person edited its mixed
  Chinese/English transcript before pressing Send. The resulting real Agent
  reply said today's menu was locked and suggested tomorrow; inventory
  revision 11 and one confirmed execution record remained unchanged. A real
  intake handoff opened the existing review; after removing an unwanted
  prefilled food and confirming breakfast tofu, stock changed once and the
  three-meal plan remained locked. A later lunch handoff was cancelled and
  appended a local result without a business write. The final-digest local
  host repeated the real microphone test: ASR filled a mixed Chinese/English
  request about Greek yogurt and tomatoes, the person added `只给建议` and
  pressed Send. The persisted user message included that edit; the real Agent
  replied with tomorrow-only advice while explaining that today's menu was
  locked. Inventory revision remained 11 with one confirmed execution record.
- **OctoSense:** `cargo test --locked --offline -p octosense-llm-service
  --test media --quiet` passed 28 cases; `cargo test --locked --offline
  -p octosense-shell --features app-hub --lib audio_service --quiet` passed 8;
  `cargo check --locked --offline -p octosense` and
  `python tools/setup.py --check --cargo` passed. The shell test without
  `app-hub` selected zero cases and is not counted. Windows speaker playback,
  hosted CI and sealed Store publication were not tested.


## Issue #3 M3 本地提案与业务确认集成 — 2026-10-13

在 `feat/issue-3-global-agent-voice` 上接入七个文字 Agent 工具值：`none`、库存
add/edit/remove、完整三餐 generate/adjust 和实际摄入 handoff。模型只返回一份提案；
本地逐字段校验并显示固定卡片。点击卡片进入现有核对页，取消或状态快照变化时
丢弃内存提案。库存仅在最终确认时走 `apply_inventory_operation()`；菜单复用
`build_ai_menu()`、`save_day_menu()` 和 `accept()`；实际摄入仍由用户核对后走
`confirm_consume()`/`finalize_actual()`。普通偏好只在接受同一份有效菜单后写入
M1 软记忆。内部 `food_id` 等编号从用户可见回复中剔除。

已合入的业务契约使用 `state.plans[]` 三餐，而非设计稿中的独立 `daily_menu`。
本次补齐常规日菜单逐餐确认：第一餐记录 slot/menu_id 并扣对应实际库存，
保留三餐菜单；任意一餐确认后锁定当日菜单，三餐确认完才结束 active 菜单。

- 从生产 `bundle/main.splash` 提取的函数 VM：**30 个场景通过**，覆盖七种工具值、
  批次歧义、非法参数与旧快照、核对/取消、菜单一次纠正、完整三餐接受和记忆。
- `python -X utf8 -m unittest discover -s tools -p 'test_*.py'`：正常本机权限下
  **36/36 passed**。默认沙箱的 Windows 临时目录 ACL 会使其中 6 项文件测试出现
  `PermissionError`；正常权限复跑全部通过。
- 固定 App Hub `hub stamp bundle` digest
  `4bd53dd902385ec7b76fbbd2b22e53109d621eac0af39fbb7a93e867241cad2c`；
  `python -X utf8 tools/launch.py --hub ..\OctoSense\target\release\hub.exe --check`：
  **PASSED**，仅有 unsigned editable bundle 提示，版本仍为 0.8.0。
- 任务专用官方 OctoSense 宿主与真实已配置提供方：新增鸡蛋 2 个在核对前零写入，
  最终确认只产生一次 `add`；新增菠菜 200 g 后取消，`pantry.json` 字节不变。
  生成与调整完整三餐在核对前零写入，接受后仅菜单变化，库存未提前扣减。
  豆腐 250→230 g 编辑及菠菜移除各在核对前零写入，确认后分别只产生一次
  `edit`/`discard`；移除不计实际摄入。
- 真实模型的“我吃了早餐的豆腐”进入摄入核对；用户取消建议的菠菜后确认豆腐
  80 g，豆腐库存 250→170 g，执行记录带 slot 0/menu_id，完整三餐菜单仍在，
  随后备选菜单被本地锁定。最终代码还在官方宿主再次调用真实模型：模型回复
  “内部 food_id 为 1” 时，保存的 assistant 消息只含公开的“豆腐 230 克”，
  业务 revision 仍为 5。部分摄入 `recorded_kcal` 的最后展示修补通过代码检查、
  全量测试与 App Hub gate，最终版的原生逐餐回放 **not run**。M4 麦克风/ASR
  亦 **not run**。测试结束后已恢复任务专用 profile 的原始业务及会话文件。

## Issue #3 M2 阶段与菜单回调快照补齐 — 2026-10-13

在已有 M2 纯文字 Agent 主流程上，发送前显式记录当前确认阶段 ID/完整阶段快照、
今日已接受菜单 ID/状态/完整菜单快照和实际摄入锁定标志，同时保留日期、档案/库存版本、
消息 ID、输入原文和整份业务状态快照。回调先检查 token、阶段与快照，再验证模型信封；
阶段或菜单变更后旧回复只显示重试提示，不追加 assistant 消息。

- 生产 Splash 函数 VM：**25/25** 场景通过，新增阶段/菜单标识与内容、菜单锁定、
  旧 token 在新请求期间迟到以及状态变化后的重试覆盖。
- `python -X utf8 -m unittest discover -s tools -p test_*.py`：正常本机权限下
  **36/36 passed**。默认沙箱和仓库内临时目录均触发 Windows tempfile ACL 的 6 项
  PermissionError；正常本机权限复跑成功。
- 固定 App Hub `hub stamp bundle`：digest
  `18761744c455a504d105607b9e3ee323316468d3994e49141790a49f6a8e6ff2`；
  `tools/launch.py --hub ... --check`：**PASSED**（仅 unsigned editable bundle 提示）。
- 使用既有本地测试密钥在独立 `target/m2-completion-profile` 签名、发布、安装成功，
  官方桌面窗口已在用户交互桌面启动。合成豆腐库存建档后，第一次真实文字请求
  保存了 user 消息并收到宿主 `no_provider`；检查时任务专用宿主的已保存模型 profile
  尚不存在。用户随后在 AI providers 完成模型列表保存；同一任务专用配置复跑通过。
- 宿主返回已知错误码时 Agent 现在显示具体可重试提示；未知错误仍使用通用提示，
  不向应用界面暴露提供方、密钥或原始响应。
- 官方宿主原生 UI + 真实提供方：主页、库存页、菜单页共用当天对话，7 条真实
  assistant 回复均落入本地 `agent-session.json`；模型正确读取合成库存 1 批豆腐
  250 克、今日无已接受菜单和当前阶段。达到第 15 条消息时 UI 实际显示压缩提示，
  摘要游标从 0 推进到 6，再返回本轮回复；16 条 UI 消息原文均保留，滚动可看
  首条与最新回复。截图：`target/m2-completion-profile/m2-live-latest.png`。
- 同日关闭并重启官方宿主后，session 文件 SHA-256 均为
  `12A329319B7E43B6B2A3D2CBCC6126D197A32D2E8630FCC27588EC6C6D80F26C`；
  16 条消息、7 条 assistant 回复和摘要游标 6 恢复，抽屉首尾消息均可见。
  Agent 对话后业务数据仍为 1 批豆腐 250 克、0 份菜单、1 条原始入库事件。
  原生测试仅在 Windows 任务专用配置执行；没有把 VM 回调算作真实提供方证据。

## Issue #3 M1 当日会话、权威上下文与软记忆 — 2026-10-13

在 Pantry `origin/main` `c6f4d80` 上补齐 M1：每轮 Agent 输入从已确认档案、`current_stage()`、
库存批次、今日已接受 `state.plans` 菜单和本地软记忆重建。菜单未接受时不进入投影；
今天已有实际摄入记录时投影标为锁定。投影不带购物车、订单、原始执行记录、
图片／音频路径或模型配置。

- 压缩前与每次压缩后均按完整 `input.to_json()` 的 UTF-8 字节数检查 24 KiB。
  超量且无法继续压缩时保留当前消息与 UI 历史，提示用户缩短输入。
- 用户在现有在线日菜单入口明确输入普通偏好、生成菜单通过 Issue #5 校验后，
  候选只暂存在内存。用户接受同一份、未改动的菜单后写入独立
  `agent-memory.json`；删除、修改或跨日菜单不会写入。记忆写入失败不回滚菜单。
- 生产 Splash 函数 VM 覆盖 24 个场景，包括跨日生成、真实 `accept()`、失败写入、
  最终输入预算、多批压缩和 UI 消息保留。`python -X utf8 -m unittest discover -s tools
  -p 'test_*.py'` 在正常本机权限下 **36 passed**；固定 App Hub 盖章与
  `hub check bundle --allow-unsigned` **PASSED**（digest
  `342f1bf84930d684ddc1e906ed932042b76fb062fc5b62a6dda51e4cefdbeb42`，仅 unsigned 提示）。
- 本次没有运行真实模型生成／压缩输出和原生 UI。Agent 可执行菜单提案属于 M3，
  本次记忆确认验证使用现有日菜单生成与接受路径。

## Issue #3 分支同步 Issue #5 主线 — 2026-10-13

`feat/issue-3-global-agent-voice` 合入 `origin/main` 的 #40、#42、#44。`plan()` 同时保留
Agent 在线操作排它检查与菜单自动纠正状态初始化；按宿主固定 App Hub
`8347a489141c0e24cab564883db7c4592935a8b2` 重新盖章，manifest 版本保持 0.8.0。

- `hub stamp bundle` 后 `hub check bundle --allow-unsigned`：PASSED（仅 editable bundle unsigned 提示）。
- `python -X utf8 -m unittest discover -s tools -p 'test_*.py'`：36 passed。本机沙箱内的
  Windows 临时目录 ACL 使 6 个测试无法创建临时文件；在正常本机权限下重跑通过。
- 未运行本次同步后的原生 UI、真实 provider 与麦克风测试；这些结果不能由离线测试替代。


## 0.8.0 bundle 合并丢失定义与官方 rc.6 实测 — 2026-10-13

在未改动宿主的前提下，用官方预编译 rc.6（`%LOCALAPPDATA%\OctoSense\octosense.exe`；
安装包 sha256 `4cced00c…` 与官方 `SHA256SUMS` 一致；旧 alpha.3 安装目录已整目录备份）
做了一次完整走查，发现并修复 0.8.0 bundle 里被合并吃掉的一块代码。宿主侧没有问题；
此前「rc.6 存储不可用」的判断是错的——那是我塞进去的非法种子文件触发了应用自带的
`storage_blocked` 保护，应用拒绝一切写入是设计行为。

- 缺失或被改动处（旧副本 `target/main.splash` 与 `.local-state/qa-29/bundle/main.splash`
  仍保留原文）：`let cycle_days`（+`cycle_view`）、`fn profile_ready()`、
  `base_daily_kcal()` 的函数体被留在重复的 `fn make_programs()` 名下、
  `plan_draft`/`draft_swap`/`stage_edit` 声明、`confirm_health_plan` 里的 `entries` 列表、
  `valid_state` 的 `programs` 上限被收窄成 `>3`（生成器实际给 18 = 6 周期 × 3 变体）、
  6 处 `active_program()` 调用（函数已改名，当前阶段取 `current_stage()`）、
  `ensure_extended_state()` 用 `program_active > 0` 判完成态而 `program_active` 从不被置位
  （旧副本用 `state.stages.len() > 0`）。宿主 API 与 provider 通路均未改动。
- 症状对应：`下一步 · 选择周期方案` 点了没反应（`save_profile()` 抛错，而该页不渲染
  `message`）；录入库存被拒 `库存操作未通过完整校验。`；首页 `on_render closure failed`；
  重启后被弹回周期选择页。
- 修后在 rc.6 的隔离 app-data 里实测（真实 provider，脚本错误 0 条）：首次建档 1/4 → 4/4、
  18 个候选、4 批库存、`生成 / 更新未确认三餐` 拿到真实 AI 三餐、状态跨重启保留；新入库
  「牛油果 120 g」得到真实估算 `kcal 160 / protein 2 / fiber 6.7 / vitamin_c 10`，
  `source: "AI 估算"`。个人库存与 provider 凭据未被读取或复制，真实档案未改动。
- 宿主级独立证据（与 bundle 同 manifest id 的最小探针，同一 rc.6 宿主与同一 provider）：
  `model.complete` 回 `{"is_ok":true,…}`（今日 1/100 次、input 310 / output 91 tokens），
  `fs` 读写正常，jail 内文件真实落盘。
- 未验证：三餐生成的实时延迟——同一流程两次撞上应用自带的 95 s 等待上限、一次按时返回；
  `tools/qa_day.py` 因此只在 provider 及时回答时继续走核对与账本断言，否则断言
  「未写入任何东西」并注明。
- 未修复（仅记录）：`valid_state` 丢掉了 `cycle_seed` 长度校验；三餐请求延迟与 95 s
  上限的关系需要产品决定；`tools/qa_actual_feedback.py`、`tools/qa_online.py`、
  `tools/qa_review_feedback.py` 仍在用旧控件名（`food_name`/`food_grams`/`food_days`），
  `qa_ai_nutrition.py` 只做了标签/字段对齐、尚未重跑。
- Bundle digest（合并 main 之前的工作区修复版）: `f26f33139ee34cf9fdc9cb3d50493bf6ce94901dbb3228aa0df0c1fe12e2a0d7`（版本保持 0.8.0；`hub stamp bundle` + `hub check bundle
  --allow-unsigned` 在 rc.6 固定的 App Hub `386359153ed6377b5f047bd9ed2767a6a2ac2bc7`
  上 PASSED，只有预期的未签名警告）。
- 合并 `origin/main` 后的回归（同一 rc.6 宿主、隔离 app-data、真实 provider）：
  `bundle/` 取主线版本（`hub check --allow-unsigned` 通过；脚本错误 0 条），
  `tools/qa_day.py` 10 项断言全过（建档 → 4 批库存 → `生成 / 更新未确认三餐` → 未写入任何东西）。
  回归同时发现三处主线漂移并已修：状态里已没有 `program_active`（改看 `stages`）、
  周期确认按钮改名 `确认计划 · 去录冰箱  →`、设置页的「改用本地规则/关闭提醒」已不存在
  （`smoke.py` 该段留了 `shortcut:` 注释，尚未重写）。三餐生成本次仍在应用自带的 95 s
  上限内没返回（状态停在「在线 AI · 正在规划」），与本轮前几次一致，属 provider 延迟。
- 合并 `origin/main` 后：主线上本来就带着这些定义（`cycle_days`/`profile_ready`/`base_daily_kcal`、
  `stages.len() > 0` 完成态判据、`>20` 候选上限），并已含 PR #45 的图片接口改造，所以合并时
  `bundle/` 取主线版本；本节记录的工作区症状只存在于工作区回退版里。

## Image contract review, 2026-10-13 — source and package checks

The app now discovers the host's `model.complete@2` image input through
`runtime.describe` instead of calling an app-specific probe. It declares
version 2 as optional, so hosts without it retain manual entry. Existing-image
selection uses `files.import`; the callback checks the returned byte count and
removes an imported file above 10 MiB before any model call. A provider may
still reject image input after host discovery.

The pinned App Hub stamped digest
`69a1df657406ecf8b69d4d76946f5b5a2c1c540a902cbf47694fea5646acb1f4`
and checked the unsigned editable bundle; 35 launcher/release Python tests
and the launcher check passed in an isolated test run. This changed
contract has not yet been replayed in a foreground window with a real
provider or camera. The earlier user-reported foreground checks below apply
to a preceding digest only.

## Issue #43 裁决：菜单只在生成时使用库存（承认现状）— 2026-10-12

产品负责人选择 #43 的**方案 1**：承认已合并实现的严格 stock-only（#21 把它钉为
`docs/ai-nutrition-validation.json` 的 `native_stock_only_checks`），改规格而不是改
代码。菜单的候选只是生成时的可用库存；模拟商品目录不参与菜单生成，其每 100 g 参考
不参与菜单核算；缺菜清单承接的因此是已生成菜单在库存变化后的差额。方案 2／3
（菜单引用库存外候选）写入 #22 的 Out of Scope。本仓库不改代码。

- GitHub #22：Problem Statement、Solution 第 1 段、User Story 9／10、
  Implementation Decisions（菜单与日菜单、缺菜清单）、Testing Decisions 闭环、
  Out of Scope、Further Notes 按该裁决改写；改动说明与跟进评论留在 #22。
- `GLOSSARY.md`：「菜单」词条不再写「它可以包含库存中没有的食材」，「缺菜清单」
  词条写明它是已生成菜单在库存变化后的差额；Related 增加 ADR-0005。
- `README.md`／`README.zh-CN.md`：日菜单生成叙述写明候选只来自生成时的库存，
  边界说明以生成后的库存变化定义「库存不足」，并注明模拟商品参考不参与菜单核算。
- `docs/adr/0005-菜单只用库存生成.md`：记录裁决、代价与备选。
- `tools/test_release.py`：新增离线守卫 `test_design_decision_stock_only_menu_source`，
  钉住 prompt 的 stock-only 候选规则与文档词条。

### 已验证

- `python -X utf8 -m unittest discover -s tools -p 'test_*.py'`：**35 passed**（新增 1 条守卫）。
- `bundle/` 无改动，manifest 摘要与版本不变，因此没有重新盖章（盖章只在 bundle
  变化后做）。

### 未验证

- 只改了文档、规格与离线守卫，没有重跑原生 QA；无行为改动，现有 stock-only
  原生断言（`docs/ai-nutrition-validation.json`）仍是该行为的证据。
- 「先有想吃的菜、再决定买什么」不在本版范围内（#22 Out of Scope），需要时另开决策。
- 发版检查点、签名与提交仍是人工决定。

## Issue #41 A4 裁决：AI 估算写回批次（基于已合并 #21）— 2026-10-12

产品负责人选择**决策 1**：以已合并 PR #21（`358d61c`）为准，A4 的边界改为
「估算可以写回批次，但必须带 `source: "AI 估算"`、`basis`、`estimated_at`、
`model` 溯源，并且仅作参考」。本仓库不改代码，只把规格与词汇表对齐到该决定；
power246《Issue #5 技术设计文档》是外部人工文档，本仓库不直接编辑它。

- `EXPERIENCE.md`：写明库存 AI 参考写回批次时的溯源字段，以及「仅作参考、用户填写
  与包装数据优先」。
- `GLOSSARY.md`：新增「营养参考」词条，并把 ADR-0004 加入 Related。
- `docs/adr/0004-AI-估算写回批次但仅作参考.md`：记录决定、代价与备选（原
  D5-015「只留菜单/执行快照」、写回+溯源、写回但可覆盖/界面区分）。
- `tools/test_release.py`：新增离线守卫
  `test_design_decision_a4_estimates_write_back_with_provenance`，钉住代码里的溯源
  字段与文档词条。

### 已验证

- `python -X utf8 -m unittest discover -s tools -p 'test_*.py'`：**34 passed**
  （新增 1 条 A4 守卫）。
- `bundle/` 无改动，manifest 摘要与版本不变，因此没有重新盖章（盖章只在 bundle
  变化后做）。

### 未验证

- 只改了文档与离线守卫，没有重跑原生 QA。决策 1 不涉及行为改动，现有
  `docs/ai-nutrition-validation.json`（30 条原生断言）仍是估算写回行为的证据。
- 发版检查点、签名与提交仍是人工决定。

## Issue #22 与 Issue #5 设计文档对齐：A6／B1／B2（基于 main 的 #21）— 2026-10-12

产品负责人在交叉设计验证后确认四项决定。这一版**从 main 重做**：A4（AI 营养估算）
已由已合并的 PR #21（`358d61c`）交付，不再重复实现；本版只带 A6／B1／B2。

- **A6 一次自动纠正**（设计 D5-007）。`plan()` 重置 `ai_correction`／
  `ai_validation_error`；`save_ai_result` 的每个失败分支（reason、三餐数、
  title／minutes／steps／uses 计数、食材数量与 grams、planned 为空、parse_recipe、
  整份 validate、解析异常）写入具体错误；`apply_model_reply` 在菜单流程首次失败时
  把该错误追加到任务描述并直接再调一次 `online_plan_ready`，第二次失败按原样
  `ai_failure` 并保留重试入口。一天体验（`save_ai_trial_result`）和自己的
  营养估算流程（`nutrition_flow`）保持各自的单次失败路径，不混入纠正。
- **B1 接受跨批次**（设计 §7.2）。新增 `allocate_uses`／`draw_split`／`draw_piece`：
  内存池按到期日从早到晚分配，未知到期最后，不跨单位族，一条 use 先花自己计划
  的批次（保留食用核对页「改用同名食材的第 N 批」），不够才补到其它兼容批次，
  且同一天的多条 use 不会重复花同一批次。`validate` 改为
  `allocate_uses(p, p.uses).fits`；`finalize_actual` 的库存核对与扣减也用同一份
  分配（`draw_split` + `merge_draws`），所以跨批次菜单从接受到扣减一致。
  `merge_draws` 还把同一批次的多笔合并成一条 `consume` 用量，因为
  `apply_inventory_operation` 拒绝同一次操作重复列同一批次。piece 仍留在单批次
  （`shortcut:` 注释说明原因：平均克数是每批次的值）。
- **B2 接受菜单才控制一键补齐**（设计 D5-008）。菜单页只在 `p.accepted` 时
  渲染「一键补齐」，未接受时显示提示；`open_market()` 也拒绝未接受的菜单。

### 已验证

- `bundle/main.splash` 通过本机 `makepad-script` 的 `ScriptVm::eval`
  （`target/parsecheck`，解析＋作用域检查）：只报预期的宿主缺失 `time_now`，
  没有解析错误。该探针直接抽取 `main.splash` 里同一段 B1 代码跑内联断言：
  use 先花自己计划的批次、不够时按到期顺序补到下一批（100＋50）、单批次不会
  被两条 use 重复花掉、同一批次的多笔 draw 被 `merge_draws` 合成一条 60 g、
  未知到期排最后、piece 不跨批次。
- `python -X utf8 -m unittest discover -s tools -p 'test_*.py'`：**33 passed**
  （新增离线守卫 `test_design_decisions_a6_b1_b2`）。
- 用宿主固定引用的 App Hub `8347a489141c0e24cab564883db7c4592935a8b2`
  （`target/hub-8347/release/hub.exe stamp bundle`）重新盖章：
  `3c4fe4bc2798b9eaf82b09228679dcfef0e0ab4009719c5bf57f5cae5b16a270`，
  并用 hub 的算法独立复算一致。manifest 版本保持 **0.8.0**，能力保持
  `storage, model, camera, files`。`hub check bundle --allow-unsigned`：
  `pantry-steward 0.8.0 — PASSED`，仅 unsigned 警告。
- `tools/smoke.py`（脚本层改动，本次未在宿主上执行）：新增
  `accept_menu_if_needed` 并在 8 处「一键补齐」之前调用；`exercise_market`
  增加「一键补齐 waits until the menu is accepted」与「an accepted menu offers
  一键补齐」两条断言。

### 未验证

- **没有在本机跑原生 QA**：本机没有完整 OctoSense 宿主 checkout，也没有
  `card-host.exe`，所以 `--menu-purchase`／`--market*` 模式未重新驱动，A6 的
  纠正回环也没有真实 `model.complete` 调用。改动是「代码完成、原生 QA 未跑」状态。
- B2 改变的先接受后补齐流程只在脚本层验证，未在真实宿主上跑通。
- A4 与已合并 #21 的分歧（决策要求估算“不写回库存批次”，#21 把估算以
  `source: "AI 估算"` 写回 `state.foods[].nutrition` 并冻结进实际记录）
  不在本 PR 处理，已另开 issue 由产品负责人决定。（#41 后来已裁决为决策 1，
  见本节上方。）
- 发版检查点、签名与提交仍是人工决定。

## Issue #29 交付检查点：标注、文档、截图、重新盖章 — 2026-10-12

This is the delivery checkpoint, not a behaviour change: `bundle/main.splash` is
byte-identical to the Issue #28 commit. Only metadata, screenshots and docs
changed.

- Renamed-repository links fixed everywhere they were still stale after the
  rename to `woshuoduijiushidui/pantry-steward`: `bundle/listing.json`
  (`publisher.support`, `publisher.privacy_policy_url`), `PRIVACY.md`,
  `SUPPORT.md`, the historical links in `SUBMISSION.md`,
  `tools/test_release.py`'s `REPOSITORY`, and the tracker note in `AGENTS.md`.
  No `OctoSense-AppCard` URL remains in the tree outside ignored local state.
- The four `bundle/screenshots/*.png` release assets were recaptured from this
  commit's bundle files in the same hidden reference card-host used since
  Issue #24 (655114c, 1200x800, synthetic inventory: 豆腐 300 g 临期, 鸡蛋
  2000 g → 100 g, 菠菜 200 g 临期, 蘑菇 150 g; local-rule day menu): 首页 (4 批);
  the candidate three-meal day menu with its derived 缺菜清单; the 缺菜清单
  after the 鸡蛋 batch was edited to 100 g, showing `需要补齐 952` / `还差 952 克`,
  the editable amount, and the `一键补齐 · 去模拟买菜` entry; and the inventory
  batch list. The old captures predated #25 and showed neither the editable gap
  nor `一键补齐`. The earlier text said 941 克; the honest recapture says 952.
- Restamped with the official App Hub revision the current host pins,
  `8347a489141c0e24cab564883db7c4592935a8b2` (`hub stamp bundle`), built with
  `cargo build --release -p octosense-app-hub --bin hub` from a task-owned
  worktree checked out at that commit (output under `target/hub-8347`, using
  the prepared sibling runtime checkouts). `bundle_blake3 =
  c75cc689a2bd050ed682d787c272b10c57541412fc0bf8e073c2dc12a40e3bc6`. Manifest
  version stays **0.8.0**; capabilities stay `storage, model, camera, files`.
- `hub check bundle --allow-unsigned` on the committed bundle **PASSED** with
  only the expected unsigned warning: `pantry-steward 0.8.0 — PASSED`, warning
  `publisher-signature: unsigned`. This is why the host pin matters: the older
  publishing pin `655114c4943cd2490daaefa2173e7b5aaa20669f` does not know the
  `files` capability and refuses it. That refusal was a pin mismatch, not a
  bundle defect; `files` is declared in App Hub from commit `30c9d19`, which is
  in the host pin's history.

### Native run, 2026-10-12 — bundle files of this commit, manifest patched in a test copy

- Same task-owned host procedure as Issue #25–#28: `.local-state/qa-29/bundle`
  with `manifest.json` patched in that copy only (drop `files`, `requires`,
  `host_api`), admitted with the pinned reference `card-host --stamp
  --allow-unsigned` at 1200x800. The copy differs from the committed bundle
  only in `manifest.json` (`diff -rq`), so no committed bundle file differed.
  This copy is used only because the machine's prebuilt card-host is the
  655114c build that lacks `files`; the committed manifest was not changed to
  accommodate it.
- The four screenshots above are real captures of that run.
- Regression on the same bundle files: `python -X utf8 tools/qa_release.py
  --port 18499 --profile .local-state/qa-29/qa-std --menu-purchase` — **13/13
  checks passed** (three meals, grams, over-budget refusal, merged 缺菜清单,
  re-derived gap, editable gap, never stored, accept, empty-meal refusal).
  Since `main.splash` is byte-identical to the #28 run, the #25–#28 mode
  regressions are unchanged and were not re-driven.
- `python -X utf8 -m unittest discover -s tools -p 'test_*.py'`: **31 passed**
  (includes the updated repository-link guard).
- `git diff --check` clean; bundle 2,518,774 / 8,388,608 bytes.
- All inventory was synthetic; no real inventory, keys or provider calls.

### Not verified

- No full OctoSense shell checkout with the 8347a489 pin exists on this
  machine, so the committed manifest was not run under the full official shell
  (only the reference card-host on a patched test copy).
- Live `model.complete` was not exercised; the QA used the local rule path.
- The publishing workflow and `publisher-toolchain.json` still pin App Hub
  `655114c4943cd2490daaefa2173e7b5aaa20669f`, which cannot gate this bundle as
  is; the publishing route must be reviewed before any 0.8.0 tag.
- Formal release evidence review, publisher identity/signing, public-link
  review, App Hub submission and competition qualification remain human
  checkpoints. No tag, Release, new issue or submission was made.

## Issue #28 确认收货：核对数量与保质期并入库 — 2026-10-12

- `bundle/main.splash` (schema stays 2, no new state field): the transient
  `receipt` draft is opened by `market_receipt_open(order_id)` from a
  `确认收货  →` action on a `待收货` 模拟订单. Each line is
  `{name, product, ordered, received, days, unit, price_cents}`; `received`
  defaults to `ordered` and `market_receipt_step` steps it within `0…ordered`
  (the `＋` undo never exceeds the ordered amount),
  so a short-shipped delivery is never accepted by default. `days` defaults to
  the 模拟商品's `shelf_days` (today + days) and is editable through
  `market_receipt_days`; blank means 保质期未知.
- `bundle/main.splash`: `market_receipt_batch` turns one checked line into one
  batch from the product's spec (`g/kg/ml/L`, or a `10 枚 / 盒` count spec as a
  piece package). `market_receipt_confirm` gathers the checked batches and calls
  `apply_inventory_operation({type: "add"})` — the one inventory-write path — so
  every arrival gets a **new batch with a new id** and its own 到货日期 instead of
  merging into an existing same-name batch. It also removes the checked-in cart
  rows, sets the order status to `已收货` in the same commit, and never touches
  `foods` for unchecked lines. It writes no `stages[].intake` and does not move
  `meal_count`/progress.
- `bundle/main.splash`: `valid_state` now accepts `order.status` of `待收货` or
  `已收货`; older files were already migrated with `orders: []`. The 缺菜清单 was
  not changed: with the new batches in stock it re-derives from
  `用量 − 库存可用` (ADR 0003), so the unchecked remainder reappears on its own.
- `tools/smoke.py` / `tools/qa_release.py`: new `--market-receive` (defaults,
  partial check-in, new-not-merged batch, edited 保质期, no intake/progress,
  `已收货`, re-derived 缺口) and `--market-receive-restart` modes; both write the
  usual `expected-state.json`/`checks.json`. The restart check compares the
  persisted domain keys (`foods`, `orders`, `cart`, `stages`, `meal_count`)
  because the boot reminder legitimately rewrites the volatile `risk_key`/`log`.
- `tools/test_release.py`: offline guard
  `test_receipt_checks_quantities_and_adds_new_batches` (markers, `type: "add"`,
  status transition, unchanged app id).
- Committed manifest digest restamped with the pinned App Hub
  `655114c4943cd2490daaefa2173e7b5aaa20669f` (`hub stamp bundle`):
  `adb074b02773439eaffff3c67240ee39f4ee36b068280b1ec8f98b98daa53686`.
  Version stays 0.8.0; capabilities stay `storage, model, camera, files`.

### Native run, 2026-10-12 — bundle files of this commit, manifest patched in a test copy

- Same pinned reference `card-host.exe` (655114c) and the same task-owned test
  copy as Issue #25–#27: `.local-state/qa-receive/bundle` with `manifest.json`
  patched in that copy only (drop `files`, `requires`, `host_api`), admitted
  with `card-host --stamp --allow-unsigned` at 1200x800. No committed bundle
  file differed. `hub check bundle --allow-unsigned` on the real bundle rejects
  only the pre-existing `files` capability and accepts the new digest (no
  digest refusal).
- Command: `python -X utf8 tools/qa_release.py --port 18499 --profile
  .local-state/qa-receive/qa-receive --market-receive` — **10/10 checks
  passed**: the demo menu needs more 蘑菇 than one 100 g batch holds; 确认收货
  pre-fills the ordered `14 盒` and the product's `保质期 5 天`; `−` reduces it to
  `13 盒`; 确认收货入库 writes a **second** 蘑菇 batch (2600 g) next to the
  untouched 100 g batch (distinct ids), the new one carrying the hand-edited
  1-day 保质期 (`today + 1`) while the old one keeps `today + 30`; the stage JSON
  (`intake` empty, counters identical) and `meal_count` are byte-identical; the
  order shows `已收货`; and the 缺菜清单 re-derives to `库存可用 2700 g` with the
  remaining `300` gap.
- Relaunched the same host/profile and ran `--market-receive-restart`: **4/4**
  (`foods`/`orders`/`cart`/`stages`/`meal_count` identical, dashboard restored,
  the fridge still shows `蘑菇 · 2 批`, the order is `已收货` and no longer offers
  `确认收货  →`).
- Regression on the same bundle copy: `--market-order` **10/10**,
  `--market-order-restart` **3/3**, `--market-cart` **13/13**, `--market`
  **12/12**, `--menu-purchase` **13/13**, so the Issue #23–#27 flows still pass.
- `python -X utf8 -m unittest discover -s tools -p 'test_*.py'`: **30 passed**.
- Screenshot `docs/qa/issue-28-receive.png` is a real 1200x800 capture of the
  same run: 模拟订单 #1 待收货, 蘑菇 14 盒, and the 核对实际收到的食材 panel with the
  14→13 stepper and the editable 保质期天数 5.
- All inventory was synthetic; no real inventory, keys or provider calls.

### Not verified

- The committed manifest still cannot be admitted by the locally available
  reference host (pre-existing `files`/`host-api-v1` mismatch, unchanged by this
  work), so the bundle was not run under the full OctoSense shell.
- Live `model.complete` was not exercised; the QA used the local rule path.
- The receive flow was exercised for gram-spec products (菠菜/蘑菇). The count
  spec path (`10 枚 / 盒` → a piece-package batch) and the `ml/L` path are
  implemented and unit-guarded but not driven by the native QA, whose demo menu
  only needs gram ingredients.
- Pre-existing, unrelated: the generic `qa_release.py` default flow (no mode
  flag) still stops at `ui.fill(text, index)` on the onboarding page (six
  positional values, five `TextInput`s), unchanged by this work.
- #29 owns the release checkpoint: bilingual README wording, real screenshots,
  VALIDATION.md summary and the re-stamp are prepared here, but the final
  delivery review, signing and submission remain human checkpoints.

## Issue #27 模拟订单：确认、状态、不改变库存 — 2026-10-14

- `bundle/main.splash`: a 模拟订单 is user input kept in `state.orders` (like
  `state.cart`; the 缺菜清单 stays derived, ADR 0003). Each order is
  `{id, day, status, total_cents, lines}` where each line is
  `{name, product, quantity, unit, price_cents}`. `migrate_state` seeds
  `orders: []` for older files and `valid_state` bounds and type-checks it on
  load, so a restart keeps the submitted orders exactly. Schema stays 2.
- `bundle/main.splash`: the 购物车 tab shows `提交模拟订单  →`, and the order is
  written only by `market_submit_order`, which refuses to run unless
  `market.confirming` is true. `提交模拟订单  →` opens a `确认提交模拟订单？`
  panel with `确认提交订单`/`取消`; `取消` writes nothing. This is the only gate,
  so no order exists before the user confirms.
- `bundle/main.splash`: `market_order_lines` includes only non-dropped cart rows
  whose 模拟商品 is picked; a `无匹配` row has nothing to buy and stays in the
  cart, and a `可售不足` row is ordered at the product's `stock` (never more than
  可售数量). `market_order_total`/`market_order_line_total` use the simulated
  unit prices. The write skips `foods`, `stages`, `intake`, `meal_count` and
  progress entirely.
- `bundle/main.splash`: the 订单 tab lists each order as
  `模拟订单 #id · <下单日>`, a `待收货` badge, `共 N 样 · 模拟总价`, the lines and
  the note `下单不等于货到手…`. The footer states the 模拟下单 no-real-payment
  rule on every region page.
- `tools/smoke.py` / `tools/qa_release.py`: new `--market-order` (confirm-then-
  submit, status, stock/progress untouched, on-sale cap, unmatched row excluded)
  and `--market-order-restart` QA modes; both write the usual
  `expected-state.json`/`checks.json`.
- `tools/test_release.py`: offline guard
  `test_market_order_requires_confirmation_and_changes_no_stock` (markers,
  confirm/status/no-payment labels, orders in state, unchanged app id).
- Committed manifest digest restamped with the pinned App Hub
  `655114c4943cd2490daaefa2173e7b5aaa20669f` (`hub stamp bundle`):
  `cd69dfec7ecf8aa843f22a62c8398d071e1bf81cbbc5b6f9d50245ca1981ed88`.
  Version stays 0.8.0; capabilities stay `storage, model, camera, files`.

### Native run, 2026-10-14 — bundle files of this commit, manifest patched in a test copy

- Same pinned reference `card-host.exe` (655114c) and the same task-owned test
  copy as Issue #25/#26: `.local-state/qa-order/bundle` with `manifest.json`
  patched in that copy only (drop `files`, `requires`, `host_api`), admitted
  with `card-host --stamp --allow-unsigned` at 1200x800. No committed bundle
  file differed. `hub check bundle --allow-unsigned` on the real bundle rejects
  only the pre-existing `files` capability and accepts the new digest.
- Command: `python -X utf8 tools/qa_release.py --port 18499 --profile
  .local-state/qa-order/qa-order --market-order` — **10/10 checks passed**: the
  cart offers `提交模拟订单`; clicking it first shows `确认提交模拟订单？` with
  `state.orders` still empty; `取消` writes no order; `确认提交订单` writes exactly
  one `待收货` order and the 订单 page shows `模拟订单 #1` and its status; the page
  says no real purchase or payment; the 可售不足 row is ordered at the 14-box
  on-sale maximum while the 无匹配 row is left out; and `foods`, the stage JSON
  (`intake` empty, counters unchanged) and `meal_count` are byte-identical before
  and after submitting.
- Relaunched the same host/profile and ran `--market-order-restart`: **3/3**
  (state identical, dashboard restored, the order keeps its lines, `待收货`
  status and no-payment note).
- Regression on the same bundle copy: `--market-cart` **13/13**, `--market`
  **12/12**, `--menu-purchase` **13/13**, so the Issue #23–#26 flows still pass.
- `python -X utf8 -m unittest discover -s tools -p 'test_*.py'`: **29 passed**.
- Screenshot `docs/qa/issue-27-order.png` is a real 1200x800 capture of the same
  run (order #1: 菠菜 2 把, 蘑菇 14 盒, 模拟总价 ¥96.40, 待收货).
- All inventory was synthetic; no real inventory, keys or provider calls.

### Not verified

- The committed manifest still cannot be admitted by the locally available
  reference host (pre-existing `files`/`host-api-v1` mismatch, unchanged by this
  work), so the bundle was not run under the full OctoSense shell.
- Live `model.complete` was not exercised; the QA used the local rule path.
- 确认收货 (Issue #28) is not implemented at the Issue #27 commit; the order
  page and its note said so. It is implemented by the Issue #28 section above.
- Pre-existing, unrelated: the generic `qa_release.py` default flow (no mode
  flag) stops at `ui.fill(text, index)` on the onboarding page because it passes
  six positional values while that page renders five `TextInput`s. It fails the
  same way on the unmodified Issue #26 bundle, so it is not a regression of this
  work and was left untouched.

## Issue #26 待核对购物车：匹配、无法匹配的处理、增减与总价 — 2026-10-14

- `bundle/main.splash`: the 购物车 is now user input stored in `state.cart`
  (ADR 0003: only the cart is persisted; the 缺菜清单 stays derived). Each line is
  `{name, product, quantity, dropped}`; an empty `product` means no allowed match.
  `migrate_state` seeds `cart: []` for older files and `valid_state` bounds and
  type-checks it on load, so a restart keeps the cart exactly.
- `bundle/main.splash`: entering the region (`open_market`) auto-fills the cart by
  name via `market_pick`, which refuses anything `excluded_food` (过敏与忌口).
  `market_spec_grams`/`market_packs` round the purchase quantity up to whole
  packs by the product's 规格 (g/kg); 枚/L specs fall back to 1 pack. Auto-fill
  only adds names it has never seen, so a user's own quantity, replacement and
  deletion survive every re-entry.
- `bundle/main.splash`: the 购物车 tab renders each line with its simulated unit
  price and line subtotal, `−/＋` quantity steps, `删除` (a tombstone, so a
  deleted row is never re-added) and `替换`. A row with no match or more packs
  than `stock` gets a `无匹配`/`可售不足` badge and an inline explanation instead
  of being dropped; the tab shows `共 N 样 · 模拟总价` from `market_cart_total`.
- `bundle/main.splash`: `替换` opens `market_alternatives`, ranked by
  `market_category_hint` (same 品类 first) then by spec closeness to the gap,
  with 过敏与忌口 excluded; `market_replace_with` re-picks the quantity by spec.
- `tools/smoke.py` / `tools/qa_release.py`: new `--market-cart` (auto-fill,
  rounding, flags, 增减/删除/替换, total, re-entry persistence) and
  `--market-cart-restart` QA modes. The Issue #25 `--market` cart assertion was
  updated from the retired read-only preview ("无对应模拟商品") to the new cart's
  `购物车 · 待核对` + `无匹配`.
- `tools/test_release.py`: offline guard
  `test_market_cart_auto_fill_total_and_persistence` (markers, labels, cart in
  state, unchanged app id).
- Committed manifest digest restamped with the pinned App Hub
  `655114c4943cd2490daaefa2173e7b5aaa20669f` (`hub stamp bundle`):
  `5db3570591932a0aaf856ef167f8088ba73dbfb09b2c950b26a76bcc1453b751`.
  Version stays 0.8.0; capabilities stay `storage, model, camera, files`.

### Native run, 2026-10-14 — bundle files of this commit, manifest patched in a test copy

- Same pinned reference `card-host.exe` (655114c) and the same task-owned test
  copy as Issue #25: `.local-state/qa-cart/bundle` with `manifest.json` patched
  in that copy only (drop `files`, `requires`, `host_api`), admitted with
  `card-host --stamp --allow-unsigned` at 1200x800. No committed bundle file
  differed.
- `python -X utf8 tools/qa_release.py --port 18499 --profile
  .local-state/qa-cart/qa-cart --market-cart` — **13/13 checks passed**: the demo
  menu uses 菠菜 400 g, 蘑菇 3000 g and 秋葵 200 g with the fridge emptied; opening
  the region auto-fills `购物车 · 待核对`; 菠菜 rounds to 2 把 and 蘑菇 to 15 盒;
  蘑菇 is `可售不足` (14 盒 on sale) and 秋葵 is `无匹配`, both with a `替换`
  entry and an explanation; the total is `¥102.60`; `＋` on 菠菜 persists as 3 把
  and re-prices to `¥107.40`; `替换 秋葵` offers same-category 蔬菜 alternatives
  by 规格 and `换成 青菜` re-picks 1 把; `删除 蘑菇` drops it and its price to
  `¥18.60`; and re-entering the region keeps the edits.
- `--market-cart-restart` on the same profile: **4/4** — the persisted cart
  round-trips exactly, the butler dashboard resumes, and the restored cart still
  shows 3 把/青菜 with 蘑菇 gone, while the derived 缺菜清单 still lists 菠菜 and
  秋葵.
- Regressions: `--market` **12/12** and `--menu-purchase` **13/13**; the generic
  `--restart` for the Issue #25 profile **1/1**.
- `python -X utf8 -m unittest discover -s tools -p 'test_*.py'`: **28 passed**.
- Screenshots `docs/qa/issue-26-cart.png` (flags + total) and
  `docs/qa/issue-26-replace.png` (same-category 替换 list) are real 1200x800
  captures of the same synthetic run.
- All inventory was synthetic; no real inventory, keys or provider calls.

### Not verified

- As with Issue #25, the committed manifest still cannot be admitted by the
  locally available reference host (pre-existing `files`/`host-api-v1` mismatch),
  so this was not run under the full OctoSense shell.
- Live `model.complete` was not exercised; the QA used the local rule path.
- Submitting the cart as a 模拟订单, order status and 确认收货 are Issue #27 and
  are not implemented or claimed here; the cart footer says so.

## Issue #25 模拟买菜区域与商品浏览（含一键补齐入口）— 2026-10-14

- `bundle/main.splash`: the 缺菜清单 panel gains `一键补齐 · 去模拟买菜  →`
  when any line is short. It opens an in-window 模拟买菜 region (`let market`) that
  replaces the dashboard and returns via `← 返回管家`; the butler's own tabs are
  untouched. The region has its own left navigation (商品 / 购物车 / 订单) and
  carries the current derived 缺菜清单 (ADR 0003): no list is stored, it re-derives
  from `menu_stock_lines(choose_plan())` on every render and marks each line
  `已对应模拟商品` or `无对应模拟商品`.
- `bundle/main.splash`: `market_products()` is the fixed 24-item 模拟商品 catalog
  shipped in the bundle (名称、品类、规格、单位、价格、可售数量、每 100 g
  营养参考、参考保质期). The 商品 tab lists it and opens a detail page per item.
  秋葵 is deliberately absent from the catalog so at least one 缺菜 can exercise
  the no-match path instead of only describing it. The catalog is local data: no
  network call, no new capability, no new bundle unit, same `pantry-steward` id.
  Every region page carries a `模拟平台` badge and a `模拟下单` footer.
- `tools/smoke.py` / `tools/qa_release.py`: new `--market` QA mode
  (`exercise_market`). `tools/smoke.py` `exercise_menu_purchase` also gained one
  `ui.scroll(700)` before the now-longer cycle page's confirm button, which had
  become unreachable on this 1200x800 host.
- `tools/test_release.py`: offline guard `test_market_region_is_in_bundle_not_a_second_unit`
  (markers, 模拟 labels, exactly 24 catalog entries, unchanged app id).
- Committed manifest digest restamped with the pinned App Hub
  `655114c4943cd2490daaefa2173e7b5aaa20669f` (`hub stamp bundle`):
  `1639c2fcbac79c8332a5218b892a190ebdf1e3a2a724d1c2f45d736770085fc9`.
  Version stays 0.8.0; capabilities stay `storage, model, camera, files`.

### Native run, 2026-10-14 — bundle files of this commit, manifest patched in a test copy

- The only host on this machine is the pinned App Hub's prebuilt `card-host.exe`
  (655114c). Like the Issue #24 run, it refuses the committed manifest's `files`
  capability; the bundle was copied to a task-owned `.local-state/qa-market/bundle`
  and its `manifest.json` was patched in that copy only (drop `files`, `requires`,
  `host_api`), then admitted with `card-host --stamp --allow-unsigned` at
  1200x800. No committed bundle file differed. `hub check bundle --allow-unsigned`
  on the real bundle rejects only the pre-existing `files` capability and accepts
  the new digest.
- Command: `python -X utf8 tools/qa_release.py --port 18499 --profile
  .local-state/qa-market/qa-market --market` — **12/12 checks passed**: the demo
  menu uses both a catalogued (菠菜) and an uncatalogued (秋葵) ingredient; the
  fridge is emptied so the day menu's usage is the whole 缺菜清单; the panel
  offers 一键补齐; the region opens in the same window with 模拟平台/模拟下单;
  it carries `本次要补齐的缺菜` with 菠菜 and 秋葵; 菠菜 is `已对应模拟商品` and
  秋葵 is `无对应模拟商品` (not silently dropped); the list shows `共 24 条`
  catalog rows; the detail shows 品类、规格、单位、价格、可售数量、每 100 g
  营养参考 and 参考保质期; 购物车 and 订单 are the region's own pages; and
  `返回管家` restores the butler with its 菜单 tab and the region gone.
- `--restart` on the same profile: **1/1** (exact synthetic state). The region is
  in-memory only, so nothing about it was persisted.
- `python -X utf8 tools/qa_release.py --port 18498 --profile .local-state/qa-mp
  --menu-purchase`: **13/13**, so the Issue #23/#24 menu and 缺菜清单 flow still
  passes with the added button and code.
- `python -X utf8 -m unittest discover -s tools -p 'test_*.py'`: **27 passed**.
- Screenshot `docs/qa/issue-25-market.png` is a real 1200x800 capture of the same
  run (synthetic inventory: 菠菜 300 g and 秋葵 200 g, then both batches removed).
- All inventory was synthetic; no real inventory, keys or provider calls.

### Not verified

- The committed manifest still cannot be admitted by the locally available
  reference host (pre-existing `files`/`host-api-v1` mismatch, unchanged by this
  work), so the bundle was not run under the full OctoSense shell.
- Live `model.complete` was not exercised; the QA used the local rule path.
- The 购物车 and 订单 pages were read-only/preview pages at the time of the #25
  run; matching by 品类与规格, cart editing, totals and 模拟订单 were not
  implemented then. Cart editing and totals were delivered afterwards by
  Issue #26 (see the #26 section above); 模拟订单 stays Issue #27 and is still
  not implemented or claimed.

## Issue #24 缺菜清单 (derived, editable, follows stock) — 2026-10-13

- `bundle/main.splash`: the menu side panel is now the 缺菜清单. One row per
ingredient name merges the three meals (用量), shows the available stock
(库存可用) and the gap (还差 N 克 = max(0, 用量 − 库存可用)). The gap is editable:
typing a number sets the day menu's merged usage to 库存可用 + that number (a
proportional split with the rounding remainder on the last meal), and 不需要
sets the usage to what is already available. Both writes go through
`commit`, so the day menu and the list cannot disagree. The list itself is
never stored (ADR 0003); it recomputes on every render, so a stock change is
visible without a manual refresh and a restart re-derives the same numbers.
- `tools/smoke.py` / `tools/qa_release.py`: `--menu-purchase` extended with the
Issue #24 checks, and `UI.scroll` added (the three meals no longer fit one
screen). `tools/test_release.py` guards the new symbols offline.
- Committed manifest digest restamped with the pinned App Hub
`655114c4943cd2490daaefa2173e7b5aaa20669f`: `c25dc206a332269e444781692f517b5569076a8c70bf022f72ffdd8080a92bbf`.
- The README pair carried unresolved `<<<<<<< HEAD` / `>>>>>>> f0a7de7`
conflict markers from the #23 branch (the #11 Overview paragraph on one side,
the three-meal menu on the other). Both paragraphs are kept now and the markers
are gone.
- The four `bundle/screenshots/` PNGs were recaptured from the same hidden
Card-runtime run (1200x800, synthetic inventory) and replace the stale pre-#23
captures: 01 首页, 02 三餐日菜单 with the 缺菜清单, 03 the 缺菜清单 showing
还差 941 克 with its editable field, 04 the 冰箱 batch list. The listing
description now says so instead of "旧截图展示手动流程".

### Base blockers found and fixed (the app did not evaluate at all)

The branch as checked out could not run: `main.splash` failed to parse, and the
first inventory write was rejected. These are Issue #23/#9 defects, not part of
the Issue #24 feature, but nothing in the menu flow could be tested without
them:

- `fn menu_meals` ended `{ return p.meals } []`; the trailing `[]` was parsed as
  an array index. Rewritten to `return []` through a local.
- `fn distribute_meals` named a local `use`, which makepad-script reserves.
  Renamed to `planned`.
- The default `state` literal had no `program_history`, so a fresh install's
  first `apply_inventory_operation` failed `valid_state` and no batch could ever
  be added. Added `program_history: []`.
- `valid_state` validated `programs` as if they still held stages
  (`consumed_kcal`, `intake`), but Issue #9 split candidates (`programs`) from
  confirmed stages (`stages`). Candidate fields are checked on `programs` and a
  stage check (including the 12-stage cap) was restored for `stages`.

### Native run, 2026-10-13 — bundle files of this commit, adjusted manifest

- The only host on this machine is the pinned App Hub's prebuilt
  `card-host.exe`/`hub.exe`. It refuses the committed manifest: it does not know
  the `files` capability and does not implement `host-api-v1` /
  `app_policy.device_consent@1` (which `tools/install_local.rs` registers for the
  full shell). That is a pre-existing manifest/host mismatch (main already had
  `files`), not introduced here.
- To exercise the bundle anyway, the manifest was patched **in memory of the
  test directory only** to drop `files`, `requires` and `host_api`, and
  `card-host --system --allow-unsigned` was used. No bundle file other than
  `manifest.json` differed; the digest is manifest-excluded, so the same files
  hash to the committed `98444c…`. The committed manifest was then restored.
- Command: hidden `card-host.exe` (pinned 655114c) standalone at 1200x800 with a
task-owned `--app-data` under `.local-state/qa-issue24`, then
  `python -X utf8 tools/qa_release.py --port 18499 --profile .local-state/qa-issue24 --menu-purchase`
  — **13/13 checks passed**: one generation gives 早/中/晚, every meal lists grams,
  an over-budget portion is refused, the three meals merge into one line with the
  day's total, every meal shows a nutrition reference, a shrunk batch plus an
  expired batch leaves 库存可用 at the unexpired 100 g, the gap re-derives without
  a refresh, typing a gap rewrites the day menu's usage (300 = 100 + 200) while
  the raw state file contains no `shortfall` key, 不需要 falls the usage back to
  the available amount, the menu is then accepted, and an edit that would empty a
  meal (both batches removed, then 不需要) is refused and rolled back instead of
  writing an invalid day menu.
- `--restart` on the same profile: **1/1 checks passed** (exact synthetic state,
  so the derived list left nothing behind on disk).
- `python -X utf8 -m unittest discover -s tools -p 'test_*.py'`: **26 passed**.
- All inventory was synthetic; no real inventory, keys or provider calls.

### Not verified

The committed manifest cannot be admitted by the locally available reference
host (see above), so the bundle was not run under the full OctoSense shell, no
live `model.complete` menu was generated, 忌口-excluded batches were not exercised
through the UI (they share `plan_eligible` with expiry). The screenshots are
hidden Card-runtime captures of synthetic data, not full-shell captures, because
the committed manifest cannot be admitted locally (see above). The
pre-existing `tools/smoke.py exercise()` and the default `tools/qa_release.py`
main path remain stale for the post-#8/#23 flow and were not run.

## Issue #23 daily menu, 2026-10-12 — code complete, native QA not run on this machine

- `bundle/main.splash` now generates one day of 早／中／晚 three meals from a
  single generation (one `model.complete` call) or the local rule path, which
  returns the same shape. Each meal carries its own ingredients, grams, minutes,
  steps and per-100 g nutrition totals.
- Acceptance checks only allergies/avoidances, complete nutrition references and
  the current cycle's remaining daily kcal. Stock is no longer an acceptance
  gate: every ingredient shows 库存够 or 还差 N 克, and an accepted menu becomes
  executable by itself once the missing batches are added, with no regeneration.
- Editing a meal's portion or swapping one ingredient recomputes the nutrition at
  once; an edit that would break a taboo, leave a reference missing or exceed the
  day's remaining kcal is refused and rolled back with the reason.
- Storage stays schema 2. `state.plans` now holds day menus with a `meals` array
  and a merged `uses` list; `migrate_menus` upgrades old single-meal plans to one
  晚餐 meal on read, so old files keep loading. Menus are capped at the recent 20.
- Interface wording for the meal flow now says 菜单, not 方案.
- New QA mode `--menu-purchase` (`tools/smoke.py`, wired in `tools/qa_release.py`)
  drives onboarding with synthetic inventory, one generation, three meals,
  per-meal nutrition and an over-budget portion edit that must be refused.
- Offline guards added in `tools/test_release.py`: menu symbols present and no
  network/shopping capability in the manifest.

Resetting the base: the working tree's `bundle/main.splash` had reverted to an
older pre-Issue-#2 revision while its tools expected the later cycle work. This
change re-anchors the app, tools and docs on `origin/main` (the coherent, merged
revision) plus the existing 菜单 glossary/ADR edits, then adds Issue #23 on top.

Not verified here: the native official-shell QA (`tools/smoke.py --menu-purchase`,
`tools/qa_release.py --menu-purchase`) was not run. This machine has no built
official host and no pinned `.sources`, so the bundle was not exercised in the
unmodified shell and no live model call was made. The manifest digest was
recomputed with the App Hub's documented bundle algorithm (per-file portable
path, NUL, little-endian length, bytes; blake3) because the pinned
`hub stamp bundle` binary was unavailable:
`eead2683f8594174c877dfcd381aa193e536f2c76d2451ab97bc576f2afdb2df`. The three
screenshots under `bundle/screenshots/` still show the prior flow and were not
recaptured; they need refreshing before any release checkpoint.

## Overview page: long-term plan and progress, 2026-10-10 — unreleased working tree

Implementation for Issue #11. A dedicated Overview tab shows the long-term plan
and its progress.

- `bundle/main.splash`: the nav gains `◈  总览` between 首页 and 冰箱 (the later
tabs and their `navigate` calls were renumbered). `meals_per_day()` fixes the
daily meal count at 3 (早/中/晚); `stage_done_meals`, `stage_planned_meals`
(`days × 3`) and `stage_progress_percent` compute a stage's progress, and
`plan_done_meals` / `plan_planned_meals` / `plan_progress_percent` roll the
per-stage counts up, so a future stage with no confirmed meal cannot move the
confirmed numerator. `stage_today_intake` lists the meals confirmed today. The
Overview shows the plan (stages, total days, plan progress, per-stage progress),
the current stage's kcal and protein target against actuals, and today's
per-meal progress with its meals. Only `confirm_consume` appends to a stage's
`intake`, so generating or accepting a menu never changes progress.
`ensure_extended_state` now refreshes `state.daily_target` from `current_stage`,
so a date-driven stage switch shows the new stage's target; when the calendar has
passed every stage, the Overview says the plan has ended and offers "选择下一份
计划…" instead of showing a stale stage. `meals_per_day()` is the single source of
truth for progress; the persisted `meals_per_day` field keeps its historical
default and is no longer read for progress, so an old value cannot change the
formula, and the unused `choose_meals_per_day` setter whose text promised a
configurable meal count was deleted. `ai_watchdog` also re-renders the app when
the civil day turns over (`shown_day` compared with `health_day()`), so an
Overview left open across midnight shows the new stage and targets without a
click or restart.
- Storage schema stays 1; no new stored field.
- `tools/qa_release.py` now exercises the Overview against a real host and adds
  `--stage-switch`, `--plan-ended` and `--session-switch` modes with generated
  fixtures whose clock offset has passed the first stage, the whole plan, or the
  civil midnight; `tools/test_release.py` guards the new symbols. Bilingual
  READMEs and `CYCLE-PLANS.md` describe the page and the progress rule.

### Native run, 2026-10-10 — historical 0.6.2 bundle

These results were captured on the 0.6.2 bundle (capabilities storage+model)
before the Issue #2 capabilities landed. They are history and do **not**
describe the current commit.

- Restamped that editable bundle with the pinned official App Hub
  `655114c4943cd2490daaefa2173e7b5aaa20669f` (`hub stamp bundle`):
  `bundle_blake3 = 34666994381141739f4918c1ab8bbed31627a6c5fe16b13a377fa21b197107b7`.
  `hub check bundle --allow-unsigned` then **PASSED** with only the expected
  unsigned warning and unchanged grants (model, storage, 16 MiB, no agent, no
  hosts).
- Hidden official `card-host.exe` (same pinned revision) standalone at 1200x800
  with task-owned `--app-data` under `.local-state/qa-issue11`:
  `tools/qa_release.py --port 18571 --profile .local-state/qa-issue11` —
  **28/28 checks passed**, including the Overview tab, plan progress
  `1 / 66` (= 1 of (7+15)×3), per-stage `1 / 21` and `0 / 45`, per-meal `1 / 3`,
  the current stage's kcal/protein target against actuals, no progress change
  after generating and accepting a menu, and progress rising to `2 / 66` and
  `2 / 3` only after a confirmed meal. `--restart` then preserved the exact
  synthetic state.
- Stage switch: the main run wrote a fixture profile
  `.local-state/qa-issue11-stage` whose synthetic clock offset had passed the
  7-day first stage. A second hidden host at port 18572 plus
  `tools/qa_release.py --stage-switch` — **2/2 checks passed**: the 15-day stage
  became current and its kcal/protein target replaced the first stage's, and a
  restart preserved the fixture unchanged.
- Ended plan: a third fixture `.local-state/qa-issue11-ended` passed every stage.
  A hidden host at port 18573 plus `tools/qa_release.py --plan-ended` — **2/2
  checks passed**: the Overview says the plan has ended and marks no stage as
  current, and the 档案 tab shows the same ended summary instead of a stale
  "当前阶段".
- No real inventory, keys, provider calls or AI credentials were used.
- Real captures: `docs/qa/issue-11-overview.png` (1/66, stage 1 current),
  `docs/qa/issue-11-progress.png` (2/66, today 2/3) and
  `docs/qa/issue-11-stage-switch.png` (the 15-day stage current). These are
  hidden Card-runtime captures of synthetic data at 1200x800.
- Bundle total is 7,839,683 bytes, under the 8 MiB package guard.
- An independent two-axis review (Standards + Spec) of the commit found no
  blocker. Acting on it: `stage_progress_percent` / `plan_progress_percent` reuse
  the existing `goal_percent`; the stored `meals_per_day` defaults were left
  untouched; `choose_meals_per_day` was deleted; the dead `program == nil`
  Overview branch was removed; and the ended-plan state was added and covered by
  a native check, with `program_expired()` shared so the 档案 tab agrees.
  The reviewers read "计划进度为各阶段之和" as rolling the per-stage meal counts
  into one plan progress (1/66), which is what the implementation does and what
  the acceptance criterion calls 汇总.

### Current bundle verification, 2026-10-11 — pending a capabilities host

- The current bundle is 0.8.0 and declares `storage, model, camera, files`.
  Restamped with the pinned official App Hub
  `655114c4943cd2490daaefa2173e7b5aaa20669f` (`hub stamp bundle`):
  `bundle_blake3 = 0fe1939edb8186990d8e4b9ffb12bc426c626f6fdfcdb3c18d51ce497e52cbdb`.
- The pinned host cannot run it: `hub check` and `card-host` refuse with
  `unknown capability "files"`; stripping `files`/`camera` then gets
  `app pantry-steward needs a host implementing app_policy.device_consent@1`.
  The Issue #11 native results above therefore belong to the 0.6.2 bundle and
  were not re-run on this commit.
- `tools/qa_release.py --session-switch` was added for the day turn-over fix. It
  keeps one host open across the civil midnight and expects the Overview to
  advance itself with no click and no restart. It is ready but could not be
  executed here for the host-capability reason above; it needs a host that
  implements the Issue #2 `camera`/`files` capabilities.
- `python -X utf8 -m unittest discover -s tools -p 'test_*.py'` — **23 passed**
  (offline guards on the current tree).

### Still unverified

- The full `tools/smoke.py` regression was not run: on the standalone
  `card-host` the AI-provider status check (`宿主服务可用`) fails because that host
  intentionally has no model service. It needs the full desktop host.
- A stage switch was verified by advancing the synthetic clock offset, not by
  waiting real days. Re-running the native checks and the new `--session-switch`
  day turn-over case needs a host that implements the current `camera`/`files`
  capabilities; `tools/launch.py --check` against a full host workspace, live
  provider calls, non-Windows platforms, signing and submission remain
  unverified human checkpoints.
- The four `bundle/screenshots/*.png` release assets were not re-captured, so
  they still show the old five-item navigation; regenerate them with the full
  desktop host at the release checkpoint. No tag, release, new Issue or
  submission was performed.

## Stage locking and future-stage editing, 2026-10-10 — unreleased 0.6.2 working tree

Implementation for Issue #10. A confirmed plan can be edited only in front of
its started date.

- `bundle/main.splash`: `stage_locked` treats a stage as locked from the day its
  start date arrives (`floor(started / 86400) <= health_day()`), which also
  covers a user who has fallen behind on logging. `stage_lock_hint` explains the
  reason; the Archive-tab row for a started stage shows the reason and offers no
  edit controls, while an unstarted stage gets 上移 / 下移 / 改目标 / 移除.
  `stage_move`, `stage_remove` and `stage_replace` refuse any locked target, and
  `stage_replace` snapshots another candidate (same or different cycle) over a
  future stage, so 替换 and 改目标 share one safe path. `relayout_stages`
  re-anchors the not-yet-started suffix end-to-start from the fixed locked
  prefix; `future_stage_names` names the affected future goals in the notice.
  `plan_done_meals` / `plan_planned_meals` / `plan_progress_percent` show plan
  progress, whose denominator changes with an edit while the confirmed numerator
  does not. Later stages' nutrient targets are deliberately left as their own
  snapshots (docs/adr/0001); an edit moves their date ranges and the plan
  totals, not their targets. `migrate_state` now fills only the missing
  `intake`/`consumed_*` keys of a legacy stage, so an existing aggregate is
  never zeroed by the migration.
- Storage schema stays 1; no new stored field. Only `started`, `name`, `days`,
  `goal` and the four target fields of an unstarted stage can change, so a
  locked stage's `consumed_*` and `intake` are byte-identical across edits.
- `tools/qa_release.py` now confirms a 7+15+30-day plan and then exercises:
  the calendar lock reason, reorder of only the future suffix, retargeting a
  future stage to a 1-day candidate, one real confirmed meal on the started
  stage, and a later future-stage removal that leaves that meal intact while
  the plan totals fall from 52 to 22 days. `tools/test_release.py` guards the
  new symbols. Bilingual READMEs and `CYCLE-PLANS.md` describe the flow.

### Native run, 2026-10-10 — unreleased 0.6.2 working tree

- Restamped the editable bundle with the pinned official App Hub
  `655114c4943cd2490daaefa2173e7b5aaa20669f` (`hub stamp bundle`):
  `bundle_blake3 = f7a75404fb6fc48e4fcd7d12e5cd63a6d94417caf3df6e27a958b0afd61770a6`.
  `hub check bundle --allow-unsigned` then **PASSED** with only the expected
  unsigned warning and unchanged grants (model, storage, 16 MiB, no agent, no
  hosts).
- Hidden official `card-host.exe` (same pinned revision) standalone at 1200x800
  with task-owned `--app-data` under `.local-state/qa-issue10`:
  `tools/qa_release.py --port 18528 --profile .local-state/qa-issue10` —
  **21/21 checks passed**, then `--restart` preserved the exact synthetic state.
  New checks: the started stage locks by calendar with a readable reason;
  reorder touches only the not-yet-started stages and names the moved future
  goals; retargeting a future stage snapshots the new candidate while the
  locked stage stays byte-identical; a confirmed meal records on the started
  stage and survives a later edit to a future stage; the plan totals recalculate
  (52 -> 22 days) with the confirmed count unchanged.
- No real inventory, keys, provider calls or AI credentials were used.
- Real captures: `docs/qa/issue-10-stage-lock.png` (three stages, the current
  one locked with its calendar reason, the next editable) and
  `docs/qa/issue-10-future-edited.png` (progress 1/44 after a future-stage
  removal). These are hidden Card-runtime captures of synthetic data.
- The bundle had only 8,639 bytes under the 8 MiB package guard once the new
  code was added, so the five bundled PNGs (`assets/sunlit-pantry-bg.png` and
  the four `screenshots/*.png`) were recompressed losslessly with Pillow
  (`optimize=True`). Pixels are identical (verified by decoding before/after);
  bundle total is now 7,831,339 bytes.

### Still unverified

- A two-axis review (Standards + Spec) of the commit found no blocker. Acting on
  it: the migration now preserves existing aggregates, the retarget picker uses
  its own `stage_swap_cycle` instead of the compose page's
  `cycle_view`/`program_selected`, and the target-copy duplication was folded
  into `copy_stage_targets`. `GLOSSARY.md` says the meal count is 3 while the
  shipped default is 2; that wording predates this change and is a tracker
  document, so it was not edited under the Parent-Issue comment rule.
- Not run: the full `tools/smoke.py` regression and its `--legacy` fixture; on
  the standalone `card-host` the AI-provider check (`宿主服务可用`) fails because
  that host intentionally has no model service, so that check needs the full
  desktop host. `tools/launch.py --check` against a full host workspace, live
  provider calls, and non-Windows platforms remain unverified. Signing and
  submission remain human checkpoints. No tag, release, new Issue or submission
  was performed.

## Composed plans with ordered stages, 2026-10-10 — unreleased 0.6.2 working tree

Implementation for Issue #9. Candidates and confirmed stages are now separate
records, and a plan is an ordered list of stage snapshots.

- `bundle/main.splash`: `state.programs` holds unconfirmed candidates only;
  `state.stages` holds the confirmed plan's snapshots in order, and
  `state.plan_history` holds archived plans. `make_stage` copies a candidate's
  targets at confirmation; the compose page shows total days and each stage's
  date range and targets, with add / move / remove / replace and a hard cap of
  12 stages. The current stage is the first stage whose date range still covers
  today, so a multi-stage plan advances on its own dates. The GPU renderer is
  unchanged.
- Storage schema stays 1. `migrate_state` splits a previously active program
  into a one-stage plan and turns legacy `program_history` entries into plan
  history without dropping `consumed_kcal` or `intake`. A re-serialization after
  the split prevents the fallback defaults from overwriting the split result.
- Review fixes: the archive page and the `model.complete` payload now derive
  their daily/protein/fibre targets from the stage covering today; a failed save
  keeps the composed draft and stays on the candidate page; migration detects
  `stages` / `stage_next` / `plan_history` by exact key instead of substring-
  searching the whole JSON (a `diet` value containing `stages` no longer skips
  it); and each menu records the stage that generated it, so crossing a stage
  boundary invalidates the old menu.
- `tools/qa_release.py` gained compose, cap, and ordered-stage assertions;
  `tools/smoke.py` follows the new `确认计划 · 去录冰箱  →` label, its
  `stages` schema, and a small `scroll` helper; `tools/test_release.py` guards the
  new symbols. Bilingual READMEs and `CYCLE-PLANS.md` describe the flow. The
  version stays 0.6.2 because it is set at release, not per feature PR.

### Native run, 2026-10-10 — unreleased 0.6.2 working tree

- The original `14/14` run in this entry was on the pre-rebase commit (digest
  `54f917fc…`), before Issue #9 was restacked on the updated Issue #8 branch; it
  no longer describes this head.
- Review fixes (stage-derived targets, save-failure draft recovery, exact-key
  migration, stage-bound menus) were applied and verified against the Issue #9
  bundle alone. Restamped it with the pinned official App Hub
  `655114c4943cd2490daaefa2173e7b5aaa20669f` (`hub stamp bundle`):
  `bundle_blake3 = 791b647235eb090b1c5a4c26dd275bca0b0288d3a95de5f820b426b0affc49bb`.
  `hub check bundle --allow-unsigned` then **PASSED** with only the expected
  unsigned warning and unchanged grants (model, storage, 16 MiB, no agent, no
  hosts).
- Re-ran `tools/qa_release.py` against this fixed head: **14/14 passed**. Extra
  regression runs on the same head: a legacy archive whose user text contains
  `stages` still migrates its active program into `stages` (17 candidates kept);
  a menu generated for one stage is invalidated once the calendar enters the
  next stage; and the archive page shows the stage covering today (`/ 1800 kcal`)
  instead of the stale first-stage target.
- Hidden official `card-host.exe` (same pinned revision) standalone at 1200x800
  with task-owned `--app-data` under `.local-state/qa-*`:
  `tools/qa_release.py` — **14/14 checks passed**: first-run onboarding; six
  cycles x three candidates without auto-activation; cycle switching;
  per-cycle regeneration; reorder, remove and replace in the draft; the 12-stage
  cap; clearing the draft leaves candidates unconfirmed; the compose page sums
  cycles (7+15 = 22 days); confirmation writes two ordered stages whose start
  dates meet end-to-start; inventory preview does not commit; explicit commit
  persists; manual default does not generate. A restart then preserved the exact
  synthetic state.
- Migration checks with real old-schema fixtures (copies of the Issue #8
  synthetic profile): the previously active 7-day program opened as a
  one-stage plan with its 11550 kcal target, 17 candidates stayed unconfirmed,
  and `stage_next` continued its id space. A fixture with a legacy
  `program_history` entry migrated it into `plan_history` with its 3210 kcal
  preserved. Tab 3 rendered the plan stages and plan history; `选择下一份计划…`
  archived the 2-stage plan (`2 个阶段 · 22 天`) and returned to candidate
  selection; the demo profile resolved its stage so menu generation still
  worked.
- No real inventory, keys, provider calls or AI credentials were used.
- Real captures of this run: `docs/qa/issue-9-compose.png` (a 7+15+21 draft:
  43 total days, stages 10月10日–10月16日 / 10月17日–10月31日 / 11月1日–11月21日),
  `docs/qa/issue-9-plan.png` (the confirmed plan's stages) and
  `docs/qa/issue-9-history.png` (the archived 3-stage plan under 计划历史).
  These are hidden Card-runtime captures of synthetic data, not phone images.

An independent two-axis review (standards + spec) of the feature commit found
no blocker. Acting on it: `draft_move` now clears the armed replace target so a
reorder cannot make 替换 hit the wrong stage; the replace prompt is shown inline
and points to the candidates above; the archive/clear sequence is one
`archive_plan` helper; and `tools/smoke.py`'s `--legacy` assertions now compare
the migrated field set (`foods`, `plans`, active/revision/meal fields) instead of
requiring the pre-migration `programs` shape.

### Still unverified

- Not run: the full `tools/smoke.py` regression and its `--legacy` fixture. On
  the standalone `card-host` the AI-provider check (`宿主服务可用`) fails because
  that host intentionally has no model service; that check needs the full
  desktop host. `tools/launch.py --check` against a full host workspace, live
  provider calls, and non-Windows platforms are also unverified. Signing and
  submission remain human checkpoints. No tag, release, new Issue or submission
  was performed.

## Six cycle candidates and per-cycle regeneration, 2026-10-10 — unreleased 0.6.2 working tree
## Issue #8 six-cycle candidates, merged onto the #2 rework

`bundle/main.splash` was reworked by Issue #2 while Issue #8 added the six-cycle
candidate picker, so this merge re-applies #8's feature onto #2's script instead
of a line merge:

- Cycles 1/3/7/15/21/30 with three profile-derived candidates each; each shows
  name, goal, execution trait, daily and cycle totals, and the difference from
  the cycle baseline. A seeded line-up means `重新生成本周期候选` replaces only the
  viewed cycle's unconfirmed candidates.
- The candidate/config migration is factored into `migrate_candidates`, applied
  to both freshly converted schema-1 states and current schema-2 states. It adds
  `cycle_seed` and rebuilds old-format candidates by shape (`variant` field), so
  user text (preferences, food names) cannot be mistaken for a field name.
- Verified live in the hidden official host after the merge: the cycle page
  renders the six lengths, switching cycles and regenerating the viewed cycle
  keep a confirmed plan and the other cycles untouched, and re-saving the profile
  from a non-default cycle returns the page and marker to 7 days. `hub check
  bundle --allow-unsigned` PASSED.

## Issue #2 foreground verification, 2026-10-11 — user reported pass

After installing digest `ba2d1a2bf588bd48a74c9c6112cfa706146375649c45cdff0fad5e2449498ff5`,
the user reported that the remaining manual checks listed under the historical
foreground checklist below passed: receipt and food-image import, OBS
camera recognition, cancellations and immediate retry, restart persistence,
adjacent profile/menu/consumption flows, and the official-host unsupported
image path. This is a user report, not an independently captured per-step log
or a fresh automated full-shell replay on this digest. The user explicitly
excluded demonstration-video recording from their task and this PR. The old
0.7.0 recording remains historical evidence only. Current synthetic-data
QA captures of the home, profile edit, inventory, image chooser,
official-host fallback, recipe, and consumption review are in `docs/qa/`.
They use synthetic data and do not claim to prove a real provider response.
The prior `main` screenshots were kept under `bundle/screenshots/` at
`af85d81f`; the PR review pairs them by screen while noting that the fixture
data and capture times differ.

Issue #2's four-way quantity distinction is not complete in this PR. The app
records confirmed stock, planned recipe use, and confirmed consumption, but
does not record or display pending-receipt quantities. Its purchase button is
still a placeholder. The simulated-order work in Issue #5 must retain each
pending food, quantity, and unit separately from actual stock, then add only
the quantities the user confirms as received. Issue #2 should remain open
until that integration is verified; this report does not count pending receipt
as passed.

During PR preparation, the pinned App Hub bundle check passed again and all
19 Pantry Python tests passed. The sandboxed run initially hit Windows
`PermissionError` in Python temporary directories; rerunning the same tests
outside that filesystem restriction passed without code changes.

## Issue #2 recipe wording, 2026-10-11 — installed and foreground replayed

The live MiniMax recipe exposed internal fields such as `nutrition_known=false`
and `profile` in its explanation, and `unknown expiry` / `food_id` in its
cooking steps. Recipe prompts now require user-facing Chinese in the title,
explanation, and steps. The app translates these observed internal terms when
saving new model output and when rendering previously saved plans, so the
existing accepted recipe needs no inventory migration.

Bundle digest: `ba2d1a2bf588bd48a74c9c6112cfa706146375649c45cdff0fad5e2449498ff5`.
The pinned Hub check and 19/19 Pantry Python tests passed. In a separate
synthetic official-shell profile, an existing saved plan containing the exact
raw terms rendered as readable Chinese in both its explanation and expanded
steps. The fixture was not copied from the person's inventory. After the user
closed the visible shell, this exact digest was signed, verified, and installed
into the same isolated MiniMax profile. The pantry JSON SHA-256 stayed
`60f59dd3930f36085eb8ceb83366cc18fc73336a94d75d28d265b7cfebda02d1`:
six foods, five inventory events, and one accepted/consumed recipe remain.
Exactly one local catalog matches the new digest. The user reopened that
profile in the foreground, expanded the saved recipe, and reported that none
of `nutrition_known`, `profile`, `food_id`, or `unknown expiry` appeared. This
confirms the saved-plan display; a new live MiniMax completion was not rerun.

## Issue #2 recipe generation with missing nutrition, 2026-10-11 — installed locally

The visible profile has seven confirmed food batches, four inventory events,
and no recipe candidates. None of its seven batches has a complete per-100-g
nutrition reference, so the earlier generator discarded every batch before
calling the model. Some count items also lack an average item weight, and one
package item lacks a package conversion. No private inventory was used as a
test fixture.

Generation now prefers batches with complete nutrition and convertible grams
for numeric planning. If there are no such batches, it uses eligible stock in
native g, ml, or piece units to create a recipe marked `营养未核算`. Expired or
excluded stock remains ineligible; unknown expiry requires a freshness check.
Package stock without a conversion remains ineligible. The model request for
this path omits nutrition totals and numeric cycle budgets. Accepting the
recipe and confirming consumption deducts the actual native quantities and
records a meal with `nutrition_known: false`; it does not add invented kcal or
nutrients to cycle totals. The profile labels numeric balances as known-only.

Final bundle digest: `031cc4e93300982d9afdcd507af997a928a8ebf1471ead540d8b53e5462ba58e`.
Pinned Hub check and 19/19 Pantry Python tests passed. On the preceding
`1b277a009256be8536f20f16a782c7765e07f48d5ad1117f07d7e7728de79e1a`
digest, the unmodified official shell passed 27/27 existing UI/data checks,
2/2 restart checks, 2/2 focused unquantified-recipe checks using a count item
without an average weight, and a focused unquantified-meal restart check. The
final edit restores strict legacy-state validation and treats only explicit
`numeric: false` plans as unquantified. On the final digest, a synthetic
official-shell profile loaded its prior unquantified meal, then generated and
confirmed another count-item recipe; inventory decreased and neither cycle
kcal nor weekly nutrients were invented. A separate synthetic g-quantity
replay on an earlier digest also verified inventory deduction and zero added
kcal. The `ce016c254f0768019a1efeab8c6f6e9577aa78b869f84ebab97d09057d9e735b`
digest entered `model.complete` and reported the expected `no_provider`
result because that synthetic profile has no model credentials. After the user
reopened the final digest in the visible isolated host, a read-only check found
one new candidate persisted with source `在线 AI · 营养未核算`, five inventory uses,
and no acceptance or consumption. The live UI showed the candidate title,
unquantified source, and `就吃这套` action; the seven food batches and four
inventory events were unchanged. The host produced an online recipe result.
The user previously reported MiniMax `Connected`; the provider identity was
not independently inspected during this recipe call. This is a text recipe
completion, not evidence of image recognition, which was still pending then.

After the user closed the visible shell, the final digest was signed, verified,
and installed into the same isolated MiniMax profile using existing local test
keys. The profile JSON SHA-256 remained
`472c26fa4dd699422719957dacfc1a991e60e859fceb2d1e0af2c54d3e5e3a8e`:
seven foods, four events, zero plans, and completed onboarding immediately
after installation. The later visible run created the candidate described
above. Receipt import, cancellation, and video checks were still open then.

## Issue #2 profile return and selected controls, 2026-10-11 — installed locally

The inventory date inputs now have separate full-width rows in onboarding and
the regular inventory form; a native capture showed the complete date
placeholder. Expanded inventory rows and the consumption review use a
per-food `第 N 批` label without exposing the global storage ID.

`重新设置用户画像` now opens an editable three-step profile flow. The existing
profile and inventory stay on disk while it is open. `取消修改 · 返回设置`
restores the original in-memory state from any step; closing the host before
confirmation also leaves the saved profile intact. Confirming a new cycle
plan saves the edited profile and returns to Settings without repeating the
initial inventory step. Selected scene, sex, activity, cycle plan, meal-goal,
unit, draft-row, and navigation controls use a dark fill and light text.

The 0.8.0 bundle digest is
`aeb5dccc946b5a289b05aeade5ee896f468750e206b175c3472b7287000b547d`.
Pinned Hub check and 19/19 Pantry Python tests passed. In task-owned profiles,
the unmodified official shell passed 27/27 UI/data checks and 2/2 restart
checks. A separate focused replay verified profile cancel leaves the saved
JSON byte-for-byte unchanged, successful confirmation preserves the foods and
events, and closing mid-edit restores the prior profile on restart. Native
captures covered the date field, selected controls, and per-food batch label.
After the user closed the visible host, the exact bundle was signed, verified,
and installed into the existing isolated MiniMax profile with the existing
local test keys. The profile JSON SHA-256 stayed
`e9d0e54235447b6b917679fc5aa4896b910e0410e58a02da49153f7efca76701`:
seven foods, four inventory events, and completed onboarding remain. Exactly
one local catalog matches the new digest. The user's foreground view of this
bundle, receipt import, remaining cancellation stages, and a final video were
still pending at this checkpoint.

## Issue #2 chooser retry and inventory labels, 2026-10-11 — installed locally

After a native file-picker cancellation, the user saw an occasional
`foreground_required` error on an immediate second attempt; waiting restored
the import path. The host checks that the requesting app is the active
foreground surface. Pantry now treats this specific error as retryable: the
picture chooser stays open, explains that the user should click the Pantry
window, and keeps `选择已有图片` and Cancel available. A normal file-picker
cancellation still returns to manual inventory input. No host permission check
was relaxed and no automatic second import is sent.

Recognition draft rows now show the compact `✓ 已选中` / `○ 未选中` status, with
an adjacent explanation that only selected rows are confirmed. Inventory
groups continue to show their own batch count. Expanded rows now use `第 N 批`
for the position within that food and identify the persistent global key as
`库存 ID #N`; the consumption selector uses the same ID terminology.

Stamped 0.8.0 digest at that checkpoint:
`04d8bd5ccf1fdcd7cf45ea8b72fc9ebd7815def3e6bd68ff89ee62502b4d5e3b`.
Pinned Hub check and 19/19 Pantry tests passed. In task-owned
an isolated test profile, the unmodified official shell passed 26/26
UI/data and 2/2 restart checks. Native captures showed both selection states
fully visible and a milk row labelled `第 1 批` with a separate global ID.
A task-only bundle injected the exact host error:
the chooser retained its retry and cancel buttons, showed the focus hint,
and left foods/events unchanged; the fixture was not shipped. The restamped
bundle was signed, verified, and installed into the existing isolated MiniMax
profile with existing local test keys. Its six foods, three inventory events,
and completed onboarding were unchanged; one mirror matches the new digest.
The actual native cancel/immediate-retry timing still needed a user foreground
replay. Receipt import, remaining cancellation stages, and a final video were
also pending at this checkpoint.

## Issue #2 recognized-unit correction, 2026-10-11 — installed locally

The foreground custom host showed a real OBS Virtual Camera preview and returned
five editable rows from a MiniMax image request. One row was `Green Onion`,
quantity `2`, unit `bunch`; this unit is outside Pantry's eight selectable
inventory units and blocked the selected-row confirmation. The user corrected
the draft by excluding that row, confirmed the remaining rows, and closed the
host. The isolated profile now contains four `food_image` batches with app-local
image paths and one inventory event; onboarding is complete. This is live
provider/camera/confirmation evidence for that one image. Receipt import,
stage-by-stage cancellation, and final video remain unverified.

The 0.8.0 bundle digest at that checkpoint was
`83fec87ae1f98177285c2b996a19b4a7f2f2cbaab8041990fa7136cd32cfd772`.
Recognition now retains only the eight inventory units shown by the UI; unknown
units become blank and require an explicit choice. Unsupported package-size
units also become blank. The draft labels its current selection state, reports
the row and reason beside the confirmation button without resetting scroll,
and makes unfinished-draft actions visibly unavailable. The bundle was
restamped, signed, verified, and installed into the same isolated profile using
its existing test keys; provider settings and inventory were preserved.

The pinned Hub check and 19/19 Pantry Python tests passed. A task-only response
fixture returned `2 bunch` and `2 个`: the first row displayed an unselected
unit, confirmation refused it without writing inventory, then choosing `个`
produced two batches in one event and allowed onboarding to finish. This
fixture was never shipped. The unmodified official shell passed 26/26 UI/data
checks and 2/2 restart checks on the exact current bundle in an isolated
test profile; both image buttons retained the manual fallback.
The updated unit behavior has not yet been replayed by the user in the real
foreground MiniMax host.

## Issue #2 camera consent visibility repair, 2026-10-11 — foreground preview verified

The user reported that both buttons on the camera screen appeared inert. A
read-only snapshot of their running host found a live `DevicePermissionPrompt`
with `Continue` and `Not now` buttons above the app, although the user's screen
showed only the Pantry camera card. An isolated replay reproduced the invisible
sheet: Pantry's root `GlassPanel` moved its children into an overlay draw list
above the native consent sheet, while the sheet still captured clicks.

The root app surface now uses a normal `RoundedView` and the camera stage shows
an authorization hint plus the camera's native error text on failure. With the
restamped 0.8.0 digest
`e01f367bf455c41fa8b4d1e6b2b6c3cf5cba71938ab2c09cf00475f6e5f3f925`,
an isolated local-host installation rendered the native camera-consent sheet
clearly on top of Pantry. Choosing `Not now` returned to manual entry with a
visible authorization message. The pinned Hub gate and 19/19 Pantry tests
passed; the unmodified official full shell passed 26/26 UI/data and 2/2
restart checks in an isolated test profile. Native `Continue` requires a
physical foreground click and was not automated. After the user relaunched the
visible host, a read-only remote capture showed the OBS Virtual Camera image
inside Pantry's camera preview. Capture, file selection, MiniMax image
completion, and the final video remain unverified. After the user closed the
previous visible host, the new bundle was signed,
verified, and installed into the existing isolated MiniMax profile without
regenerating keys or changing provider settings. Foreground capture and model
replay are pending.

## Issue #2 foreground chooser visibility repair, 2026-10-11 — awaiting user replay

The user opened the real local-host Pantry window and reported that the photo
recognition screen was dark with unreadable controls. A remote snapshot showed
that the `打开摄像头` and `选择已有图片` widgets existed, but a native capture confirmed
the full-screen dim layer covered their text. An isolated test of draw-list
batching did not fix the image. The recognition chooser was then moved into the
main app body as a centered, readable screen; the overlapping dim layer was
removed. The same selected camera/import/model states and cancel action remain.

The 0.8.0 digest at that checkpoint was
`849dd4d7b721076d41d57bd603900d398c23a39b83d9fdb60300885a322d4af9`.
The pinned Hub gate passed, and Pantry tests passed 19/19. The first sandboxed
test attempts hit Windows ACL failures in Python's temporary directories; the
same 19 tests passed when their process could access its own temporary files.
An isolated local-host installation with the exact bundle digest displayed the
chooser title, both buttons, and Cancel in native captures from onboarding and
the later inventory tab. Both photo and receipt chooser cancellation left zero
foods and inventory events in onboarding; a later inventory-tab cancellation
left its existing inventory event count unchanged and restored manual entry. On the same
new digest, the unmodified official full shell passed 26/26 UI/data checks and
2/2 restart checks in an isolated test profile. The new bundle was
installed into the original isolated MiniMax profile after the user closed the
old window. Foreground user replay, native file selection, camera capture,
actual Pantry MiniMax image results, and final video are still pending.

## Issue #2 documentation and manual handoff, 2026-10-11 — local preparation complete

At this handoff checkpoint, the 0.8.0 bundle had `storage`, `model`, `camera`, and `files` grants,
the optional `camera.permission.request@1` host API, and digest
`0f08bd1b1044e56b70f66e1d6af45be56cff01ff1cf8d37aedc611961171cbb5`.
The later chooser repair above changed the bundle digest. Its listing was
reviewed against the image-recognition evidence; no bundle bytes changed during
this documentation pass.
The bilingual READMEs, privacy policy, review answers, submission checkpoint,
and historical brief now distinguish the official manual fallback from the
Windows local-host image path. The four bundled screenshots and existing video
are explicitly labelled as historical 0.7.0 manual-flow material. New captures
must come from a real foreground demonstration, so they were not replaced.
Older sections below are point-in-time evidence, not claims about today's bundle.

Repository handoff: Pantry is on
`feat/issue-2-pantry-inventory-multimodal` at HEAD
`af85d81f0027507ec2a74f3b1afe4838b9371257` (base `main` at
`d6d08d1ccf67b785ecf8813ea3b5a0eb6be04588`). Its earlier inventory,
menu, image-intake, and documentation work shares 21 modified tracked paths and
remains uncommitted; an isolated documentation commit
would misleadingly include earlier edits. OctoSense is on
`feat/pantry-steward-vision-bridge` at local HEAD
`808005eaabe00b60f4fc37cc1967e4fa4fc061a2` (base `main` at
`40ca21da68cc05ae930931adcfcf6d382d49ec26`) with a clean worktree.
No branch was pushed, no production identity was used, and no release, Hub
submission, or upstream platform PR was made.

### Historical foreground checklist — later user-reported pass

The checks used an isolated test profile, synthetic fixtures, and OBS Virtual
Camera. API keys stayed in the host-owned AI providers page. The user launched
the local test host from their own PowerShell so native windows had foreground
access.

The local test launch selected the then-stamped 0.8.0 bundle and started the
modified release host in a foreground window. The configured
`minimax-cn / MiniMax-M3` had shown `Connected` in AI providers; that host
connection check is prior user-reported evidence, not a Pantry image result.
At this earlier checkpoint, the following checks were pending. The user later
reported that checks 1–5 passed; see the current report at the top of this
file. No per-step log was independently captured. Model outputs must be judged
as actual provider results rather than fixed fixture rows:

1. Before recognition, note inventory count and event count. Click `导入小票`
   then `选择已有图片`; select the synthetic receipt image.
   Check that the real model returns an editable draft, uncertain values remain
   blank, and no inventory changes before confirmation. Edit one field,
   deselect/remove a row, confirm selected valid rows once, and inspect the
   resulting separate batches/events.
2. Click `拍照识别` then `选择已有图片`; select the synthetic fridge image.
   Check the food-photo prompt, editable rows, and final confirmation. Model
   names, row counts, and units may vary; correct them rather than assuming the
   synthetic illustration proves recognition quality.
3. Exercise the camera path from `拍照识别` → `打开摄像头`; personally grant host
   consent if asked. Check the OBS preview, then `拍照并识别`; verify that capture
   yields an app-local image and a real editable model draft. Use an OBS image
   source with the synthetic fixture if avoiding personal imagery. Camera
   source selection is automatic in the current minimum demo.
4. Cancel once in the chooser, native file picker, camera preview, model wait,
   and draft review. Compare inventory/events before and after each cancellation;
   manual entry must still work. Immediately retry `导入小票` after canceling
   the native file picker. If the host briefly returns `foreground_required`,
   confirm Pantry remains on its picture chooser with a focus hint and an
   available `选择已有图片` button; click the Pantry window and retry. A request
   already sent to a provider may still be billed after the app stops waiting.
5. Restart the same isolated profile; verify confirmed batches persist and
   adjacent dietary profile, menu, and consumption flows remain usable.
   The unmodified official full shell already passed 26 UI/data checks and two
   restart checks with the **same digest**. A human visual spot check of both
   official-host image buttons should show `当前宿主暂不支持图片识别，请使用手动录入`, without
   a chooser or recognition call.
6. Review screenshots and host logs for secrets or personal paths before
   sharing. Review the public support/privacy links and final release identity
   separately before publication. The user later excluded new video recording
   from this PR; the current synthetic inventory comparison only illustrates
   UI changes.

## Issue #2 image-intake verification, 2026-10-11 — earlier checkpoint

At the first image-intake checkpoint, the unpublished Pantry 0.8.0 bundle
digest was
`0f08bd1b1044e56b70f66e1d6af45be56cff01ff1cf8d37aedc611961171cbb5`.
`python -X utf8 tools/launch.py --hub D:\projects\GOSIMAPP\OctoSense\target\release\hub.exe --check`
passed; `python -X utf8 -m unittest discover -s tools -p 'test_*.py' -q`
passed 19/19 with the test process allowed to clean its own Windows temporary
directories. The locally modified OctoSense branch passed
`cargo test --locked --offline -p octosense-llm-service --test complete -- --test-threads=1`
(23/23), `cargo test
--locked --offline -p octosense-shell --features app-hub platform_services --lib
-- --test-threads=1` (12/12), and `cargo build --release --locked --offline -p
octosense --no-default-features --features octos-core,app-hub`. The unchanged
official release executable was preserved separately in ignored `target` before
that custom build. Both worktrees were checked for credential-shaped values and
tracked/untracked key, profile, app-data, log, or build artifacts; none appeared
in the changed file lists. OctoSense's tracked tree remains clean.

The unmodified official full shell with that earlier bundle in an isolated
test profile passed all 26 `tools/smoke.py` UI/data checks and
both restart checks. Both recognition buttons displayed the exact unsupported
message without a chooser; manual inventory, menu, consumption, and profile
flows worked. The negative `begin_recognition` path returns before file, camera,
or image-model requests, and the isolated host created no model ledger. This
supports zero admitted model calls; no separate request trace was captured.

The locally modified OctoSense release host opened the shared chooser using
the same bundle and a task-owned profile configured for `minimax-cn / MiniMax-M3`.
Before a provider call, cancel left zero foods and zero inventory events. Native
UI capture exposed a retained overlay after cancel; the bundle now toggles the
overlay view's visibility, and a new capture confirmed that the chooser closes
and manual entry remains usable. This change was restamped and reinstalled.
No real MiniMax image result, Pantry camera capture, native file import, or
final demo video had yet to be verified. Those checks needed a foreground host
window launched from the user's own Windows terminal; the agent's shell has no
Windows foreground window and cannot complete the native chooser or consent.

## Issue #2 image intake, 2026-10-11 — local implementation

The unpublished `pantry-steward` 0.8.0 bundle has `storage`, `model`, `camera`,
and `files` grants, declares the complete shell's `host-api-v1` device-consent
broker, and has digest `09543dcb848f92e32bc4565a7483c7abef5f1c144ada64090b171224a4d5c4c0`.
The pinned `hub.exe stamp bundle` and `python -X utf8 tools/launch.py --hub
<OctoSense>/target/release/hub.exe --check` passed. `python -X utf8 -m
unittest discover -s tools -p "test_*.py" -v` passed 19/19 when run with a
task-owned temporary directory; the managed Windows sandbox ACL blocked
`tempfile` cleanup in the first attempt, so that run was repeated with the
test process allowed to clean its own temporary files.

Local test signatures installed the unchanged final bundle into isolated full
shell profiles. The unmodified official release shell passed 26 checks from
`tools/smoke.py` in an isolated test profile, plus two restart checks. The
exact final bundle then passed a focused official fallback check in a second
isolated profile. Both image buttons displayed
`当前宿主暂不支持图片识别，请使用手动录入` without an image chooser;
manual inventory, menu, and consumption flows still passed. In source,
`begin_recognition` returns on that probe result before the chooser, file API,
or image `model.complete`; no separate host-call trace was recorded. The
locally modified debug shell at OctoSense commit `808005e` passed the positive
capability,
shared camera/file chooser, cancellation, and zero-inventory-write checks in
an isolated profile with the exact final bundle. An ignored, task-only
model-response fixture passed receipt/photo draft, row edit/removal, two-batch
single-operation add, cancellation, and unavailable-provider-to-manual checks
in another isolated profile. Fixture responses were never shipped in the
bundle. No real image was sent to MiniMax/Kimi from Pantry at this checkpoint;
camera capture inside the full Pantry UI, real image recognition, and a new video
remained for later foreground verification. The standalone `card-host` could
not admit this bundle because it lacked the required device-consent broker;
the official fallback was tested in the unmodified full shell.

Pantry was on `feat/issue-2-pantry-inventory-multimodal` at `af85d81` with
earlier inventory and menu work already uncommitted before image intake. The
image-intake changes were left uncommitted to avoid combining earlier work into
a misleading isolated commit. The locally modified OctoSense branch was clean at local commit
`808005e`. Neither repository was pushed or published at this checkpoint.

## Issue #2 host readiness, 2026-10-11 — incomplete at this checkpoint

The unmodified OctoSense source at
`40ca21da68cc05ae930931adcfcf6d382d49ec26` passed the locked release
build during official-host verification. This check reused that exact executable;
a redundant build retry was stopped before completion. No tracked OctoSense
source was changed for this check.

After explicit user approval, the 0.7.0 Pantry bundle was signed with local
test keys, verified and installed through App Hub in
an isolated test profile. The full official desktop launched its onboarding
page from that profile. No production signing key or personal pantry data was
used. A separate ignored host API probe bundle was signed and installed
for host API rehearsal. With a synthetic 345-byte PNG selected through the
native chooser, `files.import` returned an app-local PNG path; the file in the
probe's app jail was byte-identical to the selected image. A later second
import was refused with `foreground_required` when the app was no longer the
native foreground window; the earlier import remained intact.

The user enabled OBS Virtual Camera for the rehearsal, but the unmodified
Windows host refused `CameraPreview.start()` with `this app was not granted the
camera`. Its device-consent request API is currently limited to Android and
macOS, while the installed app runner applies host-managed consent on Windows.
Camera capture and its app-local return path have therefore **not** been
verified. The user configured MiniMax in the isolated host's AI providers UI
and reported `Connected` from `Test connection` on 2026-10-11. That host test
sends a small real provider request; this result was observed by the user,
not independently through Pantry's `model.complete` path. Camera capture and
the Pantry image-recognition path were still open at this checkpoint.

## Issue #2 local handoff, 2026-10-11 — unpublished at this checkpoint

Pantry branch: `feat/issue-2-pantry-inventory-multimodal`; local HEAD:
`af85d81f0027507ec2a74f3b1afe4838b9371257`. The working tree contains
uncommitted source, tools, docs, listing, manifest, and screenshot edits.
The two `.local-planning/` milestone sets remain ignored and local-only.
The official OctoSense checkout is on `feat/pantry-steward-vision-bridge` at
`40ca21da68cc05ae930931adcfcf6d382d49ec26` with no tracked changes.

The unpublished source candidate is `pantry-steward` **0.7.0**. Its listing
describes manual units and batch grouping, the separate consumption step,
offline/online evidence limits, and unavailable image/voice features. Four
historical screenshots were replaced with genuine 1800×1200 PNG captures
from the edited bundle in an isolated official Windows card-host using
synthetic data: home, local-rule candidate, consumption review, and grouped
inventory with batch details. They were visually inspected. The older video
was not revised and remains outside `bundle/`.

After those bundle changes, pinned App Hub commit
`8347a489141c0e24cab564883db7c4592935a8b2` stamped digest
`4df2bd4f4613b336a6782683dfec745e75423d75cc96f36122136acc222f512f`.
`python -X utf8 tools/launch.py --host-workspace D:\projects\GOSIMAPP\OctoSense
--app-hub-source D:\projects\GOSIMAPP\OctoSense\target\dependency-probe\app-hub
--check` returned `pantry-steward 0.7.0 — PASSED`, with the expected unsigned
source warning. Bundle bytes excluding manifest: 4,849,230 / 8,388,608.
No production signing identity or local test key was used.

After the 0.7.0 restamp, a fresh isolated official card-host profile passed
all 26 `tools/smoke.py` UI/data checks; a restart of the same profile passed
both persistence checks. The 19 Python `tools` unit tests passed under ordinary
Windows permissions, including the updated version/listing guards. Sandboxed
Python test attempts could not create temporary files because of Windows ACLs;
their metadata assertions were updated before the successful normal-permission
run. The unchanged business script had already passed the full pinned parser
and 33 source-extracted VM cases during official-host verification; these were
not rerun for the later metadata and screenshot edits.

Full Store installation, live model-provider calls, other platforms, sealed
publisher pack verification, current remote privacy-page review, App Hub
admission, and competition qualification remain unverified. The existing
publisher-toolchain.json and tag workflow still pin the earlier App Hub
`655114c4943cd2490daaefa2173e7b5aaa20669f`, rather than the host pin
used here; the publishing route must be reviewed before any 0.7.0 tag.
No commit, push, tag, release, review issue, or submission was made for this
candidate.

## Issue #2 official-host verification, 2026-10-11

The initial official-host retry waited for the default Cargo cache lock held by
a separate background download, then stopped without interrupting it. A later
Git CLI/OpenSSL retry fetched the pinned Git dependencies and passed
`cargo build --release --locked -p octosense` on the unmodified official
checkout (80m 37s). `target/release/octosense.exe` is 514,735,104 bytes;
OctoSense tracked files remain clean at `40ca21da68cc05ae930931adcfcf6d382d49ec26`.
The pinned App Hub `hub.exe`, `card-host.exe`, and `pantry-local-install.exe`
also built in release mode. No tracked OctoSense source was changed.

The exact pinned App Hub commit `8347a489141c0e24cab564883db7c4592935a8b2`
is present in an ignored task-owned sparse checkout. `tools/launch.py` now
accepts `--app-hub-source` and verifies that source's commit and clean status
against the official host pin. The Python tool suite passed 19 tests with normal
Windows permissions; sandbox-only temporary-directory ACL failures were not
application failures. The official `hub` CLI refused a stale digest as expected.
After the final source edit in this verification pass, `hub stamp bundle` wrote
`fc160ecda2e1f144dad4b54ee01424d7fc4876e03fac806b4fef501c6f6dea83`;
`python -X utf8 tools/launch.py --host-workspace D:\projects\GOSIMAPP\OctoSense
--app-hub-source D:\projects\GOSIMAPP\OctoSense\target\dependency-probe\app-hub
--check` passed with the expected unsigned-source warning. The bundle is
8,371,753 bytes excluding its manifest, below the 8,388,608-byte gate. Its
background PNG was recompressed losslessly to keep the bundle within that gate;
all non-IDAT chunks and the decompressed image data were preserved.

The official pinned card-host admitted the bundle in hidden standalone mode
with task-owned app data. A native UI run found that the first manual intake
form was blank; moving its dynamic controls directly into the active render
tree fixed it. The updated `tools/smoke.py` passed 26 UI/data checks on a fresh
isolated profile and its `--restart` mode passed both persistence checks.
The checks cover onboarding, atomic rejection, manual preview/add/edit/discard,
unit and package conversion, grouping, all four freshness labels, disabled
image buttons, fallback when the model service is unavailable, local rule and
automatic generation switches, candidate creation and acceptance, consumption
cancellation and confirmation, plan deletion, profile edit and restart. The state file was
byte-identical across restart. A second isolated card-host loaded a synthetic
schema-1 file, migrated and saved it as schema-2, and preserved profile fields,
two batch IDs, plan ID, program history, log and next IDs across restart.
The complete bundle passed the pinned script parser; 33 source-extracted VM
cases passed after the UI edit. No test keys, signing identity, production data,
provider credentials or live provider request were used. Full Store installation
requires the separate test-key approval in `AGENTS.md`; release version/listing,
current screenshots and live-provider validation remain open.

## Issue #2 non-multimodal plan and offline recheck, 2026-10-11 — uncommitted

At the earlier plan split, the local-only milestone covered the active profile/manual-inventory/menu plan
and `.local-planning/deferred-multimodal/` for image recognition, the local
OctoSense bridge, custom-host video, and related release claims. Neither plan
is distributed. At that point the Pantry source still had disabled image buttons;
there was no recognition request or OctoSense source patch. The image-intake section
above records the subsequent local implementation.

The full edited bundle passed the pinned Makepad parser. Two ignored harness
generators extracted functions from the current script; all 33 resulting VM
cases passed. Their storage commit and some host/UI calls are stubbed, so this
is offline behavior evidence, not native persistence or rendering. The 18
existing Python tests passed under ordinary Windows permissions. A sandboxed
attempt failed in Python temporary-directory ACL operations and was rerun;
no product assertion failed.

Both READMEs, PRIVACY.md, and the small historical brief/review/submission
notes now distinguish this uncommitted feature branch from the earlier 0.6.2
candidate. `bundle/listing.json` and `bundle/manifest.json` still identify the
old candidate. The current source digest now passes the pinned official Hub
gate, but final versioning/listing and a subsequent restamp are needed before
distribution.
The subsequent official-host verification section above supersedes the
dependency and native-check limits of this earlier offline checkpoint. No test
keys or provider credentials
were created, and no source was changed in OctoSense.

## Issue #2 local UI and menu compatibility, 2026-10-10 — uncommitted at this checkpoint

The Pantry feature branch now has separate allergy, avoidance, and preference
inputs; one editable intake draft for manual and future image rows; grouped
inventory summaries with batch detail actions; and menu uses that distinguish
confirmed quantity/unit from estimated grams. Count consumption deducts pieces,
while mass consumption deducts grams. Automatically generated menus use known,
non-expired dates in expiry order; the consumption review can switch to another
compatible batch, including one with an unknown date. Expired, volume, and
unconverted package batches are excluded from gram-based menu generation.

The task-owned ignored parser harness extracts actual script
functions and passes 19 focused Makepad VM cases for migration, calendar boundaries,
multi-row atomic confirmation, profile revision staleness, grouped totals and
freshness, manual edit/discard, rule/model menus, plan acceptance, cancellation,
count deduction, manual unknown-date allocation, and plan deletion. Its storage
commit and some host/UI functions are stubbed. The full bundle passes the pinned
script parser, and the existing Python `tools` suite passes 18 tests.

Native UI, filesystem restart, and the official bundle gate were not run. The
official OctoSense build did not reach compilation: Cargo stopped at another
pinned Git dependency, `octos-org/octos` revision
`18fcd3f16e527d2b601d7ae244f056fb711bb6b8`. The current
`tools/launch.py --host-workspace ... --check` exits because its pinned App Hub
checkout is still missing. The edited bundle's manifest
digest still needs an official Hub restamp. No local test keys were generated.

## Issue #2 local inventory data work, 2026-10-10 — uncommitted at this checkpoint

The Pantry feature branch contains schema-2 migration, unit and expiration
normalization, and one confirmed-inventory mutation boundary in
`bundle/main.splash`. The pinned Makepad script parser accepts the complete
bundle. Seven focused VM cases using the bundle's actual data-core functions
passed: representative schema-1 migration and JSON round trip; all supported
unit labels and expiration boundaries; add/edit/discard/consume, duplicate ID,
and atomic rejection; confirmed package conversion; zero-quantity removal;
confirmation-day expiry conversion and cancellation; and built-in demo data
migration. At this checkpoint the manual UI still exposed only grams; the
later UI work above added other units, unknown expiry, and confirmed printed
dates. The task-owned parser harness was ignored by Git; its commit
function is stubbed, so this is not native filesystem or host launch evidence.
The existing `tools` unittest suite passed all 18 tests. `git diff --check`
passed. The editable bundle's manifest digest has not been restamped; the
official host bundle gate, native restart, and real-provider flows were not
run while the Cargo dependency download remained incomplete. No local test
keys, publisher artifacts, or release were created.

## Original-artwork confirmation, 2026-10-08 — current 0.6.2 candidate

The author confirmed sunlit-pantry-bg.png is their own original artwork.
Recorded that declaration in root/bundle notices, bilingual READMEs, review
answers and submission checklist. This resolves the author's outstanding
asset-origin checkpoint; it is not independent rights verification. Earlier
pending-artwork statements below describe the earlier repair checkpoint.

Only notices/docs changed; application logic and artwork are unchanged.
The current official pinned hub restamped the editable bundle after this
notice edit. Current source digest:
`851f2c46a63bd1a129a8c451acbe4992e2d11a8f7e81ffa3376307268640d103`.
Source gate passed with only the expected unsigned warning; scan regenerated
seven questions; all 18 automated tests passed again; git diff --check passed.
Current total size: 8,357,004 bytes, 31,604 bytes below 8 MiB.

The seven native checks below were performed before this notice-only edit;
they were not rerun or relabelled as full functional regression. Live-provider
tests, attested-release verification, platform limits and human approval
remain as listed below. No commit, tag, push, release or Issue was made.

## Local compliance repair, 2026-10-08 — 0.6.2 candidate

This dated entry supersedes earlier pending publisher/privacy statements;
it does not rewrite the historical test records below or admit any version.
The user confirmed publisher display names, Windows-only claims and privacy
disclosure, and authorized local repair only. No commit, pushed tag, GitHub
workflow run, release or submission issue was created in this repair.

### Source and metadata

- Repair checkout: app-only remote main at
  `fd5baccd45e2aa39a8723e7c1efdd263342b0c7d`, local branch
  `codex/compliance-0.6.2`. The original full host at `E:\codeh\OctoSense`
  and its user's inventory were not replaced.
- `bundle/main.splash` is unchanged: Git blob
  `8e9660e130b45d6a3e71f8ff94f1bfb1e7d0d78e`, identical in the baseline
  remote commit, repair checkout and original full host's app directory.
- Corrected support/privacy URLs, release notes/version, bilingual launch
  instructions and review answers. Added Apache-2.0 license and notices
  at the repository root and inside the bundle with allowed `.txt` names.
- `.gitattributes` disables bundle text conversion; native installer source
  and tool scripts use LF, Windows batch entrypoint remains CRLF.
- `sunlit-pantry-bg.png` and historical screenshots were preserved. Image
  ownership/redistribution evidence remains a release-blocking author checkpoint.

### Current official source gate

- App Hub: `655114c4943cd2490daaefa2173e7b5aaa20669f`, the workflow pin.
  Built both `hub` and `card-host` on Windows with Rust 1.98.1, from the
  unmodified official checkout using `cargo build --locked --release`.
  The original workspace and lock file were unchanged. Its exact dependencies
  were reused from Cargo-managed caches via local junctions; no user's shared
  framework checkout was modified.
- Native pins: Makepad `32d6415fb7476345ad36ee4f98d6f844d1f07fd2`,
  Octoscript-Makepad `33dea2f1f3ad3f1346a219aa8cf6e91b31361e23`,
  Octoscript `2e37d9e657a246f16718d9a475e167ccd2d5b5fa`.
- The old `0d5b47...` Windows CLI first passed the pre-license bundle, then
  incorrectly treated the full Apache license URL as a remote asset. The
  current CLI also exposed its old path-hash mismatch. These were not worked
  around with extra grants, stripped legal text or changes to the gate.
- Restamped only the unsigned editable source with the current official tool:
  `4f09efe71f2db070322f4959e8e86b2b36aa8555b9426547ae45198a63661c0e`.
  This is NOT a sealed-release proof or a manually invented hash.
- `hub check bundle --allow-unsigned` and its JSON form passed, structural
  stage, with only the expected unsigned warning. Grants: storage/model,
  no outbound hosts, 16 MiB storage, no app agent.
- `hub scan bundle --packet build/review.json` generated all seven questions;
  no external reviewer ran. Answers are in REVIEW-ANSWERS.md.
- `python -B -X utf8 tools/launch.py --hub
  build/hub-reviewed/target/release/hub.exe --check` passed with no host,
  key generation, installation or implicit restamping.
- Total bundle size is 8,357,017 bytes, below 8,388,608 bytes. Remaining
  headroom is only 31,591 bytes; future artwork changes must recheck size.

### Automated and native checks

- `python -B -X utf8 -m unittest discover -s tools -p 'test_*.py'`:
  **18 passed**. Includes batch dispatch/error status, explicit tool/host
  resolution, no implicit key creation, no launcher restamp, permission and
  metadata guards, required legal files, platform and local-document links.
- Both new listing URLs returned HTTP 200. The remote pages still describe
  the previously pushed state until these local changes are authorized/pushed.
- Isolated Git index checkout with `core.autocrlf=true` under `build/`
  preserved the bundle's bytes; the current gate passed that checkout and
  SHA256 of main.splash matched. This is a local byte-conversion test,
  not a new remote tag clone or release download verification.
- Current official `card-host`, hidden 1200x800, separate synthetic
  `.local-state/qa-current-062`, remote port 18529: **7 native checks passed**.
  First run rendered; 7/21/30-day choices required confirmation; explicit
  cycle activation worked; inventory preview did not commit; confirmed
  synthetic spinach committed; manual default did not generate a plan;
  restart preserved the exact saved synthetic state.
- Native driver: `build/native_compliance.py` for the six first-run checks,
  followed by `tools/qa_release.py --port 18529 --profile
  .local-state/qa-current-062 --restart` for persistence. The equivalent
  reusable driver is now in tools/qa_release.py and requires a task-owned
  qa-* profile under .local-state. Do not point it at real inventory.
- Opened and visually inspected both genuine native test captures. They
  remain outside bundle/. No app callback/closure/error-level messages were
  found in these run/restart logs. Native startup produced informational
  UI-hang samples and the build produced upstream compiler warnings; these
  are not claimed as warning-free runs. All task-owned hidden instances quit.
- `git diff --check` passed. Local-state, build products and test captures
  are ignored. No real AI credentials, model calls or new signing keys used.

### Still pending — no approval guarantee

Background rights, full current-toolchain feature regression, live model
provider tests, fresh-computer setup, other platforms, GitHub Actions
execution, downloaded attested release-pack/receipt verification, publisher
continuity against the authenticated catalog, Store installation and Hub
approval are unverified. The prepared workflow does not supply any of that
evidence until it actually runs and its downloaded artifacts are verified.
Its pinned Rust 1.97.1 Linux environment is distinct from this Windows build.
The teacher decides competition qualification and deadline eligibility.

Issue #99 still refers to immutable 0.6.1. Current submission rules require
one issue per planned version; 0.6.2 needs a new issue linked to #99 after
human authorization, never a moved v0.6.1 tag or a replacement version comment.

## Cycle program addition, 2026-10-06

- Bundle 0.6.1 adds explicit 7/21/30-day programs to the existing desktop UI.
  Official model/storage grants, manual-default generation and deletion remain.
- Official cached Windows Card runtime: synthetic `qa-cycle` profile, hidden
  1200x800 viewport. Twelve UI/data checks passed: candidate duration and totals,
  explicit activation (21 and 30 days), no automatic generation during inventory
  entry or consumption, inventory validation, cycle intake, deletion preserving
  intake, and renewal archiving the old cycle without losing inventory.
- Restart preserved the exact saved profile, active cycle, history and inventory.
- Synthetic pre-cycle `qa-legacy`: three additional checks passed for 7-day
  confirmation, inventory/plans/meal preservation, and zero initial new-cycle
  intake. No script errors appeared in its runtime log. The quit route closes
  the server connection on this build; that cleanup is not a failed app check.
- App Hub `stamp` and `check --allow-unsigned` passed. Unsigned source warning
  is expected; production identity/signing and store publication remain unverified.
- Fresh period screenshots are hidden Card-runtime captures, not phone images.
  This update has not been tested on Android or with a live model request.
- Existing user's `.local-state/` is not used as a test profile. Original sources
  are backed up before deployment; no host code or downloaded APK is replaced.

Earlier 0.4.3 results below describe that earlier version, not the cycle change.

## Manual-default and deletion regression, 2026-10-04–05

- Bundle 0.4.3: manual generation by default; persisted opt-in automatic mode;
  invalid-plan notice and explicit Home entry; confirmed single-plan deletion.
- Current official checkout HEAD: 6794abd2026574bd283265d13fcaa76b5323a9e1.
  App Hub CLI pin: 0d5b47a2ae9eb98020feca26b7c895a3cf797dc1.
- `python -B -X utf8 apps/pantry-steward/tools/launch.py --check` passed:
  unchanged storage/model permissions, source unsigned warning expected.
- `python -B -X utf8 -m unittest discover -s apps/pantry-steward/tools
  -p 'test_*.py'`: 7 passed, including manual defaults and automatic-trigger guards.
- Native hidden official-shell tests used a cached desktop executable and separate
  synthetic profiles; no host source edits, real inventory or model calls.
  `tools/smoke.py` with qa-manual: 36 UI/data checks passed. Covers onboarding,
  cancelled edits, confirmed edits/removals without generation, expiry notice
  without generation, explicit generation, visible invalid-plan notice, no
  generation from the Home entry alone, consumption without next-plan generation,
  deletion/cancellation/last-plan/active-plan cases, automatic opt-in and opt-out.
  Same command with `--restart`: exact persistence check passed.
- A separate qa-manual-legacy profile was preloaded with synthetic old state
  (no auto_generate property) and an old before-demo backup. `--legacy`: 8 checks
  passed for manual migration, preserved stock/plans/meals, backup restoration,
  opt-in automatic consumption/addition/removal, switching back to manual, and
  the explicit alternative button. Total: 45 UI/data checks.
- After the final wording adjustment, the 36-check run was repeated in
  qa-manual-final and all 8 legacy checks were repeated; both passed with no
  native callback/closure errors. Final digest:
  `5bbfba5f084678c9009f81249cd33f93ec2a57b1c5d77f82e15dac799643a824`.
- Real native captures of invalid-plan and manual settings were visually checked.
  Existing four submission screenshots were not replaced by these QA captures.
  Task-owned hidden windows were closed using their own remote endpoint; restart
  and legacy logs contained no error-level, callback or closure-failure messages.
- Before this change, 0.4.2 deletion regression also passed 23 UI/data checks,
  persistence and two maximized-window reachability checks. Deletion remains
  included in the 0.4.3 regression above.

Limitations: setup reports the existing `.sources/octoscript-makepad` checkout is
at another revision. Its clean checkout was not updated. These script-only tests
use the existing desktop binary, so a fresh host rebuild against the current
runtime lock is **unverified**. Do not interpret the bundle gate as a host build.
Late live-network response cancellation and provider charging were not exercised;
the sequence guard is retained and disabling ignores automatic results.
The user reported successful host-AI generation, but these automated checks did
not use real credentials or make provider requests. Mobile/release signing and
publication remain unverified; no Git commit, push or submission was performed.

## Verified on Windows, 2026-10-02

- Official OctoSense source: b221f7b4c877dd823d04e4ee510cc74880de5535.
- Pinned App Hub: 58c3c8aed8fc811a16d67c5f784a8a44214ff876.
- `python -X utf8 tools/setup.py --hub <existing dependency directory>` succeeded.
- `python -X utf8 apps/pantry-steward/tools/launch.py --check` built the
  official CLI sources, reusing `.sources/` without custom host services.
- `python -X utf8 -m unittest discover -s apps/pantry-steward/tools -p 'test_*.py'`:
  3 passed (key-generation consent, no secrets/custom microphone calls in the
  bundle, official budget semantics).
- The launcher with `--prepare-local-test --hidden --remote 18442 --app-data
  apps/pantry-steward/.local-state/qa-official` generated local test keys only
  after explicit consent; signed a separate snapshot; published ONLY to a local
  mirror; verified the catalog and installed through App Hub's real Store.
- `python -X utf8 apps/pantry-steward/tools/smoke.py --profile
  apps/pantry-steward/.local-state/qa-complete`: 17 native UI/data checks passed.
  Includes first-run onboarding, invalid quantities, preview/confirmation,
  microphone-unavailable notice, honest budget status, local mode, demo consent,
  expiry replanning, acceptance, invalid consumption, cancellation, consumption,
  and returning to the profile form without losing inventory.
- Same command with `--restart`: persistence check passed (18 UI/data checks total).
- Native remote logs after the successful run/restart contained no `[E]`,
  callback errors or on_render closure failures.
- Final default profile launcher (`--hidden --remote 18443`) opened the app in
  the unmodified official shell. `cargo build --release --locked -p octosense`
  succeeded; the official source files remained unchanged.
- Independent preview (`--standalone --hidden --remote 18444`) was admitted
  by the unmodified official card-host and rendered its initial onboarding page.
- `target/release/hub scan apps/pantry-steward/bundle --packet
  apps/pantry-steward/build/review.json` created the seven-question review packet;
  no external reviewer was used. Draft answers: REVIEW-ANSWERS.md.
- Four real full-window captures from the official-shell test were opened,
  visually inspected and copied without editing to `bundle/screenshots/`:
  `01-main.png`, `02-plan.png`, `03-confirm.png`, `04-updated.png`.
- Final bundle size: 8,308,715 bytes, below the 8,388,608-byte gate limit.

Final unsigned source-bundle gate output:

```text
pantry-steward 0.4.1 — PASSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
  grants: capabilities {"model", "storage"}, hosts {}, storage 16777216 bytes, agent none
```

Local signed snapshots also passed without that unsigned warning. They are not
production publisher signatures. The source bundle remains unsigned for editing.

## Compatibility gaps found and fixed

- The Windows batch entrypoint used LF-only newlines. Running it through
  cmd.exe reproduced truncated commands before Python could start. Changed it
  to ASCII with CRLF, added a Git checkout rule, and guarded its dispatch and
  failure exit status with Windows-only tests.
  All six launcher tests passed. Running run.cmd from the app directory with
  a separate qa-batch profile opened the official shell and Pantry Steward's
  first onboarding page; verified via the native UI snapshot and real capture.
  The task-owned hidden test window was closed through its remote endpoint.
- The original 2 MiB quota failed `fs.write` in the official runner, because
  this runtime counts the installed bundle/resources inside the jail. Raised
  the requested quota to the supported 16 MiB ceiling and reran onboarding.
- Official `model.budget` returns usage, not `configured` or model identity.
  Removed that assumption and stopped labelling a successful budget query as a
  configured provider.
- The tested official host has no original `microphone.start/stop` adapter.
  Removed its calls and microphone grant. The icon now explains unavailability;
  no audio is recorded. Original speech code is preserved in the source project.
- A manifest-only edit does not change the bundle digest. Local snapshot caches
  now include manifest bytes, so storage/version changes cannot reuse stale grants.

## Not verified

Live model-provider calls, no-provider response end-to-end, speech recognition,
other operating systems, mobile devices, release signing and App Hub submission.
No real AI credentials were copied or used, and no provider API call was tested.
The original project's inventory and ai.env were not migrated. All created
hidden test windows were closed through their own remote endpoint.

Publisher identity and privacy text remain unapproved; the existing listing
keeps the author's pending identity. Local test-key creation was explicitly
approved by the user. Production signing and submission were not authorized.

## Issue #3 M2 local validation, 2026-10-12

- The global text panel and Agent request path live in `bundle/main.splash`.
  The panel is limited to home, inventory, and menu. M2 permits only a
  `none + {}` reply; proposal tools have no executable card or business write.
- The production Script VM harness passed 18 cases covering shared day session,
  one strong request, optional fast compaction, retry after provider failure,
  timeout, invalid output, stale reply, and local snapshot changes.
- `python -X utf8 -m unittest discover -s tools -p "test_*.py"`: 20 passed.
  The full suite needed local Windows temporary-directory access; the default
  sandbox's temporary-directory ACL does not permit those tests.
- `python -X utf8 tools/launch.py --host-workspace
  D:/projects/GOSIMAPP/OctoSense --check --offline`: PASSED. The editable source
  bundle has the expected unsigned warning.
- The bundle was restamped to digest
  `906f9ce1c5f4cae7731c3ef5f5c8519a0c83dd73ad94e13135dc2d2b3f0f22f6`.
  Using pre-existing local test keys, the source snapshot was signed, published,
  and installed through the official App Hub into the task-owned
  `target/m2-official-profile`; no new keys were generated.
- The unmodified official OctoSense desktop built with `cargo build --release
  --locked -p octosense --offline` and opened the installed Pantry Card. The
  local legacy App Hub mirror needs `OCTOSENSE_HUB_CATALOG=legacy`; the Pantry
  launcher now sets it for this task-owned mirror.
- Native UI with a synthetic four-batch profile: home, inventory, and menu
  each exposed `问管家`; all three reused one day session. The profile page and
  inventory intake draft hid the entry. Canceling that draft restored the
  entry without changing inventory. The panel rendered multiline input,
  microphone, send, close, and the saved message. The microphone reported
  recognition unavailable. A no-provider send stored one user message,
  retained the input, showed a retryable error, and did not append an assistant
  reply. After closing and reopening the desktop, the same-day user message
  appeared again. Host logs contained no `[E]`, callback, or render errors.
- A fresh isolated official-host profile passed 27 native UI/data checks in
  `tools/smoke.py`, covering onboarding, both available image entry choices
  and their review gate, manual inventory, menu acceptance, consumption,
  deletion, profile editing, and navigation. The old smoke assertion assumed
  image capability was unavailable; it now checks the actual available or
  unavailable path. A subsequent desktop restart passed both persistence
  checks for profile, inventory, menu, history, IDs, and home navigation.
- Real provider multi-turn/compaction calls were not run. The separate Issue
  #4 stage and Issue #5 final menu revisions/lock contract are absent from
  this checkout, so their snapshot fields and the final M2 exit remain open.

# PR #21 schema compatibility and main integration — 2026-10-12

Merged the stage/candidate split, native inventory units, image-entry drafts,
day menus, derived shortages, mock cart and orders from main `3ddeb82`, while
keeping the optional stock-only one-day experience, append-only actual intake
and online nutrition estimation. Ordinary shopping remains available; the
experience has no shopping route. The release version remains main's 0.8.0.

Removed `uniqueItems` from `recipe_steps_schema()`. `parse_recipe()` retains its
local per-step duplicate-ID guard, allocated-food-ID check and coverage check.
The old captured experience request was independently rejected by the official
host compiler with `the keyword "uniqueItems" is not supported`. The new
`tools/model_schema_probe` compiles the original host
`apps/ai-providers/host-service/src/complete/schema.rs` directly via a generated
`#[path]` module; it does not reproduce a keyword whitelist. Its source SHA256
was `a86d2c679402684730cc0b036cc9717ce5e2efc8d62b49d5c41e0d923cca50f9`.
All five native-captured schemas in `docs/model-schemas/` compiled successfully:
nutrition, ordinary day menu, one-day experience, native-quantity recipe-only
menu and image intake. An injected unsupported-keyword negative control was
rejected. This requires no provider credentials or live calls.

Validation at this checkpoint:

- 30/30 offline Python tests passed.
- Official App Hub `8347a489141c0e24cab564883db7c4592935a8b2` stamped and admitted
  the production bundle, including its retained `host-api-v1`, camera/files and
  optional camera-permission declarations. No release version bump.
- 24/24 native merge checks passed on schema-2 synthetic stock, and again
  24/24 on a schema-1 file containing field names in user text. Migration adds
  candidate/stage fields before validating old schema-1 states and uses exact
  key checks for the independent ledger. Confirmed historical nutrition and
  actual snapshots survive; exhausted legacy batches do not resurrect.
- Native checks cover duplicate and unknown recipe IDs in both menu paths,
  independent recommended/actual quantities, atomic native-unit stock updates,
  stage intake, regeneration preserving confirmed recommendations, all three
  confirmations, 100% recap and long-term history after a stage switch.
- A real process restart preserved exact inventory and execution history.
- Seven shopping checks preserved the derived shortage, editable mock cart,
  confirmation-before-order and zero stock/intake/progress change on ordering.
- Two native-unit checks preserved a piece-only recipe without inventing a
  mass conversion. Six nutrition-failure checks continued once to an online
  menu, retained unknown references, recorded external food without a stock
  deduction and counted confirmation without claiming nutritional completion.

Native tests use task-owned hidden official standalone card-host, a private
bundle with deterministic model dispatch, and isolated synthetic app data.
Standalone card-host does not link the full shell's device-consent broker, so
only its private test manifest omits `host-api-v1` and optional host API fields;
the production manifest retains them. No camera/files service is injected.
Image schema compilation is verified, but camera capture, image recognition,
the full-shell permission boundary and live provider output are not new evidence
from these tests. Model request captures are separately fed through the real
official schema compiler, addressing the prior fake-dispatch coverage gap.
Earlier schema-1 QA reports below remain historical evidence, not a claim that
their old drivers run unchanged against the new candidate/stage architecture.

Subsequent main update: `0e092ff` added Issue #28 receipt confirmation while this
repair was running. It was merged too. The final offline suite passed 31/31;
the native shopping/receipt path passed 12/12, including editable receipt
quantities, preview/cancellation without writes, a new canonical batch only
after confirmation, persisted received status and unchanged execution/stage
progress. An actual restart of the final integrated code preserved the exact
confirmed inventory and execution ledger. Production bundle digest after this
integration: `0a96264adf2b739522ee651c0b80474b1261091f9ad452b5b81ec7d4fda53ccc`.
This update leaves the five model schemas unchanged.

Current reproducible entry points: `tools/qa_merge.py` and
`tools/check_model_schema.py`; see `EXPERIENCE.md`. Personal application data,
provider settings and existing published commits were not modified for testing.

# PR #21 online opt-out and pending request control — 2026-10-12

Preserve stored `model_enabled=false` at load. Settings explicitly enables or
disables online AI and persists the choice; menus, nutrition and image-model
requests check that choice before dispatch. Disabling AI also invalidates
pending replies. Menus still use online AI only when enabled; no local fallback
was reintroduced.

Nutrition snapshots now carry the original trigger reason through success,
malformed output, failure and timeout. Turning off automatic generation
invalidates pending automatic menu/nutrition flows via the request sequence;
later re-enabling does not revive them. Both ordinary and experience menu
continuations recheck the current switch before sending. Explicit manual
generation continues when only automatic generation is turned off.

Validation on the changed bundle:

- 31/31 offline Python tests passed; `tools/launch.py --check` and official Hub
 stamp/check passed, retaining version 0.8.0 and production permissions.
- `tools/qa_request_control.py`: 54/54 native checks across 14 fresh isolated
 fixtures. Legacy schema-1 and current schema-2 opt-outs survived inventory
 removal, manual attempts, stock nutrition and image dispatch attempts, saved
 state and actual process restarts. The UI enable button persisted consent;
 the next explicit menu request sent nutrition then menu exactly once.
- Held nutrition replies covered success, error, malformed data and accelerated
 timeout. Turning auto generation off sent no second request and wrote no
 late nutrition/menu. Turning it off then on, experience auto generation,
 stock estimation and disabling online AI during a request were covered.
 Manual generation continued for each of the four reply outcomes.
- 24/24 existing `qa_merge.py` checks passed for ordinary menus, optional trial,
 immutable actual records, inventory deductions and completion recap.
- All nine current request captures (nutrition, ordinary/experience menus and
 image schema) compiled through the original official host schema compiler;
 unsupported `uniqueItems` negative control was still rejected.

The new regression driver reuses synthetic `qa_merge` state and a private
model-dispatch shim. Initial opt-out removal/enable paths use native UI;
cancellation cases invoke the same production action functions via test-only
commands. Only response delivery and the timeout deadline are controlled;
production guards, persistence, callbacks and watchdog run unchanged. The
image opt-out test verifies no dispatch, not image recognition capability.
Standalone-host test-manifest limitations described above still apply. No real
provider, personal inventory or provider credentials were used. Already sent
provider requests cannot be guaranteed to stop or avoid billing.

Machine-readable assertions: `docs/model-request-control-validation.json`.
Reproduction: `tools/qa_request_control.py --profile <fresh .local-state/qa-*>
--hub <official hub> --card-host <official card-host>`; the driver starts and
closes its own hidden hosts. Bundle digest:
`234e13907694e1efabca02da29b9e275557fd6115a4f8eeea95eaf57734c62ed`.

## Issue #3 branch sync with remote main, 2026-10-12

- Fetched `origin/main` at `358d61c` and merged its stage, three-meal,
  shopping, and actual-intake work into the Issue #3 branch. The merge kept the
  Agent busy gate on image recognition and added the new online-ready gate.
  It also remapped the Agent entry to the new Home/Inventory/Menu tabs (0/2/3)
  and leaves the Overview tab (1) without an Agent entry.
- `python -X utf8 -m unittest discover -s tools -p "test_*.py"`: 33/33 passed
  with normal local filesystem permissions. The restricted execution sandbox
  denied Python temporary-directory access; those ACL errors were not product
  failures. The production Script VM Agent harness passed 18 cases, including
  the updated tab mapping.
- The pinned local `hub.exe stamp bundle` produced digest
  `b80a513b0f3289f3a90806eb2501ece4beb62ddba41788339fb96c81482a37ac`;
  `tools/launch.py --hub <pinned hub> --check` passed with the expected unsigned
  editable-bundle warning.
- In a task-owned hidden `card-host` profile, the synthetic `qa_merge.py`
  scenario passed 24/24 native checks for stage, ordinary three-meal menu,
  one-day experience, actual consumption, and inventory writes. A separate
  native UI probe found the Agent panel on Home, Inventory, and Menu and absent
  from Overview. This fixture did not call a real provider.
- The remote main contains `current_stage()` and a three-meal `state.plans`
  path, but it does not implement Issue #5's final `state.daily_menu` draft,
  status, allocation revision, or whole-day lock after one meal. The Issue #3
  Agent still accepts only `none + {}`; proposals, full stage/menu projection,
  memory writes after confirmed menus, and ASR remain unverified or unbuilt.

## Issue #3 M5 voice integration — 2026-10-13

The Agent microphone now probes the optional host speech capability, checks
microphone consent, records one app-local WAV for at most 30 seconds, and puts
the transcript into the editable Agent input. It never sends the transcript or
writes inventory, menu, or intake state on its own. A transient host `rate`
response during startup capability probing is retried within a 12-second
budget; the initial local-host run reproduced that response before the fix.
The host-managed permission sheet uses the same device-consent route as the
Issue #2 camera flow. Waiting for a person's consent now has a 180-second
application deadline instead of 30 seconds.

- Final bundle digest: `e400d0b8f899b78e4638d7093953f693c30fa191c554b47a4b9b57d6c93c0e9e`.
  The pinned Hub stamp/check and `tools/launch.py --check --offline` passed.
  Existing local test keys signed task-owned isolated profiles; no new key or
  production signature was generated.
- Offline Pantry suite: 36/36 passed with a task-owned temporary directory.
  The production Script VM cases cover unsupported/no MiniMax, consent and
  refusal, manual and automatic stop, cancellation, stale callbacks, empty
  transcription, editable draft versus send, transient startup `rate`, and a
  late recording-status reply arriving after Stop.
- The unmodified official desktop installed this same bundle in an isolated
  profile. Its microphone showed the exact unsupported message without an app
  WAV. An earlier real provider reply remained readable after restart, and a
  fresh text request returned a real Agent reply on the final bundle.
- The rebuilt local desktop opened the host's microphone consent sheet. After
  consent, a person recorded and manually stopped a mixed Chinese/English food
  request. The app-local 16 kHz mono WAV contained 4.38 seconds of audio; the
  actual MiniMax transcription appeared in the editable Agent input. The
  person did not press Send and the inventory revision did not change.
- In a separate run on the final bundle, the person clicked the microphone
  only once. The host automatically stopped at 30 seconds; the 16 kHz mono WAV
  contained exactly 30.0 seconds of audio, and a mixed Chinese/English
  transcript appeared in the editable input without a Send action.
- During a later live recording, closing the Agent panel removed the temporary
  WAV. A further recording was started with the task-owned window in the
  foreground, then the host was quit normally while recording. Its process
  exited and no temporary WAV remained. Across these unsent voice runs, no
  Agent session file was created and the inventory revision stayed at 8.
- Windows mouse activation initially made the pinned Makepad runtime report a
  focus loss. The OctoSense patch now treats `WA_CLICKACTIVE` as focus gain;
  its regression test and release build passed. Earlier `device_unavailable:
  No audio frames arrived` results came from a restricted test-host process
  without microphone-device access. The task-owned host launched on the
  interactive desktop with normal device access produced both live recordings.
