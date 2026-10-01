"""Independent integer reference against structural Verilog exported by Quartus."""
import json,hashlib,time
from pathlib import Path
from netlist_eval import Circuit
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
SEG=[0x40,0x79,0x24,0x30,0x19,0x12,0x02,0x78,0x00,0x10]
def sm(n): return -(n&15) if n&16 else n&15
def encode(n): return abs(n)|(32 if n<0 else 0)
def expected(a,b,s):
    x,y=sm(a),sm(b)
    if s<2: f=encode(x+y if s==0 else x-y)
    elif s==2: f=(-(b|(32 if b&16 else 0)))%64
    elif s<6: f=0
    else:
        v=a&b if s==6 else a^b; f=(v&15)|((v&16)<<1)
    status=int(x==y) if s==3 else int(x>y) if s==4 else int(x<y) if s==5 else 0
    return dict(F=f,STATUS=status,ENF=int(s<2))

def main():
    for source in ROOT.glob('*.bdf'):
        assert source.read_bytes()==(HERE/'netlist'/source.name).read_bytes(),f'Stale exported BDF: {source.name}; run executar_verificacao.ps1'
    start=time.time(); c=Circuit(HERE/'netlist'); counts={}
    def check(group,mod,inputs,want):
        got=c.run(mod,**inputs)
        for name,val in want.items():
            assert got[name]==val,(group,mod,inputs,name,got[name],val)
        counts[group]=counts.get(group,0)+1
    for a in range(2):
        for b in range(2):
            for ci in range(2):
                n=a+b+ci; check('somador_1bit','somador_1bit',dict(A=a,B=b,Cin=ci),dict(S=n%2,Cout=n//2))
    for a in range(32):
        for b in range(32):
            check('somador_5bit','somador_5bit',dict(A=a,B=b),dict(S=(a+b)%32,Cout=(a+b)//32))
            check('Somador_5bits_compat','Somador_5bits',dict(A=a,B=b),dict(S=(a+b)%32,Cout=(a+b)//32))
    for a in range(2):
        for b in range(2):
            check('Maior_1bit','Maior_1bit',dict(A=a,B=b),dict(A_maior_que_B=int(a>b)))
            for s in range(2): check('MUX1','MUX1',dict(D0=a,D1=b,SEL=s),dict(Y=b if s else a))
    for a in range(16):
        for b in range(16): check('Maior_4bits','Maior_4bits',dict(A=a,B=b),dict(A_maior_que_B=int(a>b)))
    for a in range(32):
        for b in range(32):
            for mod,out,fn in [('Igual_5bits','A_igual_B',lambda:sm(a)==sm(b)),('Maior_5bits','A_maior_que_B',lambda:sm(a)>sm(b)),('Menor_5bits','A_menor_que_B',lambda:sm(a)<sm(b))]:
                check(mod,mod,dict(A=a,B=b),{out:int(fn())})
            for mod,v in [('And_5bits',a&b),('Xor_5bits',a^b)]: check(mod,mod,dict(A=a,B=b),dict(F=(v&15)|((v&16)<<1)))
    for a in range(64):
        for b in range(64):
            for sub in range(2):
                n=a+(b^63 if sub else b)+sub
                check('ADD_SUB6','ADD_SUB6',dict(X=a,Y=b,SUB=sub),dict(R=n%64,COUT=n//64))
    for n in range(32):
        check('SM_C2','SM_C2',dict(A=n),dict(R=sm(n)%64))
        check('Complemento_2','Complemento_2',dict(B=n),dict(F=(-(n|(32 if n&16 else 0)))%64))
        check('MAG_ENTRADA','MAG_ENTRADA',dict(X=n),dict(MAG=n&15))
    for n in range(-30,31): check('C2_SM','C2_SM',dict(R=n%64),dict(F=encode(n)))
    for n in range(32):
        for en in range(2): check('displays','decod_7seg_base',dict(MAG=n,EN=en),dict(HEX_UNI=SEG[n%10] if en else 127,HEX_DEZ=SEG[n//10] if en else 127))
    for n in range(64): check('BIN_DC6bits','BIN_DC6bits',dict(F=n),dict(D=(n&31)//10,U=(n&31)%10,LED_SINAL=int(bool(n&32) and bool(n&31))))
    for bit in range(6):
        for sel in range(2):
            for a in range(64):
                b=(a^(1<<bit))&63; check('MUX2_6','MUX2_6',dict(D0=a,D1=b,SEL=sel),dict(Y=b if sel else a))
    for bit in range(6):
        for k in range(8):
            data=[(i*7+11)^(1<<bit) for i in range(8)]
            for s in range(8):
                args={f'D{i}':((data[i] if i!=k else (~data[i]))&63) for i in range(8)}
                check('MUX8_6','MUX8_6',dict(args,S=s),dict(F=args[f'D{s}']))
    for s in range(8):
        for eq in range(2):
            for gt in range(2):
                for lt in range(2): check('CONTROLE','CONTROLE',dict(S=s,EQ=eq,GT=gt,LT=lt),dict(SUB=(s&1)|((s>>2)&1),ENF=int(s<2),STATUS=[0,0,0,eq,gt,lt,0,0][s]))
    for a in range(32):
        for b in range(32):
            for s in range(8):
                e=expected(a,b,s); check('ULA','ULA',dict(A=a,B=b,S=s),e)
                sw=(a<<13)|(b<<8)|s; f=e['F']; mag=f&31
                top=dict(LEDR=sw,LEDG=f|(e['STATUS']<<6),HEX6=SEG[(a&15)%10],HEX7=SEG[(a&15)//10],HEX4=SEG[(b&15)%10],HEX5=SEG[(b&15)//10],HEX0=SEG[mag%10] if e['ENF'] else 127,HEX1=SEG[mag//10] if e['ENF'] else 127,HEX2=127,HEX3=127)
                check('TOP_leds_displays','TOP',dict(SW=sw),top)
                if a in (0,15,16,31) and b in (0,15,16,31):
                    for unused in range(1,32):
                        check('TOP_unused_switches','TOP',dict(SW=sw|(unused<<3)),top)
    explicit=[]
    for a,b,s in [(15,15,0),(31,31,0),(3,20,0),(19,4,1),(3,20,1),(16,0,3),(19,20,4),(20,19,5),(19,21,6),(19,21,7)]+[(0,b,2) for b in [0,1,3,15,16,19,31]]:
        r=c.run('ULA',A=a,B=b,S=s); assert r==expected(a,b,s); explicit.append(dict(A=f'{a:05b}',B=f'{b:05b}',S=f'{s:03b}',F=f'{r["F"]:06b}',STATUS=r['STATUS'],ENF=r['ENF']))
    hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(ROOT.glob('*.bdf'))}
    report=dict(result='PASS',method='Interpretação estrutural combinacional das netlists Verilog exportadas dos BDF pelo Quartus; sem atrasos.',cases=counts,total=sum(counts.values()),seconds=round(time.time()-start,2),explicit_cases=explicit,bdf_sha256=hashes)
    (HERE/'resultados_testes.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(result=report['result'],total=report['total'],cases=counts,seconds=report['seconds']),indent=2))
if __name__=='__main__': main()
