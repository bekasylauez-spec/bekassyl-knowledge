import os
for dp,_,fs in os.walk('.'):
    for f in fs:
        if f.endswith(('.py','.ps1','.cs')):
            p=os.path.join(dp,f); b=open(p,'rb').read()
            nb=b.replace(b'scratchpad'+bytes([8])+b'3', b'scratchpad'+bytes([92])+b'b3').replace(b'3'+bytes([4])+b'.', b'3'+bytes([92])+b'4.')
            if nb!=b: open(p,'wb').write(nb); print('fixed',p)
