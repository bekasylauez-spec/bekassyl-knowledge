import io
S=r'D:\_claude_work\zavod_km'; D=r'D:\_claude_work\zavod_km_uz'
def rw(src,dst,reps,enc='utf-8-sig'):
    t=io.open(src,encoding=enc).read()
    for a,b in reps:
        assert a in t,(src,a); t=t.replace(a,b)
    io.open(dst,'w',encoding=enc).write(t)
rw(S+r'\net\rz.cs',D+r'\net\rz.cs',[(r'zavod_km\job',r'zavod_km_uz\job')])
rw(S+r'\net\rzlisten.cs',D+r'\net\uzlisten.cs',[(r'zavod_km\job',r'zavod_km_uz\job'),('"ZKLISTEN"','"UZLISTEN"'),('"ZKSTOP"','"UZSTOP"'),('namespace ZKListen','namespace UZListen'),('typeof(ZKListen.Cmds)','typeof(UZListen.Cmds)')])
rw(S+r'\net\job.ps1',D+r'\net\job.ps1',[(r'zavod_km\net',r'zavod_km_uz\net'),(r'zavod_km\job',r'zavod_km_uz\job'),('"zk.dwg"','"uz.dwg"'),('"zk_"','"uz_"')])
rw(S+r'\uz2\pl2.ps1',D+r'\uz2\pl2.ps1',[(r'zavod_km\zk_p.dwg',r'zavod_km_uz\uz_p.dwg'),(r'zavod_km\plotU.log',r'zavod_km_uz\plot.log')])
B='D:/_claude_work/zavod_km_uz/'.replace('/', chr(92))
io.open(D+r'\net\boot.scr','w',encoding='cp1251').write('(setvar "FILEDIA" 0)\n(setvar "SECURELOAD" 0)\n_.NETLOAD\n"'+B+'net'+chr(92)+'uzlisten.dll"\nUZLISTEN\n_.OPEN\n"'+B+'uz.dwg"\n')
