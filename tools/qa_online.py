"""Online-only routing QA. Replies are synthetic; this is not live provider evidence.

--prepare copies the editable bundle to a private qa-* test directory and replaces
only host-request dispatch with deterministic replies. Production validation,
callbacks, generation, confirmation and storage code stay unchanged. The copied
bundle is never published or synced back to the source project.
"""
import argparse
import copy
import json
import shutil
import subprocess
import time
from pathlib import Path
from qa_day import APP, DayUI


def prepare(profile, seed, hub, mock):
    profile.mkdir(parents=True, exist_ok=True)
    data = profile/'pantry-steward'
    data.mkdir(exist_ok=True)
    s = json.loads(seed.read_text(encoding='utf-8'))
    p = copy.deepcopy(s['programs'][0])
    p.update(id=50, name='7天测试周期', kind='health', days=7, started=int(time.time()), intake=[], meals=[],
             consumed_kcal=0, consumed_protein=0, consumed_fiber=0, consumed_vitamin_c=0)
    s.update(programs=[p], program_active=50, program_next=51, plans=[], active=0,
             foods=[dict(id=i, name=name, grams=g, expires=int(time.time())+172800)
                    for i, name, g in [(1,'豆腐',100),(2,'鸡蛋',100),(3,'菠菜',80),(4,'蘑菇',100)]],
             next_id=100, revision=1, paused=False, reminders=False, demo=False,
             model_enabled=False, auto_generate=False, offset=0)
    (data/'pantry.json').write_text(json.dumps(s, ensure_ascii=False), encoding='utf-8')
    if not mock:
        return
    target = profile/'qa-bundle'
    shutil.copytree(APP/'bundle', target, dirs_exist_ok=True)
    script = target/'main.splash'
    text = script.read_text(encoding='utf-8')
    text = text.replace('host.request("model.budget", {},', 'qa_host_request("model.budget", {},')
    text = text.replace('host.request("model.complete", payload,', 'qa_host_request("model.complete", payload,')
    shim = '''// TEST ONLY: deterministic host fixture, never distributed.
fn qa_host_request(method, payload, callback){
    if method == "model.budget" { callback({is_ok: true data: {calls_today: 0}}) return 1 }
    fs.write("qa-request.json", payload.to_json())
    let fixture = fs.read("qa-reply.json").parse_json()
    if fixture.delay { start_timeout(3.0, || callback(fixture.reply)) }
    else { callback(fixture.reply) }
    return 1
}
'''
    script.write_bytes((text+'\n'+shim).encode('utf-8'))
    subprocess.run([str(hub), 'stamp', str(target)], check=True)
    subprocess.run([str(hub), 'check', str(target), '--allow-unsigned'], check=True)


def fixture(ui, output=None, error=None, delay=False):
    reply = dict(is_ok=False, error=error) if error else dict(is_ok=True, data=dict(output=output))
    (ui.profile/'pantry-steward/qa-reply.json').write_text(json.dumps(dict(delay=delay, reply=reply), ensure_ascii=False), encoding='utf-8')


def request(ui):
    return json.loads((ui.profile/'pantry-steward/qa-request.json').read_text(encoding='utf-8'))


def trial_output(ui):
    s=ui.state()
    p=next(p for p in s['programs'] if p['id']==s['program_active'])
    stock=copy.deepcopy(s['foods'])
    meals=[]
    templates=[('早餐AI菜谱',[('鸡蛋',100),('菠菜',80)]),('午餐AI菜谱',[('豆腐',150),('蘑菇',100),('菠菜',100)]),('晚餐AI菜谱',[('豆腐',150),('菠菜',120),('蘑菇',100)])]
    for slot,(title,items) in enumerate(templates):
        if any(e['program_id']==p['id'] and e['slot']==slot for e in s['execution_records']):
            continue
        uses=[];missing=[]
        for name,g in items:
            needed=g
            for f in stock:
                if f['name']==name:
                    take=min(needed,f['grams'])
                    if take:
                        uses.append(dict(food_id=f['id'],grams=take));f['grams']-=take;needed-=take
            if needed:missing.append(dict(name=name,grams=needed))
        meals.append(dict(slot=slot,title=title,uses=uses,missing=missing,steps=['按推荐克数称重。','充分做熟并核对实际用量。']))
    return dict(feasible=True,reason='合成响应用于验证，不是在线AI实际输出',meals=meals)


def wait(ui):
    time.sleep(.5)


def unsupported(ui):
    before=ui.state()
    ui.check('unsupported host shows online-only status', '在线 AI' in ui.text() and '手动生成' not in ui.text())
    ui.click('生成这一餐  →');wait(ui)
    ui.check('unsupported host cannot generate local candidate', ui.state()==before and not ui.state()['plans'])
    ui.click('⚙  设置')
    ui.check('local-rule toggle removed', '改用本地规则' not in ui.text() and '启用在线 AI' not in ui.text())
    ui.click('选择下一周期方案…')
    ui.click('选择1天体验方案')
    ui.click('确认选中方案 · 去录冰箱  →')
    ui.click('完成建档 · 开始托管  →')
    before=ui.state()
    ui.click('✦  方案');ui.click('生成 / 更新未确认三餐');wait(ui)
    ui.check('unsupported host cannot create fixed trial templates', ui.state()==before and next(p for p in before['programs'] if p['id']==before['program_active'])['meals']==[])


def exercise(ui):
    before=ui.state()
    fixture(ui,error='no_provider')
    ui.click('生成这一餐  →');wait(ui)
    ui.check('no-provider keeps inventory and menus unchanged', ui.state()['foods']==before['foods'] and not ui.state()['plans'])
    ui.check('no-provider gives setup guidance without fallback', '设置配置后重新生成' in ui.text() and '本地规则' not in ui.text())
    ui.click('⚙  设置');ui.click('重新读取 AI 配置');wait(ui)
    ui.check('settings has no local generator toggle', '改用本地规则' not in ui.text())
    ui.click('⌂  首页')
    normal=dict(feasible=True,title='AI豆腐餐',minutes=10,reason='合成响应',uses=[dict(food_id=1,grams=100)],steps=['称重','充分做熟'])
    fixture(ui,normal)
    ui.click('生成这一餐  →');wait(ui)
    ui.check('ordinary candidate comes from online callback', ui.state()['plans'][-1]['source']=='在线 AI')
    ui.check('ordinary request uses host JSON schema', 'schema' in request(ui) and request(ui)['input']['program']['id']==50)
    ui.check('generation does not deduct stock', ui.state()['foods']==before['foods'])
    ui.click('就吃这套 · 设为今晚方案  →');ui.click('我吃完了 · 核对实际用量')
    ui.fill('50',name='actual_amount');ui.click('确认实际食用并保存')
    ui.check('online recipe records actual quantities separately', ui.state()['execution_records'][-1]['actual'][0]['grams']==50 and ui.state()['plans'][-1]['uses'][0]['grams']==100)
    ui.click('⚙  设置');ui.click('选择下一周期方案…');ui.click('选择1天体验方案')
    ui.click('确认选中方案 · 去录冰箱  →');ui.click('完成建档 · 开始托管  →');ui.click('✦  方案')
    before=ui.state()
    valid=trial_output(ui)
    for label,alter in [
        ('duplicate trial slots',lambda out:out['meals'].__setitem__(1,copy.deepcopy(out['meals'][0]))),
        ('unknown stock id',lambda out:out['meals'][0]['uses'][0].__setitem__('food_id',9999)),
        ('aggregate stock overbooking',lambda out:out['meals'][1]['uses'].append(dict(food_id=2,grams=100))),
        ('unknown replenishment nutrition',lambda out:out['meals'][1]['missing'].append(dict(name='未知成分',grams=10))),
        ('daily calories overflow',lambda out:out['meals'][1]['missing'].append(dict(name='鸡蛋',grams=100000))),
    ]:
        out=copy.deepcopy(valid);alter(out);fixture(ui,out)
        ui.click('生成 / 更新未确认三餐');wait(ui)
        s=ui.state()
        ui.check(label+' rejected without stock or ledger writes', s['foods']==before['foods'] and s['execution_records']==before['execution_records'] and next(p for p in s['programs'] if p['id']==s['program_active'])['meals']==[])
    fixture(ui,valid)
    ui.click('生成 / 更新未确认三餐');wait(ui)
    s=ui.state();p=next(p for p in s['programs'] if p['id']==s['program_active'])
    ui.check('trial creates three AI meals atomically', len(p['meals'])==3 and all(m['source']=='在线 AI' for m in p['meals']))
    ui.check('trial request includes only unconfirmed slots', request(ui)['input']['slots']==[0,1,2] and request(ui)['schema']['properties']['meals']['items']['properties']['slot']['maximum']==2)
    ui.check('trial generation does not change intake or stock', s['foods']==before['foods'] and s['execution_records']==before['execution_records'])
    ui.click('预览模拟补菜')
    ui.check('AI replenishment preview does not alter stock', ui.state()['foods']==s['foods'])
    # Response to the subsequent generation sees the replenished stock.
    # Prepare it after simulated stock is committed; delay gives the driver time.
    fixture(ui,valid,error='network unavailable')
    ui.click('确认模拟补菜入库');wait(ui)
    stock=ui.state()['foods']
    ui.check('simulation remains explicit and no real purchase', any(f.get('origin')=='模拟补菜' for f in stock))
    fixture(ui,trial_output(ui));ui.click('生成 / 更新未确认三餐');wait(ui)
    p=next(p for p in ui.state()['programs'] if p['id']==ui.state()['program_active'])
    ui.check('AI regeneration uses confirmed simulated stock', all(not m['missing'] for m in p['meals']))
    for slot,name,progress in [(0,'早餐',33),(1,'午餐',66),(2,'晚餐',100)]:
        ui.click('我吃完了 · 核对'+name);ui.click('确认实际食用并保存')
        ui.check('AI '+name+' actual confirmation advances '+str(progress), ('已确认进度 '+str(progress)+'%') in ui.text() if progress<100 else '体验复盘 · 100%' in ui.text())
        if slot==0:
            history=copy.deepcopy(ui.state()['execution_records'])
            fixture(ui,trial_output(ui));ui.click('生成 / 更新未确认三餐');wait(ui)
            ui.check('regeneration requests only remaining slots', request(ui)['input']['slots']==[1,2])
            ui.check('confirmed recommendation and actual history survive AI', ui.state()['execution_records']==history)
    ui.shot('online-trial-complete.png')
    ui.check('header removed manual-generation wording', '手动生成' not in ui.text() and '本地三餐规则' not in ui.text())
    ui.click('选择后续健康方案');ui.click('确认选中方案 · 去录冰箱  →')
    # All demo ingredients were consumed; the next program still needs stock.
    ui.fill('豆腐',name='food_name');ui.fill('200',name='food_grams');ui.fill('2',name='food_days')
    ui.click('预览并确认入库  →');ui.click('确认入库')
    ui.click('完成建档 · 开始托管  →')
    ui.click('⌂  首页')
    before=ui.state()
    fixture(ui,normal,delay=True);ui.click('生成这一餐  →')
    ui.click('停止等待');time.sleep(3.5)
    ui.check('cancelled AI response cannot write late menus', ui.state()['plans']==before['plans'] and ui.state()['foods']==before['foods'] and ui.state()['execution_records']==before['execution_records'])
    ui.click('⌂  首页');fixture(ui,normal,delay=True);ui.click('生成这一餐  →')
    ui.click('⌂  首页');ui.fill('等待时修改目标',name='request');time.sleep(3.5)
    ui.check('changed goal discards a stale AI response', '丢弃旧结果' in ui.text() and ui.state()['plans']==before['plans'] and ui.state()['execution_records']==before['execution_records'])


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--port',type=int)
    parser.add_argument('--profile',type=Path,required=True)
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--seed',type=Path)
    parser.add_argument('--hub',type=Path)
    parser.add_argument('--mock',action='store_true')
    args=parser.parse_args();profile=args.profile.resolve()
    if not profile.is_relative_to((APP/'.local-state').resolve()) or not profile.name.startswith('qa-'):
        parser.error('requires a task-owned qa-* profile')
    if args.prepare:
        if not args.seed or not args.hub:parser.error('--prepare requires --seed and --hub')
        prepare(profile,args.seed,args.hub,args.mock)
    else:
        if not args.port:parser.error('requires --port')
        ui=DayUI(args.port,profile)
        exercise(ui) if args.mock else unsupported(ui)
        (profile/'checks.json').write_text(json.dumps(ui.checks,ensure_ascii=False,indent=2),encoding='utf-8')
