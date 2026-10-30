import sys, re
md=open(sys.argv[1],encoding='utf-8').read(); live=open(sys.argv[2],encoding='utf-8').read()
norm=lambda s: re.sub(r'\s+',' ',re.sub(r'[`*_\[\]()|>#]','',s)).strip()
L=norm(live)
frags=[]
for line in md.splitlines():
    t=norm(re.sub(r'\]\([^)]*\)','',line))
    if len(t)>=60 and not t.startswith(('---','title:','description:')): frags.append(t[:60])
hit=sum(1 for f in frags if f in L)
print(sys.argv[1].split('/')[-1], 'fragments', len(frags), 'found', hit, f'{hit/len(frags):.1%}' if frags else '')
for f in [f for f in frags if f not in L][:int(sys.argv[3]) if len(sys.argv)>3 else 3]: print('  missing:', f)
