// zipcheck.exe <zip> <baseDir> : zip central directory (ZIP64) CRC32/size vs extracted files under baseDir. Read-only.
using System;
using System.IO;
using System.Text;
using System.Collections.Generic;

static class ZipCheck
{
    static readonly uint[] T = MakeTable();
    static uint[] MakeTable()
    {
        var t = new uint[256];
        for (uint i = 0; i < 256; i++) { uint c = i; for (int k = 0; k < 8; k++) c = (c & 1) != 0 ? 0xEDB88320u ^ (c >> 1) : c >> 1; t[i] = c; }
        return t;
    }
    static uint Crc(string path)
    {
        uint crc = 0xFFFFFFFF;
        using (var fs = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read, 1 << 20, FileOptions.SequentialScan))
        {
            var buf = new byte[4 << 20]; int n;
            while ((n = fs.Read(buf, 0, buf.Length)) > 0)
                for (int i = 0; i < n; i++) crc = T[(crc ^ buf[i]) & 0xFF] ^ (crc >> 8);
        }
        return crc ^ 0xFFFFFFFF;
    }
    static void ReadFull(Stream s, byte[] b, int n) { int o = 0; while (o < n) { int r = s.Read(b, o, n - o); if (r <= 0) throw new EndOfStreamException(); o += r; } }

    class Entry { public string Name; public uint Crc; public long Size; }

    static List<Entry> ReadCD(string zip)
    {
        var list = new List<Entry>();
        using (var fs = new FileStream(zip, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete))
        {
            long flen = fs.Length;
            int tail = (int)Math.Min(flen, 65536 + 22 + 20);
            var buf = new byte[tail];
            fs.Seek(flen - tail, SeekOrigin.Begin); ReadFull(fs, buf, tail);
            int eocd = -1;
            for (int i = tail - 22; i >= 0; i--) if (BitConverter.ToUInt32(buf, i) == 0x06054b50) { eocd = i; break; }
            if (eocd < 0) throw new Exception("EOCD not found");
            long nEnt = BitConverter.ToUInt16(buf, eocd + 10);
            long cdSize = BitConverter.ToUInt32(buf, eocd + 12);
            long cdOff = BitConverter.ToUInt32(buf, eocd + 16);
            if (eocd >= 20 && BitConverter.ToUInt32(buf, eocd - 20) == 0x07064b50)
            {
                long z64 = BitConverter.ToInt64(buf, eocd - 20 + 8);
                var b = new byte[56]; fs.Seek(z64, SeekOrigin.Begin); ReadFull(fs, b, 56);
                if (BitConverter.ToUInt32(b, 0) != 0x06064b50) throw new Exception("bad zip64 eocd");
                nEnt = BitConverter.ToInt64(b, 32); cdSize = BitConverter.ToInt64(b, 40); cdOff = BitConverter.ToInt64(b, 48);
            }
            var cd = new byte[cdSize]; fs.Seek(cdOff, SeekOrigin.Begin); ReadFull(fs, cd, (int)cdSize);
            int p = 0; var oem = Encoding.GetEncoding(866);
            for (long e = 0; e < nEnt; e++)
            {
                if (BitConverter.ToUInt32(cd, p) != 0x02014b50) throw new Exception("bad CD header at " + p);
                ushort flags = BitConverter.ToUInt16(cd, p + 8);
                uint crc = BitConverter.ToUInt32(cd, p + 16);
                long csize = BitConverter.ToUInt32(cd, p + 20);
                long usize = BitConverter.ToUInt32(cd, p + 24);
                int nlen = BitConverter.ToUInt16(cd, p + 28), xlen = BitConverter.ToUInt16(cd, p + 30), clen = BitConverter.ToUInt16(cd, p + 32);
                long lho = BitConverter.ToUInt32(cd, p + 42);
                int xp = p + 46 + nlen, xend = xp + xlen; string uname = null;
                while (xp + 4 <= xend)
                {
                    ushort id = BitConverter.ToUInt16(cd, xp), sz = BitConverter.ToUInt16(cd, xp + 2); int dp = xp + 4;
                    if (id == 0x0001)
                    {
                        if (usize == 0xFFFFFFFF) { usize = BitConverter.ToInt64(cd, dp); dp += 8; }
                        if (csize == 0xFFFFFFFF) { csize = BitConverter.ToInt64(cd, dp); dp += 8; }
                        if (lho == 0xFFFFFFFF) { lho = BitConverter.ToInt64(cd, dp); dp += 8; }
                    }
                    else if (id == 0x7075 && sz >= 5) uname = Encoding.UTF8.GetString(cd, xp + 4 + 5, sz - 5);
                    xp += 4 + sz;
                }
                string name = uname ?? ((flags & 0x800) != 0 ? Encoding.UTF8.GetString(cd, p + 46, nlen) : oem.GetString(cd, p + 46, nlen));
                list.Add(new Entry { Name = name, Crc = crc, Size = usize });
                p += 46 + nlen + xlen + clen;
            }
        }
        return list;
    }

    static int Main(string[] a)
    {
        var sw = System.Diagnostics.Stopwatch.StartNew();
        var ents = ReadCD(a[0]);
        string bas = a[1].TrimEnd('\\');
        int files = 0, ok = 0, missing = 0, badSize = 0, badCrc = 0; long bytes = 0;
        var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        foreach (var e in ents)
        {
            if (e.Name.EndsWith("/") || e.Name.EndsWith("\\")) continue;
            files++; bytes += e.Size;
            string path = bas + "\\" + e.Name.Replace('/', '\\');
            seen.Add(Path.GetFullPath(path));
            var fi = new FileInfo(path);
            if (!fi.Exists) { missing++; if (missing <= 10) Console.WriteLine("MISSING " + e.Name); continue; }
            if (fi.Length != e.Size) { badSize++; if (badSize <= 10) Console.WriteLine("SIZE " + e.Name + " zip=" + e.Size + " disk=" + fi.Length); continue; }
            uint c = Crc(path);
            if (c != e.Crc) { badCrc++; if (badCrc <= 10) Console.WriteLine("CRC " + e.Name); continue; }
            ok++;
        }
        int extra = 0;
        string top = ents.Count > 0 ? ents[0].Name.Split('/')[0] : "";
        string topDir = bas + "\\" + top;
        if (Directory.Exists(topDir))
            foreach (var f in Directory.EnumerateFiles(topDir, "*", SearchOption.AllDirectories))
                if (!seen.Contains(Path.GetFullPath(f))) { extra++; if (extra <= 10) Console.WriteLine("EXTRA " + f); }
        Console.WriteLine("entries={0} files={1} GB={2:F2} ok={3} missing={4} badSize={5} badCrc={6} extraOnDisk={7} top='{8}' sec={9:F0}",
            ents.Count, files, bytes / 1073741824.0, ok, missing, badSize, badCrc, extra, top, sw.Elapsed.TotalSeconds);
        return (missing + badSize + badCrc) == 0 && ok == files ? 0 : 2;
    }
}
