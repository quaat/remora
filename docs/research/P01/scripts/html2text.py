import sys, html, re
from html.parser import HTMLParser
class P(HTMLParser):
    def __init__(s): super().__init__(); s.out=[]; s.skip=0
    def handle_starttag(s,t,a):
        if t in ('script','style'): s.skip+=1
        if t in ('p','li','tr','h1','h2','h3','h4','br','div','pre'): s.out.append('\n')
    def handle_endtag(s,t):
        if t in ('script','style') and s.skip: s.skip-=1
    def handle_data(s,d):
        if not s.skip: s.out.append(d)
for path in sys.argv[1:]:
    p=P(); p.feed(open(path,encoding='utf-8',errors='replace').read())
    txt=re.sub(r'\n\s*\n+','\n',''.join(p.out))
    open(path+'.txt','w').write(txt)
    print(path, len(txt))
