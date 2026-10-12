"""Task-owned, hidden compatibility preview; uses only synthetic inventory."""
import importlib.util
import argparse
import json
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("smoke", APP / "tools/smoke.py")
smoke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smoke)


class PreviewUI(smoke.UI):
    def state_path(self):
        files = list((self.profile / "pantry-steward").rglob("pantry.json"))
        assert len(files) == 1, files
        return files[0]


parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=18528)
parser.add_argument("--profile", type=Path, required=True, help="task-owned synthetic directory under .local-state/")
parser.add_argument("--restart", action="store_true")
parser.add_argument("--stage-switch", action="store_true",
                    help="boot a profile whose calendar has already reached the next stage")
parser.add_argument("--plan-ended", action="store_true",
                    help="boot a profile whose calendar has passed every stage")
parser.add_argument("--session-switch", action="store_true",
                    help="keep one host open across the civil day and expect the overview to advance itself")
parser.add_argument("--menu-purchase", action="store_true",
                    help="Issue #23/#24 daily menu: three meals, nutrition, over-limit refusal, derived 缺菜清单")
parser.add_argument("--market", action="store_true",
                    help="Issue #25 模拟买菜: 一键补齐 entry, carried 缺菜清单, catalog list/detail, 模拟 labels")
parser.add_argument("--market-cart", action="store_true",
                    help="Issue #26 购物车: auto-fill, pack rounding, flags, 增减/删除/替换, total, persistence")
parser.add_argument("--market-cart-restart", action="store_true",
                    help="Issue #26: the persisted 购物车 survives a restart")
parser.add_argument("--market-order", action="store_true",
                    help="Issue #27 模拟订单: confirm-then-submit, 待收货 status, stock/progress untouched")
parser.add_argument("--market-order-restart", action="store_true",
                    help="Issue #27: the submitted 模拟订单 survives a restart")
parser.add_argument("--market-receive", action="store_true",
                    help="Issue #28 确认收货: check quantities/保质期, new batches, no progress, remaining 缺口")
parser.add_argument("--market-receive-restart", action="store_true",
                    help="Issue #28: received batches and 已收货 status survive a restart")
args = parser.parse_args()
profile = args.profile.resolve()
if not profile.is_relative_to((APP / ".local-state").resolve()) or not profile.name.startswith("qa-"):
    parser.error("use a task-owned qa-* directory under this app's .local-state/")
ui = PreviewUI(args.port, profile)
if args.restart:
    expected = json.loads((ui.profile / "expected-state.json").read_text(encoding="utf-8"))
    ui.check("restart preserves exact synthetic state", ui.state() == expected)
elif args.stage_switch:
    # The fixture advances the clock past the first stage's end, so the current
    # stage must be the second one and the overview must show its targets.
    stages = ui.state()["stages"]
    current = stages[1]
    ui.click("◈  总览")
    ui.scroll(700)
    overview = ui.text()
    ui.check("after its start date the next stage becomes current",
             "当前阶段 · " + current["name"] in overview)
    ui.check("the switch shows the new stage's targets, not the old one's",
             str(current["protein_goal"]) + " g" in overview
             and str(stages[0]["protein_goal"]) + " g" not in overview)
    ui.shot("10-stage-switch.png")
elif args.plan_ended:
    ui.click("◈  总览")
    ui.scroll(700)
    ui.check("an ended plan is not presented as a current stage",
             "这一份计划已结束" in ui.text() and "· 当前" not in ui.text()
             and "选择下一份计划…" in ui.text())
    ui.click("◔  档案")
    ui.check("the archive tab agrees the plan has ended",
             "当前计划 · 已结束" in ui.text() and "所有阶段已结束" in ui.text())
elif args.session_switch:
    # No click after the first frame: the civil day turns over while the
    # Overview stays open, so only the day watchdog can redraw it onto stage 2.
    stages = ui.state()["stages"]
    ui.click("◈  总览")
    ui.scroll(-2000)
    ui.check("the session starts on its first stage",
             "第 1 阶段 · " + stages[0]["name"] + " · 当前" in ui.text())
    ui.shot("11-session-stage-before.png")
    app_now = time.time() + ui.state()["offset"]
    remaining = (int(app_now // 86400) + 1) * 86400 - app_now
    time.sleep(max(0.0, remaining) + 3)
    ui.check("the day turn-over redraws the overview onto the next stage",
             "第 2 阶段 · " + stages[1]["name"] + " · 当前" in ui.text()
             and "第 1 阶段 · " + stages[0]["name"] + " · 当前" not in ui.text())
    ui.shot("11-session-stage-after.png")
elif args.menu_purchase:
    smoke.exercise_menu_purchase(ui)
elif args.market:
    smoke.exercise_market(ui)
elif args.market_cart:
    smoke.exercise_market_cart(ui)
elif args.market_cart_restart:
    smoke.exercise_market_cart_restart(ui)
elif args.market_order:
    smoke.exercise_market_order(ui)
elif args.market_order_restart:
    smoke.exercise_market_order_restart(ui)
elif args.market_receive:
    smoke.exercise_market_receive(ui)
elif args.market_receive_restart:
    smoke.exercise_market_receive_restart(ui)
else:
    ui.check("first-run onboarding rendered", "首次建档  1 / 4" in ui.text())
    ui.shot("01-first-run.png")
    ui.click("选择", index=1)
    ui.click("女性")
    for index, text in enumerate(("30", "170", "65", "", "清淡", "")):
        ui.fill(text, index)
    ui.click("下一步 · 选择周期方案  →")
    programs = ui.state()["programs"]
    ui.check("six cycles with three candidates require confirmation",
             sorted({p["days"] for p in programs}) == [1, 3, 7, 15, 21, 30]
             and len(programs) == 18 and ui.state()["stages"] == [])
    ui.click("15 天")
    ui.check("switching cycles shows that cycle's candidates", "候选方案 · 15 天 · 日常健康" in ui.text())
    ui.click("7 天")
    ui.shot("03-six-cycles.png")
    ui.click("重新生成本周期候选")
    after = ui.state()["programs"]
    ui.check("regeneration replaces only the viewed cycle",
             len([p for p in after if p["days"] == 7]) == 3
             and {(p["id"], p["variant"]) for p in after if p["days"] == 7}
                 != {(p["id"], p["variant"]) for p in programs if p["days"] == 7}
             and {p["id"] for p in after if p["days"] != 7} == {p["id"] for p in programs if p["days"] != 7}
             and ui.state()["stages"] == [])
    ui.shot("04-regenerated.png")
    # Issue #9 acceptance: reorder, remove and replace stay in the draft only.
    ui.click("7 天")
    ui.click("＋ 加入计划")
    ui.click("＋ 加入计划")
    ui.click("上移")
    ui.scroll(-2000)
    ui.check("reorder keeps both stages and their total", "总天数 14 天" in ui.text())
    ui.click("移除")
    ui.scroll(-2000)
    ui.check("remove drops one stage", "总天数 7 天" in ui.text())
    ui.click("替换")
    ui.click("30 天")
    ui.click("用这份替换第 1 阶段")
    ui.scroll(-2000)
    ui.check("replace swaps in another cycle's candidate", "总天数 30 天" in ui.text())
    ui.click("清空草稿")
    # Issue #9: candidates are composed before confirmation, capped at 12 stages.
    for _ in range(12):
        ui.click("＋ 加入计划")
    ui.check("twelve-stage cap is an explicit visible prompt",
             "已达 12 阶段上限" in ui.text())
    ui.click("清空草稿")
    ui.check("clearing the draft leaves candidates unconfirmed", ui.state()["stages"] == [])
    ui.click("7 天")
    ui.click("＋ 加入计划")
    ui.click("15 天")
    ui.click("＋ 加入计划")
    ui.click("30 天")
    ui.click("＋ 加入计划")
    ui.scroll(700)
    ui.check("compose page sums stage cycles", "总天数 52 天" in ui.text())
    ui.shot("05-compose.png")
    ui.click("确认计划 · 去录冰箱  →")
    stages = ui.state()["stages"]
    ui.check("confirmation snapshots ordered stages with meeting dates",
             len(stages) == 3 and [s["days"] for s in stages] == [7, 15, 30]
             and stages[1]["started"] - stages[0]["started"] == 7 * 86400
             and stages[2]["started"] - stages[1]["started"] == 15 * 86400
             and stages[0]["kcal_goal"] > 0 and stages[0]["consumed_kcal"] == 0)
    smoke.enter(ui, "食材名称", "菠菜")
    smoke.enter(ui, "数量", "200")
    smoke.enter(ui, "还剩几天（可留空）", "3")
    ui.click("预览并确认  →")
    ui.check("inventory preview has not committed", ui.state()["foods"] == [])
    ui.click("最终确认入库")
    ui.check("explicit inventory commit persists", len(ui.state()["foods"]) == 1)
    ui.check("manual default does not silently generate", ui.state()["auto_generate"] is False and ui.state()["plans"] == [])
    ui.shot("02-confirmed-inventory.png")
    (ui.profile / "expected-state.json").write_text(json.dumps(ui.state(), ensure_ascii=False), encoding="utf-8")
    (ui.profile / "checks.json").write_text(json.dumps(ui.checks), encoding="utf-8")
    # Issue #11 stage switch: simulate the calendar passing the first stage so a
    # second host boot can assert the overview shows the new stage's targets.
    advanced = json.loads(json.dumps(ui.state()))
    advanced["offset"] = advanced["offset"] + 8 * 86400
    advanced["cycle_start"] = int(time.time()) + advanced["offset"]
    advanced["reminders"] = False
    advanced["daily_target"] = advanced["stages"][1]["daily_kcal"]
    stage_profile = ui.profile.parent / (ui.profile.name + "-stage")
    (stage_profile / "pantry-steward").mkdir(parents=True, exist_ok=True)
    (stage_profile / "pantry-steward/pantry.json").write_text(json.dumps(advanced, ensure_ascii=False), encoding="utf-8")
    (stage_profile / "expected-state.json").write_text(json.dumps(advanced, ensure_ascii=False), encoding="utf-8")
    # Issue #11 ended plan: the calendar has passed the whole plan, so no stage is
    # current and the page must say so instead of showing a stale stage.
    ended = json.loads(json.dumps(advanced))
    ended["offset"] = ended["offset"] + 30 * 86400
    ended["cycle_start"] = int(time.time()) + ended["offset"]
    ended_profile = ui.profile.parent / (ui.profile.name + "-ended")
    (ended_profile / "pantry-steward").mkdir(parents=True, exist_ok=True)
    (ended_profile / "pantry-steward/pantry.json").write_text(json.dumps(ended, ensure_ascii=False), encoding="utf-8")
    (ended_profile / "expected-state.json").write_text(json.dumps(ended, ensure_ascii=False), encoding="utf-8")
    # Issue #11 same-session day turn-over: stage 1 ends at the civil midnight
    # about a minute after this fixture is written, so the Overview must advance
    # itself while it stays open, with no click and no restart.
    session = json.loads(json.dumps(ui.state()))
    now = int(time.time())
    offset = (86400 - (now % 86400)) - 60
    if offset < 0:
        offset = offset + 86400
    app_day = (now + offset) // 86400
    template = session["stages"][0]

    def session_stage(identifier, name, days, started):
        stage = json.loads(json.dumps(template))
        stage.update({"id": identifier, "name": name, "days": days, "started": started,
                      "kcal_goal": template["daily_kcal"] * days,
                      "protein_goal": template["protein_goal"] // template["days"] * days,
                      "fiber_goal": template["fiber_goal"] // template["days"] * days,
                      "vitamin_c_goal": template["vitamin_c_goal"] // template["days"] * days,
                      "consumed_kcal": 0, "consumed_protein": 0, "consumed_fiber": 0,
                      "consumed_vitamin_c": 0, "intake": []})
        return stage

    session["stages"] = [session_stage(900, "1天起步 · 会话", 1, app_day * 86400),
                         session_stage(901, "7天起步 · 会话", 7, (app_day + 1) * 86400)]
    session["stage_next"] = 902
    session["offset"] = offset
    session["cycle_start"] = now + offset
    session["health"]["day"] = app_day
    session["health"]["meals_today"] = 0
    session["reminders"] = False
    session["daily_target"] = session["stages"][0]["daily_kcal"]
    session_profile = ui.profile.parent / (ui.profile.name + "-session")
    (session_profile / "pantry-steward").mkdir(parents=True, exist_ok=True)
    (session_profile / "pantry-steward/pantry.json").write_text(json.dumps(session, ensure_ascii=False), encoding="utf-8")
    (session_profile / "expected-state.json").write_text(json.dumps(session, ensure_ascii=False), encoding="utf-8")
