"""Task-owned, hidden compatibility preview; uses only synthetic inventory."""
import importlib.util
import argparse
import json
from pathlib import Path
import time

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
    ui.fill("菠菜", name="food_name")
    ui.fill("200", name="food_grams")
    ui.fill("3", name="food_days")
    ui.click("预览并确认入库  →")
    ui.check("inventory preview has not committed", ui.state()["foods"] == [])
    ui.click("确认入库")
    ui.check("explicit inventory commit persists", len(ui.state()["foods"]) == 1)
    ui.check("manual default does not silently generate", ui.state()["auto_generate"] is False and ui.state()["plans"] == [])
    ui.shot("02-confirmed-inventory.png")
    ui.click("完成建档 · 开始托管  →")
    # ---- Issue #10: started stages lock; only the future suffix can be edited.
    # The plan is 7 + 15 + 30 days, so stages 2 and 3 have not started yet.
    ui.click("◔  档案")
    ui.scroll(240)
    ui.check("started stage locks by calendar with a readable reason",
             "阶段起始日期已到但还没有确认用餐记录；按日历锁定，不是故障。" in ui.text()
             and "尚未开始 · 替换、移除或改目标不受限" in ui.text())
    ui.shot("06-stage-lock.png")
    locked = ui.state()["stages"][0]
    first_locked = json.dumps(locked, ensure_ascii=False)
    ui.scroll(240)
    ui.click("上移")  # the only enabled move target is the last future stage
    ui.check("reorder touches only the not-yet-started stages",
             [s["days"] for s in ui.state()["stages"]] == [7, 30, 15]
             and json.dumps(ui.state()["stages"][0], ensure_ascii=False) == first_locked
             and ui.state()["stages"][1]["started"] - locked["started"] == 7 * 86400)
    ui.check("reorder names the future goals it moved",
             "受影响的未来目标" in ui.text())
    ui.click("改目标")  # first enabled retarget control = the 30-day stage
    ui.click("1 天")
    ui.click("改为这份目标")
    edited = ui.state()["stages"]
    ui.check("retargeting a future stage snapshots the new candidate",
             [s["days"] for s in edited] == [7, 1, 15]
             and edited[2]["started"] - edited[1]["started"] == 1 * 86400
             and json.dumps(edited[0], ensure_ascii=False) == first_locked)
    # A confirmed meal lands on the started stage, then a later edit must keep it.
    ui.click("⌂  首页")
    ui.click("生成这一餐  →")
    ui.click("就吃这套 · 设为今晚方案  →")
    ui.click("我吃完了 · 核对实际用量")
    ui.click(name="confirm_consumption")
    recorded = ui.state()["stages"][0]
    ui.check("the started stage records the confirmed meal",
             recorded["consumed_kcal"] > 0 and len(recorded["intake"]) == 1)
    ui.click("◔  档案")
    ui.scroll(240)
    ui.scroll(240)
    ui.click("移除")  # drop the first editable future stage (1 day)
    after = ui.state()["stages"]
    ui.check("editing a future stage preserves obtained progress and intake",
             json.dumps(after[0], ensure_ascii=False) == json.dumps(recorded, ensure_ascii=False)
             and after[0]["intake"][0]["kcal"] == recorded["intake"][0]["kcal"])
    ui.scroll(240)
    ui.check("plan totals are recalculated after the edit",
             "总天数 22 天" in ui.text() and "已确认 1 / " in ui.text())
    ui.shot("07-future-edited.png")
    # ---- Issue #11: the overview page, long-term plan and progress.
    stages = ui.state()["stages"]
    ui.click("◈  总览")
    ui.scroll(-2000)
    ui.check("overview shows the long-term plan and every stage",
             "长期计划" in ui.text() and stages[0]["name"] in ui.text()
             and stages[1]["name"] in ui.text())
    ui.check("plan progress counts confirmed meals over days x 3 meals",
             "计划进度 1% · 已确认 1 / 66 餐" in ui.text()
             and "进度 4%" in ui.text() and "0 / 45 餐" in ui.text())
    ui.scroll(700)
    ui.check("today shows per-meal progress out of three",
             "每餐进度 · 已确认 1 / 3 餐" in ui.text())
    ui.check("the current stage compares kcal and protein targets with actuals",
             "当前阶段 · " + stages[0]["name"] in ui.text()
             and "热量" in ui.text() and str(stages[0]["kcal_goal"]) + " kcal" in ui.text()
             and "蛋白质" in ui.text() and str(stages[0]["protein_goal"]) + " g" in ui.text())
    ui.shot("08-overview.png")
    # Generating and confirming a menu must not move progress; only a confirmed
    # meal does.
    ui.click("⌂  首页")
    ui.click("生成这一餐  →")
    ui.click("就吃这套 · 设为今晚方案  →")
    ui.click("◈  总览")
    ui.scroll(-2000)
    ui.check("generating and confirming a menu leaves progress unchanged",
             "计划进度 1% · 已确认 1 / 66 餐" in ui.text()
             and len(ui.state()["stages"][0]["intake"]) == 1)
    ui.click("✦  方案")
    ui.click("我吃完了 · 核对实际用量")
    ui.click(name="confirm_consumption")
    ui.click("◈  总览")
    ui.scroll(-2000)
    ui.check("confirming a meal increases per-stage and plan progress",
             "计划进度 3% · 已确认 2 / 66 餐" in ui.text()
             and "进度 9%" in ui.text()
             and len(ui.state()["stages"][0]["intake"]) == 2)
    ui.scroll(700)
    ui.check("today per-meal progress advances to two of three",
             "每餐进度 · 已确认 2 / 3 餐" in ui.text())
    ui.shot("09-progress.png")
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
