"""Render BDF geometry directly for visual inspection (not a Quartus GUI capture)."""
from bdf_tools import *
from PIL import Image,ImageDraw,ImageFont
import math
OUT=ROOT/'verificacao/desenhos'; OUT.mkdir(exist_ok=True)
FONT='C:/Windows/Fonts/arial.ttf'
def render(path):
    nodes=parse(path.read_text()); boxes=[list(map(int,child(n,'rect')[1:])) for n in nodes if n[0] in ['pin','symbol']]
    minx=min(r[0] for r in boxes)-40; miny=min(r[1] for r in boxes)-40
    maxx=max(r[2] for r in boxes)+40; maxy=max(r[3] for r in boxes)+40
    scale=min(1.25,2600/(maxx-minx)); im=Image.new('RGB',(int((maxx-minx)*scale),int((maxy-miny)*scale)),'white'); dr=ImageDraw.Draw(im)
    def coord(p,ox,oy): return ((int(p[1])+ox-minx)*scale,(int(p[2])+oy-miny)*scale)
    def draw(n,ox=0,oy=0):
        tag=n[0]
        if tag=='text':
            if ['invisible'] in n:return
            r=child(n,'rect'); f=child(n,'font'); fs=children(f,'font_size'); size=int(fs[0][1]) if fs else 8
            # Point sizes in BDF are rendered in device pixels by the editor.
            font=ImageFont.truetype(FONT,max(8,int(size*1.35*scale)))
            dr.text(((int(r[1])+ox-minx)*scale,(int(r[2])+oy-miny)*scale),unquote(n[1]),fill='#101010',font=font)
        elif tag in ['line','connector']:
            ps=children(n,'pt'); bus=['bus'] in n or any(c[0]=='line_width' and int(c[1])>1 for c in n if isinstance(c,list)); width=max(1,int((3 if bus else 1)*scale))
            dr.line([coord(p,ox,oy) for p in ps],fill='#111111',width=width)
            for t in children(n,'text'):draw(t,ox,oy)
        elif tag=='junction':
            x,y=coord(child(n,'pt'),ox,oy);r=2*scale;dr.ellipse((x-r,y-r,x+r,y+r),fill='black')
        elif tag in ['rectangle','circle','arc']:
            r=list(map(int,child(n,'rect')[1:])); box=((r[0]+ox-minx)*scale,(r[1]+oy-miny)*scale,(r[2]+ox-minx)*scale,(r[3]+oy-miny)*scale)
            if tag=='rectangle':dr.rectangle(box,outline='black',width=max(1,int(scale)))
            elif tag=='circle':dr.ellipse(box,outline='black',width=max(1,int(scale)))
            else:
                ps=children(n,'pt');cx=(r[0]+r[2])/2;cy=(r[1]+r[3])/2
                angles=[math.degrees(math.atan2(int(p[2])-cy,int(p[1])-cx)) for p in ps]
                dr.arc(box,angles[1],angles[0],fill='black',width=max(1,int(scale)))
        elif tag in ['symbol','pin']:
            r=list(map(int,child(n,'rect')[1:])); sx,sy=r[:2]
            for t in children(n,'text'):draw(t,sx,sy)
            for p in children(n,'port'):
                for t in children(p,'text')[1:]:draw(t,sx,sy)
                for line in children(p,'line'):draw(line,sx,sy)
            for drawing in children(n,'drawing'):
                for part in drawing[1:]:draw(part,sx,sy)
    for n in nodes:
        if n[0]=='connector':draw(n)
    for n in nodes:
        if n[0]!='connector':draw(n)
    im.save(OUT/(path.stem+'.png'))
    return im.size
if __name__=='__main__':
    for name in __import__('sys').argv[1:] or [p.stem for p in ROOT.glob('*.bdf')]:
        print(name,render(ROOT/(name+'.bdf')))
