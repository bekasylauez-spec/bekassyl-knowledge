import sys,collections
D='C:/Users/Public/Documents/LIRA SAPR/LIRA SAPR 2024/Work/ABK_zavod.DOCS/AUTORES/'
MAP={'tbl01.101.csv':'tbl25.101.csv','tbl03.5_1.csv':'tbl26.5_1.csv','tbl05.9_1.csv':'tbl27.9_1.csv','tbl07.11_1.csv':'tbl28.11_1.csv','tbl08.17_1.csv':'tbl29.17_1.csv'}
def rows(fn):
    fn=MAP.get(fn,fn)
    for l in open(D+fn,'rb'):
        s=l.decode('utf-8','ignore') if b'\xef\xbb\xbf' in l else l.decode('cp1251','ignore')
        yield s.replace('\ufeff','').rstrip('\r\n').split(';')
