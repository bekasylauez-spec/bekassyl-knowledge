s=open('rmc_01b_test_planes.cs',encoding='utf-8').read()
bad="Split('\n')[0]"
print(s.count(bad))
s=s.replace(bad,"Split((char)10)[0]")
open('rmc_01b_test_planes.cs','w',encoding='utf-8').write(s)
