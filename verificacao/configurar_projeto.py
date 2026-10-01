"""Configure TOP and verified DE2-115 pins (Terasic User Manual, tables 4-1,3,4)."""
from pathlib import Path
import re,csv
ROOT=Path(__file__).resolve().parent.parent
groups={
 'SW': 'AB28 AC28 AC27 AD27 AB27 AC26 AD26 AB26 AC25 AB25 AC24 AB24 AB23',
 'LEDR':'G19 F19 E19 F21 F18 E18 J19 H19 J17 G17 J15 H16 J16 H17 F15 G15 G16 H15',
 'LEDG':'E21 E22 E25 E24 H21 G20 G22 G21 F17',
 'HEX0':'G18 F22 E17 L26 L25 J22 H22',
 'HEX1':'M24 Y22 W21 W22 W25 U23 U24',
 'HEX2':'AA25 AA26 Y25 W26 Y26 W27 W28',
 'HEX3':'V21 U21 AB20 AA21 AD24 AF23 Y19',
 'HEX4':'AB19 AA19 AG21 AH21 AE19 AF19 AE18',
 'HEX5':'AD18 AC18 AB18 AH19 AG19 AF18 AH18',
 'HEX6':'AA17 AB16 AA16 AB17 AB15 AA15 AC17',
 'HEX7':'AD17 AE17 AG17 AH17 AF17 AG18 AA14',
}
url='https://www.terasic.com.tw/wiki/images/f/ff/DE2_115_User_manual_2013.pdf'
rows=[]
for group,pins in groups.items():
    for bit,pin in enumerate(pins.split()):
        # Fixed LED banks: 2.5 V; JP7 default: 2.5 V; JP6 default: 3.3 V.
        standard='3.3-V LVTTL' if group in ['HEX4','HEX5','HEX6','HEX7'] or (group=='HEX3' and bit>=2) else '2.5 V'
        supply='JP7=2.5V' if group=='SW' or group in ['HEX1','HEX2'] or (group=='HEX0' and bit>=3) or (group=='HEX3' and bit<2) else 'JP6=3.3V' if standard=='3.3-V LVTTL' and not (group=='HEX7' and bit==6) else 'fixo'
        rows.append(dict(signal=f'{group}[{bit}]',pin='PIN_'+pin,io_standard=standard,supply=supply,source=url))
with (ROOT/'verificacao/pinagem_de2_115.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
qsf=ROOT/'projeto-ula.qsf'; s=(ROOT/'verificacao/originais/projeto-ula.qsf').read_text()
s=re.sub(r'(?m)^set_global_assignment -name BDF_FILE.*\n','',s)
s=re.sub(r'(?m)^set_global_assignment -name DEVICE .*','set_global_assignment -name DEVICE EP4CE115F29C7',s)
s=re.sub(r'(?m)^set_global_assignment -name TOP_LEVEL_ENTITY .*','set_global_assignment -name TOP_LEVEL_ENTITY TOP',s)
s=s.replace('PROJECT_OUTPUT_DIRECTORY output_files','PROJECT_OUTPUT_DIRECTORY output_files/integracao')
s+='\nset_global_assignment -name RESERVE_ALL_UNUSED_PINS "AS INPUT TRI-STATED"\n'
for f in sorted(ROOT.glob('*.bdf')): s+=f'set_global_assignment -name BDF_FILE {f.name}\n'
for r in rows:
    s+=f'set_location_assignment {r["pin"]} -to {r["signal"]}\nset_instance_assignment -name IO_STANDARD "{r["io_standard"]}" -to {r["signal"]}\n'
qsf.write_text(s)
assert len({r['pin'] for r in rows})==len(rows)==96
# Preserve VWF stimuli; use separate projects whose tops match their signal names.
for mux in ['MUX1','MUX2_6','MUX8_6']:
    folder=ROOT/'verificacao/vwf'/mux; folder.mkdir(parents=True,exist_ok=True)
    (folder/(mux+'.qpf')).write_text(f'QUARTUS_VERSION = "21.1"\nPROJECT_REVISION = "{mux}"\n')
    srcs={'MUX1':['MUX1'],'MUX2_6':['MUX1','MUX2_6'],'MUX8_6':['MUX1','MUX2_6','MUX8_6']}[mux]
    (folder/(mux+'.qsf')).write_text(f'set_global_assignment -name FAMILY "Cyclone IV E"\nset_global_assignment -name DEVICE EP4CE115F29C7\nset_global_assignment -name TOP_LEVEL_ENTITY {mux}\n'+''.join(f'set_global_assignment -name BDF_FILE ../../../{n}.bdf\n' for n in srcs))
    vf=ROOT/('Waveform'+mux+'.vwf'); s=(ROOT/'verificacao/originais'/vf.name).read_text()
    s=s.replace('D:/Users/mesa2/Documents/projeto_ula_mux/',ROOT.as_posix()+'/')
    s=s.replace('mulitplexador',mux)
    s=s.replace(f' {mux} -c {mux}',f' "{(folder/mux).as_posix()}" -c {mux}')
    s=s.replace(ROOT.as_posix()+'/simulation/qsim/',folder.as_posix()+'/simulation/qsim/')
    vf.write_text(s)
print('TOP configured; 96 physical ports assigned; VWF stimuli preserved.')
