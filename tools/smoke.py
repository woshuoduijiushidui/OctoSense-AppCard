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
        direct = self.profile / "pantry-steward" / "pantry.json"
        if direct.exists():
            return direct
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


def enter(ui, placeholder, value):
    ui.click(placeholder)
    ui.get("k", k="down", c="KeyA", ctrl=1, wait=1)
    ui.get("k", k="up", c="KeyA", ctrl=1, wait=1)
    ui.get("t", t=value, wait=1)


def add(ui, name, quantity, unit="g", days=None, printed_date=None, package=None):
    before = list(ui.state()["foods"])
    ui.get("m", k="scroll", x=450, y=450, dy=-2500, wait=1)
    enter(ui, "食材名称", name)
    enter(ui, "数量", quantity)
    if unit != "g":
        ui.click(unit)
    if days is not None:
        enter(ui, "还剩几天（可留空）", days)
    if printed_date is not None:
        enter(ui, "印刷日期 YYYY-MM-DD", printed_date)
    if package is not None:
        enter(ui, "每包装数量（可留空）", package)
        ui.click("g", index=1)
    ui.click("预览并确认  →")
    ui.check("预览未写入库存", ui.state()["foods"] == before)
    ui.click("最终确认入库")


def exercise(ui):
    ui.check("首次建档显示", "首次建档  1 / 4" in ui.text())
    ui.click("选择", index=1)
    ui.click("女性")
    for label, value in (("年龄", "30"), ("身高 cm", "170"), ("体重 kg", "65"),
                         ("例如：牛奶、花生", "花生"), ("例如：清淡、家常、少油", "清淡")):
        enter(ui, label, value)
    ui.click("下一步 · 选择周期方案  →")
    ui.check("周期候选未自动启用", [p["days"] for p in ui.state()["programs"]] == [7, 21, 30]
             and ui.state()["program_active"] == 0)
    ui.click("确认选中方案 · 去录冰箱  →")
    for entry in ("拍照识别", "导入小票"):
        ui.click(entry)
        ui.check(entry + " 官方宿主回退手动录入",
                 "当前宿主暂不支持图片识别，请使用手动录入" in ui.text()
                 and "选择已有图片" not in ui.text())
    enter(ui, "食材名称", "豆腐")
    enter(ui, "数量", "abc")
    enter(ui, "还剩几天（可留空）", "2")
    ui.click("预览并确认  →")
    ui.click("最终确认入库")
    ui.check("非法数量原子拒绝", ui.state()["foods"] == [])
    ui.get("m", k="scroll", x=450, y=450, dy=-2500, wait=1)
    ui.fill("250", index=1)
    ui.click("最终确认入库")
    ui.check("首次确认落盘", ui.state()["foods"][0]["quantity"] == 250 and
             ui.state()["inventory_events"][0]["type"] == "add")
    ui.click("完成建档 · 开始托管  →")
    ui.check("建档完成", ui.state()["profile"]["done"])
    ui.click("▣  冰箱")
    add(ui, "豆腐", "100")
    ui.check("同名批次分别保存", [f["quantity"] for f in ui.state()["foods"] if f["name"] == "豆腐"] == [250, 100])
    add(ui, "牛奶", "500", "ml", days="20")
    add(ui, "鸡蛋", "3", "个", printed_date="2020-01-01")
    add(ui, "豆浆", "2", "盒", package="300")
    foods = ui.state()["foods"]
    ui.check("单位、包装和四种有效期落盘", foods[-1]["canonical_quantity"] == 600
             and foods[-1]["canonical_unit"] == "g"
             and {f["expiry_precision"] for f in foods} == {"estimated", "unknown", "exact"}
             and "豆腐 · 2 批" in ui.text() and "正常" in ui.text() and "已过期" in ui.text()
             and "临期" in ui.text() and "保质期未知" in ui.text())
    ui.click("展开 / 收起", index=0)
    ui.click("编辑", index=0)
    ui.get("m", k="scroll", x=450, y=450, dy=-2500, wait=1)
    ui.fill("220", index=1)
    ui.click("预览并确认  →")
    ui.click("最终确认入库")
    ui.check("编辑只更新原批次", ui.state()["foods"][0]["id"] == 1 and
             ui.state()["foods"][0]["quantity"] == 220)
    ui.click("丢弃/移除", index=1)
    saved_foods = list(ui.state()["foods"])
    ui.click("确认移除")
    ui.check("丢弃需确认且不计用餐", len(ui.state()["foods"]) == len(saved_foods) - 1 and
             ui.state()["meal_count"] == 0)
    ui.click("⚙  设置")
    ui.get("m", k="scroll", x=750, y=600, dy=650, wait=1)
    ui.click("改用本地规则")
    ui.check("本地规则选择持久化", ui.state()["model_enabled"] is False)
    ui.get("m", k="scroll", x=750, y=600, dy=-650, wait=1)
    plan_count = len(ui.state()["plans"])
    ui.click("开启自动生成（可选）")
    ui.check("开启自动生成只改设置", ui.state()["auto_generate"] is True and
             len(ui.state()["plans"]) == plan_count)
    ui.click("关闭自动生成")
    ui.check("关闭自动生成只改设置", ui.state()["auto_generate"] is False and
             len(ui.state()["plans"]) == plan_count)
    ui.click("⌂  首页")
    ui.click("生成今日菜单  →")
    ui.check("手动生成日菜单", len(ui.state()["plans"]) == 1 and not ui.state()["plans"][0]["accepted"]
             and len(ui.state()["plans"][0]["meals"]) == 3)
    ui.click("接受今日菜单  →")
    ui.check("接受菜单", ui.state()["active"] == ui.state()["plans"][0]["id"])
    ui.click("我吃完了 · 核对实际用量")
    before = ui.state_path().read_bytes()
    ui.click("取消")
    ui.check("取消用餐不改存储", ui.state_path().read_bytes() == before)
    ui.click("我吃完了 · 核对实际用量")
    ui.click("确认吃完 · 扣减库存并写入档案")
    ui.check("确认用餐扣库存并写档案", ui.state()["meal_count"] == 1 and
             ui.state()["plans"][0]["consumed"] and
             ui.state()["foods"][0]["quantity"] < 220)
    ui.click("+ 再给我一个备选")
    preserved = ui.state()["foods"]
    ui.click("删除这份菜单…")
    ui.click("确认删除菜单")
    ui.check("删除候选不回滚库存", len(ui.state()["plans"]) == 1 and ui.state()["foods"] == preserved)
    ui.click("⚙  设置")
    saved_profile = ui.state_path().read_bytes()
    ui.click("重新设置用户画像")
    ui.check("画像修改可取消且尚未落盘", "取消修改 · 返回设置" in ui.text()
             and ui.state_path().read_bytes() == saved_profile)
    ui.click("取消修改 · 返回设置")
    ui.check("取消画像修改恢复原档案", ui.state_path().read_bytes() == saved_profile
             and "管家设置" in ui.text())
    ui.click("重新设置用户画像")
    ui.click("已选中")
    enter(ui, "清淡", "少油")
    ui.click("下一步 · 选择周期方案  →")
    ui.check("画像编辑保持库存且等待确认", ui.state_path().read_bytes() == saved_profile
             and len(ui.state()["foods"]) == len(preserved))
    ui.click("保存画像与周期方案  →")
    ui.check("画像确认后旧菜单失效且保留库存", ui.state()["profile"]["preferences"] == "少油"
             and ui.state()["profile"]["done"] and ui.state()["active"] == 0
             and len(ui.state()["foods"]) == len(preserved))
    (ui.profile / "expected-state.json").write_text(
        json.dumps(ui.state(), ensure_ascii=False), encoding="utf-8")
    (ui.profile / "checks.json").write_text(
        json.dumps(ui.checks, ensure_ascii=False), encoding="utf-8")


def exercise_recipe(ui):
    ui.click("选择", index=1)
    ui.click("女性")
    for label, value in (("年龄", "30"), ("身高 cm", "170"), ("体重 kg", "65")):
        enter(ui, label, value)
    ui.click("下一步 · 选择周期方案  →")
    ui.click("确认选中方案 · 去录冰箱  →")
    enter(ui, "食材名称", "番茄")
    enter(ui, "数量", "3")
    ui.click("个")
    ui.click("预览并确认  →")
    ui.click("最终确认入库")
    ui.click("完成建档 · 开始托管  →")
    ui.click("⚙  设置")
    ui.get("m", k="scroll", x=750, y=600, dy=650, wait=1)
    ui.click("改用本地规则")
    ui.click("⌂  首页")
    ui.click("生成今日菜单  →")
    plan = ui.state()["plans"][0]
    ui.check("无营养参考仍生成三餐形状但不能接受", plan["numeric"] is False and
             len(plan["meals"]) == 3 and plan["uses"][0]["unit"] == "piece" and
             plan["uses"][0]["grams"] == 0 and "暂时不能接受" in ui.text()
             and "接受今日菜单  →" not in ui.text())


def exercise_menu_purchase(ui):
    """Issue #23: one generation gives 早/中/晚 three meals, each with grams and a
    nutrition reference, and an edit that breaks the day's remaining budget is
    refused with a reason. Synthetic inventory only."""
    ui.click("选择", index=1)
    ui.click("女性")
    for label, value in (("年龄", "30"), ("身高 cm", "170"), ("体重 kg", "65")):
        enter(ui, label, value)
    ui.click("下一步 · 选择周期方案  →")
    ui.click("确认计划 · 去录冰箱  →")
    for name, grams in (("鸡蛋", "2000"),):
        enter(ui, "食材名称", name)
        enter(ui, "数量", grams)
        enter(ui, "还剩几天（可留空）", "5")
        ui.click("预览并确认  →")
        ui.click("最终确认入库")
    ui.click("完成建档 · 开始托管  →")
    ui.click("⚙  设置")
    ui.get("m", k="scroll", x=750, y=600, dy=650, wait=1)
    ui.click("改用本地规则")
    ui.click("⌂  首页")
    ui.click("生成今日菜单  →")
    plan = ui.state()["plans"][0]
    ui.check("one generation gives three meals", len(plan["meals"]) == 3
             and [m["slot"] for m in plan["meals"]] == ["早餐", "午餐", "晚餐"])
    ui.check("every meal lists ingredients with grams",
             all(m["uses"] and all(u["grams"] > 0 for u in m["uses"]) for m in plan["meals"]))
    page = ui.text()
    ui.check("each meal shows a nutrition reference and the day's remainder",
             "早餐" in page and "午餐" in page and "晚餐" in page
             and "kcal" in page and "今日剩余" in page)
    ui.check("every ingredient shows 库存够 or 还差 N 克",
             "库存够" in page or "还差" in page)
    # 越界拦截: a portion far past today's remaining budget is refused, not saved.
    ui.fill("9999", index=0)
    ui.check("an over-budget portion is refused with a reason", "被拦下" in ui.text())
    ui.click("接受今日菜单  →")
    ui.check("a menu that needs no purchase is accepted",
             ui.state()["plans"][0]["accepted"] and ui.state()["active"] == ui.state()["plans"][0]["id"])
    (ui.profile / "expected-state.json").write_text(
        json.dumps(ui.state(), ensure_ascii=False), encoding="utf-8")
    (ui.profile / "checks.json").write_text(
        json.dumps(ui.checks, ensure_ascii=False), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=18442)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--restart", action="store_true")
    parser.add_argument("--recipe", action="store_true")
    parser.add_argument("--menu-purchase", action="store_true",
                        help="Issue #23 daily-menu QA: generate, three meals, nutrition, over-limit refusal")
    args = parser.parse_args()
    ui = UI(args.port, args.profile.resolve())
    if args.restart:
        expected = json.loads((ui.profile / "expected-state.json").read_text(encoding="utf-8"))
        ui.check("重启保留画像、库存、菜单、历史和 IDs", ui.state() == expected)
        ui.check("重启进入首页", "今天想吃点什么？" in ui.text())
    elif args.menu_purchase:
        exercise_menu_purchase(ui)
    elif args.recipe:
        exercise_recipe(ui)
    else:
        exercise(ui)


if __name__ == "__main__":
    main()
