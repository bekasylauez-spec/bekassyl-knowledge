import os
root = r"C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\adfe14b1-7db1-4661-b9df-9f007fc4d82c\scratchpad\gal"
old = rb"2ce8f87a-4a49-4808-8cfa-d9a5f578e5ce\scratchpad"
new = rb"adfe14b1-7db1-4661-b9df-9f007fc4d82c\scratchpad\gal"
n = 0
for r, _, fs in os.walk(root):
    for f in fs:
        if f.split('.')[-1].lower() in ('py', 'cs', 'ps1', 'scr', 'txt', 'json'):
            p = os.path.join(r, f)
            b = open(p, 'rb').read()
            if old in b:
                open(p, 'wb').write(b.replace(old, new)); n += 1
print('fixed', n)
