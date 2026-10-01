"""Check BDF ports, BSF ports, cached parent terminals and Quartus-generated BSFs."""
from bdf_tools import *
import json,hashlib
def symbol_ports(n):
    return {unquote(children(p,'text')[0][1]):('input' if ['input'] in p else 'output',tuple(map(int,child(p,'pt')[1:]))) for p in children(n,'port')}
def symbols(f): return [n for n in parse(f.read_text()) if n[0]=='symbol']
report={}; entities={}
for f in ROOT.glob('*.bdf'):
    bs=ROOT/(f.stem+'.bsf'); assert bs.exists(),f'BSF missing: {f.name}'
    n=symbols(bs)[0]; assert unquote(child(n,'text')[1])==f.stem,(bs,'entity name')
    expected=dict((p,d) for d,p in interface(f)); actual=symbol_ports(n)
    assert expected=={p:d for p,(d,xy) in actual.items()},(f,'ports',expected,actual)
    native=ROOT/'verificacao/netlist'/(f.stem+'.bsf')
    if native.exists():
        assert expected=={p:d for p,(d,xy) in symbol_ports(symbols(native)[0]).items()},(f,'Quartus BSF mismatch')
    entities[f.stem]=actual; report[f.stem]=dict(ports=expected,children=[],sha256=hashlib.sha256(f.read_bytes()).hexdigest())
for f in ROOT.glob('*.bdf'):
    for n in symbols(f):
        entity=unquote(child(n,'text')[1])
        if entity in entities:
            assert symbol_ports(n)==entities[entity],(f,'stale cached parent symbol',entity,symbol_ports(n),entities[entity])
            report[f.stem]['children'].append(entity)
        else:
            installed=Path('C:/intelFPGA_lite/21.1/quartus/libraries/primitives/logic')/(entity.lower()+'.bsf')
            assert entity in PRIMS or installed.exists(),(f,'unsupported or missing entity',entity)
    # Free-standing explanatory text is prohibited.
    assert not any(n[0]=='text' for n in parse(f.read_text())),(f,'schematic comment')
(ROOT/'verificacao/hierarquia_interfaces.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(f'PASS: {len(report)} BDF/BSF interfaces and all cached parent terminals synchronized.')
