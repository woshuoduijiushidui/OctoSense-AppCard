use makepad_script::*;
use std::fs;
use std::path::Path;

fn main() {
    let app = Path::new(env!("CARGO_MANIFEST_DIR")).parent().unwrap().parent().unwrap();
    let source = fs::read_to_string(app.join("bundle/main.splash")).unwrap();
    let start = source.find("fn agent_empty_session(day)").unwrap();
    let end = source.find("fn canonical_unit(unit)").unwrap();
    let helpers = &source[start..end];
    let voice_start = source.find("fn probe_voice(){").unwrap();
    let voice_end = source.find("fn stop_ai(){").unwrap();
    let voice_helpers = &source[voice_start..voice_end];
    let save_start = source.find("fn save_day_menu(meals, reason, source, numeric)").unwrap();
    let save_end = source.find("fn rule_plan(reason)").unwrap();
    let menu_save = &source[save_start..save_end];
    let accept_start = source.find("fn accept(){").unwrap();
    let accept_end = source.find("fn begin_consume(){").unwrap();
    let menu_accept = &source[accept_start..accept_end];
    let builder_start = source.find("fn build_ai_menu(output, requested_goal, recipe_only)").unwrap();
    let builder_end = source.find("fn online_plan(reason)").unwrap();
    let menu_builder = &source[builder_start..builder_end];
    let recipe_start = source.find("fn recipe_titles()").unwrap();
    let recipe_end = source.find("fn trial_meal_calories(m)").unwrap();
    let recipe_helpers = &source[recipe_start..recipe_end];
    let batch_start = source.find("fn canonical_unit(unit)").unwrap();
    let batch_end = source.find("fn valid_state(value)").unwrap();
    let batch_helpers = &source[batch_start..batch_end];
    let draft_start = source.find("fn draft_batch(row, mode, image_path, edit_id)").unwrap();
    let draft_end = source.find("fn preview_food()").unwrap();
    let draft_helper = &source[draft_start..draft_end];
    let prelude = r#"
        use mod.std.assert
        use mod.std.regex
        use mod.math.floor
        use mod.math.max
        let agent_session = nil
        let agent_memory = nil
        let agent_open = false
        let agent_origin_tab = 0
        let agent_input = ""
        let agent_phase = "idle"
        let agent_sequence = 0
        let agent_deadline = 0
        let agent_current_id = 0
        let agent_call_snapshot = nil
        let agent_batch = nil
        let agent_reply = nil
        let agent_error = ""
        let agent_memory_pending = nil
        let agent_proposal = nil
        let agent_review = nil
        let agent_answer_input = nil
        let agent_correction = 0
        let voice_phase = 0
        let voice_sequence = 0
        let voice_deadline = 0
        let voice_reply = nil
        let voice_capability = "checking"
        let voice_probe_sequence = 0
        let voice_probe_reply = nil
        let voice_probe_deadline = 0
        let voice_probe_next = 0
        let voice_probe_attempts = 0
        let voice_action = ""
        let voice_session = ""
        let voice_next_poll = 0
        let voice_path = "/agent/voice-latest.wav"
        let ui_state = {text: "" focused: false}
        let ui = {agent_input_field: {
            set_text: |text| { ui_state.text = text }
            take_key_focus: || { ui_state.focused = true }
        }}
        let ai_validation_error = ""
        let goal = ""
        let selected = 0
        let message = ""
        let state = {profile: {done: true scene: "日常健康" sex: "女" age: "30" height: "165"
            weight: "60" activity: "轻活动" allergies: "" avoidances: "" preferences: "" special: ""}
            foods: [] plans: [] stages: [] execution_records: [] active: 0
            next_id: 1 revision: 1 profile_revision: 1}
        let disk = {session: "" memory: "" voice: false fail: false}
        let fs = {
            exists: |path| { if path == "agent-session.json" { disk.session != "" }
                else if path == "/agent/voice-latest.wav" { disk.voice }
                else { disk.memory != "" } }
            read: |path| { if path == "agent-session.json" { disk.session } else { disk.memory } }
            remove: |path| { if path == "/agent/voice-latest.wav" { disk.voice = false } }
            write: |path, value| {
                if disk.fail { return "failed" }
                if path == "agent-session.json" { disk.session = value }
                else { disk.memory = value }
                nil
            }
        }
        let host = {}
        let fake_day = 100
        let fake_time = 8640000
        let booted = true
        let onboarding_step = 4
        let tab = 0
        let recognition_phase = ""
        let intake_draft = nil
        let editing_id = 0
        let removal = nil
        let pending = false
        let plan_removal = nil
        let reset_pending = false
        let market = nil
        let receipt = nil
        let ai_busy = false
        let storage_blocked = false
        let use_ai = true
        fn today_day(){ fake_day }
        fn health_day(){ fake_day }
        fn time_now(){ fake_time }
        fn current_stage(){ if state.stages.len() == 0 { return nil } state.stages[0] }
        fn program_expired(){ false }
        fn program_remaining_daily(stage){ stage.daily_kcal - stage.consumed_kcal }
        fn menu_meals(menu){ menu.meals }
        fn menu_issue(menu){ if menu == nil || menu.consumed { return "invalid" } "" }
        fn menu_title(menu){ menu.title }
        fn auto_plan_eligible(food){ if has_field(food, "eligible") { return food.eligible } false }
        fn recipe_eligible(food){ false }
        fn batch_grams(food){ food.canonical_quantity }
        fn plan_use(food, grams){
            if !auto_plan_eligible(food) || grams > food.canonical_quantity { return nil }
            {food_id: food.id name: food.name quantity: grams unit: "g" grams: grams}
        }
        fn recipe_use(food, quantity){ nil }
        fn meal_label(slot){ if slot == 0 { return "早餐" } if slot == 1 { return "午餐" } "晚餐" }
        fn recipe_display_text(value){ value }
        fn calendar_day(text){ 100 }
        fn has_field(value, name){ let wanted = name.to_json() for key item in value { if key.to_json() == wanted { return true } } false }
        fn active_plan(){ nil }
        fn choose_plan(){ if selected >= state.plans.len() { return nil } state.plans[selected] }
        fn validate(menu){ true }
        fn prune_menus(){ }
        fn record(text){ }
        fn commit(before){ true }
        fn redraw(){ }
    "#;
    let cases: &[(&str, &str)] = &[
        ("session_restart_and_local", r#"
            let s = agent_empty_session(100)
            s = agent_append_to_session(s, "user", "少放辣", 1)
            s = agent_append_to_session(s, "local", "已确认", 2)
            s = agent_append_to_session(s, "assistant", "好的", 3)
            let restored = agent_decode_session(s.to_json(), 100)
            assert(restored.messages.len() == 3)
            assert(agent_uncompressed_messages(restored, 0).len() == 2)
            assert(agent_decode_session(s.to_json(), 101).messages.len() == 0)
            assert(agent_decode_session("{bad", 100).messages.len() == 0)
            true
        "#),
        ("session_file_and_failed_write", r#"
            agent_load_session()
            assert(agent_append("user", "少放辣") == 1)
            agent_session = nil
            agent_load_session()
            assert(agent_session.messages.len() == 1)
            agent_input = "今天刚输入"
            fake_day = 101
            agent_ensure_today()
            assert(agent_session.day == 101 && agent_session.messages.len() == 0)
            assert(agent_input == "今天刚输入")
            fake_day = 100
            agent_load_session()
            assert(agent_session.messages.len() == 0)
            disk.fail = true
            assert(agent_append("assistant", "好的") == 0)
            assert(agent_session.messages.len() == 0)
            disk.fail = false
            disk.session = "{broken"
            agent_load_session()
            assert(agent_session.messages.len() == 0)
            agent_load_memory()
            let pending = agent_memory_after_confirm(agent_memory, "少放辣", "平时少放辣", true, true, 100)
            assert(agent_store_memory(pending))
            agent_memory = nil
            agent_load_memory()
            assert(agent_memory.items.len() == 1)
            disk.fail = true
            let pending = agent_memory_after_confirm(agent_memory, "偏好清淡", "平时偏好清淡", true, true, 100)
            assert(!agent_store_memory(pending))
            assert(agent_memory.items.len() == 1)
            disk.fail = false
            disk.memory = "{broken"
            agent_load_memory()
            assert(agent_memory.items.len() == 0)
            let stale = agent_memory_after_confirm(agent_memory, "少放辣", "平时少放辣", true, true, 100)
            fake_day = 131
            assert(agent_store_memory(stale))
            assert(agent_memory.items.len() == 0)
            true
        "#),
        ("session_cap", r#"
            let s = agent_empty_session(100)
            for i in 120 { s = agent_append_to_session(s, "local", "提示", i) }
            assert(s.messages.len() == 120)
            s = agent_append_to_session(s, "local", "新提示", 121)
            assert(s.messages.len() == 120 && s.messages[0].id == 2)
            assert(agent_append_to_session(s, "user", "中", 122) != nil)
            assert(agent_append_to_session(s, "user", "", 122) != nil)
            let long = ""
            for i in 1501 { long = long + "中" }
            assert(agent_append_to_session(s, "user", long, 122) == nil)
            let full = agent_empty_session(100)
            for i in 120 { full = agent_append_to_session(full, "user", "保留原文", i) }
            assert(agent_append_to_session(full, "user", "不能挤掉未摘要内容", 120) == nil)
            true
        "#),
        ("budget_and_current_once", r#"
            let s = agent_empty_session(100)
            for i in 14 { s = agent_append_to_session(s, "user", "你好", i) }
            s = agent_append_to_session(s, "user", "当前原文", 15)
            let input = agent_context_input({current_day: 100}, s, 15, "当前原文")
            assert(input.recent_messages.len() == 14)
            assert(input.current_user_message == "当前原文")
            assert(agent_context_plan({current_day: 100}, s, 15, "当前原文").status == "compact")
            assert(agent_input_bytes({text: "中A"}) == 15)
            true
        "#),
        ("projection_known_fields_only", r#"
            state = {profile: {scene: "日常" sex: "女" age: "30" height: "165" weight: "60"
                activity: "轻活动" allergies: "花生" avoidances: "" preferences: "清淡" special: ""}
                foods: [{id: 7 name: "米" canonical_quantity: 500 canonical_unit: "g"
                    expires_on_day: 120 expiry_precision: "exact" average_item_grams: 0
                    quantity: 500 unit: "g" package_size: 0 package_size_unit: ""
                    source_image_path: "/private/photo.jpg"}] plans: [] stages: []
                    execution_records: [] active: 0 log: ["private-log"]}
            agent_memory = agent_memory_after_confirm(agent_empty_memory(), "少放辣", "平时少放辣", true, true, 100)
            let projection = agent_projection_base("inventory")
            assert(projection.current_day == 100 && projection.entry_context == "inventory")
            assert(projection.inventory_batches[0].food_id == 7)
            assert(projection.profile.allergies == "花生" && projection.soft_memories[0] == "少放辣")
            assert(projection.to_json().search("private") < 0)
            assert(agent_projection_base("unknown") == nil)
            true
        "#),
        ("projection_real_stage_and_accepted_menu", r#"
            state.stages = [{id: 4 kind: "health" name: "均衡阶段" started: 8640000
                days: 7 daily_kcal: 1800 kcal_goal: 12600 protein_goal: 350
                fiber_goal: 175 vitamin_c_goal: 500 consumed_kcal: 300
                intake: [{day: 100 title: "私人执行记录"}]}]
            state.plans = [{id: 7 day: 100 accepted: true consumed: false stage_id: 4
                meals: [{slot: "早餐" title: "米粥" uses: [{food_id: 7 name: "米" grams: 80}]
                    steps: "私人做法"}]}
                {id: 8 day: 100 accepted: false consumed: false stage_id: 4
                    meals: [{slot: "早餐" title: "未确认草稿" uses: []}]}]
            state.active = 7
            let projection = agent_projection_base("menu")
            assert(projection.current_stage.stage_id == 4)
            assert(projection.current_stage.remaining_daily_kcal == 1500)
            assert(projection.daily_menu.menu_id == 7 && projection.daily_menu.status == "accepted")
            assert(projection.daily_menu.meals[0].uses[0].food_id == 7)
            assert(projection.to_json().search("未确认草稿") < 0)
            assert(projection.to_json().search("私人") < 0)
            state.execution_records.push({day: 100 title: "私人摄入"})
            projection = agent_projection_base("menu")
            assert(projection.daily_menu.locked && projection.daily_menu.status == "locked")
            state.active = 0
            state.plans = [{id: 9 day: 100 accepted: true consumed: false
                meals: [{slot: "午餐" title: "豆腐" uses: []}]}]
            projection = agent_projection_base("menu")
            assert(projection.daily_menu.menu_id == 0)
            state.plans[0].consumed = true
            projection = agent_projection_base("menu")
            assert(projection.daily_menu.stage_id == 0)
            fake_day = 101
            projection = agent_projection_base("menu")
            assert(projection.daily_menu.menu_id == 0 && projection.current_stage.stage_id == 4)
            true
        "#),
        ("byte_trigger_under_fifteen", r#"
            let long = ""
            for i in 1200 { long = long + "中" }
            let s = agent_empty_session(100)
            for i in 7 { s = agent_append_to_session(s, "user", long, i) }
            s = agent_append_to_session(s, "user", "当前原文", 8)
            assert(agent_uncompressed_messages(s, 8).len() == 7)
            assert(agent_context_plan({current_day: 100}, s, 8, "当前原文").status == "compact")
            assert(agent_context_plan({large: long + long + long + long + long + long + long}, agent_empty_session(100), 0, "当前原文").status == "too_large")
            assert(agent_context_plan({}, s, 8, long + long).status == "too_large")
            true
        "#),
        ("final_input_budget_never_truncates", r#"
            let large = ""
            for i in 8400 { large = large + "中" }
            let s = agent_empty_session(100)
            s = agent_append_to_session(s, "user", "当前要求", 1)
            let plan = agent_context_plan({profile: {allergies: "花生"} large: large}, s, 1, "当前要求")
            assert(plan.status == "too_large")
            assert(s.messages[0].text == "当前要求")
            let pending = agent_empty_session(100)
            let long = ""
            for i in 1200 { long = long + "中" }
            for i in 8 { pending = agent_append_to_session(pending, "user", long, i) }
            pending = agent_append_to_session(pending, "user", "原文", 8)
            plan = agent_context_plan({profile: {allergies: "花生"}}, pending, 9, "原文")
            assert(plan.status == "compact")
            let after = agent_apply_summary(pending, {summary: "保留花生过敏和明确要求"}, plan.batch.through_id)
            assert(after.messages.len() == 9 && after.summary_through_id > 0)
            plan = agent_context_plan({profile: {allergies: "花生"}}, after, 9, "原文")
            while plan.status == "compact" {
                after = agent_apply_summary(after, {summary: "保留花生过敏和明确要求"}, plan.batch.through_id)
                plan = agent_context_plan({profile: {allergies: "花生"}}, after, 9, "原文")
            }
            assert(plan.status == "ready" && agent_input_bytes(plan.input) < 24576)
            assert(plan.input.profile.allergies == "花生" && plan.input.current_user_message == "原文")
            assert(after.messages.len() == 9)
            true
        "#),
        ("summary_failure_and_success", r#"
            assert(agent_compaction_task().len() < 4096)
            assert(agent_compaction_schema().properties.summary.maxLength == 3000)
            let s = agent_empty_session(100)
            for i in 15 { s = agent_append_to_session(s, "user", "一条消息", i) }
            let batch = agent_compaction_batch(s, 15)
            assert(batch.messages.len() == 6)
            assert(agent_input_bytes({summary: batch.summary messages: batch.messages}) <= 24576)
            assert(agent_apply_summary(s, {summary: ""}, batch.through_id) == nil)
            assert(s.summary_through_id == 0 && s.messages.len() == 15)
            let next = agent_apply_summary(s, {summary: "已确认的要求"}, batch.through_id)
            assert(next.summary_through_id == 6 && next.messages.len() == 15)
            assert(agent_uncompressed_messages(next, 15).len() == 8)
            assert(agent_context_plan({}, next, 15, "一条消息").status == "ready")
            true
        "#),
        ("summary_batches_and_visibility", r#"
            let s = agent_empty_session(100)
            for i in 30 { s = agent_append_to_session(s, "user", "一条消息", i) }
            let first = agent_compaction_batch(s, 30)
            assert(first.messages.len() == 21 && first.through_id == 21)
            let after = agent_apply_summary(s, {summary: "旧要求"}, first.through_id)
            assert(after.messages.len() == 30 && after.summary_through_id == 21)
            let second = agent_compaction_batch(after, 30)
            assert(second.messages.len() == 1 && second.messages[0].id == 22)
            assert(agent_apply_summary(after, {summary: ""}, second.through_id) == nil)
            assert(after.summary_through_id == 21 && after.messages.len() == 30)
            true
        "#),
        ("bounded_compaction_segments", r#"
            let long = ""
            for i in 1200 { long = long + "中" }
            let s = agent_empty_session(100)
            for i in 20 { s = agent_append_to_session(s, "user", long, i) }
            let first = agent_compaction_batch(s, 20)
            assert(first.messages.len() > 0 && first.messages.len() < 11)
            assert(agent_input_bytes({summary: first.summary messages: first.messages}) <= 24576)
            let after = agent_apply_summary(s, {summary: "累计摘要"}, first.through_id)
            assert(after.summary_through_id == first.through_id)
            assert(after.messages.len() == 20)
            let second = agent_compaction_batch(after, 20)
            assert(second.messages[0].id == first.through_id + 1)
            assert(agent_input_bytes({summary: second.summary messages: second.messages}) <= 24576)
            true
        "#),
        ("memory_confirmation_and_expiry", r#"
            let m = agent_empty_memory()
            assert(agent_memory_after_confirm(m, "少放辣", "请少放辣", true, false, 100) == nil)
            assert(agent_memory_after_confirm(m, "花生过敏", "我花生过敏", true, true, 100) == nil)
            m = agent_memory_after_confirm(m, "少放辣", "请少放辣", true, true, 100)
            assert(m.items.len() == 1 && m.items[0].expires_day == 130)
            m = agent_memory_after_confirm(m, "少放辣", "请少放辣", true, true, 105)
            assert(m.items.len() == 1 && m.items[0].last_used_day == 105)
            assert(agent_decode_memory(m.to_json(), 136).items.len() == 0)
            assert(agent_decode_memory("{bad", 100).items.len() == 0)
            true
        "#),
        ("memory_rules_and_limit", r#"
            let m = agent_empty_memory()
            for text in ["偏好甲" "偏好乙" "偏好丙" "偏好丁" "偏好戊" "偏好己" "偏好庚" "偏好辛" "偏好壬" "偏好癸" "偏好子"] {
                m = agent_memory_after_confirm(m, text, text, true, true, 100)
            }
            assert(m.items.len() == 10 && m.next_id == 12)
            assert(m.items[0].text == "偏好乙")
            assert(agent_memory_after_confirm(m, "库存还有米", "库存还有米", true, true, 100) == nil)
            assert(agent_memory_after_confirm(m, "今天少放辣", "今天少放辣", true, true, 100) == nil)
            assert(agent_memory_after_confirm(m, "少放辣", "今天少放辣", true, true, 100) == nil)
            assert(agent_memory_after_confirm(m, "少放辣", "花生过敏，平时少放辣", true, true, 100) == nil)
            assert(agent_memory_after_confirm(m, "米饭", "今晚想吃米饭", true, true, 100) == nil)
            assert(agent_memory_after_confirm(m, "少放辣", "模型建议少放辣", true, true, 100) == nil)
            assert(agent_memory_after_confirm(m, "少放辣", "少放辣", true, false, 100) == nil)
            true
        "#),
        ("menu_memory_final_confirmation", r#"
            agent_memory = agent_empty_memory()
            let menu = {id: 10 accepted: false consumed: false meals: []}
            agent_stage_menu_memory(menu, "平时少放辣", "用户请求")
            assert(agent_memory_pending.menu_id == 10 && agent_memory.items.len() == 0)
            agent_confirm_menu_memory(menu)
            assert(agent_memory.items.len() == 0 && agent_memory_pending == nil)
            agent_stage_menu_memory(menu, "平时少放辣", "用户请求")
            menu.accepted = true
            agent_confirm_menu_memory(menu)
            assert(agent_memory.items.len() == 1 && agent_memory.items[0].text == "平时少放辣")
            assert(agent_memory.items[0].expires_day == 130)
            agent_confirm_menu_memory(menu)
            assert(agent_memory.items.len() == 1)
            agent_stage_menu_memory({id: 11 accepted: false consumed: false meals: []}, "平时少放辣", "用户请求")
            agent_confirm_menu_memory({id: 12 accepted: true consumed: false})
            assert(agent_memory.items.len() == 1)
            agent_stage_menu_memory({id: 13 accepted: false consumed: false meals: []}, "花生过敏，平时少放辣", "用户请求")
            assert(agent_memory_pending == nil)
            agent_stage_menu_memory({id: 14 accepted: false consumed: false meals: []}, "平时少放辣", "库存移除")
            assert(agent_memory_pending == nil)
            let changed = {id: 16 accepted: false consumed: false meals: []}
            agent_stage_menu_memory(changed, "平时少放辣", "用户请求")
            changed.meals.push({title: "菜单已被改动"})
            changed.accepted = true
            agent_confirm_menu_memory(changed)
            assert(agent_memory.items.len() == 1)
            agent_stage_menu_memory({id: 15 accepted: false consumed: false meals: []}, "平时少放辣", "用户请求")
            fake_day = 101
            agent_ensure_today()
            assert(agent_memory_pending == nil)
            true
        "#),
        ("menu_memory_write_failure_keeps_confirmation", r#"
            agent_memory = agent_empty_memory()
            let menu = {id: 20 accepted: false consumed: false meals: []}
            agent_stage_menu_memory(menu, "平时少放辣", "用户请求")
            menu.accepted = true
            disk.fail = true
            agent_confirm_menu_memory(menu)
            assert(menu.accepted && agent_memory.items.len() == 0 && agent_memory_pending == nil)
            disk.fail = false
            true
        "#),
        ("production_menu_save_and_accept", r#"
            agent_session = agent_empty_session(100)
            agent_memory = agent_empty_memory()
            agent_input = "昨日未发送"
            agent_current_id = 3
            agent_memory_pending = {menu_id: 99 day: 100 candidate: "旧偏好" user_text: "旧偏好"}
            fake_day = 101
            let meals = [{slot: "早餐" title: "米粥" uses: [{food_id: 7 name: "米" grams: 80}]}]
            let menu = save_day_menu(meals, "用户请求", "在线 AI", true)
            assert(menu.id == 1 && menu.day == 101)
            assert(agent_session.day == 101 && agent_session.messages.len() == 0)
            assert(agent_input == "" && agent_current_id == 0)
            assert(agent_memory_pending == nil && agent_memory.items.len() == 0)
            agent_stage_menu_memory(menu, "平时少放辣", "用户请求")
            assert(agent_memory_pending.menu_id == menu.id)
            accept()
            assert(state.plans[0].accepted && state.active == 1)
            assert(agent_memory.items.len() == 1 && agent_memory.items[0].text == "平时少放辣")
            assert(agent_memory_pending == nil)
            true
        "#),
        ("production_accept_memory_failure", r#"
            agent_session = agent_empty_session(100)
            agent_memory = agent_empty_memory()
            let meals = [{slot: "午餐" title: "豆腐" uses: [{food_id: 8 name: "豆腐" grams: 90}]}]
            let menu = save_day_menu(meals, "用户请求", "在线 AI", true)
            agent_stage_menu_memory(menu, "平时少放辣", "用户请求")
            disk.fail = true
            accept()
            assert(state.plans[0].accepted && state.active == 1)
            assert(agent_memory.items.len() == 0 && agent_memory_pending == nil)
            true
        "#),
        ("text_entry_and_contract", r#"
            agent_load_session()
            for i in [0 2 3] {
                tab = i
                assert(agent_entry_allowed())
                agent_open_panel()
                assert(agent_open && agent_origin_tab == i)
                if i == 0 { assert(agent_append("user", "同一会话") == 1) }
                assert(agent_snapshot(1, "同一会话").entry == agent_entry_context(i))
                agent_close_panel()
                assert(!agent_open && agent_session.messages.len() == 1)
            }
            tab = 1
            assert(!agent_entry_allowed())
            tab = 0 onboarding_step = 3
            assert(!agent_entry_allowed())
            onboarding_step = 4 pending = true
            assert(!agent_entry_allowed())
            pending = false intake_draft = {rows: []}
            assert(!agent_entry_allowed())
            intake_draft = nil tab = 2 market = {tab: 0}
            assert(!agent_entry_allowed())
            market = nil tab = 0
            assert(agent_entry_allowed())
            agent_input = "先看首页"
            assert(agent_append("user", "先看首页") == 2)
            assert(agent_snapshot_matches(agent_snapshot(2, "先看首页")))
            assert(agent_task().len() < 4096)
            assert(agent_schema().to_json().len() < 8192)
            assert(agent_valid_envelope({reply: "好的" tool_name: "none" tool_args: {} memory_candidate: ""}))
            assert(!agent_valid_envelope({reply: "" tool_name: "none" tool_args: {} memory_candidate: ""}))
            assert(!agent_valid_envelope({reply: "好的" tool_name: "unknown" tool_args: {} memory_candidate: ""}))
            assert(!agent_valid_envelope({reply: "好的" tool_name: "none" tool_args: {x: 1} memory_candidate: ""}))
            assert(!agent_valid_envelope({reply: "好的" tool_name: "none" tool_args: {} memory_candidate: "偏好"}))
            assert(!agent_valid_envelope({reply: "好的" tool_name: "none" tool_args: {}
                memory_candidate: "" extra: "untrusted"}))
            let long = ""
            for i in 1201 { long = long + "中" }
            assert(!agent_valid_envelope({reply: long tool_name: "none" tool_args: {} memory_candidate: ""}))
            let oversized = ""
            for i in 6000 { oversized = oversized + "中" }
            assert(!agent_valid_envelope({reply: "好的" tool_name: "none" tool_args: {}
                memory_candidate: "" extra: oversized}))
            let max_reply = ""
            let max_memory = ""
            for i in 1200 { max_reply = max_reply + "中" }
            for i in 120 { max_memory = max_memory + "中" }
            assert(agent_input_bytes({reply: max_reply tool_name: "propose_menu_generate"
                tool_args: {} memory_candidate: max_memory}) < 16384)
            true
        "#),
        ("text_one_model_call_and_retry", r#"
            let calls = []
            let callback = nil
            host = {request: |name, args, cb| { calls.push({name: name args: args}) callback = cb 1 }}
            agent_open_panel()
            agent_input = "  冰箱里有什么  "
            agent_send()
            assert(agent_phase == "answering" && calls.len() == 1)
            assert(calls[0].name == "model.complete" && calls[0].args.class == "strong")
            assert(calls[0].args.input.current_user_message == "  冰箱里有什么  ")
            assert(calls[0].args.input.recent_messages.len() == 0)
            agent_close_panel()
            tab = 2
            agent_open_panel()
            assert(agent_phase == "answering" && agent_session.messages.len() == 1)
            callback({is_ok: true data: {output: {reply: "目前没有已确认的库存。" tool_name: "none" tool_args: {} memory_candidate: ""}}})
            agent_watchdog()
            assert(agent_phase == "idle" && agent_session.messages.len() == 2)
            assert(agent_session.messages[1].text == "目前没有已确认的库存。")
            assert(agent_input == "" && agent_current_id == 0)
            agent_close_panel()
            tab = 3
            agent_open_panel()
            assert(agent_session.messages.len() == 2 && agent_origin_tab == 3)
            true
        "#),
        ("text_compaction_then_one_answer", r#"
            let calls = []
            let callback = nil
            host = {request: |name, args, cb| { calls.push(args) callback = cb 1 }}
            agent_open_panel()
            for i in 14 { assert(agent_append("user", "旧消息") > 0) }
            agent_input = "当前原文"
            agent_send()
            assert(agent_phase == "compacting" && calls.len() == 1 && calls[0].class == "fast")
            callback({is_ok: true data: {output: {summary: "此前讨论了库存"}}})
            agent_watchdog()
            assert(agent_phase == "answering" && calls.len() == 2 && calls[1].class == "strong")
            assert(agent_session.summary_through_id > 0 && agent_session.messages.len() == 15)
            assert(calls[1].input.current_user_message == "当前原文")
            assert(calls[1].input.recent_messages.len() <= 8)
            callback({is_ok: true data: {output: {reply: "我会按当前原文回答。" tool_name: "none" tool_args: {} memory_candidate: ""}}})
            agent_watchdog()
            assert(agent_session.messages.len() == 16 && agent_phase == "idle")
            true
        "#),
        ("text_compaction_failure_stops_answer", r#"
            let calls = []
            let callback = nil
            host = {request: |name, args, cb| { calls.push(args) callback = cb 1 }}
            agent_open_panel()
            let business_before = state.to_json()
            for i in 14 { assert(agent_append("user", "旧消息") > 0) }
            agent_input = "当前原文"
            agent_send()
            assert(calls.len() == 1 && calls[0].class == "fast")
            callback({is_ok: false error: "no provider"})
            agent_watchdog()
            assert(calls.len() == 1 && agent_phase == "idle")
            assert(agent_session.summary_through_id == 0 && agent_session.messages.len() == 15)
            assert(agent_input == "当前原文" && agent_current_id == 15)
            assert(state.to_json() == business_before)
            true
        "#),
        ("text_invalid_provider_and_stale_reply", r#"
            let calls = []
            let callback = nil
            host = {request: |name, args, cb| { calls.push(args) callback = cb 1 }}
            agent_open_panel()
            agent_input = "请回答"
            agent_send()
            callback({is_ok: true data: {output: {reply: "" tool_name: "none" tool_args: {} memory_candidate: ""}}})
            agent_watchdog()
            assert(agent_phase == "idle" && agent_session.messages.len() == 1 && agent_input == "请回答")
            agent_send()
            assert(calls.len() == 2 && agent_session.messages.len() == 1)
            callback({is_ok: true data: {output: {reply: "改好了" tool_name: "propose_inventory_edit" tool_args: {} memory_candidate: ""}}})
            agent_watchdog()
            assert(agent_session.messages.len() == 1 && agent_current_id == 1)
            agent_send()
            callback({is_ok: false error: "no provider"})
            agent_watchdog()
            assert(agent_session.messages.len() == 1 && agent_input == "请回答")
            assert(agent_provider_error({error: "no_provider: No AI provider is set up."}) ==
                "宿主没有可用的 AI 提供方，请在 AI 提供方设置中核对后重试。")
            assert(agent_provider_error({error: "bad_request: Invalid schema."}) ==
                "本轮请求未通过宿主校验，请缩短问题后重试。")
            agent_send()
            let late = callback
            fake_time = fake_time + 96
            agent_watchdog()
            assert(agent_phase == "idle" && agent_session.messages.len() == 1)
            late({is_ok: true data: {output: {reply: "迟到" tool_name: "none" tool_args: {} memory_candidate: ""}}})
            agent_watchdog()
            assert(agent_session.messages.len() == 1)
            agent_send()
            assert(agent_phase == "answering")
            late({is_ok: true data: {output: {reply: "上一轮迟到"
                tool_name: "none" tool_args: {} memory_candidate: ""}}})
            agent_watchdog()
            assert(agent_phase == "answering" && agent_session.messages.len() == 1)
            callback({is_ok: true data: {output: {reply: "新一轮回复"
                tool_name: "none" tool_args: {} memory_candidate: ""}}})
            agent_watchdog()
            assert(agent_phase == "idle" && agent_session.messages[1].text == "新一轮回复")
            true
        "#),
        ("text_snapshot_changes", r#"
            agent_open_panel()
            agent_input = "当前消息"
            assert(agent_append("user", "当前消息") == 1)
            let snapshot = agent_snapshot(1, "当前消息")
            assert(snapshot.authority.stage_id == 0 && snapshot.authority.stage_revision == "")
            assert(snapshot.authority.menu_id == 0 && snapshot.authority.menu_status == "none"
                && snapshot.authority.menu_revision == "")
            assert(!snapshot.authority.menu_locked)
            assert(agent_snapshot_matches(snapshot))
            state.revision = 2
            assert(!agent_snapshot_matches(snapshot))
            state.revision = 1 state.profile_revision = 2
            assert(!agent_snapshot_matches(snapshot))
            state.profile_revision = 1
            state.stages.push({id: 4 daily_kcal: 1800})
            assert(!agent_snapshot_matches(snapshot))
            state.stages = []
            state.plans.push({id: 1 day: 100 accepted: true consumed: false
                title: "今日菜单" meals: []})
            state.active = 1
            assert(!agent_snapshot_matches(snapshot))
            let menu_snapshot = agent_snapshot(1, "当前消息")
            assert(menu_snapshot.authority.menu_id == 1 && menu_snapshot.authority.menu_status == "accepted"
                && menu_snapshot.authority.menu_revision != "")
            assert(!menu_snapshot.authority.menu_locked)
            state.plans[0].title = "调整后的菜单"
            assert(!agent_snapshot_matches(menu_snapshot))
            state.plans[0].title = "今日菜单"
            state.execution_records.push({day: 100})
            assert(!agent_snapshot_matches(menu_snapshot))
            assert(agent_authority_marker().menu_locked)
            assert(agent_authority_marker().menu_status == "locked")
            state.execution_records = []
            state.plans[0].id = 2 state.active = 2
            assert(!agent_snapshot_matches(menu_snapshot))
            state.plans = [] state.active = 0 fake_day = 101
            assert(!agent_snapshot_matches(snapshot))
            fake_day = 100 agent_input = "修改了输入"
            assert(!agent_snapshot_matches(snapshot))
            agent_input = "当前消息" agent_session.next_message_id = 3
            assert(!agent_snapshot_matches(snapshot))
            agent_session.next_message_id = 2 pending = true
            assert(!agent_snapshot_matches(snapshot))
            pending = false ai_busy = true
            assert(!agent_snapshot_matches(snapshot))
            ai_busy = false agent_session.messages[0].text = "被改写的消息"
            assert(!agent_snapshot_matches(snapshot))
            true
        "#),
        ("text_stage_and_callback_guard", r#"
            agent_open_panel()
            agent_input = "请看当前阶段"
            assert(agent_append("user", "请看当前阶段") == 1)
            agent_current_id = 1
            state.stages.push({id: 4 daily_kcal: 1800})
            let snapshot = agent_snapshot(1, "请看当前阶段")
            assert(snapshot.authority.stage_id == 4 && snapshot.authority.stage_revision != "")
            assert(agent_snapshot_matches(snapshot))
            state.stages[0].daily_kcal = 1900
            assert(!agent_snapshot_matches(snapshot))
            state.stages[0].daily_kcal = 1800
            state.stages[0].id = 5
            assert(!agent_snapshot_matches(snapshot))
            state.stages = []
            let callback = nil
            host = {request: |name, args, cb| { callback = cb 1 }}
            agent_send()
            assert(agent_phase == "answering")
            state.execution_records.push({day: 100})
            callback({is_ok: true data: {output: {reply: "旧状态的回复"
                tool_name: "none" tool_args: {} memory_candidate: ""}}})
            agent_watchdog()
            assert(agent_phase == "idle" && agent_session.messages.len() == 1)
            assert(agent_input == "请看当前阶段" && agent_current_id == 1)
            assert(agent_error != "")
            state.execution_records = []
            agent_send()
            assert(agent_phase == "answering" && agent_session.messages.len() == 1)
            callback({is_ok: true data: {output: {reply: "当前状态的回复"
                tool_name: "none" tool_args: {} memory_candidate: ""}}})
            agent_watchdog()
            assert(agent_phase == "idle" && agent_session.messages.len() == 2)
            assert(agent_session.messages[1].text == "当前状态的回复")
            true
        "#),
        ("text_day_rollover", r#"
            agent_open_panel()
            agent_input = "昨天的问题"
            assert(agent_append("user", "昨天的问题") == 1)
            fake_day = 101
            agent_watchdog()
            assert(agent_session.day == 101 && agent_session.messages.len() == 0)
            assert(agent_input == "" && agent_current_id == 0)
            true
        "#),
        ("proposal_inventory_contract_and_review", r#"
            assert(agent_task().len() < 4096)
            assert(agent_public_reply("豆腐（food_id: 7）请核对") == "豆腐请核对")
            assert(agent_public_reply("豆腐 230 克，内部 food_id 为 1。") == "豆腐 230 克。")
            agent_load_session()
            let row = {name: "鸡蛋" quantity_text: "2" unit: "个" package_size_text: ""
                package_size_unit: "" average_item_grams_text: "" remaining_days_text: "2"
                printed_expires_on: "" kcal_text: "" protein_text: "" fiber_text: "" vitamin_c_text: ""}
            let snap = {day: 100 profile_revision: 1 inventory_revision: 1
                authority: agent_authority_marker() message_text: "加入两个鸡蛋"}
            let output = {reply: "请核对鸡蛋" tool_name: "propose_inventory_add"
                tool_args: {rows: [row]} memory_candidate: ""}
            let before = state.to_json()
            let proposal = agent_proposal_from(output, snap)
            assert(proposal != nil && proposal.rows.len() == 1 && state.to_json() == before)
            output.tool_args = {rows: []}
            assert(agent_proposal_from(output, snap) == nil)
            output.tool_args = {rows: "not an array"}
            assert(agent_proposal_from(output, snap) == nil)
            output.tool_args = {rows: [row] extra: 1}
            assert(agent_proposal_from(output, snap) == nil)
            output.tool_args = {rows: [row]}
            output.memory_candidate = "少盐"
            assert(agent_proposal_from(output, snap) == nil)
            output.memory_candidate = ""
            agent_proposal = agent_proposal_from(output, snap)
            agent_open_review()
            assert(tab == 2 && intake_draft.rows.len() == 1 && agent_review != nil)
            assert(!agent_entry_allowed())
            assert(state.to_json() == before)
            agent_finish_review("已取消")
            assert(agent_review == nil && tab == 0 && state.to_json() == before)
            assert(agent_session.messages[0].kind == "local")
            true
        "#),
        ("proposal_specific_batch_and_handoff", r#"
            state.foods = [{id: 7 name: "豆腐" canonical_unit: "g" quantity: 100 unit: "g"}
                {id: 8 name: "豆腐" canonical_unit: "g" quantity: 80 unit: "g"}]
            let row = {name: "豆腐" quantity_text: "90" unit: "g" package_size_text: ""
                package_size_unit: "" average_item_grams_text: "" remaining_days_text: ""
                printed_expires_on: "" kcal_text: "" protein_text: "" fiber_text: "" vitamin_c_text: ""}
            let snap = {day: 100 profile_revision: 1 inventory_revision: 1
                authority: agent_authority_marker() message_text: "修改第二批豆腐"}
            let edit = {reply: "请核对" tool_name: "propose_inventory_edit"
                tool_args: {food_id: 8 row: row} memory_candidate: ""}
            assert(agent_proposal_from(edit, snap).food.id == 8)
            let vague = snap.to_json().parse_json()
            vague.message_text = "修改豆腐"
            assert(agent_proposal_from(edit, vague) == nil)
            edit.tool_args.food_id = 99
            assert(agent_proposal_from(edit, snap) == nil)
            edit.tool_args.food_id = "8"
            assert(agent_proposal_from(edit, snap) == nil)
            edit.tool_args.food_id = 8
            edit.tool_args.row.name = "鸡蛋"
            assert(agent_proposal_from(edit, snap) == nil)
            let remove = {reply: "请核对" tool_name: "propose_inventory_remove"
                tool_args: {food_id: 7 reason: "变质"} memory_candidate: ""}
            let remove_snap = snap.to_json().parse_json()
            remove_snap.message_text = "移除第一批豆腐"
            assert(agent_proposal_from(remove, remove_snap).food.id == 7)
            remove.tool_args.reason = ""
            assert(agent_proposal_from(remove, remove_snap) == nil)
            remove.tool_args = {food_id: 99 reason: "变质"}
            assert(agent_proposal_from(remove, remove_snap) == nil)
            remove.tool_args = {food_id: 7 reason: "变质" extra: true}
            assert(agent_proposal_from(remove, remove_snap) == nil)
            let eat = {reply: "请记录" tool_name: "handoff_consumption"
                tool_args: {text: "我吃了两个鸡蛋" food_hints: ["鸡蛋"]} memory_candidate: ""}
            assert(agent_proposal_from(eat, snap).tool_name == "handoff_consumption")
            eat.tool_args = {text: "我吃了两个鸡蛋"}
            assert(agent_proposal_from(eat, snap) == nil)
            eat.tool_args = {text: "我吃了两个鸡蛋" food_hints: ["鸡蛋"]}
            eat.tool_args.food_hints = [7]
            let invalid = nil
            try { invalid = agent_proposal_from(eat, snap) } catch { }
            assert(invalid == nil)
            true
        "#),
        ("proposal_menu_lock_and_revision", r#"
            state.stages = [{id: 4 daily_kcal: 1800}]
            state.foods = [{id: 7 name: "豆腐" canonical_quantity: 300 canonical_unit: "g" eligible: true}]
            let snap = {day: 100 profile_revision: 1 inventory_revision: 1
                authority: agent_authority_marker() message_text: "安排三餐"}
            let step1 = {action: "清洗" food_ids: [7] minutes: 1}
            let step2 = {action: "充分煮熟" food_ids: [7] minutes: 10}
            let menu = {feasible: true reason: "家常" meals: [
                {title: "水煮" minutes: 20 uses: [{food_id: 7 grams: 50}] steps: [step1 step2]}
                {title: "水煮" minutes: 20 uses: [{food_id: 7 grams: 60}] steps: [step1 step2]}
                {title: "水煮" minutes: 20 uses: [{food_id: 7 grams: 70}] steps: [step1 step2]}]}
            let output = {reply: "请核对" tool_name: "propose_menu_generate"
                tool_args: menu memory_candidate: ""}
            let before = state.to_json()
            let proposal = agent_proposal_from(output, snap)
            assert(proposal != nil && proposal.menu.meals.len() == 3)
            assert(proposal.menu.meals[0].slot == "早餐" && state.to_json() == before)
            assert(agent_marker_matches(proposal.marker))
            state.revision = 2
            assert(!agent_marker_matches(proposal.marker))
            state.revision = 1
            output.tool_args = {feasible: true reason: "家常" meals: [menu.meals[0]]}
            assert(agent_proposal_from(output, snap) == nil)
            output.tool_args = menu.to_json().parse_json()
            output.tool_args.meals[0].uses[0].grams = 301
            assert(agent_proposal_from(output, snap) == nil)
            output.tool_args = menu
            output.tool_args = {feasible: true reason: "家常" meals: "wrong"}
            assert(agent_proposal_from(output, snap) == nil)
            output.tool_args = menu
            state.execution_records.push({day: 100})
            assert(agent_proposal_from(output, snap) == nil)
            state.execution_records = []
            output.tool_name = "propose_menu_adjust"
            assert(agent_proposal_from(output, snap) == nil)
            state.plans = [{id: 9 day: 100 accepted: true consumed: false stage_id: 4 title: "旧菜单"
                meals: [{slot: "早餐" title: "旧早餐" uses: [{food_id: 7 name: "豆腐" grams: 50}]}]}]
            state.active = 9
            assert(agent_proposal_from(output, snap) != nil)
            state.execution_records.push({day: 100})
            assert(agent_proposal_from(output, snap) == nil)
            assert(!agent_valid_envelope({reply: "改档案" tool_name: "profile_edit"
                tool_args: {} memory_candidate: ""}))
            true
        "#),
        ("proposal_menu_one_correction", r#"
            state.stages = [{id: 4 kind: "health" name: "当前阶段" started: 8640000
                days: 7 daily_kcal: 1800 kcal_goal: 12600 protein_goal: 350
                fiber_goal: 175 vitamin_c_goal: 500 consumed_kcal: 0}]
            agent_open_panel()
            agent_input = "请安排完整三餐"
            let calls = 0
            let callback = nil
            host = {request: |name, args, cb| { calls = calls + 1 callback = cb calls }}
            agent_send()
            assert(calls == 1 && agent_phase == "answering")
            let invalid = {reply: "请核对" tool_name: "propose_menu_generate"
                tool_args: {feasible: true reason: "家常" meals: []} memory_candidate: ""}
            callback({is_ok: true data: {output: invalid}})
            agent_watchdog()
            assert(calls == 2 && agent_correction == 1 && agent_phase == "answering")
            callback({is_ok: true data: {output: invalid}})
            agent_watchdog()
            assert(calls == 2 && agent_phase == "idle" && agent_proposal == nil)
            assert(agent_session.messages.len() == 1 && state.plans.len() == 0)
            true
        "#),
        ("proposal_menu_confirm_memory", r#"
            state.stages = [{id: 4 daily_kcal: 1800}]
            state.foods = [{id: 7 name: "豆腐" canonical_quantity: 300 canonical_unit: "g" eligible: true}]
            agent_load_session()
            agent_memory = agent_empty_memory()
            let step1 = {action: "清洗" food_ids: [7] minutes: 1}
            let step2 = {action: "充分煮熟" food_ids: [7] minutes: 10}
            let output = {feasible: true reason: "少油家常" meals: [
                {title: "水煮" minutes: 20 uses: [{food_id: 7 grams: 50}] steps: [step1 step2]}
                {title: "水煮" minutes: 20 uses: [{food_id: 7 grams: 60}] steps: [step1 step2]}
                {title: "水煮" minutes: 20 uses: [{food_id: 7 grams: 70}] steps: [step1 step2]}]}
            let draft = agent_menu_from_output(output, "平时少油安排三餐")
            assert(draft != nil)
            let marker = {day: 100 profile_revision: 1 inventory_revision: 1
                authority: agent_authority_marker()}
            assert(agent_marker_matches(marker))
            assert(menu_issue(draft) == "" && validate(draft))
            agent_review = {tool_name: "propose_menu_generate" marker: marker menu: draft
                user_text: "平时少油安排三餐" memory_candidate: "少油" origin: 2}
            let foods_before = state.foods.to_json()
            agent_confirm_menu_review()
            assert(state.plans.len() == 1)
            assert(state.plans[0].accepted)
            assert(state.active == state.plans[0].id)
            assert(state.foods.to_json() == foods_before)
            assert(agent_memory.items.len() == 1)
            assert(agent_memory.items[0].text == "少油")
            assert(tab == 2 && agent_review == nil)
            true
        "#),
        ("voice_fallback_and_transcript_draft", r#"
            agent_load_session()
            agent_open_panel()
            let calls = []
            let callback = nil
            host = {request: |name, args, cb| { calls.push(name) callback = cb }}
            voice_capability = "unsupported"
            agent_microphone()
            assert(calls.len() == 0 && agent_error == "当前宿主暂不支持语音识别，请使用文字输入。")
            voice_capability = "unconfigured"
            agent_microphone()
            assert(calls.len() == 0 && agent_error.search("MiniMax") >= 0)
            voice_capability = "ready"
            agent_input = "先前文字"
            disk.voice = true
            agent_microphone()
            assert(calls.len() == 1 && calls[0] == "microphone.permission.status")
            callback({is_ok: true data: {supported: true app_policy_granted: true
                app_consent: true os_permission: "granted"}})
            voice_watchdog()
            assert(!disk.voice && calls[1] == "microphone.record_start")
            let session = "12345678-1234-1234-1234-123456789012"
            callback({is_ok: true data: {session: session status: "starting"}})
            voice_watchdog()
            assert(voice_phase == 2 && voice_session == session)
            voice_stop()
            assert(calls[2] == "microphone.record_stop" && voice_phase == 5)
            callback({is_ok: true data: {session: session status: "stopping"}})
            voice_watchdog()
            fake_time = fake_time + 1
            voice_watchdog()
            assert(calls[3] == "microphone.record_status")
            callback({is_ok: true data: {session: session status: "saved" path: voice_path}})
            voice_watchdog()
            assert(calls[4] == "model.transcribe" && voice_phase == 3)
            callback({is_ok: true data: {text: "请买 Greek yogurt"}})
            voice_watchdog()
            assert(voice_phase == 0 && agent_input == "先前文字\n请买 Greek yogurt")
            assert(ui_state.text == agent_input && ui_state.focused)
            assert(agent_session.messages.len() == 0 && state.foods.len() == 0)
            agent_input = "请买无糖 Greek yogurt"
            agent_send()
            assert(agent_session.messages.len() == 1)
            assert(agent_session.messages[0].text == "请买无糖 Greek yogurt")
            assert(calls.len() == 6 && calls[5] == "model.complete")
            true
        "#),
        ("voice_rate_retries_before_permission", r#"
            agent_load_session()
            agent_open_panel()
            let calls = []
            let callback = nil
            host = {request: |name, args, cb| { calls.push(name) callback = cb }}
            probe_voice()
            assert(calls.len() == 1 && calls[0] == "model.transcribe_capability")
            let old_probe = callback
            callback({is_ok: false error: "rate: Model workers are busy; retry later."})
            voice_watchdog()
            assert(voice_capability == "checking" && calls.len() == 1)
            agent_microphone()
            assert(calls.len() == 1 && agent_error.search("正在检查") >= 0)
            fake_time = fake_time + 1
            voice_watchdog()
            assert(calls.len() == 2 && calls[1] == "model.transcribe_capability")
            callback({is_ok: true data: {schema: 1 supported: true configured: true}})
            old_probe({is_ok: false error: "rate: late response"})
            voice_watchdog()
            assert(voice_capability == "ready")
            agent_microphone()
            assert(calls.len() == 3 && calls[2] == "microphone.permission.status")
            true
        "#),
        ("voice_late_status_cannot_hide_stop", r#"
            agent_load_session()
            agent_open_panel()
            let calls = []
            let callback = nil
            host = {request: |name, args, cb| { calls.push(name) callback = cb }}
            voice_capability = "ready"
            agent_microphone()
            callback({is_ok: true data: {supported: true app_policy_granted: true
                app_consent: true os_permission: "granted"}})
            voice_watchdog()
            let session = "12345678-1234-1234-1234-123456789012"
            callback({is_ok: true data: {session: session status: "starting"}})
            voice_watchdog()
            fake_time = fake_time + 1
            voice_watchdog()
            assert(calls[2] == "microphone.record_status")
            let old_status = callback
            voice_stop()
            assert(calls[3] == "microphone.record_stop")
            callback({is_ok: true data: {session: session status: "stopping"}})
            old_status({is_ok: true data: {session: session status: "recording"}})
            voice_watchdog()
            assert(voice_action == "" && voice_phase == 5)
            fake_time = fake_time + 1
            voice_watchdog()
            assert(calls[4] == "microphone.record_status")
            true
        "#),
        ("voice_denied_empty_cancel_stale", r#"
            agent_load_session()
            agent_open_panel()
            let calls = []
            let callback = nil
            host = {request: |name, args, cb| { calls.push(name) callback = cb }}
            voice_capability = "ready"
            agent_input = "保留我"
            agent_microphone()
            callback({is_ok: true data: {supported: true app_policy_granted: true
                app_consent: false os_permission: "settings_required"}})
            voice_watchdog()
            assert(voice_phase == 0 && agent_input == "保留我" && calls.len() == 1)
            agent_microphone()
            let old = callback
            agent_close_panel()
            old({is_ok: true data: {supported: true app_policy_granted: true
                app_consent: true os_permission: "granted"}})
            voice_watchdog()
            assert(voice_phase == 0 && calls.len() == 2)
            agent_open_panel()
            agent_microphone()
            fake_time = fake_time + 181
            voice_watchdog()
            assert(voice_phase == 0 && agent_input == "保留我")
            true
        "#),
        ("voice_auto_stop_empty_and_busy", r#"
            agent_load_session()
            agent_open_panel()
            let calls = []
            let callback = nil
            host = {request: |name, args, cb| { calls.push(name) callback = cb }}
            probe_voice()
            assert(calls[0] == "model.transcribe_capability")
            callback({is_ok: true data: {schema: 1 supported: true configured: false}})
            voice_watchdog()
            assert(voice_capability == "unconfigured")
            agent_microphone()
            assert(calls.len() == 1)
            voice_capability = "ready"
            agent_input = "旧内容"
            agent_microphone()
            callback({is_ok: true data: {supported: true app_policy_granted: true
                app_consent: true os_permission: "granted"}})
            voice_watchdog()
            let session = "12345678-1234-1234-1234-123456789012"
            callback({is_ok: true data: {session: session status: "starting"}})
            voice_watchdog()
            fake_time = fake_time + 31
            voice_watchdog()
            assert(calls[3] == "microphone.record_status")
            callback({is_ok: true data: {session: session status: "saved" path: voice_path}})
            voice_watchdog()
            assert(calls[4] == "model.transcribe")
            callback({is_ok: true data: {text: "  "}})
            voice_watchdog()
            assert(voice_phase == 0 && agent_input == "旧内容")
            assert(agent_session.messages.len() == 0)
            agent_proposal = {tool_name: "none"}
            agent_microphone()
            assert(voice_phase == 0 && calls.len() == 6)
            agent_proposal = nil
            agent_microphone()
            callback({is_ok: true data: {supported: true app_policy_granted: true
                app_consent: true os_permission: "granted"}})
            voice_watchdog()
            callback({is_ok: true data: {session: session status: "starting"}})
            voice_watchdog()
            assert(voice_phase == 2)
            agent_close_panel()
            assert(voice_phase == 0 && calls[calls.len()-1] == "microphone.record_cancel")
            true
        "#),
        ("voice_permission_request_and_late_start", r#"
            agent_load_session()
            agent_open_panel()
            let calls = []
            let callback = nil
            host = {request: |name, args, cb| { calls.push(name) callback = cb }}
            voice_capability = "ready"
            agent_input = "已有草稿"
            agent_microphone()
            callback({is_ok: true data: {supported: true app_policy_granted: true
                app_consent: false os_permission: "not_determined"}})
            voice_watchdog()
            assert(calls[1] == "microphone.permission.request")
            callback({is_ok: true data: {supported: true app_policy_granted: true
                app_consent: false os_permission: "denied"}})
            voice_watchdog()
            assert(voice_phase == 0 && agent_input == "已有草稿")
            agent_microphone()
            callback({is_ok: true data: {supported: true app_policy_granted: true
                app_consent: false os_permission: "not_determined"}})
            voice_watchdog()
            callback({is_ok: true data: {supported: true app_policy_granted: true
                app_consent: true os_permission: "granted"}})
            voice_watchdog()
            assert(calls[calls.len()-1] == "microphone.record_start")
            let late = callback
            agent_close_panel()
            late({is_ok: true data: {session: "12345678-1234-1234-1234-123456789012" status: "starting"}})
            assert(calls[calls.len()-1] == "microphone.record_cancel")
            assert(voice_phase == 0 && agent_input == "已有草稿")
            true
        "#),
    ];
    for (name, script) in cases {
        let mut host = ScriptVmHost::new((), ());
        let mut vm = ScriptVm { host: &mut host, bx: Box::new(ScriptVmBase::new()) };
        vm.bx.captured_errors = Some(Vec::new());
        let code = format!("{prelude}\n{helpers}\n{voice_helpers}\n{menu_save}\n{menu_accept}\n{recipe_helpers}\n{menu_builder}\n{batch_helpers}\n{draft_helper}\n{script}\n;");
        let result = vm.with_instruction_limit(2_000_000, |vm| vm.eval(ScriptMod {
            file: format!("agent_core_{name}.splash"), code, ..Default::default()
        }));
        let errors = vm.take_errors();
        assert!(errors.is_empty() && result.as_bool() == Some(true), "{name}: {errors:?}, result={result:?}");
        println!("{name}: ok");
    }
}
