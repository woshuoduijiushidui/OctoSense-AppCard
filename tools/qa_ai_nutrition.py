"""Native model-fixture regression for automatic estimates, never user data."""
import argparse, copy, json, time, subprocess
from pathlib import Path
from qa_day import APP,DayUI
import smoke
from qa_recipe import menu
from qa_online import prepare,fixture,request,wait

def seed(profile, seed_file, hub):
    prepare(profile,seed_file,hub,True)
    path=profile/'pantry-steward/pantry.json'
    s=json.loads(path.read_text(encoding='utf-8'))
    expiry=int(time.time())+86400
    s['profile']['avoid']='花生'
    s['foods']=[dict(id=i,name=n,grams=g,expires=e) for i,n,g,e in
                [(1,'牛肉',200,expiry),(2,'白菜',300,expiry),(3,'鱼',500,expiry),
                 (4,'豆腐',0,expiry),(5,'猪肉',200,int(time.time())-86400),(6,'花生',50,expiry)]]
    path.write_text(json.dumps(s,ensure_ascii=False),encoding='utf-8')
    (profile/'before.json').write_text(json.dumps(s,ensure_ascii=False),encoding='utf-8')


def trial(slots=(0,1,2)):
    names=['牛肉','白菜','鱼'];grams=[50,60,70]
    return dict(feasible=True,reason='合成测试：库存可用，营养未知',meals=[menu([dict(food_id=k+1,grams=grams[k])],slot=k) for k in slots])





def estimate_fixture(ui,values=None,error=None,delay=False):
    reply=dict(is_ok=False,error=error) if error else dict(is_ok=True,data=dict(output=dict(estimates=values)))
    (ui.profile/'pantry-steward/qa-nutrition-reply.json').write_text(json.dumps(dict(delay=delay,reply=reply),ensure_ascii=False),encoding='utf-8')


def estimates(items=((1,'牛肉',200,20,0,0),(2,'白菜',20,1,2,20),(3,'鱼',100,15,0,0))):
    # Synthetic reference values test arithmetic only; not nutritional guidance.
    return [dict(key=k,name=name,known=True,kcal=c,protein=p,fiber=f,vitamin_c=v,basis='通用生重，合成测试') for k,name,c,p,f,v in items]


def exercise(ui):
    baseline=ui.state();history=copy.deepcopy(baseline['execution_records'])
    normal=dict(feasible=True,minutes=15,reason='合成菜单',**menu([dict(food_id=1,grams=100),dict(food_id=2,grams=80)]))
    fixture(ui,normal);estimate_fixture(ui,error='network unavailable')
    ui.click('生成今日菜单  →');time.sleep(1)
    ui.check('estimate failure preserves stock and history while allowing unknown menu',ui.state()['foods']==baseline['foods'] and ui.state()['execution_records']==history and len(ui.state()['plans'])==1)
    req=json.loads((ui.profile/'pantry-steward/qa-nutrition-request.json').read_text(encoding='utf-8'))
    ui.check('physical unknown stock sent for automatic estimates',[(x['key'],x['name']) for x in req['input']['items']]==[(1,'牛肉'),(2,'白菜'),(3,'鱼')])
    ui.check('zero expired avoided stock excluded from estimates',len(req['input']['items'])==3)
    ui.check('estimate requests omit body profile and demand per100 units','profile' not in req['input'] and '每100g' in req['task'] and req['schema']['properties']['estimates']['items']['properties']['vitamin_c']['maximum']==1000)
    for label,edit in [('duplicate keys',lambda v:v.__setitem__(1,copy.deepcopy(v[0]))),('invalid range',lambda v:v[0].__setitem__('protein',1000)),('wrong name',lambda v:v[0].__setitem__('name','鸡肉'))]:
        count=len(ui.state()['plans']);vals=estimates();edit(vals);estimate_fixture(ui,vals)
        ui.click('⌂  首页');ui.click('生成今日菜单  →');time.sleep(1)
        ui.check(label+' nutrition rejected without losing usable stock',ui.state()['foods']==baseline['foods'] and ui.state()['execution_records']==history and len(ui.state()['plans'])==count+1)
    estimate_fixture(ui,estimates());ui.click('⌂  首页');ui.click('生成今日菜单  →');time.sleep(1.6)
    s=ui.state();inv=request(ui)['input']['inventory']
    ui.check('estimated stock flows into ordinary online menu',len(s['plans'])==5 and all(x['nutrition']['known'] and x['nutrition']['source']=='AI 估算' for x in inv))
    ui.check('estimate metadata keeps quantity and history intact',[(f['id'],f['grams']) for f in s['foods']]==[(f['id'],f['grams']) for f in baseline['foods']] and s['execution_records']==history)
    ui.check('estimates persist source time and assumptions',all(f['nutrition']['estimated_at']>0 and f['nutrition']['basis'] for f in s['foods'][:3]))
    ui.check('menu labels AI approximate estimates','AI 估算' in ui.text() and '仅作参考' in ui.text())
    ui.click('接受今日菜单  →');ui.click('我吃完了 · 核对实际用量');ui.fill('50',name='actual_amount',index=0)
    before=ui.state();ui.check('editing actual grams does not deduct stock',before==s or before['foods']==s['foods'])
    ui.click('确认实际食用并保存');s=ui.state();first=copy.deepcopy(s['execution_records'][-1])
    ui.check('confirmed intake uses estimated actual quantity',first['kcal']==116 and first['protein']==10.8 and first['actual'][0]['grams']==50 and first['recommendation']['uses'][0]['grams']==100)
    ui.check('confirmed record freezes estimate provenance',first['nutrition_complete'] is True and all(u['nutrition']['source']=='AI 估算' for u in first['actual']))
    ui.check('only confirmed actual grams deduct stock',s['foods'][0]['grams']==150 and s['foods'][1]['grams']==220)
    # Adding ordinary stock automatically starts estimation without menu generation.
    stock_id=ui.state()['next_id'];estimate_fixture(ui,estimates(((stock_id,'牛油果',160,2,6,10),)))
    ui.click('▣  冰箱');smoke.enter(ui,'食材名称','牛油果');smoke.enter(ui,'数量','120');smoke.enter(ui,'还剩几天（可留空）','2');ui.click('预览并确认  →');ui.click('最终确认入库');time.sleep(1)
    s=ui.state();f=next(f for f in s['foods'] if f['id']==stock_id)
    ui.check('new stock estimates automatically after confirmation',f['grams']==120 and f['nutrition']['source']=='AI 估算' and f['nutrition']['kcal']==160)
    ui.check('stock estimates do not generate unwanted menus',len(s['plans'])==5 and s['execution_records'][-1]==first)
    # Packaging correction affects future references, not a confirmed snapshot.
    ui.click('编辑',index=0);ui.fill('300',index=3);ui.click('预览并确认  →');ui.click('最终确认入库');time.sleep(.6)
    s=ui.state();ui.check('package correction takes precedence over AI',s['foods'][0]['nutrition']['kcal']==300 and s['foods'][0]['nutrition']['source']=='用户填写')
    ui.check('correcting reference never rewrites history',s['execution_records'][-1]==first)
    ui.click('⚙  设置');ui.click('选择下一周期方案…');ui.click('先体验 1 天轻食流程');ui.click('确认选中方案 · 去录冰箱  →');ui.click('完成建档 · 开始托管  →');ui.click('✦  菜单')
    fixture(ui,trial());ui.click('生成 / 更新未确认三餐');time.sleep(1)
    ui.check('three meals generated with estimated available stock',len(next(p for p in ui.state()['programs'] if p['id']==ui.state()['program_active'])['meals'])==3)
    ui.shot('ai-estimated-three-meals.png')
    ui.click('我吃完了 · 核对');ui.click('确认实际食用并保存');saved=copy.deepcopy(ui.state()['execution_records'][-1])
    fixture(ui,trial((1,2)));ui.click('生成 / 更新未确认三餐');time.sleep(1)
    ui.check('regeneration preserves confirmed nutrition snapshots',ui.state()['execution_records'][-1]==saved and request(ui)['input']['slots']==[1,2])
    ui.click('我吃完了 · 核对');ui.click('确认实际食用并保存')
    ui.click('我吃完了 · 核对')
    # A cancelled late estimate cannot write stock or a confirmed intake.
    estimate_fixture(ui,estimates(((2,'米饭',130,3,1,0),)),delay=True)
    ui.fill('米饭',name='external_name');ui.fill('80',name='external_grams');before=ui.state();ui.click('添加库存外实际食物');ui.click('取消实际食用确认');time.sleep(3.5)
    ui.check('cancelled late nutrition reply does not write',ui.state()==before and '旧营养估算已忽略' in ui.text())
    ui.click('我吃完了 · 核对')
    ambiguous=dict(key=2,name='沙拉',known=False,kcal=0,protein=0,fiber=0,vitamin_c=0,basis='无法判断原料')
    estimate_fixture(ui,[ambiguous])
    ui.fill('沙拉',name='external_name');ui.fill('20',name='external_grams');before=ui.state();ui.click('添加库存外实际食物');time.sleep(1)
    ui.check('ambiguous food remains unknown without fake zero nutrition',ui.state()==before and '部分食物无法估算' in ui.text() and '营养待估算' in ui.text())
    estimate_fixture(ui,error='network unavailable');ui.click('重新估算实际餐食营养');time.sleep(1)
    ui.check('failed outside estimate preserves draft and stock',ui.state()==before and '营养估算失败' in ui.text() and '营养待估算' in ui.text())
    estimate_fixture(ui,[ambiguous]);ui.click('重新生成');time.sleep(1)
    ui.check('pending global retry estimates without generating a menu',ui.state()==before and '部分食物无法估算' in ui.text())
    ui.click('移除',index=1)
    estimate_fixture(ui,estimates(((2,'米饭',130,3,1,0),)))
    ui.fill('米饭',name='external_name');ui.fill('80',name='external_grams');before=ui.state();ui.click('添加库存外实际食物');time.sleep(1)
    ui.check('outside food auto estimation does not confirm or deduct',ui.state()==before and 'AI 估算' in ui.text() and '确认实际食用' in ui.text())
    ui.click('确认实际食用并保存');s=ui.state();last=s['execution_records'][-1]
    ui.check('outside food estimate included by actual quantity',last['kcal']==174 and last['protein']==12.9 and last['actual'][1]['nutrition']['source']=='AI 估算' and last['actual'][1]['food_id']==0)
    ui.check('outside food never deducts pantry stock',next(f['grams'] for f in s['foods'] if f['id']==3)==430 and next(f['grams'] for f in s['foods'] if f['id']==stock_id)==120)
    ui.check('three confirmed meals complete trial with estimates','1 天体验复盘' in ui.text() and '含 AI 估算' in ui.text())
    ui.check('all baseline and ordinary history retained',s['execution_records'][:len(history)]==history and s['execution_records'][len(history)]==first)
    ui.shot('ai-estimated-trial-complete.png')
    (ui.profile/'checks.json').write_text(json.dumps(ui.checks,ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--profile',type=Path,required=True);parser.add_argument('--port',type=int);parser.add_argument('--prepare',action='store_true');parser.add_argument('--seed',type=Path);parser.add_argument('--hub',type=Path)
    a=parser.parse_args();profile=a.profile.resolve()
    if not profile.is_relative_to((APP/'.local-state').resolve()) or not profile.name.startswith('qa-'):parser.error('isolated qa-* profile required')
    if a.prepare:
        seed(profile,a.seed,a.hub)
        p=profile/'qa-bundle/main.splash';s=p.read_text(encoding='utf-8').replace('let fixture = fs.read("qa-reply.json").parse_json()', '''let file = "qa-reply.json"
    if has_field(payload.input, "items") { fs.write("qa-nutrition-request.json", payload.to_json()) file = "qa-nutrition-reply.json" }
    let fixture = fs.read(file).parse_json()''');p.write_bytes(s.encode('utf-8'));subprocess.run([str(a.hub),'stamp',str(p.parent)],check=True)
    else:exercise(DayUI(a.port,profile))
