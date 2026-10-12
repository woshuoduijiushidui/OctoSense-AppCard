# Pantry Steward · 冰箱管家

English | [简体中文](README.zh-CN.md)

Turn confirmed pantry inventory into a meal you can review and execute.

## Version and evidence

This branch contains the unpublished **0.8.0 source candidate** for Issue #2 and the Issue #8–#11 and #23–#28 features (six-cycle candidates, composed plans, future-stage editing, the Overview page, the three-meal day menu and its derived 缺菜清单, the 模拟买菜 region, its 待核对购物车 and 确认收货). Alongside manual inventory, cycles, and menus, it creates editable drafts from a camera or imported image when the locally modified host reports image capability. The official host falls back to manual entry. The bundle passes the pinned App Hub gate. [Issue #99](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/99) reviews **0.6.1**, not this candidate; no release or Hub approval is claimed.

Only Windows is targeted. On 2026-10-11 the 0.8.0 bundle passed the pinned App Hub gate and 19 Python tests. In an isolated profile, the unmodified full official host passed 26 UI/data checks and restart checks, including manual fallback from both image buttons. The locally modified host passed the capability probe, shared chooser, and cancellation checks; task-only model fixtures exercised both editable image drafts and a multi-row inventory commit. The user reported that the remaining foreground MiniMax image, camera, retry, and restart checks passed; per-step logs were not captured independently. Formal Store publication remains unverified. See [VALIDATION.md](VALIDATION.md).

## What it does

Confirm a dietary profile and 1/3/7/15/21/30-day cycles with three comparable candidates each (the regular 1-day health cycle is separate from the optional flow experience); regenerate one cycle's candidates without touching a confirmed plan. Confirm a single candidate as a one-stage plan, or add candidates of different cycles in order (repeats allowed, e.g. 7+7) and reorder, remove or replace stages before confirming; the compose page shows the summed total days and each stage's date range and targets, up to 12 stages. A confirmed stage locks on its start date; stages that have not started can still be reordered, replaced, removed or retargeted in the Archive tab, which recalculates the later stages' dates and the plan totals while confirmed progress and intake records stay untouched. Then preview inventory batches; generate an online AI three-meal day menu through the host model.complete service in one call (早/中/晚); review each meal's ingredients, grams and nutrition reference; accept it (a menu needing a purchase can still be accepted — the derived 缺菜清单 merges repeated ingredients into one gap of 用量 − 库存可用, edits there rewrite the day menu's usage and are never stored, and the list re-derives whenever stock changes); separately confirm actual consumption before deducting inventory and recording intake. Each confirmed stage snapshots its candidate's targets, so later edits to a candidate do not change it. Daily/cycle values are prototype estimates. Archive a plan without deleting stock. The Overview tab shows the long-term plan, the current stage, today's per-meal progress and the current stage's kcal/protein target against actuals; progress counts only confirmed meals over days × 3 meals and never moves when a menu is only generated or confirmed — only a confirmed meal increases it. The target follows the stage whose dates cover today.

The profile separates allergies, avoidances, and preferences. Intake creates editable batches before confirmation and accepts g/kg, ml/L, pieces, or simple packages with a user-confirmed conversion. Inventory retains separate batches and freshness states. Image recognition is enabled only after a positive `model.vision_capability` probe from the locally modified host; users fill uncertain fields before confirming.

一键补齐 on the 缺菜清单 opens an in-app 模拟买菜 region in the same window (no second bundle unit, no new app id or capability). It carries the current derived 缺菜清单, marking each line 已对应模拟商品 or 无对应模拟商品, and browses a fixed 24-item 模拟商品 catalog with both a list and a detail page (品类、规格、单位、价格、可售数量、每 100 g 营养参考、参考保质期). 商品/购物车/订单 are the region's own navigation and 返回管家 restores the butler without changing its tabs. Every page is labelled 模拟平台/模拟下单; the catalog ships in the bundle and the app declares no shopping network capability, so nothing is bought or paid for and inventory never changes. Entering the region prefills a 待核对购物车 from the 缺菜清单 by name, spec and quantity (packs round up); a line the catalog cannot match or cannot stock is flagged 无匹配/可售不足 with a 替换 entry rather than dropped, and 替换 offers same-category, spec-compatible alternatives with allergies and avoidances excluded. The cart is user input: 增减数量, 删除 and 替换 persist across restarts and show simulated unit prices and a total. The cart is submitted as a 模拟订单 only after the user confirms it, then the 订单 page shows the order with its 待收货 status, its lines and a simulated total; the page says submitting produces no real purchase or payment. Submitting writes the order and nothing else: 库存、进度 and 实际执行记录 are unchanged, and the order survives a restart. An unmatched row has no product to order and stays in the cart; an over-stock row is ordered at the on-sale maximum. 确认收货 on a 待收货 order opens a per-line check: the received quantity defaults to the ordered amount and can only be reduced, and the 保质期 defaults to the 模拟商品's 保质期天数 from today and can be edited. Only checked-in quantities become new inventory batches, each with a new id and its own arrival date rather than being merged into an existing batch, so the 库存页 shows them at once; the unchecked remainder re-derives into the 缺菜清单. 确认收货 writes no 实际执行记录 and does not move 进度.

Generation is manual by default. Optional automatic generation must be enabled in Settings; acceptance and consumption still require confirmation. Deleting a plan does not restore inventory or erase meal records. See [cycle details](CYCLE-PLANS.md).

## Demo

[Historical manual-flow recording](video/演示视频.mp4)

![Windows card-host home capture](bundle/screenshots/01-main.png)

[Three-meal day menu and 缺菜清单](bundle/screenshots/02-plan.png) · [缺菜清单 with an editable gap](bundle/screenshots/03-confirm.png) · [Inventory](bundle/screenshots/04-updated.png)

The four captures are current 0.8.0 captures from a hidden Windows card-host with synthetic inventory (1200x800): 首页; the three-meal day menu (早/中/晚) with its derived 缺菜清单; the 缺菜清单 showing 还差 941 克 with an editable quantity; and the inventory batch list. The recording is the historical 0.7.0 manual-flow video. More synthetic-data captures: [home](docs/qa/issue-2-home-after.png), [profile editing](docs/qa/issue-2-profile-edit-after.png), [inventory](docs/qa/issue-2-inventory-after.png), [local-host image chooser](docs/qa/issue-2-image-chooser-after.png), [official-host fallback](docs/qa/issue-2-official-fallback-after.png), [recipe](docs/qa/issue-2-recipe-after.png), [consumption review](docs/qa/issue-2-consumption-after.png), the [模拟买菜 region](docs/qa/issue-25-market.png), its [待核对购物车 with 无匹配/可售不足 flags and a simulated total](docs/qa/issue-26-cart.png), the [same-category 替换 list](docs/qa/issue-26-replace.png), and the [submitted 模拟订单 showing 待收货](docs/qa/issue-27-order.png), and the [确认收货 quantity/保质期 check](docs/qa/issue-28-receive.png). The captures illustrate the UI only; they do not prove live image recognition, Store publication, or a live provider response. Recording a new video is outside this PR.

## Windows source launch

This is an app-only repository, not its host or an installer. Use root run.cmd, not the absent apps/pantry-steward/run.cmd path.

Prerequisites: Git, Python 3.11+, Rust, Windows C++ tools and Windows SDK. Follow the [official Quickstart](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/QUICKSTART.md) to prepare the current native workspace. The 0.8.0 camera consent declaration requires the full OctoSense shell; standalone card-host lacks that broker.

The older 0.6.2 publishing workflow pins App Hub 655114c4943cd2490daaefa2173e7b5aaa20669f. The current OctoSense host instead pins App Hub 8347a489141c0e24cab564883db7c4592935a8b2. Use the current host pin to validate this edited bundle.

With the pinned tools built under the sibling OctoSense checkout, run from this app directory using a fresh test profile. The second command uses that checkout's current branch; its host identity depends on whether the checkout is the unmodified official base or the local patch. Keep it running and execute the third in another terminal:

```cmd
run.cmd --hub ..\OctoSense\target\release\hub.exe --check
run.cmd --host-workspace ..\OctoSense --hidden --remote 18442 --app-data target\qa-d2
python -X utf8 tools\smoke.py --port 18442 --profile target\qa-d2
```

`--hub --check` needs no host workspace or keys. Isolated installation in the full shell uses local test keys created with prior consent. The native smoke driver expects a fresh, isolated `--app-data` directory. Restart the same profile and rerun with `--restart` to check persistence.

The launcher checks the existing digest without silently repairing it. The current 0.8.0 candidate was restamped with the pinned App Hub and passed its bundle check. Restamp after any later bundle change.

D2 was installed with a local test signature in an isolated full-shell profile; this is not Store publication. `--prepare-local-test` creates local test keys outside Git and requires human consent. Do not use a person's existing inventory for testing.

Live AI requires the locally modified OctoSense host and a provider configured in its AI providers panel. The unmodified official shell was checked separately for manual fallback; the command above alone does not identify a host as official. The user reported a successful foreground MiniMax image-provider flow. The final sealed pack also requires publisher-github-v1. Local test-signature installation is not formal publication.

## AI, privacy and limitations

- storage saves this app's inventory, profile, plans, history, backups, and selected images.
- model sends goals, the entered profile (including allergies, avoidances, and preferences), and eligible batch names with native units and quantities through the official host to the person's configured provider. Numerical planning also sends gram estimates, nutrition references, and cycle budgets; unquantified recipe planning sends only whether each nutrition reference is complete. Credentials stay with the host. No ai.env or key input.
- Configure the host's own AI providers panel. model.budget success is not provider readiness. On failure, check the host provider settings and retry; no local menu fallback is used. Already-sent calls may incur charges despite stopping the wait.
- Image recognition requests camera/files permission. The Windows local host accepts one app-local JPEG, PNG, or WebP image up to 10 MiB with `MiniMax-M3` on `minimax`/`minimax-cn` or `kimi-k2.5` on `moonshot`; it sends the image and recognition prompt to the configured provider and returns an editable draft. The official host shows a manual-entry fallback. There are no direct network hosts, microphone grant, independent app-agent tools, voice capture, or execution after the host closes.
- Nutrition is a prototype estimate, not medical advice, allergy safety or food-safety assurance. Planning prefers ingredients with complete nutrition references. A day menu is acceptable only when allergies/avoidances are respected, every reference is complete and the three meals together stay within the cycle's remaining daily kcal; insufficient stock is a per-ingredient status (库存够 / 还差 N 克) and does not block acceptance. The 缺菜清单 is derived, not stored: it recomputes from the day menu and available stock (only unexpired, non-avoided batches count), so editing a row edits the day menu's usage and no stale number can survive a restart. An accepted menu becomes executable on its own once the missing batches are added, with no regeneration.

The user reported foreground online recipe and image-recognition checks on this candidate; a complete independently logged provider regression was not captured. See the publisher-confirmed [privacy policy](PRIVACY.md), [support](SUPPORT.md) and [review answers](REVIEW-ANSWERS.md).

## Publishing

Only bundle/ is distributed; tools, video, review packets and local state stay outside it. Git attributes preserve its exact bytes on Windows.

The [App Hub submission guide](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md) describes publication. The 0.8.0 candidate still needs a formal release evidence review, public-link review, and separate human authorization to publish. No publishing workflow, tag, release, new issue, or approval is claimed.

See [SUBMISSION.md](SUBMISSION.md) for pending human checkpoints. A source check or workflow success is not competition qualification or Hub admission.

## License and source

[Apache License 2.0](LICENSE), with [NOTICE](NOTICE). Dependencies and third-party assets retain their own licenses. On 2026-10-08 the author confirmed sunlit-pantry-bg.png is their own original artwork; this declaration is recorded in NOTICE, not independently verified or a Hub approval.

Authors: leoniaodo, zix, power胖丸, Roooy.

[OctoSense](https://github.com/OctoSense-org/OctoSense) · [Design Flow](https://github.com/OctoSense-org/OctoScript-App-Design-Flow) · [App Hub](https://github.com/OctoSense-org/OctoSense-App-Hub)

## Optional one-day flow experience

After profiling, select “先体验 1 天轻食流程”, confirm the plan, confirm inventory entry and finish onboarding. Open 菜单 and generate the three unconfirmed meals. This experience uses existing stock only; the ordinary daily menu keeps main’s derived shortages, mock cart and orders. Missing nutrition references are estimated by online AI with provenance and assumptions.

After each meal, open its actual-intake editor, change foods and native quantities, and explicitly confirm. Only confirmation updates inventory, intake and completion. Recommendations and actuals are independent snapshots; subsequent menus and stages cannot overwrite confirmed history. Three confirmations show a 100% recap and lead to subsequent single or composed health stages. See [EXPERIENCE.md](EXPERIENCE.md) for persistence rules and current schema/native regression commands.
