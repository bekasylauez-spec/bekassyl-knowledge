// Fast disk usage scanner (read-only). Usage: scan.exe <root e.g. C:> <outDir> <dirThreshMB> <fileThreshMB> <maxDepth>
using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using System.Runtime.InteropServices;

static class Scan
{
    const uint FILE_ATTRIBUTE_DIRECTORY = 0x10;
    const uint FILE_ATTRIBUTE_REPARSE_POINT = 0x400;

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    struct WIN32_FIND_DATAW
    {
        public uint dwFileAttributes;
        public uint ftCreationTimeLow, ftCreationTimeHigh;
        public uint ftLastAccessTimeLow, ftLastAccessTimeHigh;
        public uint ftLastWriteTimeLow, ftLastWriteTimeHigh;
        public uint nFileSizeHigh, nFileSizeLow;
        public uint dwReserved0, dwReserved1;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 260)] public string cFileName;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 14)] public string cAlternateFileName;
    }

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    static extern IntPtr FindFirstFileExW(string lpFileName, int fInfoLevelId, out WIN32_FIND_DATAW lpFindFileData, int fSearchOp, IntPtr lpSearchFilter, int dwAdditionalFlags);
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    static extern bool FindNextFileW(IntPtr hFindFile, out WIN32_FIND_DATAW lpFindFileData);
    [DllImport("kernel32.dll", SetLastError = true)]
    static extern bool FindClose(IntPtr hFindFile);

    static readonly IntPtr INVALID = new IntPtr(-1);
    static StreamWriter dirsW, filesW, reparseW, errW;
    static long threshDir, threshFile;
    static int maxDepth;
    static long errors, totalFiles, totalDirs;
    static readonly HashSet<string> archExt = new HashSet<string>(StringComparer.OrdinalIgnoreCase) {
        ".zip", ".rar", ".7z", ".iso", ".tar", ".gz", ".tgz", ".bz2", ".xz", ".cab", ".wim", ".esd", ".img",
        ".vhd", ".vhdx", ".bak", ".zst", ".arj", ".lzh", ".r00", ".001", ".msi", ".exe" };

    static string Ext(string name)
    {
        int i = name.LastIndexOf('.');
        return i < 0 ? "" : name.Substring(i);
    }

    static long Walk(string dir, int depth, out long fileCount)
    {
        long total = 0; fileCount = 0;
        WIN32_FIND_DATAW fd;
        IntPtr h = FindFirstFileExW(@"\\?\" + dir + @"\*", 1, out fd, 0, IntPtr.Zero, 2);
        if (h == INVALID) { errors++; errW.WriteLine(dir + "\t" + Marshal.GetLastWin32Error()); return 0; }
        var subdirs = new List<string>();
        try
        {
            do
            {
                string name = fd.cFileName;
                if (name == "." || name == "..") continue;
                string full = dir + "\\" + name;
                if ((fd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) != 0)
                {
                    if ((fd.dwFileAttributes & FILE_ATTRIBUTE_REPARSE_POINT) != 0) { reparseW.WriteLine(full); continue; }
                    subdirs.Add(full);
                }
                else
                {
                    long sz = ((long)fd.nFileSizeHigh << 32) | fd.nFileSizeLow;
                    total += sz; fileCount++; totalFiles++;
                    if (sz >= threshFile || (sz >= 1048576 && archExt.Contains(Ext(name))))
                    {
                        long ft = ((long)fd.ftLastWriteTimeHigh << 32) | fd.ftLastWriteTimeLow;
                        string dt;
                        try { dt = DateTime.FromFileTime(ft).ToString("yyyy-MM-dd HH:mm"); } catch { dt = "?"; }
                        filesW.WriteLine(full + "\t" + sz + "\t" + dt);
                    }
                }
            } while (FindNextFileW(h, out fd));
        }
        finally { FindClose(h); }
        totalDirs++;
        foreach (var sd in subdirs)
        {
            long fc;
            long s = Walk(sd, depth + 1, out fc);
            total += s; fileCount += fc;
        }
        if (total >= threshDir && depth <= maxDepth) dirsW.WriteLine(dir + "\t" + total + "\t" + fileCount + "\t" + depth);
        return total;
    }

    static int Main(string[] a)
    {
        string root = a[0].TrimEnd('\\');
        string outDir = a[1];
        threshDir = long.Parse(a[2]) * 1048576L;
        threshFile = long.Parse(a[3]) * 1048576L;
        maxDepth = int.Parse(a[4]);
        string tag = a.Length > 5 ? a[5] : "scan";
        var enc = new UTF8Encoding(false);
        dirsW = new StreamWriter(Path.Combine(outDir, tag + "_dirs.tsv"), false, enc);
        filesW = new StreamWriter(Path.Combine(outDir, tag + "_files.tsv"), false, enc);
        reparseW = new StreamWriter(Path.Combine(outDir, tag + "_reparse.tsv"), false, enc);
        errW = new StreamWriter(Path.Combine(outDir, tag + "_errors.tsv"), false, enc);
        var sw = System.Diagnostics.Stopwatch.StartNew();
        long fc;
        long tot = Walk(root, 0, out fc);
        dirsW.Close(); filesW.Close(); reparseW.Close(); errW.Close();
        Console.WriteLine("root={0} totalGB={1:F2} files={2} dirs={3} errors={4} sec={5:F0}", root, tot / 1073741824.0, totalFiles, totalDirs, errors, sw.Elapsed.TotalSeconds);
        return 0;
    }
}
