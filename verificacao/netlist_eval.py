"""Evaluate Quartus BDF-exported combinational Verilog; no behavioral model here.

Supports only wires, continuous bitwise assignments, constants, concatenations
and named structural instances. Unsupported syntax fails closed.
"""
import re
from pathlib import Path
from functools import lru_cache

def names(expr):
    return set(re.findall(r'\b[A-Za-z_]\w*', re.sub(r"\d+'[bdh][0-9a-fA-F]+", '', expr)))

def expression(s):
    toks = re.findall(r"\d+'[bdh][0-9a-fA-F]+|[A-Za-z_]\w*|\d+|~\^|[~&|^(){}\[\]:,]", s)
    if ''.join(toks) != re.sub(r'\s+', '', s):
        raise ValueError('Unsupported expression: '+s)
    pos=0
    def parse(minp=0):
        nonlocal pos
        t=toks[pos]; pos+=1
        if t=='~':
            a=parse(4); node=('not',a)
        elif t=='(':
            node=parse(); assert toks[pos]==')'; pos+=1
        elif t=='{':
            args=[parse()]
            while toks[pos]==',': pos+=1; args.append(parse())
            assert toks[pos]=='}'; pos+=1; node=('cat',args)
        elif re.fullmatch(r"\d+'[bdh][0-9a-fA-F]+",t):
            w,base,num=re.fullmatch(r"(\d+)'([bdh])([0-9a-fA-F]+)",t).groups()
            node=('const',int(num,{'b':2,'d':10,'h':16}[base]),int(w))
        elif t.isdigit(): node=('const',int(t),max(1,int(t).bit_length()))
        else:
            node=('var',t)
            if pos<len(toks) and toks[pos]=='[':
                pos+=1; hi=int(toks[pos]); pos+=1; lo=hi
                if toks[pos]==':': pos+=1; lo=int(toks[pos]); pos+=1
                assert toks[pos]==']'; pos+=1; node=('slice',t,hi,lo)
        prec={'|':1,'^':2,'~^':2,'&':3}
        while pos<len(toks) and prec.get(toks[pos],0)>minp:
            op=toks[pos]; pos+=1; node=(op,node,parse(prec[op]))
        return node
    ast=parse(); assert pos==len(toks)
    return ast

def value(n,env,widths):
    op=n[0]
    if op=='var': return env[n[1]],widths[n[1]][0]
    if op=='const': return n[1],n[2]
    if op=='slice':
        w=n[2]-n[3]+1
        return (env[n[1]]>>(n[3]-widths[n[1]][1]))&((1<<w)-1),w
    if op=='not':
        v,w=value(n[1],env,widths); return (~v)&((1<<w)-1),w
    if op=='cat':
        v=w=0
        for a in n[1]:
            av,aw=value(a,env,widths); v=(v<<aw)|av; w+=aw
        return v,w
    a,wa=value(n[1],env,widths); b,wb=value(n[2],env,widths); w=max(wa,wb)
    v={'&':lambda:a&b,'|':lambda:a|b,'^':lambda:a^b,'~^':lambda:~(a^b)}[op]()
    return v&((1<<w)-1),w

class Circuit:
    def __init__(self,folder):
        self.modules={}
        for f in Path(folder).glob('*.v'):
            s=re.sub(r'//[^\n]*','',f.read_text())
            mod=re.search(r'module\s+(\w+)\s*\([^;]*\);(.*?)endmodule',s,re.S)
            if not mod: continue
            name,s=mod.groups(); widths={}; inputs=[]; outputs=[]
            for direction,hi,lo,n in re.findall(r'\b(input wire|output wire|wire)\s*(?:\[(\d+):(\d+)\])?\s*(\w+)\s*;',s):
                widths[n]=(int(hi)-int(lo)+1,int(lo)) if hi else (1,0)
                if direction=='input wire': inputs.append(n)
                if direction=='output wire': outputs.append(n)
            ops=[]
            for target,expr in re.findall(r'assign\s+([^=]+)=([^;]+);',s):
                ops.append(('assign',target.strip(),expression(expr.strip()),names(expr)))
            for entity,inst,body in re.findall(r'^\s*(\w+)\s+(\w+)\s*\((.*?)\);',s,re.M|re.S):
                if entity=='module': continue
                conns={p:e.strip() for p,e in re.findall(r'\.(\w+)\(([^()]*)\)',body)}
                ops.append(('inst',entity,conns,None))
            self.modules[name]=(widths,inputs,outputs,ops)
        self.cache={}

    def run(self,name,**args):
        widths,inputs,outputs,ops=self.modules[name]
        key=(name,tuple(args[n] for n in inputs))
        if key in self.cache: return self.cache[key]
        env=dict(args); masks={n:((1<<widths[n][0])-1) for n in args}
        def ready(e):
            for n in names(e):
                if masks.get(n,0)!=((1<<widths[n][0])-1): return False
            return True
        def put(target,v):
            m=re.fullmatch(r'(\w+)(?:\[(\d+)(?::(\d+))?\])?',target)
            if not m: raise ValueError('Target '+target)
            n,hi,lo=m.groups(); w,base=widths[n]
            if hi is None: env[n]=v&((1<<w)-1); masks[n]=(1<<w)-1
            else:
                hi=int(hi); lo=int(lo) if lo else hi
                mask=((1<<(hi-lo+1))-1)<<(lo-base)
                env[n]=(env.get(n,0)&~mask)|((v<<(lo-base))&mask)
                masks[n]=masks.get(n,0)|mask
        todo=list(ops)
        while todo:
            pending=[]
            for op in todo:
                if op[0]=='assign':
                    _,t,ast,deps=op
                    if all(masks.get(n,0)==((1<<widths[n][0])-1) for n in deps): put(t,value(ast,env,widths)[0])
                    else: pending.append(op)
                else:
                    _,entity,conns,_=op
                    child=self.modules[entity]
                    if all(n in conns and ready(conns[n]) for n in child[1]):
                        res=self.run(entity,**{n:value(expression(conns[n]),env,widths)[0] for n in child[1]})
                        for n in child[2]:
                            if n in conns and conns[n]: put(conns[n],res[n])
                    else: pending.append(op)
            if len(pending)==len(todo): raise ValueError(f'{name}: floating or cyclic nets: {pending[:2]}')
            todo=pending
        res={n:env[n] for n in outputs}; self.cache[key]=res
        return res

if __name__=='__main__':
    c=Circuit(Path(__file__).parent/'netlist_original')
    seg=[0x40,0x79,0x24,0x30,0x19,0x12,0x02,0x78,0x00,0x10]
    sm=lambda a:-(a&15) if a&16 else a&15
    for mod,out,pred in [('Igual_5bits','A_igual_B',lambda a,b:sm(a)==sm(b)),('Maior_5bits','A_maior_que_B',lambda a,b:sm(a)>sm(b)),('Menor_5bits','A_menor_que_B',lambda a,b:sm(a)<sm(b))]:
        failures=[]
        for a in range(32):
            for b in range(32):
                r=c.run(mod,A=a,B=b)[out]
                if r!=pred(a,b): failures.append((a,b,r,int(pred(a,b))))
        print(mod,'failures',len(failures),'examples',failures[:5])
    for mod,out,fn in [('decof7_unidade','HEX_UNI',lambda n:n%10),('decof7_dezena','HEX_DEZ',lambda n:n//10)]:
        failures=[]
        for n in range(32):
            r=c.run(mod,MAG=n)[out]
            if r!=seg[fn(n)]: failures.append((n,r,seg[fn(n)]))
        print(mod,'failures',len(failures),'examples',failures[:10])
