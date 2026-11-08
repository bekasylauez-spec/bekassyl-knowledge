var src = System.IO.File.ReadAllText(@"__FILE__", System.Text.Encoding.UTF8);
var full = "using System; using System.Linq; using System.Collections.Generic; using Autodesk.Revit.DB; using Autodesk.Revit.UI;\nnamespace ClaudeRun { public static class E { public static object Run(Document document, object[] parameters) {\n" + src + "\n} } }";
var tree = Microsoft.CodeAnalysis.CSharp.CSharpSyntaxTree.ParseText(full);
var refs = AppDomain.CurrentDomain.GetAssemblies().Where(a => !a.IsDynamic && !string.IsNullOrEmpty(a.Location)).Select(a => (Microsoft.CodeAnalysis.MetadataReference)Microsoft.CodeAnalysis.MetadataReference.CreateFromFile(a.Location)).ToList();
var comp = Microsoft.CodeAnalysis.CSharp.CSharpCompilation.Create("cr" + Guid.NewGuid().ToString("N"), new[] { tree }, refs, new Microsoft.CodeAnalysis.CSharp.CSharpCompilationOptions(Microsoft.CodeAnalysis.OutputKind.DynamicallyLinkedLibrary));
using (var ms = new System.IO.MemoryStream())
{
    var res = comp.Emit(ms);
    if (!res.Success) return "COMPILE: " + string.Join("\n", res.Diagnostics.Where(d => d.Severity == Microsoft.CodeAnalysis.DiagnosticSeverity.Error).Take(15).Select(d => d.ToString()));
    var asm = System.Reflection.Assembly.Load(ms.ToArray());
    return asm.GetType("ClaudeRun.E").GetMethod("Run").Invoke(null, new object[] { document, parameters });
}

