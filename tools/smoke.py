"""Exercise the task-owned official shell with synthetic data, never real keys."""
import argparse
import json
from pathlib import Path
import time
import urllib.parse
import urllib.request

APP = Path(__file__).resolve().parents[1]


class UI:
    def __init__(self, port, profile):
        self.base = f"http://127.0.0.1:{port}/"
        self.profile = profile
        self.checks = []

    def get(self, route, **params):
        with urllib.request.urlopen(self.base + route + "?" + urllib.parse.urlencode(params), timeout=15) as response:
            return json.loads(response.read())

    def snap(self):
        return [w for w in self.get("snap")["s"] if w["ty"] not in ("Splash", "Window", "KeyboardView")]

    def click(self, text=None, name=None, index=0):
        for _ in range(9):
            candidates = [w for w in self.snap() if (w.get("t") == text if text else w.get("i") == name)
                          and w.get("enabled", True) and w["r"][2] > 0 and w["r"][3] > 0]
            if len(candidates) <= index:
                card = next(w for w in self.get("snap")["s"] if w.get("i") == "card" and w["ty"] == "Splash")
                left, top, cw, ch = card["r"]
                self.get("m", k="scroll", x=left + cw * 0.6, y=top + ch * 0.6, dy=240, wait=1)
                continue
            widget = candidates[index]
            x, y, width, height = widget["r"]
            card = next(w for w in self.get("snap")["s"] if w.get("i") == "card" and w["ty"] == "Splash")
            left, top, cw, ch = card["r"]
            if top <= y + height / 2 < top + ch:
                self.get("click", x=x + width / 2, y=y + height / 2, wait=1)
                time.sleep(0.15)
                return
            self.get("m", k="scroll", x=left + cw * 0.6, y=top + ch * 0.6, dy=240, wait=1)
        raise AssertionError(f"cannot reach {text or name}")

    def fill(self, text, index=0, name=None):
        inputs = [w for w in self.snap() if w["ty"] == "TextInput" and w["r"][2] > 0]
        field = next(w for w in inputs if w.get("i") == name) if name else inputs[index]
        x, y, width, height = field["r"]
        self.get("click", x=x + width / 2, y=y + height / 2, wait=1)
        self.get("k", k="down", c="KeyA", ctrl=1, wait=1)
        self.get("k", k="up", c="KeyA", ctrl=1, wait=1)
        self.get("t", t=text, wait=1)

    def state_path(self):
        files = list((self.profile / "apps/pantry-steward").rglob("pantry.json"))
        assert len(files) == 1, files
        return files[0]

    def state(self):
        return json.loads(self.state_path().read_text(encoding="utf-8"))

    def check(self, name, condition):
        if not condition:
            self.shot("failure.png")
            raise AssertionError(name)
        print("PASS " + name, flush=True)
        self.checks.append(name)

    def shot(self, name):
        path = self.profile / name
        with urllib.request.urlopen(self.base + "g?raw=1", timeout=15) as response:
            data = response.read()
        assert data.startswith(b"\x89PNG\r\n\x1a\n")
        path.write_bytes(data)

    def text(self):
        return "\n".join(w.get("t", "") for w in self.snap())


def exercise(ui):
    ui.check("官方宿主显示首次建档", "首次建档" in ui.text())
    if "首次建档  1 / 3" in ui.text():
        ui.click("选择", index=1)
    if "首次建档  1 / 4" in ui.text():
        ui.click("选择", index=1)
        ui.click("女性")
        for index, text in enumerate(("30", "170", "65", "", "清淡", "无")):
            ui.fill(text, index)
        ui.click("下一步 · 选择周期方案  →")
        programs = ui.state()["programs"]
        ui.check("六周期各3份候选且未自动启用",
                 sorted({p["days"] for p in programs}) == [1, 3, 7, 15, 21, 30]
                 and all(sum(1 for p in programs if p["days"] == days) == 3 for days in (1, 3, 7, 15, 21, 30))
                 and len({(p["days"], p["variant"]) for p in programs}) == 18
                 and ui.state()["program_active"] == 0)
        ui.check("每份候选都有目标、特点、差异与指标",
                 all(p["goal"] and p["trait"] and p["difference"] and p["kcal_goal"] > 0 for p in programs))
        on_cycle_before = {p["id"] for p in programs if p["days"] != 7}
        seven_before = {(p["id"], p["variant"]) for p in programs if p["days"] == 7}
        ui.click("15 天")
        ui.check("切换周期只展示该周期候选", "候选方案 · 15 天 · 日常健康" in ui.text())
        ui.click("7 天")
        ui.click("重新生成本周期候选")
        after = ui.state()["programs"]
        ui.check("重新生成只替换当前周期候选",
                 len([p for p in after if p["days"] == 7]) == 3
                 and {(p["id"], p["variant"]) for p in after if p["days"] == 7} != seven_before
                 and {p["id"] for p in after if p["days"] != 7} == on_cycle_before
                 and ui.state()["program_active"] == 0)
        ui.click("确认选中方案 · 去录冰箱  →")
    else:
        for index, text in enumerate(("30", "170", "65", "清淡", "无")):
            ui.fill(text, index)
        ui.click("下一步 · 建立冰箱档案  →")
    ui.check("档案保存并进入入库页", ui.state()["profile"]["scene"] == "日常健康")
    ui.fill("豆腐", name="food_name")
    ui.fill("abc", name="food_grams")
    ui.fill("2", name="food_days")
    ui.click("预览并确认入库  →")
    ui.check("非法数量不写库存", not ui.state()["foods"])
    ui.fill("250", name="food_grams")
    ui.click("预览并确认入库  →")
    ui.check("预览不写库存", not ui.state()["foods"])
    ui.click("确认入库")
    ui.check("确认才写库存", ui.state()["foods"][0]["grams"] == 250)
    ui.click("完成建档 · 开始托管  →")
    ui.check("首页完整显示", "今天想吃点什么？" in ui.text() and ui.state()["profile"]["done"])
    ui.click(name="voice_button")
    ui.check("麦克风明确说明不支持，不启动录音", "语音识别服务" in ui.text())
    ui.click("⚙  设置")
    ui.check("预算不冒充模型已配置", "宿主服务可用" in ui.text() and "在线 AI 已配置" not in ui.text())
    ui.click("改用本地规则")
    ui.check("本地规则开关持久化", ui.state()["model_enabled"] is False)
    ui.check("默认关闭自动生成且建档未生成方案", ui.state()["auto_generate"] is False and not ui.state()["plans"])
    ui.click("▣  冰箱")
    ui.click("编辑", index=0)
    saved = ui.state_path().read_bytes()
    ui.click("取消修改")
    ui.check("取消编辑不改库存或生成方案", ui.state_path().read_bytes() == saved)
    ui.click("编辑", index=0)
    ui.fill("300", name="food_grams")
    ui.click("预览并确认  →")
    ui.click("确认入库")
    ui.check("编辑确认仅更新库存不生成", ui.state()["foods"][0]["grams"] == 300 and not ui.state()["plans"])
    ui.click("编辑", index=0)
    ui.click("移除这批…")
    ui.click("确认移除")
    ui.check("移除库存不自动生成", not ui.state()["foods"] and not ui.state()["plans"])
    ui.click("⚙  设置")
    ui.click("载入演示数据…")
    before = ui.state_path().read_bytes()
    ui.check("演示替换需要确认", "确认替换并开始演示" in ui.text())
    ui.click("确认替换并开始演示")
    ui.check("演示库存建立且正式菜单保留", ui.state()["active"] == 5 and len(ui.state()["foods"]) == 4)
    ui.shot("01-main.png")
    ui.click("⚙  设置")
    ui.click("时间 +12 小时")
    ui.check("默认临期只提醒，不生成或跳转方案", len(ui.state()["plans"]) == 1 and ui.state()["active"] == 5 and "不会自动创建方案" in ui.text())
    ui.click("⌂  首页")
    ui.click("生成这一餐  →")
    ui.check("手动生成才创建候选且不替换今晚方案", len(ui.state()["plans"]) == 2 and ui.state()["active"] == 5)
    ui.click("▣  冰箱")
    ui.click("编辑", index=2)
    ui.fill("300", name="food_grams")
    ui.click("预览并确认  →")
    ui.click("确认入库")
    ui.check("库存变化使旧候选失效但不创建新方案", len(ui.state()["plans"]) == 2)
    ui.click("✦  方案")
    ui.check("失效方案有明确提示及手动入口", "方案已失效 · 请重新生成" in ui.text() and "回首页重新生成" in ui.text())
    ui.click("回首页重新生成")
    ui.check("回首页入口本身不生成", len(ui.state()["plans"]) == 2)
    ui.click("生成这一餐  →")
    ui.shot("02-plan.png")
    ui.click("就吃这套 · 设为今晚方案  →")
    ui.check("用户接受候选成为正式菜单", ui.state()["active"] != 5)
    ui.click("我吃完了 · 核对实际用量")
    before = ui.state_path().read_bytes()
    ui.fill("999999", 1)
    ui.click(name="confirm_consumption")
    ui.check("超库存扣减被拒绝", ui.state_path().read_bytes() == before and "不能超出库存" in ui.text())
    ui.click("取消")
    ui.check("取消不改库存", ui.state_path().read_bytes() == before)
    ui.click("我吃完了 · 核对实际用量")
    ui.shot("03-confirm.png")
    prior = sum(f["grams"] for f in ui.state()["foods"])
    plan_count = len(ui.state()["plans"])
    ui.click(name="confirm_consumption")
    ui.check("确认扣减并记录用餐", sum(f["grams"] for f in ui.state()["foods"]) < prior and ui.state()["meal_count"] == 2)
    ui.check("确认吃完不自动创建下一餐", len(ui.state()["plans"]) == plan_count)
    ui.click("▣  冰箱")
    ui.shot("04-updated.png")
    ui.click("⌂  首页")
    ui.click("生成这一餐  →")
    deletion_checks(ui)
    automatic_checks(ui)
    ui.click("⚙  设置")
    ui.click("重新设置用户画像")
    ui.check("可返回资料页且库存保留", "首次建档" in ui.text() and len(ui.state()["foods"]) == 4)
    (ui.profile / "expected-state.json").write_text(json.dumps(ui.state(), ensure_ascii=False), encoding="utf-8")
    (ui.profile / "checks.json").write_text(json.dumps(ui.checks, ensure_ascii=False), encoding="utf-8")
    ui.shot("return-profile.png")


def deletion_checks(ui):
    def preserved(value):
        fields = ("foods", "revision", "consumed_kcal", "meal_count", "last_meal", "last_goal", "handled")
        return {key: value[key] for key in fields}

    ui.click("✦  方案")
    before = ui.state()
    protected = preserved(before)
    target = before["plans"][-1]["id"]
    saved = ui.state_path().read_bytes()
    ui.click("删除这个方案…")
    ui.check("删除前展示确认且不改存储", "确认删除这个方案？" in ui.text() and ui.state_path().read_bytes() == saved)
    ui.click("取消删除")
    ui.check("取消删除保留全部方案和数据", ui.state_path().read_bytes() == saved)
    ui.click("删除这个方案…")
    ui.click("确认删除方案")
    after = ui.state()
    ui.check("仅删除选中的候选且不改库存档案", [p["id"] for p in after["plans"]] == [p["id"] for p in before["plans"] if p["id"] != target] and preserved(after) == protected)
    ui.shot("delete-candidate.png")
    completed = next(p for p in after["plans"] if p["consumed"])
    while completed["title"] not in ui.text():
        ui.click("‹ 上一个")
    ui.click("删除这个方案…")
    ui.click("确认删除方案")
    ui.check("删除已完成方案不回滚库存和用餐记录", not any(p["id"] == completed["id"] for p in ui.state()["plans"]) and preserved(ui.state()) == protected)
    ui.click("⚙  设置")
    ui.click("载入演示数据…")
    ui.click("确认替换并开始演示")
    before = ui.state()
    protected = preserved(before)
    ui.click("✦  方案")
    ui.click("删除这个方案…")
    ui.check("删除今晚方案时明确警告", "这是当前今晚方案" in ui.text() and ui.state()["active"] == before["active"])
    ui.click("确认删除方案")
    after = ui.state()
    ui.check("删除最后的今晚方案清除选中且不改库存档案", after["active"] == 0 and after["plans"] == [] and preserved(after) == protected and "还没有候选方案" in ui.text())
    ui.shot("delete-empty.png")


def automatic_checks(ui):
    ui.click("⚙  设置")
    ui.click("载入演示数据…")
    ui.click("确认替换并开始演示")
    ui.click("⚙  设置")
    ui.click("开启自动生成（可选）")
    ui.check("可选自动开关保存且切换不生成", ui.state()["auto_generate"] is True and len(ui.state()["plans"]) == 1)
    ui.click("时间 +12 小时")
    ui.check("开启后临期可生成候选不替换菜单", len(ui.state()["plans"]) == 2 and ui.state()["active"] == 5)
    ui.click("▣  冰箱")
    ui.click("编辑", index=2)
    ui.fill("300", name="food_grams")
    ui.click("预览并确认  →")
    ui.click("确认入库")
    ui.check("开启后编辑确认可生成候选", len(ui.state()["plans"]) == 3 and ui.state()["active"] == 5)
    ui.click("⚙  设置")
    plan_count = len(ui.state()["plans"])
    ui.click("关闭自动生成")
    ui.check("关闭自动开关保存且不生成", ui.state()["auto_generate"] is False and len(ui.state()["plans"]) == plan_count)
    ui.shot("manual-setting.png")


def legacy_checks(ui):
    before = ui.state()
    ui.check("旧数据未预置开关且加载为手动", "auto_generate" not in before and "手动生成" in ui.text())
    ui.click("⚙  设置")
    ui.click("开启自动生成（可选）")
    ui.click("关闭自动生成")
    after = ui.state()
    ui.check("旧数据迁移保留库存方案和用餐数据", after["auto_generate"] is False and all(after[key] == value for key, value in before.items() if key != "log"))
    ui.click("恢复演示前数据")
    ui.check("恢复旧备份也默认手动且保留数据", ui.state() == dict(before, auto_generate=False))
    ui.click("开启自动生成（可选）")
    ui.click("✦  方案")
    ui.click("我吃完了 · 核对实际用量")
    ui.click(name="confirm_consumption")
    ui.check("可选自动模式吃完生成下一餐但不接受", len(ui.state()["plans"]) == 2 and ui.state()["meal_count"] == before["meal_count"] + 1 and ui.state()["active"] == 0)
    ui.click("▣  冰箱")
    ui.fill("菠菜", name="food_name")
    ui.fill("200", name="food_grams")
    ui.fill("3", name="food_days")
    ui.click("预览并确认  →")
    ui.click("确认入库")
    ui.check("可选自动模式入库生成候选", len(ui.state()["plans"]) == 3)
    ui.click("编辑", index=0)
    ui.click("移除这批…")
    ui.click("确认移除")
    ui.check("可选自动模式移除后按剩余库存生成", len(ui.state()["plans"]) == 4 and len(ui.state()["foods"]) == 1)
    ui.click("⚙  设置")
    ui.click("关闭自动生成")
    ui.click("▣  冰箱")
    ui.fill("豆腐", name="food_name")
    ui.fill("200", name="food_grams")
    ui.fill("3", name="food_days")
    ui.click("预览并确认  →")
    ui.click("确认入库")
    ui.check("关闭可选自动模式后入库再次不生成", len(ui.state()["plans"]) == 4 and ui.state()["auto_generate"] is False)
    ui.click("✦  方案")
    ui.shot("invalid-plan.png")
    ui.click("+ 再给我一个备选")
    ui.check("手动备选按钮仍可生成", len(ui.state()["plans"]) == 5)
    (ui.profile / "checks.json").write_text(json.dumps(ui.checks, ensure_ascii=False), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=18442)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--restart", action="store_true")
    parser.add_argument("--legacy", action="store_true", help="独立 profile 需预置合成旧数据与 before-demo.json")
    args = parser.parse_args()
    ui = UI(args.port, args.profile.resolve())
    if args.legacy:
        legacy_checks(ui)
    elif args.restart:
        expected = json.loads((ui.profile / "expected-state.json").read_text(encoding="utf-8"))
        ui.check("重启保留档案、库存、菜单与选项", ui.state() == expected)
    else:
        exercise(ui)


if __name__ == "__main__":
    main()
