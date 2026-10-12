"""Offline release-metadata guards, not publisher-proof or approval checks."""
import json
from pathlib import Path
import re
import unittest

APP = Path(__file__).resolve().parents[1]
BUNDLE = APP / "bundle"
REPOSITORY = "https://github.com/woshuoduijiushidui/pantry-steward"


class ReleaseMetadataTests(unittest.TestCase):
    def test_version_permissions_and_digest_shape(self):
        manifest = json.loads((BUNDLE / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["id"], "pantry-steward")
        self.assertEqual(manifest["version"], "0.8.0")
        self.assertEqual(set(manifest["capabilities"]), {"storage", "model", "camera", "files"})
        self.assertEqual(manifest["requires"], ["host-api-v1"])
        self.assertEqual(manifest["host_api"]["optional"], {"camera.permission.request": 1})
        self.assertRegex(manifest["integrity"]["bundle_blake3"], r"^[0-9a-f]{64}$")

    def test_listing_links_assets_and_platform(self):
        listing = json.loads((BUNDLE / "listing.json").read_text(encoding="utf-8"))
        self.assertEqual(listing["publisher"]["support"], REPOSITORY + "/issues")
        self.assertEqual(listing["publisher"]["privacy_policy_url"], REPOSITORY + "/blob/main/PRIVACY.md")
        self.assertEqual(listing["platforms"], ["windows"])
        self.assertTrue(listing["release_notes"].startswith("0.8.0"))
        for name in listing["screenshots"] + [listing["icon"]]:
            path = (BUNDLE / name).resolve()
            self.assertTrue(path.is_relative_to(BUNDLE.resolve()))
            self.assertTrue(path.is_file(), name)

    def test_no_stale_repository_name_in_published_metadata(self):
        # The repository was renamed to pantry-steward. A stale link is a dead
        # end for users and would disagree with REPOSITORY above, so guard it.
        for name in ("README.md", "README.zh-CN.md", "PRIVACY.md", "SUPPORT.md",
                     "SUBMISSION.md", "AGENTS.md"):
            self.assertNotIn("OctoSense-AppCard", (APP / name).read_text(encoding="utf-8"), name)
        self.assertNotIn("OctoSense-AppCard", (BUNDLE / "listing.json").read_text(encoding="utf-8"))

    def test_package_size_and_no_private_configuration(self):
        files = [path for path in BUNDLE.rglob("*") if path.is_file()]
        self.assertLessEqual(sum(path.stat().st_size for path in files), 8 * 1024 * 1024)
        for path in files:
            self.assertNotIn(path.name.lower(), ("ai.env", ".env", "tools.json", "agent.md"))
            self.assertNotIn(path.suffix.lower(), (".key", ".pem", ".pfx", ".mp4"))

    def test_document_local_links_exist(self):
        for name in ("README.md", "README.zh-CN.md", "PRIVACY.md", "SUPPORT.md", "SUBMISSION.md"):
            path = APP / name
            for link in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                if "://" in link or link.startswith("#"):
                    continue
                self.assertTrue((path.parent / link.split("#")[0]).is_file(), f"{name}: {link}")

    def test_official_publishing_pin_and_separation(self):
        pin = json.loads((APP / "publisher-toolchain.json").read_text(encoding="utf-8"))
        self.assertEqual(pin["repository"], "OctoSense-org/OctoSense-App-Hub")
        self.assertRegex(pin["revision"], r"^[0-9a-f]{40}$")
        workflow = (APP / ".github/workflows/publish-app.yml").read_text(encoding="utf-8")
        self.assertIn("ref: " + pin["revision"], workflow)
        self.assertIn("publisher-verify", workflow)
        self.assertIn("hub_admission", workflow)
        self.assertNotIn("__HUB_REVISION__", workflow)
        self.assertNotIn("hub stamp", workflow)

    def test_six_cycle_candidates_and_regeneration_exist(self):
        # Offline guard only: the native smoke test exercises the real behaviour.
        script = (BUNDLE / "main.splash").read_text(encoding="utf-8")
        self.assertIn("let cycle_days = [1 3 7 15 21 30]", script)
        self.assertIn("fn make_cycle_candidates", script)
        self.assertIn("fn regenerate_cycle", script)
        for key in ('"balance"', '"protein"', '"fiber"', '"trim"'):
            self.assertIn(key, script)

    def test_composed_plan_separates_candidates_from_stages(self):
        # Offline guard only: qa_release.py composes and confirms for real.
        script = (BUNDLE / "main.splash").read_text(encoding="utf-8")
        self.assertIn("stages: [] stage_next: 1 plan_history: []", script)
        self.assertIn("fn make_stage(candidate, started){", script)
        for marker in ("fn draft_add(", "fn draft_move(", "fn draft_remove(",
                       "fn draft_replace(", "fn draft_total_days(){", "fn stage_range(",
                       "fn confirm_health_plan(){", "plan_draft.len() >= 12"):
            self.assertIn(marker, script)

    def test_future_stage_editing_locks_started_stages(self):
        # Offline guard only: qa_release.py performs the edits against a real host.
        script = (BUNDLE / "main.splash").read_text(encoding="utf-8")
        self.assertIn("fn stage_locked(", script)
        for marker in ("fn stage_lock_hint(", "fn relayout_stages(", "fn stage_move(",
                       "fn stage_remove(", "fn stage_replace(", "fn plan_done_meals(){",
                       "fn plan_planned_meals(){", "fn plan_progress_percent(){"):
            self.assertIn(marker, script)
        self.assertIn("按日历锁定，不是故障", script)

    def test_overview_long_term_plan_and_progress(self):
        # Offline guard only: qa_release.py exercises the page against a real host.
        script = (BUNDLE / "main.splash").read_text(encoding="utf-8")
        for marker in ("fn meals_per_day(){", "fn stage_done_meals(",
                       "fn stage_planned_meals(", "fn stage_progress_percent(",
                       "fn stage_today_intake(", "fn program_expired(){",
                       "fn plan_planned_meals(){"):
            self.assertIn(marker, script)
        self.assertIn('"◈  总览"', script)
        self.assertIn("每餐进度 ", script)
        self.assertIn("计划进度 ", script)
        # The date-driven view must re-render when the civil day turns over.
        self.assertIn("today != shown_day", script)
    def test_daily_menu_shape_exists(self):
        # Offline guard only: qa_release.py --menu-purchase drives the real behaviour.
        script = (BUNDLE / "main.splash").read_text(encoding="utf-8")
        for marker in ("fn menu_issue(", "fn menu_ready(", "fn menu_stock_lines(",
                       "fn menu_executable(", "fn menu_ingredients(",
                       "fn distribute_meals(", "fn save_day_menu(",
                       "fn revise_meal(", "fn swap_meal_food(", "fn migrate_menus(",
                       "fn meal_label(index)"):
            self.assertIn(marker, script)
        self.assertIn('库存够', script)
        self.assertIn('"还差 "', script)
        self.assertIn('"早餐"', script)
        self.assertIn('"午餐"', script)
        self.assertIn('"晚餐"', script)

    def test_design_decisions_a6_b1_b2(self):
        # Issue #22 decisions taken against the Issue #5 design doc, on top of the
        # AI nutrition estimation that main already ships: A6 one automatic
        # correction, B1 cross-batch allocation, B2 一键补齐 behind menu
        # acceptance. Offline guard only; qa_release.py drives the real behaviour.
        script = (BUNDLE / "main.splash").read_text(encoding="utf-8")
        for marker in ("fn draw_split(", "fn draw_piece(", "fn allocate_uses(",
                       "fn merge_draws(", "let ai_correction", "let ai_validation_error"):
            self.assertIn(marker, script)
        # A6: one re-ask, carrying the concrete error; no second correction.
        self.assertIn("if !ai_snapshot.experience && ai_correction < 1", script)
        self.assertIn('task = task + "上一次输出未通过本地校验：" + ai_validation_error', script)
        self.assertNotIn("ai_feedback", script)
        # B1: validation and consumption share the one allocation; the consume
        # operation never lists the same batch twice.
        self.assertIn("allocate_uses(p, p.uses).fits", script)
        self.assertIn("let uses = merge_draws(actual_draws)", script)
        # B2: the entry is gated, and open_market refuses an unaccepted menu.
        self.assertIn("接受这份菜单后即可一键补齐", script)
        self.assertIn("请先接受这份菜单，再一键补齐", script)
        manifest = json.loads((BUNDLE / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["capabilities"], ["storage", "model", "camera", "files"])

    def test_design_decision_a4_estimates_write_back_with_provenance(self):
        # Issue #41 settled the D5-015 conflict in favour of PR #21: an AI
        # estimate may write back to state.foods[].nutrition, but only as a
        # reference that carries provenance. Offline guard only; the estimate
        # behaviour itself is driven natively by qa_ai_nutrition.py.
        script = (BUNDLE / "main.splash").read_text(encoding="utf-8")
        for marker in ("known: true kcal: n.kcal",
                       'source: "AI 估算" basis: n.basis estimated_at: time_now() model: ai_model',
                       "for f in state.foods { if f.id == n.key { f.nutrition = ref",
                       "consumption[n.key - 1].nutrition = ref"):
            self.assertIn(marker, script)
        # The decision is recorded in the vocabulary and an accepted ADR.
        self.assertIn("**营养参考**:", (APP / "GLOSSARY.md").read_text(encoding="utf-8"))
        adr = (APP / "docs/adr/0004-AI-估算写回批次但仅作参考.md").read_text(encoding="utf-8")
        self.assertIn('source: "AI 估算"', adr)
        self.assertIn("**Status**: accepted", adr)

    def test_manifest_has_no_network_shopping_capability(self):
        manifest = json.loads((BUNDLE / "manifest.json").read_text(encoding="utf-8"))
        capabilities = set(manifest["capabilities"])
        self.assertTrue({"storage", "model"} <= capabilities)
        for name in capabilities:
            for forbidden in ("network", "http", "shop", "purchase", "payment"):
                self.assertNotIn(forbidden, name)

    def test_market_region_is_in_bundle_not_a_second_unit(self):
        # Offline guard only: qa_release.py --market drives the real behaviour.
        script = (BUNDLE / "main.splash").read_text(encoding="utf-8")
        for marker in ("fn market_products(){", "fn market_match(", "fn market_lines(",
                       "fn market_short_count(", "fn open_market(){", "fn close_market(){",
                       "fn market_price("):
            self.assertIn(marker, script)
        for label in ("一键补齐", "模拟平台", "模拟下单", "无对应模拟商品", "模拟商品"):
            self.assertIn(label, script)
        # The fixed demo catalog ships in the bundle; the region is not a second
        # bundle unit, so it lives in the same splash and manifest id.
        self.assertEqual(script.count("shelf_days:"), 24)
        manifest = json.loads((BUNDLE / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["id"], "pantry-steward")

    def test_market_cart_auto_fill_total_and_persistence(self):
        # Offline guard only: qa_release.py --market-cart drives the real behaviour.
        script = (BUNDLE / "main.splash").read_text(encoding="utf-8")
        for marker in ("fn market_packs(", "fn market_spec_grams(", "fn market_pick(",
                       "fn market_fill_cart(){", "fn market_cart_step(", "fn market_cart_drop(",
                       "fn market_replace_with(", "fn market_line_flag(", "fn market_cart_total(",
                       "fn market_alternatives(", "fn market_category_hint("):
            self.assertIn(marker, script)
        for label in ("购物车 · 待核对", "模拟总价", "可售不足", "替换"):
            self.assertIn(label, script)
        # The cart is user input stored in state (ADR 0003), migrated for old files
        # and validated on load, not kept in the transient market view.
        self.assertIn("cart: [] orders: []", script)
        self.assertIn("state.cart.push(", script)
        self.assertIn("value.cart = []", script)
        manifest = json.loads((BUNDLE / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["id"], "pantry-steward")

    def test_market_order_requires_confirmation_and_changes_no_stock(self):
        # Offline guard only: qa_release.py --market-order drives the real behaviour.
        script = (BUNDLE / "main.splash").read_text(encoding="utf-8")
        for marker in ("fn market_order_next_id(){", "fn market_order_lines(){",
                       "fn market_order_total(", "fn market_order_line_total(",
                       "fn market_order_open_confirm(){", "fn market_order_cancel_confirm(){",
                       "fn market_submit_order(){"):
            self.assertIn(marker, script)
        for label in ("提交模拟订单", "确认提交模拟订单？", "确认提交订单", "待收货", "不产生真实支付"):
            self.assertIn(label, script)
        # The order is user input stored in state (like the cart), migrated for
        # old files and validated on load, not kept in the transient market view.
        self.assertIn("orders: []", script)
        self.assertIn("state.orders.push(", script)
        self.assertIn("value.orders = []", script)
        manifest = json.loads((BUNDLE / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["id"], "pantry-steward")

    def test_receipt_checks_quantities_and_adds_new_batches(self):
        # Offline guard only: qa_release.py --market-receive drives the real behaviour.
        script = (BUNDLE / "main.splash").read_text(encoding="utf-8")
        for marker in ("fn market_receipt_open(", "fn market_receipt_step(",
                       "fn market_receipt_days(", "fn market_receipt_batch(",
                       "fn market_receipt_confirm(){"):
            self.assertIn(marker, script)
        for label in ("确认收货", "确认收货入库", "核对实际收到的食材", "已收货"):
            self.assertIn(label, script)
        # Received lines go through the one inventory-write path as a new
        # batch (type "add"); nothing merges into an existing same-name batch.
        self.assertIn('type: "add" batches: batches', script)
        self.assertIn('order.status = "已收货"', script)
        # Orders may now be either 待收货 or 已收货; schema stays 2.
        self.assertIn('order.status != "待收货" && order.status != "已收货"', script)
        manifest = json.loads((BUNDLE / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["id"], "pantry-steward")

    def test_shortfall_list_is_derived_and_editable(self):
        # Offline guard only: qa_release.py --menu-purchase drives the real behaviour.
        script = (BUNDLE / "main.splash").read_text(encoding="utf-8")
        for marker in ("fn set_menu_ingredient(", "fn revise_shortfall(", "fn drop_shortfall(",
                       "fn item_average_grams("):
            self.assertIn(marker, script)
        self.assertIn('"缺菜清单"', script)
        self.assertIn("on_change: |text| revise_shortfall(line.name, text)", script)
        # The gap is derived from the merged day menu minus available stock.
        self.assertIn("fn available_grams(name){", script)
        self.assertIn("fn menu_stock_lines(p){", script)

    def test_byte_protection_and_license_files(self):
        attributes = (APP / ".gitattributes").read_text(encoding="utf-8")
        self.assertIn("bundle/** -text", attributes.splitlines())
        for name in ("LICENSE", "NOTICE", "PRIVACY.md", "SUPPORT.md"):
            self.assertTrue((APP / name).is_file(), name)
        for name in ("LICENSE.txt", "NOTICE.txt"):
            self.assertTrue((BUNDLE / name).is_file(), name)


if __name__ == "__main__":
    unittest.main()
