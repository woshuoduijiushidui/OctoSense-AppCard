use makepad_script::*;
use std::fs;
use std::path::Path;

fn main() {
    let app = Path::new(env!("CARGO_MANIFEST_DIR")).parent().unwrap().parent().unwrap();
    let source = fs::read_to_string(app.join("bundle/main.splash")).unwrap();
    let start = source.find("fn agent_empty_session(day)").unwrap();
    let end = source.find("fn canonical_unit(unit)").unwrap();
    let helpers = &source[start..end];
    let prelude = r#"
        use mod.std.assert
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
        let state = {profile: {done: true scene: "日常健康" sex: "女" age: "30" height: "165"
            weight: "60" activity: "轻活动" allergies: "" avoidances: "" preferences: "" special: ""}
            foods: [] plans: [] revision: 1 profile_revision: 1}
        let disk = {session: "" memory: "" fail: false}
        let fs = {
            exists: |path| { if path == "agent-session.json" { disk.session != "" } else { disk.memory != "" } }
            read: |path| { if path == "agent-session.json" { disk.session } else { disk.memory } }
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
        let show_shopping = false
        let ai_busy = false
        let voice_phase = 0
        let storage_blocked = false
        let use_ai = true
        fn today_day(){ fake_day }
        fn time_now(){ fake_time }
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
            fake_day = 101
            agent_ensure_today()
            assert(agent_session.day == 101 && agent_session.messages.len() == 0)
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
                    source_image_path: "/private/photo.jpg"}] log: ["private-log"]}
            agent_memory = agent_memory_after_confirm(agent_empty_memory(), "少放辣", "平时少放辣", true, true, 100)
            let projection = agent_projection_base("inventory")
            assert(projection.current_day == 100 && projection.entry_context == "inventory")
            assert(projection.inventory_batches[0].food_id == 7)
            assert(projection.profile.allergies == "花生" && projection.soft_memories[0] == "少放辣")
            assert(projection.to_json().search("private") < 0)
            assert(agent_projection_base("unknown") == nil)
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
        ("text_entry_and_contract", r#"
            agent_load_session()
            for i in 3 {
                tab = i
                assert(agent_entry_allowed())
                agent_open_panel()
                assert(agent_open && agent_origin_tab == i)
                if i == 0 { assert(agent_append("user", "同一会话") == 1) }
                assert(agent_snapshot(1, "同一会话").entry == agent_entry_context(i))
                agent_close_panel()
                assert(!agent_open && agent_session.messages.len() == 1)
            }
            tab = 3
            assert(!agent_entry_allowed())
            tab = 0 onboarding_step = 3
            assert(!agent_entry_allowed())
            onboarding_step = 4 pending = true
            assert(!agent_entry_allowed())
            pending = false intake_draft = {rows: []}
            assert(!agent_entry_allowed())
            intake_draft = nil tab = 2 show_shopping = true
            assert(!agent_entry_allowed())
            tab = 0
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
            tab = 1
            agent_open_panel()
            assert(agent_session.messages.len() == 2 && agent_origin_tab == 1)
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
            for i in 14 { assert(agent_append("user", "旧消息") > 0) }
            agent_input = "当前原文"
            agent_send()
            assert(calls.len() == 1 && calls[0].class == "fast")
            callback({is_ok: false error: "no provider"})
            agent_watchdog()
            assert(calls.len() == 1 && agent_phase == "idle")
            assert(agent_session.summary_through_id == 0 && agent_session.messages.len() == 15)
            assert(agent_input == "当前原文" && agent_current_id == 15)
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
            agent_send()
            let late = callback
            fake_time = fake_time + 96
            agent_watchdog()
            assert(agent_phase == "idle" && agent_session.messages.len() == 1)
            late({is_ok: true data: {output: {reply: "迟到" tool_name: "none" tool_args: {} memory_candidate: ""}}})
            agent_watchdog()
            assert(agent_session.messages.len() == 1)
            true
        "#),
        ("text_snapshot_changes", r#"
            agent_open_panel()
            agent_input = "当前消息"
            assert(agent_append("user", "当前消息") == 1)
            let snapshot = agent_snapshot(1, "当前消息")
            assert(agent_snapshot_matches(snapshot))
            state.revision = 2
            assert(!agent_snapshot_matches(snapshot))
            state.revision = 1 state.profile_revision = 2
            assert(!agent_snapshot_matches(snapshot))
            state.profile_revision = 1 state.plans.push({id: 1 title: "新方案"})
            assert(!agent_snapshot_matches(snapshot))
            state.plans = [] fake_day = 101
            assert(!agent_snapshot_matches(snapshot))
            fake_day = 100 agent_input = "修改了输入"
            assert(!agent_snapshot_matches(snapshot))
            agent_input = "当前消息" agent_session.next_message_id = 3
            assert(!agent_snapshot_matches(snapshot))
            agent_session.next_message_id = 2 pending = true
            assert(!agent_snapshot_matches(snapshot))
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
    ];
    for (name, script) in cases {
        let mut host = ScriptVmHost::new((), ());
        let mut vm = ScriptVm { host: &mut host, bx: Box::new(ScriptVmBase::new()) };
        vm.bx.captured_errors = Some(Vec::new());
        let code = format!("{prelude}\n{helpers}\n{script}\n;");
        let result = vm.with_instruction_limit(2_000_000, |vm| vm.eval(ScriptMod {
            file: format!("agent_core_{name}.splash"), code, ..Default::default()
        }));
        let errors = vm.take_errors();
        assert!(errors.is_empty() && result.as_bool() == Some(true), "{name}: {errors:?}, result={result:?}");
        println!("{name}: ok");
    }
}
