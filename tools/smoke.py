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

    def scroll(self, dy):
        card = next(w for w in self.get("snap")["s"] if w.get("i") == "card" and w["ty"] == "Splash")
        left, top, cw, ch = card["r"]
        self.get("m", k="scroll", x=left + cw * 0.5, y=top + ch * 0.5, dy=dy, wait=1)

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
    refused with a reason. Issue #24: the derived 缺菜清单 merges the three meals,
    re-derives its gap from eligible stock, and edits the day menu's usage.
    Synthetic inventory only."""
    ui.click("选择", index=1)
    ui.click("女性")
    for label, value in (("年龄", "30"), ("身高 cm", "170"), ("体重 kg", "65")):
        enter(ui, label, value)
    ui.click("下一步 · 选择周期方案  →")
    ui.scroll(700)
    ui.click("确认计划 · 去录冰箱  →")
    enter(ui, "食材名称", "鸡蛋")
    enter(ui, "数量", "2000")
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
    # 越界拦截: a portion far past today's remaining budget is refused, not saved.
    portion = plan["meals"][0]["uses"][0]["grams"]
    ui.fill("9999", index=0)
    ui.check("an over-budget portion is refused with a reason",
             "被拦下" in ui.text()
             and ui.state()["plans"][0]["meals"][0]["uses"][0]["grams"] == portion)
    # Issue #24: the three meals merge into one 缺菜清单 line holding the day's total.
    merged = sum(u["grams"] for m in plan["meals"] for u in m["uses"] if u["name"] == "鸡蛋")
    ui.check("the three meals merge into one line with the day's total",
             f"用量 {merged} g · 库存可用 2000 g" in ui.text())
    page = ui.text()
    ui.scroll(600)
    page = page + ui.text()
    ui.check("every meal shows a nutrition reference and the day's remainder",
             "早餐" in page and "午餐" in page and "晚餐" in page
             and "kcal" in page and "今日剩余" in page)
    ui.scroll(-2000)
    # 库存可用 counts only eligible batches: shrink the batch and add an expired one.
    ui.click("▣  冰箱")
    ui.click("展开 / 收起", index=0)
    ui.click("编辑", index=0)
    ui.fill("100", index=1)
    ui.click("预览并确认  →")
    ui.click("最终确认入库")
    add(ui, "鸡蛋", "500", printed_date="2020-01-01")
    foods = ui.state()["foods"]
    today = int((time.time() + ui.state()["offset"]) // 86400)
    batches = [f for f in foods if f["name"] == "鸡蛋"]
    available = sum(f["canonical_quantity"] for f in batches if f["expires_on_day"] >= today)
    gap = max(0, merged - available)
    ui.click("✦  菜单")
    ui.scroll(-2000)
    page = ui.text()
    ui.check("an expired batch is not counted as available",
             available == 100 and len(batches) == 2)
    ui.check("a stock change re-derives the gap without a refresh",
             f"用量 {merged} g · 库存可用 {available} g" in page and f"还差 {gap} 克" in page)
    # Editing the gap writes the day menu's usage; the list only re-derives from it.
    ui.fill("200", name="shortfall_amount")
    revised = sum(u["grams"] for m in ui.state()["plans"][0]["meals"]
                  for u in m["uses"] if u["name"] == "鸡蛋")
    ui.check("editing the gap edits the day menu's usage, not the list",
             revised == available + 200
             and f"用量 {revised} g · 库存可用 {available} g" in ui.text()
             and "还差 200 克" in ui.text())
    ui.check("the shortfall list is never stored",
             "shortfall" not in ui.state_path().read_text(encoding="utf-8"))
    # "不需要" is the same write with the target already in stock.
    ui.click("不需要")
    dropped = sum(u["grams"] for m in ui.state()["plans"][0]["meals"]
                  for u in m["uses"] if u["name"] == "鸡蛋")
    ui.check("removing a row falls back on the day menu's usage",
             dropped == available and "库存够，不用买。" in ui.text())
    ui.click("接受今日菜单  →")
    ui.check("a menu that needs no purchase is accepted",
             ui.state()["plans"][0]["accepted"] and ui.state()["active"] == ui.state()["plans"][0]["id"])
    # Removing the last batch leaves nothing to cover a row; refusing beats writing
    # a day menu with an empty meal (valid_state would reject it on the next load).
    ui.click("▣  冰箱")
    if "丢弃/移除" not in ui.text():
        ui.click("展开 / 收起", index=0)
    ui.click("丢弃/移除", index=0)
    ui.click("确认移除")
    ui.click("丢弃/移除", index=0)
    ui.click("确认移除")
    ui.click("✦  菜单")
    ui.scroll(-2000)
    ui.click("不需要")
    kept = sum(u["grams"] for m in ui.state()["plans"][0]["meals"]
               for u in m["uses"] if u["name"] == "鸡蛋")
    ui.check("an edit that would empty a meal is refused",
             "会让这一餐为空" in ui.text() and kept == dropped)
    (ui.profile / "expected-state.json").write_text(
        json.dumps(ui.state(), ensure_ascii=False), encoding="utf-8")
    (ui.profile / "checks.json").write_text(
        json.dumps(ui.checks, ensure_ascii=False), encoding="utf-8")


def exercise_market(ui):
    """Issue #25: 一键补齐 opens the in-app 模拟买菜 region in the same window,
    carrying the derived 缺菜清单 (ADR 0003), with its own 商品/购物车/订单
    navigation, a fixed 模拟商品 catalog with list and detail, one ingredient the
    catalog deliberately lacks, and 模拟平台/模拟下单 labels. Synthetic inventory
    only; the manifest has no shopping network capability to call."""
    ui.click("选择", index=1)
    ui.click("女性")
    for label, value in (("年龄", "30"), ("身高 cm", "170"), ("体重 kg", "65")):
        enter(ui, label, value)
    ui.click("下一步 · 选择周期方案  →")
    ui.scroll(700)
    ui.click("确认计划 · 去录冰箱  →")
    # 菠菜 is a 模拟商品; 秋葵 is deliberately absent from the catalog.
    enter(ui, "食材名称", "菠菜")
    enter(ui, "数量", "300")
    ui.click("预览并确认  →")
    ui.click("最终确认入库")
    ui.get("m", k="scroll", x=450, y=450, dy=-2500, wait=1)
    enter(ui, "食材名称", "秋葵")
    enter(ui, "数量", "200")
    ui.click("填写 / 收起包装营养参考")
    enter(ui, "每100g热量 kcal", "30")
    enter(ui, "每100g蛋白质 g", "2")
    enter(ui, "每100g膳食纤维 g", "3")
    enter(ui, "每100g维生素C mg", "20")
    ui.click("预览并确认  →")
    ui.click("最终确认入库")
    ui.click("完成建档 · 开始托管  →")
    ui.click("⚙  设置")
    ui.get("m", k="scroll", x=750, y=600, dy=650, wait=1)
    ui.click("改用本地规则")
    ui.click("⌂  首页")
    ui.click("生成今日菜单  →")
    plan = ui.state()["plans"][0]
    ui.check("the market demo menu uses a catalogued and an uncatalogued ingredient",
             {u["name"] for m in plan["meals"] for u in m["uses"]} == {"菠菜", "秋葵"})
    # Empty the fridge so the day menu's usage is the whole 缺菜清单.
    ui.click("▣  冰箱")
    ui.click("展开 / 收起")
    ui.click("丢弃/移除")
    ui.click("确认移除")
    ui.click("展开 / 收起")
    ui.click("丢弃/移除")
    ui.click("确认移除")
    ui.check("the synthetic fridge is empty before 一键补齐", ui.state()["foods"] == [])
    ui.click("✦  菜单")
    ui.scroll(-2500)
    ui.check("the 缺菜清单 offers 一键补齐", "一键补齐" in ui.text())
    ui.click("一键补齐 · 去模拟买菜  →")
    page = ui.text()
    ui.check("一键补齐 opens the 模拟买菜 region in the same window",
             "模拟买菜" in page and "模拟平台" in page and "模拟下单" in page)
    ui.check("the region carries the current 缺菜清单 in",
             "本次要补齐的缺菜" in page and "菠菜" in page and "秋葵" in page)
    ui.check("a catalogued 缺菜 names its 模拟商品", "已对应模拟商品：菠菜" in page)
    ui.check("an uncatalogued 缺菜 is marked, not silently dropped",
             "无对应模拟商品" in page)
    ui.check("the product list shows the fixed catalog",
             "模拟商品" in page and "共 24 条随包演示商品" in page and "菠菜 · 蔬菜" in page)
    ui.click("查看详情", index=0)
    detail = ui.text()
    ui.check("the product detail shows 品类、规格、单位、价格、可售数量与营养参考",
             "模拟商品详情" in detail and "规格" in detail and "单位" in detail
             and "可售数量" in detail and "每 100 g 营养参考" in detail
             and "参考保质期" in detail)
    ui.click("‹ 返回商品列表")
    ui.click("▧  购物车")
    ui.check("the region has its own 购物车 page",
             "购物车 · 待核对" in ui.text() and "无匹配" in ui.text())
    ui.click("▦  订单")
    ui.check("the region has its own 订单 page with 模拟下单 labelling",
             "还没有模拟订单" in ui.text() and "模拟下单" in ui.text())
    ui.click("← 返回管家")
    back = ui.text()
    ui.check("返回管家 restores the butler and keeps its 菜单 tab",
             "▧  购物车" not in back and "模拟商品详情" not in back
             and "今日菜单" in back and "缺菜清单" in back)
    (ui.profile / "expected-state.json").write_text(
        json.dumps(ui.state(), ensure_ascii=False), encoding="utf-8")
    (ui.profile / "checks.json").write_text(
        json.dumps(ui.checks, ensure_ascii=False), encoding="utf-8")


def market_cart_rows(ui):
    return [line["name"] for line in ui.state()["cart"] if not line.get("dropped")]


def exercise_market_cart(ui):
    """Issue #26: entering 模拟买菜 auto-fills a 待核对 购物车 by name/spec/quantity,
    rounds each purchase quantity up to whole packs, flags unmatched or
    under-stocked rows with a 替换 entry instead of dropping them, and keeps
    quantity/delete/replace edits in persisted state. Synthetic inventory only."""
    ui.click("选择", index=1)
    ui.click("女性")
    for label, value in (("年龄", "30"), ("身高 cm", "170"), ("体重 kg", "65")):
        enter(ui, label, value)
    ui.click("下一步 · 选择周期方案  →")
    ui.scroll(700)
    ui.click("确认计划 · 去录冰箱  →")
    # 菠菜 400 g against a 300 g/把 spec rounds up to 2 把.
    # 蘑菇 3000 g against a 200 g/盒 spec needs 15 盒, but only 14 are on sale.
    # 秋葵 has no catalog product at all.
    for name, quantity in (("菠菜", "400"), ("蘑菇", "3000"), ("秋葵", "200")):
        ui.get("m", k="scroll", x=450, y=450, dy=-2500, wait=1)
        enter(ui, "食材名称", name)
        enter(ui, "数量", quantity)
        if name == "秋葵":
            ui.click("填写 / 收起包装营养参考")
            enter(ui, "每100g热量 kcal", "30")
            enter(ui, "每100g蛋白质 g", "2")
            enter(ui, "每100g膳食纤维 g", "3")
            enter(ui, "每100g维生素C mg", "20")
        ui.click("预览并确认  →")
        ui.click("最终确认入库")
    ui.click("完成建档 · 开始托管  →")
    ui.click("⚙  设置")
    ui.get("m", k="scroll", x=750, y=600, dy=650, wait=1)
    ui.click("改用本地规则")
    ui.click("⌂  首页")
    ui.click("生成今日菜单  →")
    plan = ui.state()["plans"][0]
    ui.check("the cart demo menu uses all three synthetic ingredients",
             {u["name"] for m in plan["meals"] for u in m["uses"]} == {"菠菜", "蘑菇", "秋葵"})
    ui.click("▣  冰箱")
    for _ in range(3):
        ui.click("展开 / 收起")
        ui.click("丢弃/移除")
        ui.click("确认移除")
    ui.check("the synthetic fridge is empty before 一键补齐", ui.state()["foods"] == [])
    ui.click("✦  菜单")
    ui.scroll(-2500)
    ui.click("一键补齐 · 去模拟买菜  →")
    ui.click("▧  购物车")
    cart = ui.text()
    ui.check("entering the region auto-fills a 待核对 购物车", "购物车 · 待核对" in cart)
    ui.check("the purchase quantity rounds up by 规格与单位", "2 把" in cart and "15 盒" in cart)
    ui.check("an under-stocked row is flagged, not silently dropped",
             "可售不足" in cart and "14 盒" in cart)
    ui.check("an uncatalogued row is flagged with a 替换 entry",
             "无匹配" in cart and "替换" in cart)
    ui.check("the cart shows unit prices and a simulated total",
             "模拟总价" in cart and "¥102.60" in cart)
    rows = market_cart_rows(ui)
    picked = [line["name"] for line in ui.state()["cart"]
              if not line.get("dropped") and line["product"]]
    ui.click("＋", index=picked.index("菠菜"))
    ui.check("increasing a quantity persists and re-prices the cart",
             ui.state()["cart"][rows.index("菠菜")]["quantity"] == 3
             and "3 把" in ui.text() and "¥107.40" in ui.text())
    ui.click("替换", index=rows.index("秋葵"))
    picker = ui.text()
    ui.check("替换 offers same-category alternatives by 规格",
             "优先显示同品类（蔬菜）" in picker and "青菜 · 蔬菜" in picker and "换成 青菜" in picker)
    ui.click("换成 青菜")
    replaced = ui.text()
    ui.check("replacing an unmatched row gives it a product and a rounded quantity",
             "青菜" in replaced and "无匹配" not in replaced
             and ui.state()["cart"][rows.index("秋葵")]["product"] == "青菜")
    ui.click("删除", index=rows.index("蘑菇"))
    deleted = ui.text()
    ui.check("deleting a row removes it and its price from the cart",
             "蘑菇" not in deleted and "可售不足" not in deleted
             and ui.state()["cart"][rows.index("蘑菇")]["dropped"] is True)
    ui.check("the total reflects the decrease, the replacement and the deletion",
             "¥18.60" in deleted)
    ui.click("← 返回管家")
    ui.click("✦  菜单")
    ui.scroll(-2500)
    ui.click("一键补齐 · 去模拟买菜  →")
    ui.click("▧  购物车")
    reopened = ui.text()
    ui.check("re-entering the region keeps the user's cart edits",
             "3 把" in reopened and "青菜" in reopened
             and "蘑菇" not in reopened and "无匹配" not in reopened)
    (ui.profile / "expected-state.json").write_text(
        json.dumps(ui.state(), ensure_ascii=False), encoding="utf-8")
    (ui.profile / "checks.json").write_text(
        json.dumps(ui.checks, ensure_ascii=False), encoding="utf-8")


def exercise_market_cart_restart(ui):
    """Issue #26: the persisted 购物车 survives a host restart, and the derived
    缺菜清单 still agrees with it."""
    expected = json.loads((ui.profile / "expected-state.json").read_text(encoding="utf-8"))
    ui.check("restart keeps the persisted cart exactly", ui.state() == expected)
    ui.check("restart resumes on the butler dashboard", "今天想吃点什么？" in ui.text())
    ui.click("✦  菜单")
    ui.scroll(-2500)
    ui.click("一键补齐 · 去模拟买菜  →")
    ui.click("▧  购物车")
    cart = ui.text()
    ui.check("the restored cart keeps the user's quantity, replacement and deletion",
             "3 把" in cart and "青菜" in cart and "蘑菇" not in cart and "无匹配" not in cart)
    ui.check("the derived 缺菜清单 still lists every ingredient the cart came from",
             "菠菜" in cart and "秋葵" in cart)


def exercise_market_order(ui):
    """Issue #27: a 模拟订单 is submitted only after the user confirms the cart, and
    then shows its 待收货 status. Submitting it leaves 库存、进度 and 实际执行记录
    untouched, the page says no real payment, and the order survives a restart.
    Synthetic inventory only."""
    ui.click("选择", index=1)
    ui.click("女性")
    for label, value in (("年龄", "30"), ("身高 cm", "170"), ("体重 kg", "65")):
        enter(ui, label, value)
    ui.click("下一步 · 选择周期方案  →")
    ui.scroll(700)
    ui.click("确认计划 · 去录冰箱  →")
    # 菠菜 orders fine; 蘑菇 needs 15 盒 but only 14 are on sale; 秋葵 has no product.
    for name, quantity in (("菠菜", "400"), ("蘑菇", "3000"), ("秋葵", "200")):
        ui.get("m", k="scroll", x=450, y=450, dy=-2500, wait=1)
        enter(ui, "食材名称", name)
        enter(ui, "数量", quantity)
        if name == "秋葵":
            ui.click("填写 / 收起包装营养参考")
            enter(ui, "每100g热量 kcal", "30")
            enter(ui, "每100g蛋白质 g", "2")
            enter(ui, "每100g膳食纤维 g", "3")
            enter(ui, "每100g维生素C mg", "20")
        ui.click("预览并确认  →")
        ui.click("最终确认入库")
    ui.click("完成建档 · 开始托管  →")
    ui.click("⚙  设置")
    ui.get("m", k="scroll", x=750, y=600, dy=650, wait=1)
    ui.click("改用本地规则")
    ui.click("⌂  首页")
    ui.click("生成今日菜单  →")
    ui.click("▣  冰箱")
    for _ in range(3):
        ui.click("展开 / 收起")
        ui.click("丢弃/移除")
        ui.click("确认移除")
    ui.check("the synthetic fridge is empty before 一键补齐", ui.state()["foods"] == [])
    ui.click("✦  菜单")
    ui.scroll(-2500)
    ui.click("一键补齐 · 去模拟买菜  →")
    ui.click("▧  购物车")
    ui.scroll(900)
    ui.check("the cart offers 提交模拟订单", "提交模拟订单" in ui.text())
    before_foods = list(ui.state()["foods"])
    before_stage = json.dumps(ui.state()["stages"][0], ensure_ascii=False)
    before_meals = ui.state()["meal_count"]
    ui.click("提交模拟订单  →")
    ui.scroll(500)
    ui.check("submitting first asks for confirmation, with no order yet",
             "确认提交模拟订单？" in ui.text() and ui.state()["orders"] == [])
    ui.click("取消")
    ui.check("cancelling the confirmation writes no order", ui.state()["orders"] == [])
    ui.click("提交模拟订单  →")
    ui.click("确认提交订单")
    ui.scroll(-2000)
    order = ui.state()["orders"][0]
    ui.check("only after confirmation is a 模拟订单 created",
             len(ui.state()["orders"]) == 1 and order["status"] == "待收货")
    page = ui.text()
    ui.check("the order and its status are shown after submitting",
             "模拟订单 #" + str(order["id"]) in page and "待收货" in page)
    ui.check("the order page says no real purchase or payment", "不产生真实支付" in page)
    ui.check("the order keeps the on-sale maximum and leaves the unmatched row out",
             [line["name"] for line in order["lines"]] == ["菠菜", "蘑菇"]
             and [line["quantity"] for line in order["lines"]] == [2, 14]
             and "秋葵" not in page)
    ui.check("submitting changes no 库存", ui.state()["foods"] == before_foods)
    ui.check("submitting changes no 进度 and writes no 实际执行记录",
             json.dumps(ui.state()["stages"][0], ensure_ascii=False) == before_stage
             and ui.state()["meal_count"] == before_meals
             and ui.state()["stages"][0]["intake"] == [])
    ui.shot("issue-27-order.png")
    (ui.profile / "expected-state.json").write_text(
        json.dumps(ui.state(), ensure_ascii=False), encoding="utf-8")
    (ui.profile / "checks.json").write_text(
        json.dumps(ui.checks, ensure_ascii=False), encoding="utf-8")


def exercise_market_order_restart(ui):
    """Issue #27: the submitted 模拟订单 survives a host restart with its status."""
    expected = json.loads((ui.profile / "expected-state.json").read_text(encoding="utf-8"))
    ui.check("restart keeps the persisted order exactly", ui.state() == expected)
    ui.check("restart resumes on the butler dashboard", "今天想吃点什么？" in ui.text())
    ui.click("✦  菜单")
    ui.scroll(-2500)
    ui.click("一键补齐 · 去模拟买菜  →")
    ui.click("▦  订单")
    page = ui.text()
    order = expected["orders"][0]
    ui.check("the restored order keeps its lines, status and no-payment note",
             "模拟订单 #" + str(order["id"]) in page and "待收货" in page
             and "菠菜" in page and "蘑菇" in page and "不产生真实支付" in page)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=18442)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--restart", action="store_true")
    parser.add_argument("--recipe", action="store_true")
    parser.add_argument("--menu-purchase", action="store_true",
                        help="Issue #23/#24 daily menu: three meals, nutrition, over-limit refusal, derived 缺菜清单")
    parser.add_argument("--market", action="store_true",
                        help="Issue #25 模拟买菜: 一键补齐 entry, carried 缺菜清单, catalog list/detail, 模拟 labels")
    parser.add_argument("--market-cart", action="store_true",
                        help="Issue #26 购物车: auto-fill, pack rounding, flags, 增减/删除/替换, total, persistence")
    parser.add_argument("--market-cart-restart", action="store_true",
                        help="Issue #26: the persisted 购物车 survives a restart")
    parser.add_argument("--market-order", action="store_true",
                        help="Issue #27 模拟订单: confirm-then-submit, 待收货 status, stock/progress untouched, persistence")
    parser.add_argument("--market-order-restart", action="store_true",
                        help="Issue #27: the submitted 模拟订单 survives a restart")
    args = parser.parse_args()
    ui = UI(args.port, args.profile.resolve())
    if args.restart:
        expected = json.loads((ui.profile / "expected-state.json").read_text(encoding="utf-8"))
        ui.check("重启保留画像、库存、菜单、历史和 IDs", ui.state() == expected)
        ui.check("重启进入首页", "今天想吃点什么？" in ui.text())
    elif args.menu_purchase:
        exercise_menu_purchase(ui)
    elif args.market:
        exercise_market(ui)
    elif args.market_cart:
        exercise_market_cart(ui)
    elif args.market_cart_restart:
        exercise_market_cart_restart(ui)
    elif args.market_order:
        exercise_market_order(ui)
    elif args.market_order_restart:
        exercise_market_order_restart(ui)
    elif args.recipe:
        exercise_recipe(ui)
    else:
        exercise(ui)


if __name__ == "__main__":
    main()
