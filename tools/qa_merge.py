"""Native merge/schema regression in a task-owned hidden official card-host.

--prepare writes synthetic stock and deterministic model replies into a private
bundle. Production state, validators, callbacks and persistence are unchanged.
No real provider is configured or called. Compile the resulting request-*.json
with check_model_schema.py to cover the official host's schema compiler too.
"""
import argparse
import copy
import json
from pathlib import Path
import shutil
import subprocess
import time
from qa_day import DayUI, APP


def prepare(profile, hub, legacy=False, recipe_only=False, nutrition_failure=False):
    profile.mkdir(parents=True, exist_ok=True)
    data = profile / 'pantry-steward'
    data.mkdir(exist_ok=True)
    now = int(time.time()); day = now // 86400
    stage = dict(id=50,name='7天合成测试',days=7,kind='health',meals=[],goal='均衡',started=day*86400,
                 daily_kcal=2000,kcal_goal=14000,protein_goal=350,fiber_goal=175,vitamin_c_goal=525,
                 consumed_kcal=0,consumed_protein=0,consumed_fiber=0,consumed_vitamin_c=0,intake=[])
    state = dict(schema=2,foods=[],plans=[],active=0,next_id=100,revision=1,profile_revision=1,
                 next_operation_id=1,inventory_events=[],offset=0,demo=False,paused=False,reminders=False,
                 snooze=0,risk_key='',handled=0,baseline=0,cycle_start=now,log=[],model_enabled=True,auto_generate=False,
                 profile=dict(done=True,scene='日常健康',sex='女性',age='30',height='165',weight='55',allergies='',
                              avoidances='',preferences='清淡',special='',activity='轻活动',basics_done=True,plan_approved=True),
                 programs=[],stages=[stage],stage_next=51,plan_history=[],program_history=[],program_next=1,
                 cycle_seed=[0]*6,health=dict(start=now,day=day,meals_per_day=3,meals_week=0,meals_today=0,
                                            protein_week=0,fiber_week=0,protein_goal=350,fiber_goal=175,calcium_goal=0,iron_goal=0),
                 daily_target=2000,consumed_kcal=0,meal_count=0,last_meal='',last_goal='',cart=[],orders=[],
                 execution_records=[],execution_next=1)
    for i,name in enumerate(['豆腐','牛肉','白菜'],1):
        state['foods'].append(dict(id=i,name=name,quantity=300,unit='g',canonical_quantity=300,canonical_unit='g',
                                  package_size=0,package_size_unit='',average_item_grams=0,
                                  expires_on_day=day+3,expiry_precision='estimated',source='manual'))
    if legacy:
        state['schema']=1
        state['last_goal']='execution_records execution_next programs health stage_next'
        state['programs']=[copy.deepcopy(stage)]; state['program_active']=50; state['program_next']=51
        for key in ('stages','stage_next','plan_history','profile_revision','next_operation_id','inventory_events','execution_records','execution_next'):
            del state[key]
        state['profile']['avoid']=state['profile'].pop('avoidances')
        state['profile']['diet']=state['profile'].pop('preferences')
        state['profile'].pop('allergies')
        state['foods']=[dict(id=i,name=n,grams=300,expires=now+3*86400) for i,n in enumerate(['豆腐','牛肉','白菜'],1)]
    if recipe_only:
        batch=copy.deepcopy(state['foods'][0]);batch.update(name='梨',quantity=3,unit='个',canonical_quantity=3,canonical_unit='piece',average_item_grams=0)
        state['foods']=[batch]
    if nutrition_failure:
        state['foods']=state['foods'][:1];state['foods'][0]['name']='梨'
    (data/'pantry.json').write_text(json.dumps(state,ensure_ascii=False),encoding='utf-8')
    (data/'qa-mode.txt').write_text('nutrition_error' if nutrition_failure else 'pass',encoding='utf-8')
    target=profile/'qa-bundle'
    shutil.copytree(APP/'bundle',target,dirs_exist_ok=True)
    # The official standalone card-host does not link OctoSense's device
    # consent broker. Only this private synthetic preview drops that host
    # requirement; production keeps it. No camera/files service is injected.
    manifest=target/'manifest.json'
    contract=json.loads(manifest.read_text(encoding='utf-8'))
    contract['requires']=[]
    contract.pop('host_api',None)
    manifest.write_bytes((json.dumps(contract,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    text=(target/'main.splash').read_text(encoding='utf-8')
    text=text.replace('host.request("model.budget", {},','qa_host_request("model.budget", {},')
    text=text.replace('host.request("model.complete", payload,','qa_host_request("model.complete", payload,')
    shim='''
// TEST ONLY, lives in an ignored private bundle, never distributed.
let qa_requests = 0
fn qa_host_request(method, payload, callback){
    if method == "model.budget" { callback({is_ok: true data: {calls_today: 0}}) return 1 }
    qa_requests = qa_requests + 1
    fs.write("request-" + qa_requests + ".json", payload.to_json())
    let mode = fs.read("qa-mode.txt").trim()
    if has_field(payload.input, "items") {
        if mode == "nutrition_error" { callback({is_ok: false error: "synthetic nutrition failure"}) return 1 }
        let estimates = []
        for item in payload.input.items {
            estimates.push({key: item.key name: item.name known: true kcal: 100 protein: 10 fiber: 2 vitamin_c: 5 basis: "合成参考，非提供方输出"})
        }
        callback({is_ok: true data: {output: {estimates: estimates}}}) return 1
    }
    let meals = [] let slots = [0 1 2]
    if has_field(payload.input, "slots") { slots = payload.input.slots }
    for slot in slots {
        let id = payload.input.inventory[0].food_id
        let ids = [id]
        if mode == "duplicate" { ids = [id id] }
        if mode == "unknown" { ids = [99999] }
        let uses = [{food_id: id grams: 10}]
        if !has_field(payload.input.inventory[0], "grams") { uses = [{food_id: id quantity: 1}] }
        meals.push({slot: slot title: "水煮" minutes: 10 uses: uses
            steps: [{action: "清洗" food_ids: ids minutes: 0} {action: "充分煮熟" food_ids: [id] minutes: 10}]})
    }
    callback({is_ok: true data: {output: {feasible: true reason: "合成菜单，不调用提供方" meals: meals}}}) return 1
}
start_timeout(0.2, || fs.write("request-image.json", {schema: recognition_schema()}.to_json()))
'''
    (target/'main.splash').write_bytes((text+shim).encode('utf-8'))
    subprocess.run([str(hub),'stamp',str(target)],check=True)
    subprocess.run([str(hub),'check',str(target),'--allow-unsigned'],check=True)


def wait(): time.sleep(1.3)


def mode(ui,value):
    (ui.profile/'pantry-steward/qa-mode.txt').write_text(value,encoding='utf-8')


def exercise(ui):
    before=ui.state()
    ui.click('生成今日菜单  →');wait()
    s=ui.state()
    ui.check('main six cycles retain three candidates each',len(s['programs'])==18 and all(sum(p['days']==d for p in s['programs'])==3 for d in [1,3,7,15,21,30]))
    ui.check('ordinary day menu uses online callback and three structured recipes',len(s['plans'])==1 and len(s['plans'][0]['meals'])==3)
    ui.check('generation and nutrition estimates do not deduct stock',[f['canonical_quantity'] for f in s['foods']]==[300]*3)
    ui.check('missing nutrition estimated with source and basis',s['foods'][1]['nutrition']['source']=='AI 估算' and s['foods'][1]['nutrition']['basis'])
    stable=copy.deepcopy(s['plans'])
    for failure in ['duplicate','unknown']:
        mode(ui,failure);ui.click('⌂  首页');ui.click('生成今日菜单  →');wait()
        ui.check('ordinary rejects '+failure+' step IDs',ui.state()['plans']==stable)
    mode(ui,'pass');ui.click('✦  菜单');ui.click('接受今日菜单  →');ui.click('我吃完了 · 核对实际用量')
    frozen=ui.state()
    ui.fill('5',name='actual_amount',index=0)
    ui.check('unconfirmed edits do not change inventory or history',ui.state()==frozen)
    ui.click('确认实际食用并保存');wait()
    s=ui.state();first=copy.deepcopy(s['execution_records'][0])
    ui.check('ordinary actual snapshot differs without overwriting recommendation',first['actual'][0]['grams']==5 and s['plans'][0]['uses'][0]['grams']==10)
    ui.check('canonical inventory decremented by actual totals',s['foods'][0]['canonical_quantity']==275)
    ui.check('main stage tracking reads confirmed actual ledger',s['stages'][0]['intake'][0]==first)
    ui.click('⚙  设置');ui.click('选择下一份计划…');ui.click('先体验 1 天轻食流程');ui.click('确认计划 · 去录冰箱  →');ui.click('完成建档 · 开始托管  →')
    ui.check('one-day experience is an independent confirmed stage',ui.state()['stages'][0]['kind']=='experience' and ui.state()['stages'][0]['days']==1)
    ui.click('✦  菜单');ui.click('生成 / 更新未确认三餐');wait()
    s=ui.state();stock=copy.deepcopy(s['foods']);menus=copy.deepcopy(s['stages'][0]['meals'])
    ui.check('trial creates exactly three meals and no shopping',len(menus)==3 and len(s['execution_records'])==1 and s['foods']==stock and not s['cart'])
    for failure in ['duplicate','unknown']:
        mode(ui,failure);ui.click('生成 / 更新未确认三餐');wait()
        ui.check('trial rejects '+failure+' step IDs',ui.state()['stages'][0]['meals']==menus)
    mode(ui,'pass')
    for slot,label in enumerate(['早餐','午餐','晚餐']):
        ui.click('我吃完了 · 核对'+label)
        ui.fill(str(5+slot),name='actual_amount')
        ui.click('确认实际食用并保存');wait()
        s=ui.state()
        ui.check(label+' confirmation is counted once',len(s['execution_records'])==slot+2)
        ui.check(label+' actual grams used for intake',s['execution_records'][-1]['actual'][0]['grams']==5+slot)
        if slot==0:
            entry=copy.deepcopy(s['execution_records'][-1])
            ui.click('生成 / 更新未确认三餐');wait()
            ui.check('regeneration keeps confirmed history and recommendation',ui.state()['execution_records'][-1]==entry and ui.state()['stages'][0]['meals'][0]==entry['recommendation'])
    ui.check('three confirmations show 100 percent recap','1 天体验复盘 · 100%' in ui.text() and '体验完成！早、中、晚三餐均已确认。' in ui.text())
    ui.check('old ordinary history retained after stage switch',ui.state()['execution_records'][0]==first)
    ui.check('actual inventory operation is recorded',len(ui.state()['inventory_events'])==4)
    (ui.profile/'expected-state.json').write_text(json.dumps(ui.state(),ensure_ascii=False),encoding='utf-8')


def main_features(ui):
    ui.click('生成今日菜单  →');wait()
    ui.click('✦  菜单');ui.click('接受今日菜单  →')
    ui.click('▣  冰箱');ui.click('展开 / 收起',index=0);ui.click('丢弃/移除');ui.click('确认移除')
    ui.check('main inventory removal records discard rather than consumption',not ui.state()['execution_records'] and ui.state()['inventory_events'][-1]['type']=='discard')
    ui.click('✦  菜单')
    ui.check('main derived shortfall survives merge','缺菜清单' in ui.text() and '一键补齐 · 去模拟买菜  →' in ui.text())
    before=ui.state()
    ui.click('一键补齐 · 去模拟买菜  →');ui.click('▧  购物车')
    ui.check('main mock cart fills with matched product',bool(ui.state()['cart']) and ui.state()['cart'][0]['product']=='豆腐')
    ui.click('＋')
    ui.check('cart quantity editing persists',ui.state()['cart'][0]['quantity']==2)
    ui.click('提交模拟订单  →')
    ui.check('order preview creates no order',ui.state()['orders']==[])
    ui.click('确认提交订单')
    after=ui.state()
    ui.check('mock order creates pending receipt',len(after['orders'])==1 and after['orders'][0]['status']=='待收货')
    ui.check('shopping does not add stock or food records',after['foods']==before['foods'] and after['execution_records']==before['execution_records'] and after['stages']==before['stages'])
    (ui.profile/'expected-state.json').write_text(json.dumps(after,ensure_ascii=False),encoding='utf-8')


def recipe_only_request(ui):
    before=ui.state()['foods']
    ui.click('生成今日菜单  →');wait()
    s=ui.state()
    ui.check('main native-piece recipe-only route retained',len(s['plans'])==1 and s['plans'][0]['numeric'] is False)
    ui.check('unknown piece weight remains unknown and stock unchanged',s['foods']==before and all(u['unit']=='piece' and u['grams']==0 for u in s['plans'][0]['uses']))


def failed_nutrition(ui):
    ui.click('生成今日菜单  →');wait()
    s=ui.state()
    ui.check('nutrition failure continues to one online menu attempt',len(s['plans'])==1 and len(list((ui.profile/'pantry-steward').glob('request-[0-9]*.json')))==2)
    ui.check('failure preserves real stock and unknown nutrition',s['foods'][0]['canonical_quantity']==300 and 'nutrition' not in s['foods'][0])
    ui.click('⚙  设置');ui.click('选择下一份计划…');ui.click('先体验 1 天轻食流程');ui.click('确认计划 · 去录冰箱  →');ui.click('完成建档 · 开始托管  →')
    ui.click('✦  菜单');ui.click('生成 / 更新未确认三餐');wait()
    ui.check('trial nutrition failure still produces stock-only recipes',len(ui.state()['stages'][0]['meals'])==3)
    ui.click('我吃完了 · 核对早餐');wait()
    ui.fill('5',name='actual_amount');ui.fill('',name='actual_extra')
    ui.fill('面包',name='external_name');ui.fill('40',name='external_grams');ui.click('添加库存外实际食物');wait()
    ui.click('确认实际食用并保存');wait()
    s=ui.state();e=s['execution_records'][-1]
    ui.check('unknown nutrition recorded without pretending goal completion',e['nutrition_complete'] is False and e['kcal']==0 and '营养未估算' in ui.text())
    ui.check('external food recorded without inventory deduction',e['actual'][1]['food_id']==0 and e['actual'][1]['grams']==40 and s['foods'][0]['canonical_quantity']==295)
    ui.check('unknown confirmed meal counts toward execution only','已确认进度 33%' in ui.text() and len(s['stages'][0]['intake'])==1)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile',type=Path,required=True)
    parser.add_argument('--hub',type=Path)
    parser.add_argument('--port',type=int,default=18672)
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--restart',action='store_true')
    parser.add_argument('--legacy',action='store_true',help='prepare text-collision schema-1 inventory')
    parser.add_argument('--main-features',action='store_true',help='shortfalls, mock cart and order regression')
    parser.add_argument('--recipe-only',action='store_true',help='native piece units without a mass conversion')
    parser.add_argument('--nutrition-failure',action='store_true',help='estimate failure and unknown actual intake')
    args=parser.parse_args();profile=args.profile.resolve()
    if not profile.is_relative_to((APP/'.local-state').resolve()) or not profile.name.startswith('qa-'):
        parser.error('use a task-owned qa-* directory under .local-state')
    if args.prepare:
        if not args.hub:parser.error('--prepare requires --hub')
        prepare(profile,args.hub,args.legacy,args.recipe_only,args.nutrition_failure);return
    ui=DayUI(args.port,profile)
    if args.restart:
        expected=json.loads((profile/'expected-state.json').read_text(encoding='utf-8'))
        ui.check('true restart preserves canonical inventory and confirmed history',ui.state()==expected)
    elif args.main_features:main_features(ui)
    elif args.recipe_only:recipe_only_request(ui)
    elif args.nutrition_failure:failed_nutrition(ui)
    else:exercise(ui)
    print('PASS',len(ui.checks),'native merge checks')


if __name__=='__main__': main()
