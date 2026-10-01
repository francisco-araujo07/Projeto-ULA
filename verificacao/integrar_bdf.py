"""Reproducible schematic repairs and integration. Sources remain BDF/BSF."""
from bdf_tools import *

def fix_library():
    # Only remap two output bit labels; preserve all five original logic gates.
    for name in ['And_5bits','Xor_5bits']:
        f=ROOT/(name+'.bdf'); s=(ROOT/'verificacao/originais'/f.name).read_text(); s=s.replace('"F[4]"','"F[_TMP]"').replace('"F[5]"','"F[4]"').replace('"F[_TMP]"','"F[5]"'); f.write_text(s)
    f=ROOT/'Maior_4bits.bdf'; f.write_text(f.read_text().replace('[4..0]','[3..0]')); regen('Maior_4bits')
    # Display equations already pass all 32 values. Preserve their complete circuits.
    for old,new in [('decof7_unidade','decod_7seg_unidade'),('decof7_dezena','decod_7seg_dezena')]:
        (ROOT/(new+'.bdf')).write_text((ROOT/'verificacao/originais'/(old+'.bdf')).read_text()); regen(new)
        d=Diagram(old); ip=d.pin('MAG[4..0]','input',192,160)
        outname='HEX_UNI[6..0]' if 'unidade' in old else 'HEX_DEZ[6..0]'
        p=d.inst(new,'decoder',352,128); out=d.pin(outname,'output',800,160)
        d.wire(ip,p['MAG[4..0]'],bus=True); d.wire(p[outname],out,bus=True); d.save()
    regen('BIN_DC6bits'); regen('somador_5bit')
    # Compatibility entity uses one canonical five-bit chain, preserving external behavior.
    d=Diagram('Somador_5bits'); iface=interface(ROOT/'somador_5bit.bdf')
    p=d.inst('somador_5bit','adder',400,128)
    for i,(direction,name) in enumerate(iface):
        a=p[name]; pin=d.pin(name,direction,192 if direction=='input' else 900,a[1]); d.wire(pin,a,bus='[' in name)
    d.save()

def complement():
    d=Diagram('Complemento_2'); d.pin('B[4..0]','input',192,96); d.wire((192,96),(256,96),bus=True); d.rail(256,96,1040,'B[4..0]')
    out=d.pin('F[5..0]','output',992,96); d.wire((880,96),out,bus=True); d.rail(880,96,1040,'F[5..0]')
    previous=None
    for i in range(6):
        y=160+144*i; n=d.inst('NOT',f'invert_bit{i}',400,y+16); a=d.inst('somador_1bit',f'add_bit{i}',576,y)
        d.tap(256,n['IN'],f'B[{min(i,4)}]'); d.wire(n['OUT'],a['A'])
        z=d.inst('GND',f'cin_zero{i}',496,y+48)['1']; d.wire(z,a['Cin'])
        if previous:
            d.route([previous,(752,previous[1]),(752,y-24),(552,y-24),(552,a['B'][1]),a['B']])
        else:
            v=d.inst('VCC','add_one',448,y+32)['1']; d.wire(v,a['B'])
        d.tap(880,a['S'],f'F[{i}]'); previous=a['Cout']
    # Carry past bit 5 is intentionally discarded, not the sign bit.
    d.save()

def logic5(name,gate):
    d=Diagram(name)
    for x,n,y in [(256,'A[4..0]',64),(304,'B[4..0]',96)]:
        p=d.pin(n,'input',192,y); d.wire(p,(x,y),bus=True); d.rail(x,y,816,n)
    d.rail(800,64,944,'F[5..0]'); d.wire((800,64),d.pin('F[5..0]','output',912,64),bus=True)
    for i in range(5):
        a=d.inst(gate,f'bit{i}',512,192+i*128)
        d.tap(256,a['IN1'],f'A[{i}]'); d.tap(304,a['IN2'],f'B[{i}]'); d.tap(800,a['OUT'],f'F[{i if i<4 else 5}]')
    z=d.inst('GND','extra_magnitude_zero',512,912)['1']; d.tap(800,z,'F[4]'); d.save()

def mux2():
    d=Diagram('MUX2_6')
    for x,n,y in [(256,'D0[5..0]',64),(304,'D1[5..0]',96)]:
        p=d.pin(n,'input',192,y); d.wire(p,(x,y),bus=True); d.rail(x,y,1160,n)
    sel=d.pin('SEL','input',192,128); d.wire(sel,(352,128)); d.wire((352,128),(352,1160))
    d.rail(832,64,1160,'Y[5..0]'); d.wire((832,64),d.pin('Y[5..0]','output',944,64),bus=True)
    for i in range(6):
        a=d.inst('MUX1',f'bit{i}',544,192+i*176)
        d.tap(256,a['D0'],f'D0[{i}]'); d.tap(304,a['D1'],f'D1[{i}]'); d.wire((352,a['SEL'][1]),a['SEL']); d.junction((352,a['SEL'][1])); d.tap(832,a['Y'],f'Y[{i}]')
    d.save()

def menor5():
    d=Diagram('Menor_5bits')
    for name,x,y in [('A[4..0]',256,64),('B[4..0]',304,96)]:
        p=d.pin(name,'input',192,y); d.wire(p,(x,y),bus=True); d.rail(x,y,512,name)
    gt=d.inst('Maior_5bits','greater',496,160); eq=d.inst('Igual_5bits','equal',496,416)
    for a in [gt,eq]:
        for name,x in [('A[4..0]',256),('B[4..0]',304)]: d.wire((x,a[name][1]),a[name],bus=True)
    ng=d.inst('NOT','not_greater',896,176); ne=d.inst('NOT','not_equal',896,432)
    d.wire(gt['A_maior_que_B'],ng['IN']); d.wire(eq['A_igual_B'],ne['IN'])
    a=d.inst('AND2','strict_less',1216,288)
    for src,dest,x in [(ng['OUT'],a['IN1'],1072),(ne['OUT'],a['IN2'],1104)]: d.route([src,(x,src[1]),(x,dest[1]),dest])
    d.wire(a['OUT'],d.pin('A_menor_que_B','output',1440,a['OUT'][1])); d.save()

def add_sub_bit():
    d=Diagram('ADD_SUB_BIT')
    x=d.pin('X','input',192,160); y=d.pin('Y','input',192,208); sub=d.pin('SUB','input',192,256); ci=d.pin('CI','input',192,304)
    g=d.inst('XOR','invert_y',368,192); a=d.inst('somador_1bit','adder',576,128)
    d.route([x,a['A']]); d.route([y,g['IN1']]); d.route([sub,(336,256),(336,g['IN2'][1]),g['IN2']]); d.route([g['OUT'],(520,g['OUT'][1]),(520,a['B'][1]),a['B']])
    d.route([ci,(544,304),(544,a['Cin'][1]),a['Cin']])
    d.wire(a['Cout'],d.pin('CO','output',800,a['Cout'][1])); d.wire(a['S'],d.pin('R','output',800,a['S'][1])); d.save()

def add_sub6():
    d=Diagram('ADD_SUB6')
    for x,name,y in [(256,'X[5..0]',64),(304,'Y[5..0]',96)]:
        p=d.pin(name,'input',192,y); d.wire(p,(x,y),bus=True); d.rail(x,y,1384,name)
    sub=d.pin('SUB','input',192,128); d.wire(sub,(352,128)); d.wire((352,128),(352,1400))
    d.pin('R[5..0]','output',960,64); d.wire((864,64),(960,64),bus=True); d.rail(864,64,1384,'R[5..0]')
    prev=None
    for i in range(6):
        y=192+200*i; a=d.inst('ADD_SUB_BIT',f'bit{i}',496,y)
        d.tap(256,a['X'],f'X[{i}]'); d.tap(304,a['Y'],f'Y[{i}]')
        d.wire((352,a['SUB'][1]),a['SUB']); d.junction((352,a['SUB'][1]))
        if prev: d.route([prev,(800,prev[1]),(800,y-24),(448,y-24),(448,a['CI'][1]),a['CI']])
        else: d.wire((352,a['CI'][1]),a['CI']); d.junction((352,a['CI'][1]))
        d.tap(864,a['R'],f'R[{i}]'); prev=a['CO']
    d.wire(prev,d.pin('COUT','output',960,prev[1])); d.save()

def sm_c2():
    d=Diagram('SM_C2'); ip=d.pin('A[4..0]','input',192,96); d.wire(ip,(256,96),bus=True); d.rail(256,96,464,'A[4..0]')
    a=d.inst('ADD_SUB6','convert',640,96); d.rail(560,128,424,'Z[5..0]'); d.rail(416,160,424,'MAG6[5..0]')
    for i in range(6):
        y=240+i*32; z=d.inst('GND',f'zero{i}',496,y)['1']; d.tap(560,z,f'Z[{i}]')
        if i<4: d.map_bit(256,416,y,f'A[{i}]',f'MAG6[{i}]',336)
        else:
            z=d.inst('GND',f'upper_zero{i}',336,y-16)['1']; d.tap(416,z,f'MAG6[{i}]')
    d.wire((560,a['X[5..0]'][1]),a['X[5..0]'],bus=True); d.wire((416,a['Y[5..0]'][1]),a['Y[5..0]'],bus=True)
    d.tap(256,a['SUB'],'A[4]'); d.wire(a['R[5..0]'],d.pin('R[5..0]','output',1040,a['R[5..0]'][1]),bus=True); d.save()

def c2_sm():
    d=Diagram('C2_SM'); p=d.pin('R[5..0]','input',192,160); d.wire(p,(256,160),bus=True); d.rail(256,160,600,'R[5..0]')
    a=d.inst('ADD_SUB6','magnitude',560,128); d.rail(384,160,520,'Z[5..0]')
    for i in range(6):
        z=d.inst('GND',f'zero{i}',320,320+i*32)['1']; d.tap(384,z,f'Z[{i}]')
    d.wire((384,a['X[5..0]'][1]),a['X[5..0]'],bus=True); d.wire((256,a['Y[5..0]'][1]),a['Y[5..0]'],bus=True); d.tap(256,a['SUB'],'R[5]')
    r=a['R[5..0]']; d.wire(r,(864,r[1]),'MAG6[5..0]',bus=True); d.rail(864,r[1],560,'MAG6[5..0]')
    # Result sign comes from R5; zero in C2 is necessarily positive.
    o=d.pin('F[5..0]','output',1168,160); d.wire((1056,160),o,bus=True); d.rail(1056,160,600,'F[5..0]')
    for i in range(5):
        y=336+i*32; d.map_bit(864,1056,y,f'MAG6[{i}]',f'F[{i}]',944)
    d.map_bit(256,1056,592,'R[5]','F[5]',944); d.save()

def mux8():
    d=Diagram('MUX8_6'); rows=[]
    # Preserve the same seven MUX2_6 instances and exact three-level selection.
    for i in range(4):
        y=208+i*224; a=d.inst('MUX2_6',f'mux{i}',400,y); rows.append(a)
        for j,p in enumerate(['D0[5..0]','D1[5..0]']):
            ip=d.pin(f'D{2*i+j}[5..0]','input',192,a[p][1]); d.wire(ip,a[p],bus=True)
    mids=[]
    for i in range(2):
        a=d.inst('MUX2_6',f'mux{4+i}',864,320+i*448); mids.append(a)
        for j in range(2):
            src=rows[2*i+j]['Y[5..0]']; dest=a[f'D{j}[5..0]']; x=736+j*32
            d.route([src,(x,src[1]),(x,dest[1]),dest],bus=True)
    last=d.inst('MUX2_6','mux6',1328,544)
    for i in range(2):
        src=mids[i]['Y[5..0]']; dest=last[f'D{i}[5..0]']; x=1200+i*32
        d.route([src,(x,src[1]),(x,dest[1]),dest],bus=True)
    d.wire(last['Y[5..0]'],d.pin('F[5..0]','output',1728,last['Y[5..0]'][1]),bus=True)
    ip=d.pin('S[2..0]','input',192,96); d.wire(ip,(256,96),bus=True); d.rail(256,96,192,'S[2..0]')
    for bit,x,sy,targets in [(0,336,128,rows),(1,800,160,mids),(2,1264,192,[last])]:
        d.wire((256,sy),(x,sy),f'S[{bit}]'); d.junction((256,sy)); end=max(a['SEL'][1] for a in targets)
        d.wire((x,sy),(x,end))
        for a in targets: d.wire((x,a['SEL'][1]),a['SEL']); d.junction((x,a['SEL'][1]))
    d.save()

def maior5():
    # Repair the original dual magnitude-comparator architecture, adding numerical EQ guard.
    d=Diagram('Maior_5bits')
    for name,x,y in [('A[4..0]',256,64),('B[4..0]',304,96)]:
        p=d.pin(name,'input',192,y); d.wire(p,(x,y),bus=True); d.rail(x,y,1120,name)
    ab=d.inst('Maior_4bits','magnitude_ab',480,160); ba=d.inst('Maior_4bits','magnitude_ba',480,384); eq=d.inst('Igual_5bits','numeric_eq',480,928)
    for a,left,right in [(ab,256,304),(ba,304,256)]:
        d.wire((left,a['A[3..0]'][1]),a['A[3..0]'],('A' if left==256 else 'B')+'[3..0]',True)
        d.wire((right,a['B[3..0]'][1]),a['B[3..0]'],('A' if right==256 else 'B')+'[3..0]',True)
    for name,x in [('A[4..0]',256),('B[4..0]',304)]: d.wire((x,eq[name][1]),eq[name],bus=True)
    na=d.inst('NOT','positive_a',480,624); nb=d.inst('NOT','positive_b',480,736)
    d.tap(256,na['IN'],'A[4]'); d.tap(304,nb['IN'],'B[4]')
    pp=d.inst('AND3','positive_gt',960,80); nn=d.inst('AND3','negative_gt',960,416); pn=d.inst('AND2','opposite_sign',960,624)
    d.route([ab['A_maior_que_B'],(800,ab['A_maior_que_B'][1]),(800,pp['IN1'][1]),pp['IN1']])
    d.route([ba['A_maior_que_B'],(816,ba['A_maior_que_B'][1]),(816,nn['IN1'][1]),nn['IN1']])
    d.route([(256,544),(864,544),(864,nn['IN2'][1]),nn['IN2']],'A[4]'); d.junction((256,544))
    d.route([(304,576),(880,576),(880,nn['IN3'][1]),nn['IN3']],'B[4]'); d.junction((304,576))
    d.tap(304,pn['IN2'],'B[4]')
    d.route([na['OUT'],(752,na['OUT'][1]),(752,pp['IN2'][1]),pp['IN2']]); d.route([nb['OUT'],(736,nb['OUT'][1]),(736,pp['IN3'][1]),pp['IN3']])
    d.route([na['OUT'],(752,na['OUT'][1]),(752,pn['IN1'][1]),pn['IN1']]); d.junction((752,na['OUT'][1]))
    g=d.inst('OR3','raw_gt',1280,288)
    for i,a in enumerate([pp,nn,pn]):
        src=a['OUT']; dest=g[f'IN{i+1}']; x=1120+i*24; d.route([src,(x,src[1]),(x,dest[1]),dest])
    ne=d.inst('NOT','not_equal',960,944); d.wire(eq['A_igual_B'],ne['IN'])
    guard=d.inst('AND2','strict_gt',1472,384); d.route([g['OUT'],(1424,g['OUT'][1]),(1424,guard['IN1'][1]),guard['IN1']])
    d.route([ne['OUT'],(1400,ne['OUT'][1]),(1400,guard['IN2'][1]),guard['IN2']]); d.wire(guard['OUT'],d.pin('A_maior_que_B','output',1696,guard['OUT'][1])); d.save()

def enable7():
    d=Diagram('ENABLE7'); p=d.pin('HEX_IN[6..0]','input',192,64); d.wire(p,(256,64),bus=True); d.rail(256,64,1096,'HEX_IN[6..0]')
    en=d.pin('EN','input',192,96); n=d.inst('NOT','disable',368,80); d.wire(en,n['IN']); d.wire(n['OUT'],(480,n['OUT'][1])); d.wire((480,n['OUT'][1]),(480,1096))
    d.rail(800,64,1096,'HEX_OUT[6..0]'); d.wire((800,64),d.pin('HEX_OUT[6..0]','output',912,64),bus=True)
    for i in range(7):
        a=d.inst('OR2',f'segment{i}',608,192+i*128); d.tap(256,a['IN1'],f'HEX_IN[{i}]'); d.wire((480,a['IN2'][1]),a['IN2']); d.junction((480,a['IN2'][1])); d.tap(800,a['OUT'],f'HEX_OUT[{i}]')
    d.save()

def display_pair():
    d=Diagram('decod_7seg_base'); mag=d.pin('MAG[4..0]','input',192,160); d.wire(mag,(256,160),bus=True); d.rail(256,160,448,'MAG[4..0]')
    en=d.pin('EN','input',192,96); d.wire(en,(752,96)); d.wire((752,96),(752,480))
    for i,(entity,out) in enumerate([('decod_7seg_unidade','HEX_UNI[6..0]'),('decod_7seg_dezena','HEX_DEZ[6..0]')]):
        a=d.inst(entity,f'decoder{i}',400,128+i*288); e=d.inst('ENABLE7',f'enable{i}',848,128+i*288)
        d.wire((256,a['MAG[4..0]'][1]),a['MAG[4..0]'],bus=True)
        d.wire(a[out],e['HEX_IN[6..0]'],bus=True); d.wire((752,e['EN'][1]),e['EN']); d.junction((752,e['EN'][1]))
        d.wire(e['HEX_OUT[6..0]'],d.pin(out,'output',1328,e['HEX_OUT[6..0]'][1]),bus=True)
    d.save()

def control():
    d=Diagram('CONTROLE'); s=d.pin('S[2..0]','input',192,96); d.wire(s,(256,96),bus=True); d.rail(256,96,1200,'S[2..0]')
    sub=d.inst('OR2','subtract',400,144); d.tap(256,sub['IN1'],'S[0]'); d.tap(256,sub['IN2'],'S[2]'); d.wire(sub['OUT'],d.pin('SUB','output',1248,sub['OUT'][1]))
    n1=d.inst('NOT','not_s1',400,272); n2=d.inst('NOT','not_s2',400,400); n0=d.inst('NOT','not_s0',400,528)
    for i,n in [(1,n1),(2,n2),(0,n0)]: d.tap(256,n['IN'],f'S[{i}]')
    en=d.inst('AND2','display_enable',768,272); d.route([n1['OUT'],(624,n1['OUT'][1]),(624,en['IN1'][1]),en['IN1']]); d.route([n2['OUT'],(656,n2['OUT'][1]),(656,en['IN2'][1]),en['IN2']]); d.wire(en['OUT'],d.pin('ENF','output',1248,en['OUT'][1]))
    terms=[]
    for i in range(3):
        y=720+i*176; a=d.inst('AND4',f'status_op{i+3}',768,y); terms.append(a)
        inp=d.pin(['EQ','GT','LT'][i],'input',192,a['IN4'][1]); d.wire(inp,a['IN4'])
        # decode 011, 100, 101 and include the comparison predicate.
        bits=[(i+3)>>j&1 for j in range(3)]
        for bit,dest in enumerate([a['IN1'],a['IN2'],a['IN3']]):
            if bits[bit]: d.tap(256,dest,f'S[{bit}]')
            else:
                n=[n0,n1,n2][bit]; x=560+bit*32
                d.route([n['OUT'],(x,n['OUT'][1]),(x,dest[1]),dest]); d.junction((x,n['OUT'][1]))
    o=d.inst('OR3','combine_status',1056,896)
    for i,t in enumerate(terms):
        src=t['OUT']; dest=o[f'IN{i+1}']; x=944+i*24; d.route([src,(x,src[1]),(x,dest[1]),dest])
    d.wire(o['OUT'],d.pin('STATUS','output',1248,o['OUT'][1])); d.save()

def arithmetic():
    d=Diagram('ARITMETICA'); ap=d.pin('A[4..0]','input',192,160); bp=d.pin('B[4..0]','input',192,448); sub=d.pin('SUB','input',192,96)
    ca=d.inst('SM_C2','convert_a',352,128); cb=d.inst('SM_C2','convert_b',352,416); a=d.inst('ADD_SUB6','arithmetic',768,224); out=d.inst('C2_SM','convert_result',1168,224)
    d.wire(ap,ca['A[4..0]'],bus=True); d.wire(bp,cb['A[4..0]'],bus=True)
    for c,p,x in [(ca,'X[5..0]',656),(cb,'Y[5..0]',688)]:
        src=c['R[5..0]']; dest=a[p]; d.route([src,(x,src[1]),(x,dest[1]),dest],bus=True)
    d.route([sub,(720,96),(720,a['SUB'][1]),a['SUB']]); d.wire(a['R[5..0]'],out['R[5..0]'],bus=True); d.wire(out['F[5..0]'],d.pin('F[5..0]','output',1568,out['F[5..0]'][1]),bus=True); d.save()

def ula():
    d=Diagram('ULA')
    for name,x,y in [('A[4..0]',256,64),('B[4..0]',304,96),('S[2..0]',352,128)]:
        ip=d.pin(name,'input',192,y); d.wire(ip,(x,y),bus=True); d.rail(x,y,1680,name)
    a=d.inst('ARITMETICA','arithmetic',496,160); c=d.inst('Complemento_2','raw_complement',496,384)
    comps=[d.inst(entity,inst,496,608+i*224) for i,(entity,inst) in enumerate([('Igual_5bits','equal'),('Maior_5bits','greater'),('Menor_5bits','less')])]
    logic=[d.inst(entity,inst,496,1280+i*224) for i,(entity,inst) in enumerate([('And_5bits','bit_and'),('Xor_5bits','bit_xor')])]
    for p in [a]+comps+logic:
        for name,x in [('A[4..0]',256),('B[4..0]',304)]: d.wire((x,p[name][1]),p[name],bus=True)
    d.wire((304,c['B[4..0]'][1]),c['B[4..0]'],bus=True)
    ctrl=d.inst('CONTROLE','control',976,784); mux=d.inst('MUX8_6','select_result',1696,160)
    d.wire((352,ctrl['S[2..0]'][1]),ctrl['S[2..0]'],bus=True)
    for i,(p,out,inp) in enumerate(zip(comps,['A_igual_B','A_maior_que_B','A_menor_que_B'],['EQ','GT','LT'])):
        src=p[out]; dest=ctrl[inp]; x=816+i*32; d.route([src,(x,src[1]),(x,dest[1]),dest])
    src=ctrl['SUB']; dest=a['SUB']; d.route([src,(1232,src[1]),(1232,32),(448,32),(448,dest[1]),dest])
    for out in ['ENF','STATUS']: d.wire(ctrl[out],d.pin(out,'output',2112,ctrl[out][1]))
    src=a['F[5..0]']; x=1296
    d.wire(src,(x,src[1]),'AR[5..0]',True); d.wire((x,mux['D0[5..0]'][1]),mux['D0[5..0]'],bus=True)
    d.wire((x,src[1]),(x,mux['D1[5..0]'][1]),bus=True); d.wire((x,mux['D1[5..0]'][1]),mux['D1[5..0]'],bus=True); d.junction((x,src[1]))
    for i,p,x in [(2,c,1344),(6,logic[0],1504),(7,logic[1],1536)]:
        src=p['F[5..0]']; dest=mux[f'D{i}[5..0]']; d.route([src,(x,src[1]),(x,dest[1]),dest],bus=True)
    d.rail(1440,mux['D3[5..0]'][1],672,'ZERO6[5..0]')
    for i in range(6):
        z=d.inst('GND',f'zero{i}',1360,480+i*32)['1']; d.tap(1440,z,f'ZERO6[{i}]')
    for i in [3,4,5]: d.wire((1440,mux[f'D{i}[5..0]'][1]),mux[f'D{i}[5..0]'],bus=True)
    d.wire((352,mux['S[2..0]'][1]),mux['S[2..0]'],'S[2..0]',True)
    d.wire(mux['F[5..0]'],d.pin('F[5..0]','output',2112,mux['F[5..0]'][1]),bus=True); d.save()

def magnitude_input():
    d=Diagram('MAG_ENTRADA'); ip=d.pin('X[4..0]','input',192,96); d.wire(ip,(256,96),bus=True); d.rail(256,96,400,'X[4..0]')
    op=d.pin('MAG[4..0]','output',640,96); d.wire((528,96),op,bus=True); d.rail(528,96,400,'MAG[4..0]')
    for i in range(4): d.map_bit(256,528,192+i*48,f'X[{i}]',f'MAG[{i}]',368)
    z=d.inst('GND','upper_zero',368,368)['1']; d.tap(528,z,'MAG[4]'); d.save()

def led_adapter():
    d=Diagram('LEDS_ULA')
    for name,x,y,end in [('SW[17..0]',256,64,944),('F[5..0]',304,96,1552)]:
        ip=d.pin(name,'input',192,y); d.wire(ip,(x,y),bus=True); d.rail(x,y,end,name)
    status=d.pin('STATUS','input',192,1584)
    for name,x,y,end in [('LEDR[17..0]',864,64,1168),('LEDG[8..0]',928,96,1776)]:
        op=d.pin(name,'output',1056,y); d.wire((x,y),op,bus=True); d.rail(x,y,end,name)
    for row,i in enumerate([0,1,2]+list(range(8,18))): d.map_bit(256,864,192+row*56,f'SW[{i}]',f'LEDR[{i}]',608)
    for i in range(3,8):
        z=d.inst('GND',f'unused_red{i}',608,960+(i-3)*40)['1']; d.tap(864,z,f'LEDR[{i}]')
    for i in range(6): d.map_bit(304,928,1248+i*56,f'F[{i}]',f'LEDG[{i}]',608)
    p=d.inst('WIRE','status_led',608,1568); d.wire(status,p['IN']); d.tap(928,p['OUT'],'LEDG[6]')
    for i in [7,8]:
        z=d.inst('GND',f'unused_green{i}',608,1632+(i-7)*56)['1']; d.tap(928,z,f'LEDG[{i}]')
    d.save()

def top():
    d=Diagram('TOP'); sw=d.pin('SW[17..0]','input',192,96); d.wire(sw,(256,96),bus=True); d.rail(256,96,1440,'SW[17..0]')
    u=d.inst('ULA','core',544,128)
    for port,name in [('A[4..0]','SW[17..13]'),('B[4..0]','SW[12..8]'),('S[2..0]','SW[2..0]')]: d.wire((256,u[port][1]),u[port],name,True)
    fp=u['F[5..0]']; d.wire(fp,(896,fp[1]),'F[5..0]',True); d.rail(896,fp[1],1504,'F[5..0]')
    # A/B pairs: one repeated magnitude-adapter function, then original decimal pair.
    for i,(slice_,row) in enumerate([('SW[17..13]',448),('SW[12..8]',768)]):
        m=d.inst('MAG_ENTRADA',f'magnitude_{i}',544,row); p=d.inst('decod_7seg_base',f'display_{i}',1104,row)
        d.wire((256,m['X[4..0]'][1]),m['X[4..0]'],slice_,True); d.wire(m['MAG[4..0]'],p['MAG[4..0]'],bus=True)
        v=d.inst('VCC',f'always_on_{i}',1008,p['EN'][1]-16)['1']; d.wire(v,p['EN'])
        for out,idx in [('HEX_UNI[6..0]',6-2*i),('HEX_DEZ[6..0]',7-2*i)]: d.wire(p[out],d.pin(f'HEX{idx}[6..0]','output',1552,p[out][1]),bus=True)
    p=d.inst('decod_7seg_base','display_result',1104,1088); d.wire((896,p['MAG[4..0]'][1]),p['MAG[4..0]'],'F[4..0]',True)
    en=u['ENF']; dest=p['EN']; d.route([en,(960,en[1]),(960,dest[1]),dest])
    for out,idx in [('HEX_UNI[6..0]',0),('HEX_DEZ[6..0]',1)]: d.wire(p[out],d.pin(f'HEX{idx}[6..0]','output',1552,p[out][1]),bus=True)
    led=d.inst('LEDS_ULA','leds',1104,1376); d.wire((256,led['SW[17..0]'][1]),led['SW[17..0]'],bus=True)
    d.wire((896,led['F[5..0]'][1]),led['F[5..0]'],bus=True)
    src=u['STATUS']; dest=led['STATUS']; d.route([src,(992,src[1]),(992,1488),(480,1488),(480,dest[1]),dest])
    for out in ['LEDR[17..0]','LEDG[8..0]']: d.wire(led[out],d.pin(out,'output',1552,led[out][1]),bus=True)
    for idx in [2,3]:
        y=1664+(idx-2)*416; d.rail(1376,y,y+336,f'HEX{idx}[6..0]'); d.wire((1376,y),d.pin(f'HEX{idx}[6..0]','output',1552,y),bus=True)
        for i in range(7):
            v=d.inst('VCC',f'off_hex{idx}_{i}',1248,y+64+i*40-16)['1']; d.tap(1376,v,f'HEX{idx}[{i}]')
    d.save()

if __name__=='__main__':
    fix_library(); logic5('And_5bits','AND2'); logic5('Xor_5bits','XOR'); complement(); add_sub_bit(); add_sub6(); sm_c2(); c2_sm(); mux2(); mux8(); maior5(); menor5(); enable7(); display_pair(); control(); arithmetic(); ula(); magnitude_input(); led_adapter(); top()
