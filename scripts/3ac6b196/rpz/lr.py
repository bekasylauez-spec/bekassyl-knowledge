import sys,collections
D='C:/Users/Public/Documents/LIRA SAPR/LIRA SAPR 2024/Work/ABK_zavod.DOCS/AUTORES/'
def rows(fn):
    for l in open(D+fn,'rb'):
        s=l.decode('utf-8','ignore') if b'\xef\xbb\xbf' in l else l.decode('cp1251','ignore')
        yield s.replace('\ufeff','').rstrip('\r\n').split(';')
