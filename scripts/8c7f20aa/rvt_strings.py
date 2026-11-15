# Minimal OLE/CFB reader for a Revit .rvt (no Revit needed): lists streams, saves the preview,
# inflates every gzip member of every stream and dumps the unique UTF-16LE / UTF-8 strings.
import sys, os, struct, zlib, mmap, re, collections

def cfb_streams(path):
    f = open(path, 'rb'); m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    h = m[:512]
    ss = 1 << struct.unpack_from('<H', h, 0x1E)[0]; mss = 1 << struct.unpack_from('<H', h, 0x20)[0]
    nfat = struct.unpack_from('<I', h, 0x2C)[0]; dir1 = struct.unpack_from('<I', h, 0x30)[0]
    cutoff = struct.unpack_from('<I', h, 0x38)[0]; mf1 = struct.unpack_from('<I', h, 0x3C)[0]
    difat1 = struct.unpack_from('<I', h, 0x44)[0]
    difat = list(struct.unpack_from('<109I', h, 0x4C))
    sec = lambda n: m[(n + 1) * ss:(n + 2) * ss]
    d = difat1
    while d < 0xFFFFFFFA:
        s = sec(d); vals = struct.unpack('<%dI' % (ss // 4), s); difat += vals[:-1]; d = vals[-1]
    fat = []
    for n in difat[:nfat]:
        if n >= 0xFFFFFFFA: continue
        fat += struct.unpack('<%dI' % (ss // 4), sec(n))
    def chain(st):
        out = []
        while st < 0xFFFFFFFA and len(out) < 10_000_000: out.append(st); st = fat[st]
        return out
    def read(st, size):
        b = b''.join(sec(n) for n in chain(st)); return b[:size]
    dirb = b''.join(sec(n) for n in chain(dir1))
    ents = []
    for i in range(len(dirb) // 128):
        e = dirb[i * 128:(i + 1) * 128]
        nl = struct.unpack_from('<H', e, 0x40)[0]
        name = e[:max(nl - 2, 0)].decode('utf-16le', 'replace')
        typ = e[0x42]; l, r, c = struct.unpack_from('<III', e, 0x44)
        st = struct.unpack_from('<I', e, 0x74)[0]; size = struct.unpack_from('<Q', e, 0x78)[0]
        if ss == 512: size &= 0xFFFFFFFF
        ents.append(dict(name=name, typ=typ, l=l, r=r, c=c, st=st, size=size))
    root = ents[0]; ministream = read(root['st'], root['size'])
    minifat = []
    for n in chain(mf1): minifat += struct.unpack('<%dI' % (ss // 4), sec(n))
    def readmini(st, size):
        out = []
        while st < 0xFFFFFFFA: out.append(ministream[st * mss:(st + 1) * mss]); st = minifat[st]
        return b''.join(out)[:size]
    # walk the tree for full paths
    res = []
    def walk(i, pre):
        if i == 0xFFFFFFFF or i >= len(ents): return
        e = ents[i]; walk(e['l'], pre); walk(e['r'], pre)
        p = pre + '/' + e['name'] if pre else e['name']
        if e['typ'] == 2:
            data = readmini(e['st'], e['size']) if e['size'] < cutoff else read(e['st'], e['size'])
            res.append((p, data))
        elif e['typ'] == 1: walk(e['c'], p)
    walk(root['c'], '')
    return res

def inflate_all(data):
    outs = []; i = 0; mv = memoryview(data); n = len(data)
    while True:
        j = data.find(b'\x1f\x8b\x08', i)
        if j < 0: break
        d = zlib.decompressobj(16 + 15); pos = j; parts = []; ok = True
        try:
            while pos < n:
                chunk = mv[pos:pos + 262144]; parts.append(d.decompress(chunk))
                if d.eof: pos += len(chunk) - len(d.unused_data); break
                pos += len(chunk)
        except zlib.error:
            ok = False
        if ok and parts:
            outs.append(b''.join(parts)); i = max(pos, j + 3)
        else:
            i = j + 3
    return outs

u16 = re.compile(rb'(?:[\x09\x0a\x0d\x20-\x7e\xa0-\xff]\x00|[\x00-\xff]\x04|[\x13\x14\x16\x22]\x20|\x16\x21){3,}')

def main(path, tag, outdir):
    os.makedirs(outdir, exist_ok=True)
    streams = cfb_streams(path)
    cnt = collections.Counter(); order = []
    with open(os.path.join(outdir, tag + '_streams.txt'), 'w', encoding='utf-8') as fo:
        for p, data in streams:
            fo.write('%10d  %s\n' % (len(data), p))
            if 'Preview' in p:
                k = data.find(b'\x89PNG')
                if k >= 0: open(os.path.join(outdir, tag + '_preview.png'), 'wb').write(data[k:])
            if p in ('BasicFileInfo', 'ProjectInformation', 'TransmissionData'):
                blobs = [data]
            else:
                blobs = inflate_all(data) or [data]
            print('%-40s %10d -> %d blobs %d bytes' % (p, len(data), len(blobs), sum(len(x) for x in blobs)), flush=True)
            for b in blobs:
                for mt in u16.finditer(b):
                    s = mt.group(0)
                    if len(s) % 2: s = s[:-1]
                    t = s.decode('utf-16le', 'ignore').strip()
                    if len(t) < 2 or not re.search(r'[A-Za-zА-Яа-яЁёӘәҒғҚқҢңӨөҰұҮүҺһІі0-9]', t): continue
                    if t not in cnt: order.append((t, p))
                    cnt[t] += 1
    with open(os.path.join(outdir, tag + '_strings.txt'), 'w', encoding='utf-8') as fo:
        for t, p in order:
            fo.write('%d\t%s\t%s\n' % (cnt[t], p, t.replace('\r', '\\r').replace('\n', '\\n')))
    print(tag, 'streams', len(streams), 'unique strings', len(order))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
