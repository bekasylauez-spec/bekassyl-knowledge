// treecmp.exe <src> <dst> : byte-by-byte comparison of a file or a directory tree (read-only). Exit 0 = identical.
using System;
using System.IO;
using System.Collections.Generic;

static class TreeCmp
{
    static long files, bytes; static int diff;
    static bool SameFile(string a, string b)
    {
        var fa = new FileInfo(a); var fb = new FileInfo(b);
        if (!fb.Exists) { Report("MISSING " + b); return false; }
        if (fa.Length != fb.Length) { Report("SIZE " + a + " " + fa.Length + " vs " + fb.Length); return false; }
        using (var sa = new FileStream(a, FileMode.Open, FileAccess.Read, FileShare.ReadWrite, 1 << 20, FileOptions.SequentialScan))
        using (var sb = new FileStream(b, FileMode.Open, FileAccess.Read, FileShare.ReadWrite, 1 << 20, FileOptions.SequentialScan))
        {
            var ba = new byte[4 << 20]; var bb = new byte[4 << 20];
            while (true)
            {
                int na = Fill(sa, ba), nb = Fill(sb, bb);
                if (na != nb) { Report("LEN " + a); return false; }
                if (na == 0) break;
                for (int i = 0; i < na; i++) if (ba[i] != bb[i]) { Report("BYTES " + a); return false; }
            }
        }
        files++; bytes += fa.Length; return true;
    }
    static int Fill(Stream s, byte[] b) { int o = 0; while (o < b.Length) { int r = s.Read(b, o, b.Length - o); if (r <= 0) break; o += r; } return o; }
    static void Report(string m) { diff++; if (diff <= 20) Console.WriteLine(m); }
    static void Walk(string a, string b)
    {
        var da = new DirectoryInfo(a);
        foreach (var f in da.GetFiles()) SameFile(f.FullName, Path.Combine(b, f.Name));
        foreach (var d in da.GetDirectories())
        {
            if ((d.Attributes & FileAttributes.ReparsePoint) != 0) { Report("REPARSE (skipped) " + d.FullName); continue; }
            Walk(d.FullName, Path.Combine(b, d.Name));
        }
        // extra files in dst are allowed only if dst pre-existed; report them
        if (Directory.Exists(b))
            foreach (var f in new DirectoryInfo(b).GetFiles())
                if (!File.Exists(Path.Combine(a, f.Name))) Report("EXTRA " + f.FullName);
    }
    static int Main(string[] x)
    {
        var sw = System.Diagnostics.Stopwatch.StartNew();
        if (File.Exists(x[0])) SameFile(x[0], x[1]); else Walk(x[0], x[1]);
        Console.WriteLine("files={0} GB={1:F2} diffs={2} sec={3:F0}", files, bytes / 1073741824.0, diff, sw.Elapsed.TotalSeconds);
        return diff == 0 ? 0 : 2;
    }
}
