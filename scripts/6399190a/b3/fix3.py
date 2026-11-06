import os
for dp,_,fs in os.walk('.'):
    for f in fs:
        if f.endswith(('.py','.ps1','.cs')):
            p=os.path.join(dp,f); b=open(p,'rb').read()
            if b'\x08' in b:
                open(p,'wb').write(b.replace(b'scratchpad\x083', b'scratchpad\b3')); print('fixed',p)
