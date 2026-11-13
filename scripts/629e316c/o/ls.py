import os
for f in os.listdir('D:/РАБОЧКА'):
    if 'ожарная' in f:
        p=os.path.join('D:/РАБОЧКА',f); print(ascii(os.listdir(p)))
