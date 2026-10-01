"""S-expression utilities and orthogonal BDF/BSF authoring helpers."""
import re,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def parse(s):
    s=re.sub(r'/\*.*?\*/','',s,flags=re.S)
    toks=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',s); stack=[]; result=[]
    for t in toks:
        if t=='(': a=[]; (stack[-1] if stack else result).append(a); stack.append(a)
        elif t==')': stack.pop()
        else: stack[-1].append(t)
    assert not stack
    return result
def form(n,indent=0):
    if all(not isinstance(v,list) for v in n): return '('+' '.join(n)+')'
    head=[]; rest=[]
    for v in n:
        (rest if isinstance(v,list) else head).append(v)
    return '('+' '.join(head)+'\n'+'\n'.join('  '*(indent+1)+form(v,indent+1) for v in rest)+'\n'+'  '*indent+')'
def child(n,key): return next(v for v in n if isinstance(v,list) and v[0]==key)
def children(n,key): return [v for v in n if isinstance(v,list) and v[0]==key]
def unquote(x): return x[1:-1] if x.startswith('"') else x
def q(x): return '"'+x+'"'
def rect(*xs): return ['rect',*[str(x) for x in xs]]
def pt(x,y): return ['pt',str(x),str(y)]
def text(s,x,y,size=8): return ['text',q(s),rect(x,y,x+max(12,len(s)*7),y+16),['font',q('Arial'),['font_size',str(size)]]]
HEADER=(ROOT/'somador_1bit.bdf').read_text().split('(header')[0]
def write(path,nodes,kind='graphic'):
    Path(path).write_text(HEADER+f'(header "{kind}" (version "'+('1.4' if kind=='graphic' else '1.2')+'"))\n'+'\n'.join(form(n) for n in nodes)+'\n')
def interface(path):
    result=[]
    for n in parse(Path(path).read_text()):
        if n[0]=='pin':
            direction='input' if any(v==['input'] for v in n) else 'output'
            name=unquote(children(n,'text')[1][1]); result.append((direction,name))
    return result
def symbol(name,ports):
    ins=[n for d,n in ports if d=='input']; outs=[n for d,n in ports if d=='output']
    w=max(192,((max([len(n) for _,n in ports],default=1)*14+64+7)//8)*8)
    h=max(len(ins),len(outs))*32+48
    n=['symbol',rect(0,0,w,h),text(name,20,0),text('inst',20,h-20)]
    for direction,ns in [('input',ins),('output',outs)]:
        for i,p in enumerate(ns):
            x=0 if direction=='input' else w; y=32+i*32
            line=['line',pt(x,y),pt(16 if x==0 else w-16,y)]
            if '[' in p: line.append(['line_width','3'])
            n.append(['port',pt(x,y),[direction],text(p,0,0),text(p,22 if x==0 else w-22-len(p)*7,y-8),line])
    n.append(['drawing',['rectangle',rect(16,16,w-16,h-16)]])
    return n
def regen(name): write(ROOT/(name+'.bsf'),[symbol(name,interface(ROOT/(name+'.bdf')))],'symbol')

PRIMS={}
for f in (ROOT/'verificacao/originais').glob('*.bdf'):
    for n in parse(f.read_text()):
        if n[0]!='symbol': continue
        name=unquote(child(n,'text')[1])
        if name in ['NOT','GND','VCC','XOR','XNOR'] or re.fullmatch('(AND|OR|NOR|NAND)[2-6]',name):
            r=list(map(int,child(n,'rect')[1:])); ps=children(n,'port')
            # Prefer horizontal, unrotated, left-to-right primitive drawings.
            inp=[child(p,'pt') for p in ps if ['input'] in p]
            out=[child(p,'pt') for p in ps if ['output'] in p]
            if all(int(p[1])==0 for p in inp) and all(int(p[1])==r[2]-r[0] for p in out): PRIMS.setdefault(name,n)

# Quartus built-in identity primitive provides explicit vector remapping.
_wire=Path('C:/intelFPGA_lite/21.1/quartus/libraries/primitives/buffer/wire.bsf').read_text()
PRIMS['WIRE']=next(n for n in parse(_wire[_wire.index('(header'):]) if n[0]=='symbol')

class Diagram:
    def __init__(self,name): self.name=name; self.nodes=[]; self.junc=set(); self.rails=[]
    def pin(self,name,direction,x,y):
        template=next(n for n in parse((ROOT/'somador_1bit.bdf').read_text()) if n[0]=='pin' and [direction] in n)
        n=copy.deepcopy(template); child(n,'rect')[1:]=list(map(str,[x-168,y-8,x,y+8] if direction=='input' else [x,y-8,x+176,y+8]))
        children(n,'text')[1][1]=q(name); children(n,'text')[1][2]=rect(5 if direction=='input' else 90,0,(5 if direction=='input' else 90)+len(name)*7,16)
        self.nodes.append(n); return (x,y)
    def inst(self,entity,instance,x,y):
        if entity in PRIMS: n=copy.deepcopy(PRIMS[entity])
        else:
            path=ROOT/(entity+'.bsf')
            if not path.exists(): regen(entity)
            n=copy.deepcopy(next(v for v in parse(path.read_text()) if v[0]=='symbol'))
        r=child(n,'rect'); w=int(r[3])-int(r[1]); h=int(r[4])-int(r[2]); r[1:]=list(map(str,[x,y,x+w,y+h]))
        it=children(n,'text')[1]; it[1]=q(instance); it[2]=rect(16,h-8,16+len(instance)*7,h+8)
        if entity=='WIRE': it.append(['invisible'])
        self.nodes.append(n)
        return {unquote(children(p,'text')[0][1]):(x+int(child(p,'pt')[1]),y+int(child(p,'pt')[2])) for p in children(n,'port')}
    def wire(self,a,b,name=None,bus=False):
        assert a[0]==b[0] or a[1]==b[1],(a,b)
        if a==b: return
        n=['connector']
        if name: n.append(text(name,min(a[0],b[0])+8,min(a[1],b[1])-18,7))
        n.extend([pt(*a),pt(*b)])
        if bus: n.append(['bus'])
        self.nodes.append(n)
        for x,y0,y1 in self.rails:
            for p in [a,b]:
                if p[0]==x and y0<=p[1]<=y1: self.junction(p)
    def route(self,points,name=None,bus=False):
        for i in range(len(points)-1): self.wire(points[i],points[i+1],name if i==0 else None,bus)
    def junction(self,p): self.junc.add(p)
    def rail(self,x,y0,y1,name):
        self.wire((x,y0),(x,y1),name,bus=True); self.rails.append((x,y0,y1)); return x
    def tap(self,x,dest,name):
        self.wire((x,dest[1]),dest,name)
        if dest[0]<x:
            child(self.nodes[-1],'text')[2]=rect(x-len(name)*7-16,dest[1]-18,x-16,dest[1]-2)
        self.junction((x,dest[1]))
    def constant(self,v,x,y):
        return self.inst('VCC' if v else 'GND','one' if v else 'zero',x,y)['1']
    def map_bit(self,srcx,dstx,y,srcname,dstname,x):
        p=self.inst('WIRE','map_'+dstname.replace('[','_').replace(']',''),x,y-16)
        self.tap(srcx,p['IN'],srcname); self.tap(dstx,p['OUT'],dstname)
    def save(self):
        write(ROOT/(self.name+'.bdf'),self.nodes+[['junction',pt(*p)] for p in sorted(self.junc)])
        regen(self.name)
