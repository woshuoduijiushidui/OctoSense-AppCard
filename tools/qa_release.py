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
args = parser.parse_args()
profile = args.profile.resolve()
if not profile.is_relative_to((APP / ".local-state").resolve()) or not profile.name.startswith("qa-"):
    parser.error("use a task-owned qa-* directory under this app's .local-state/")
ui = PreviewUI(args.port, profile)
if args.restart:
    expected = json.loads((ui.profile / "expected-state.json").read_text(encoding="utf-8"))
    ui.check("restart preserves exact synthetic state", ui.state() == expected)
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
    ui.scroll(700)
    ui.check("compose page sums stage cycles", "总天数 22 天" in ui.text())
    ui.shot("05-compose.png")
    ui.click("确认计划 · 去录冰箱  →")
    stages = ui.state()["stages"]
    ui.check("confirmation snapshots ordered stages with meeting dates",
             len(stages) == 2 and stages[0]["days"] == 7 and stages[1]["days"] == 15
             and stages[1]["started"] - stages[0]["started"] == 7 * 86400
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
    (ui.profile / "expected-state.json").write_text(json.dumps(ui.state(), ensure_ascii=False), encoding="utf-8")
    (ui.profile / "checks.json").write_text(json.dumps(ui.checks), encoding="utf-8")
