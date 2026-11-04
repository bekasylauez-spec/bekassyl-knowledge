param([string]$Out = "D:\Бекасыл КЖ КМ\Тассай_Б_блок\График_Тассай_Б_блок.xlsx")

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

function Esc([string]$s) { return [System.Security.SecurityElement]::Escape($s) }
function Col([int]$n) { $s=""; while ($n -gt 0) { $m=($n-1)%26; $s=[char](65+$m)+$s; $n=[int][math]::Floor(($n-1)/26) }; return $s }
function Serial([datetime]$d) { return [int]($d - [datetime]'1899-12-30').TotalDays }
function D([string]$s) { return [datetime]::ParseExact($s,'dd.MM.yyyy',$null) }

# ---------------- Schedule data ----------------
# phase rows: @{P='I'; Name='...'}   task rows: @{N='...'; S='dd.MM.yyyy'; E='dd.MM.yyyy'; Note='...'}
$rows = @(
 @{P='I';  Name='I. ҚОРАПТЫ ЖАБУ (қыс алдында)'},
 @{N='Шатыр жабуды (кровля) аяқтау';                              S='29.10.2026'; E='30.11.2026'; Note='Жалғасуда'},
 @{N='Мансард қабат: сол жақ қабырғаларды қалау';                 S='02.11.2026'; E='28.11.2026'; Note='Планировка дайын'},
 @{N='Мансард қабат: терезелерді орнату';                         S='23.11.2026'; E='12.12.2026'; Note='Қабырға біткен соң'},
 @{N='1–2 қабат: сыртқы терезе және кіреберіс есіктерді орнату'; S='09.11.2026'; E='12.12.2026'; Note='Қорапты жылы жабу'},
 @{N='Ішкі қабырғаларды сылақтау (черновая), 1–2 қабат';         S='29.10.2026'; E='31.12.2026'; Note='Жалғасуда'},
 @{N='Мансард қабатты сылақтау (черновая)';                       S='14.12.2026'; E='31.01.2027'; Note='Терезе қойылған соң'},
 @{N='Уақытша жылыту мен жарықтандыруды ұйымдастыру';            S='01.12.2026'; E='12.12.2026'; Note='Қыста ішкі жұмыс үшін'},

 @{P='II'; Name='II. ФАСАД'},
 @{N='Фасадты жылыту (утеплитель, дюбель, тор)';                  S='02.11.2026'; E='05.12.2026'; Note='Терезелермен қатар'},
 @{N='Фасад әрлеу: сылақ / сырлау (немесе панель)';               S='23.11.2026'; E='31.12.2026'; Note='Ылғалды жұмыс +5°C жоғары'},
 @{N='Фасад: ағызу жүйесі, отливтер, қарнизді қаптау';           S='14.12.2026'; E='31.12.2026'; Note=''},

 @{P='III'; Name='III. ИНЖЕНЕРЛІК ЖҮЙЕЛЕР — ЧЕРНОВАЯ'},
 @{N='Электрика: кабель тарту, қораптар, щит орны';               S='04.01.2027'; E='27.02.2027'; Note='Фасад біткен соң'},
 @{N='ВК: су мен канализация құбырлары (разводка)';               S='11.01.2027'; E='06.03.2027'; Note=''},
 @{N='ОВ: жылыту құбырлары, радиатор нүктелері, вентканалдар';    S='11.01.2027'; E='13.03.2027'; Note='Стяжкаға дейін бітеді'},
 @{N='АПТ: өрт дабылы кабельдері мен қораптары';                  S='01.02.2027'; E='06.03.2027'; Note=''},
 @{N='Слабток: интернет, видеобақылау, домофон кабельдері';       S='15.02.2027'; E='13.03.2027'; Note='Электрикамен бірге'},

 @{P='IV'; Name='IV. ЕДЕН ЖӘНЕ ТЕГІСТЕУ'},
 @{N='Еден стяжкасы (барлық қабат)';                              S='01.03.2027'; E='10.04.2027'; Note='Құбырлар жабылған соң'},
 @{N='Шпатлевка — қабырға мен төбені тегістеу';                   S='15.02.2027'; E='24.04.2027'; Note='Қабат-қабат жүреді'},
 @{N='Санузелдер гидроизоляциясы';                                S='05.04.2027'; E='17.04.2027'; Note='Стяжка кепкен соң'},

 @{P='V'; Name='V. ІШКІ ӘРЛЕУ — ЧИСТОВАЯ'},
 @{N='Төбе: каркас, ГКЛ / натяжной төбе дайындығы';               S='12.04.2027'; E='15.05.2027'; Note=''},
 @{N='Плитка: санузел, ас үй, холл';                              S='19.04.2027'; E='05.06.2027'; Note=''},
 @{N='Сырлау / тұсқағаз (обои)';                                  S='17.05.2027'; E='03.07.2027'; Note=''},
 @{N='Таза еден жабыны (ламинат, паркет)';                        S='07.06.2027'; E='10.07.2027'; Note='Сырлаудан кейін'},
 @{N='Ішкі есіктерді орнату';                                     S='21.06.2027'; E='17.07.2027'; Note='Еден жабынынан кейін'},
 @{N='Электрика чистовая: розетка, қосқыш, шамдар';               S='14.06.2027'; E='17.07.2027'; Note=''},
 @{N='ВК чистовая: сантехника аспаптары';                         S='21.06.2027'; E='17.07.2027'; Note='Плиткадан кейін'},
 @{N='ОВ чистовая: радиаторлар, қазандық, іске қосу';             S='01.06.2027'; E='03.07.2027'; Note=''},
 @{N='АПТ: датчиктер, іске қосу-реттеу';                          S='05.07.2027'; E='24.07.2027'; Note='Төбе біткен соң'},
 @{N='Плинтус, ұсақ әрлеу жұмыстары';                             S='12.07.2027'; E='24.07.2027'; Note=''},

 @{P='VI'; Name='VI. АУМАҚ (жылы мезгіл)'},
 @{N='Отмостка, крыльцо, кіреберіс топтары';                      S='17.05.2027'; E='19.06.2027'; Note=''},
 @{N='Аумақты абаттандыру: жол, көгалдандыру, жарық';             S='14.06.2027'; E='24.07.2027'; Note=''},

 @{P='VII'; Name='VII. ЖИҺАЗ, ТАЗАЛАУ, ТАПСЫРУ'},
 @{N='Жиһаз жеткізу және орнату (ас үй, шкафтар)';                S='12.07.2027'; E='31.07.2027'; Note='Әрлеу біткен соң'},
 @{N='Тұрмыстық техника, жарықтандыру аспаптары';                 S='19.07.2027'; E='31.07.2027'; Note=''},
 @{N='Клининг — құрылыстан кейінгі тазалау';                      S='26.07.2027'; E='04.08.2027'; Note=''},
 @{N='Кемшіліктерді жою (дефектовка)';                            S='26.07.2027'; E='10.08.2027'; Note='Тапсырыс берушімен бірге'},
 @{N='Объектіні тапсыру';                                         S='11.08.2027'; E='15.08.2027'; Note='МЕРЗІМ: 15.08.2027'}
)

# ---------------- Layout ----------------
$firstMon = D '26.10.2026'
$lastMon  = D '16.08.2027'
$weeks = @(); $d=$firstMon; while ($d -le $lastMon) { $weeks += $d; $d = $d.AddDays(7) }
$nW = $weeks.Count
$fixedCols = 7              # A..G
$gStart = $fixedCols + 1    # H
$gEnd   = $fixedCols + $nW
$gStartL = Col $gStart; $gEndL = Col $gEnd
$hdrRow = 4; $firstData = 5
$lastData = $firstData + $rows.Count - 1

$sb = New-Object System.Text.StringBuilder
[void]$sb.Append('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
[void]$sb.Append('<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">')
[void]$sb.Append('<sheetPr><pageSetUpPr fitToPage="1"/></sheetPr>')
[void]$sb.Append("<dimension ref=`"A1:$gEndL$($lastData+8)`"/>")
[void]$sb.Append("<sheetViews><sheetView tabSelected=`"1`" zoomScale=`"85`" workbookViewId=`"0`"><pane xSplit=`"$fixedCols`" ySplit=`"$hdrRow`" topLeftCell=`"$gStartL$firstData`" activePane=`"bottomRight`" state=`"frozen`"/><selection pane=`"bottomRight`" activeCell=`"$gStartL$firstData`" sqref=`"$gStartL$firstData`"/></sheetView></sheetViews>")
[void]$sb.Append('<sheetFormatPr defaultRowHeight="15"/>')
[void]$sb.Append('<cols>')
[void]$sb.Append('<col min="1" max="1" width="5" customWidth="1"/>')
[void]$sb.Append('<col min="2" max="2" width="52" customWidth="1"/>')
[void]$sb.Append('<col min="3" max="3" width="9" customWidth="1"/>')
[void]$sb.Append('<col min="4" max="5" width="11.5" customWidth="1"/>')
[void]$sb.Append('<col min="6" max="6" width="9" customWidth="1"/>')
[void]$sb.Append('<col min="7" max="7" width="24" customWidth="1"/>')
[void]$sb.Append("<col min=`"$gStart`" max=`"$gEnd`" width=`"3.6`" customWidth=`"1`"/>")
[void]$sb.Append('</cols><sheetData>')

function CellS($ref,$s,$text) { "<c r=`"$ref`" s=`"$s`" t=`"inlineStr`"><is><t xml:space=`"preserve`">$(Esc $text)</t></is></c>" }
function CellN($ref,$s,$num)  { "<c r=`"$ref`" s=`"$s`"><v>$num</v></c>" }
function CellF($ref,$s,$f)    { "<c r=`"$ref`" s=`"$s`"><f>$(Esc $f)</f></c>" }
function CellE($ref,$s)       { "<c r=`"$ref`" s=`"$s`"/>" }

# Row 1 title, row 2 subtitle
[void]$sb.Append("<row r=`"1`" ht=`"22`" customHeight=`"1`">" + (CellS 'A1' 1 'ТАССАЙ, Б БЛОК — құрылысты аяқтау графигі') + '</row>')
[void]$sb.Append("<row r=`"2`" ht=`"15`" customHeight=`"1`">" + (CellS 'A2' 11 'Жасалған күні: 29.10.2026   |   Аяқтау мерзімі: 15.08.2027   |   Гант — апта бойынша (дүйсенбіден), сары бағана = ағымдағы апта') + '</row>')

# Row 3: month labels over weeks
$r3 = "<row r=`"3`" ht=`"16`" customHeight=`"1`">"
$r3 += (CellS 'A3' 2 'Кезеңдер / айлар')
for ($i=1; $i -lt $fixedCols; $i++) { $r3 += (CellE "$(Col ($i+1))3" 2) }
$monthMerges = @()
$i=0
$kzMonths = @('қаңтар','ақпан','наурыз','сәуір','мамыр','маусым','шілде','тамыз','қыркүйек','қазан','қараша','желтоқсан')
while ($i -lt $nW) {
  $m = $weeks[$i].Month; $y=$weeks[$i].Year; $j=$i
  while ($j+1 -lt $nW -and $weeks[$j+1].Month -eq $m) { $j++ }
  $c1 = Col ($gStart+$i); $c2 = Col ($gStart+$j)
  $r3 += (CellS "$c1`3" 9 ("{0} {1}" -f $kzMonths[$m-1], $y))
  for ($k=$i+1; $k -le $j; $k++) { $r3 += (CellE "$(Col ($gStart+$k))3" 9) }
  if ($j -gt $i) { $monthMerges += "$c1`3:$c2`3" }
  $i = $j+1
}
$r3 += '</row>'
[void]$sb.Append($r3)

# Row 4: header
$r4 = "<row r=`"4`" ht=`"42`" customHeight=`"1`">"
$hdrs = @('№','Жұмыс атауы','Кезең','Басталу','Аяқталу','Ұзақтығы, күн','Ескерту')
for ($i=0; $i -lt $hdrs.Count; $i++) { $r4 += (CellS "$(Col ($i+1))4" 2 $hdrs[$i]) }
for ($i=0; $i -lt $nW; $i++) { $r4 += (CellN "$(Col ($gStart+$i))4" 7 (Serial $weeks[$i])) }
$r4 += '</row>'
[void]$sb.Append($r4)

# Data rows
$taskNo = 0; $r = $firstData
$phaseRanges = @()   # for summary
$curPhaseRow = 0; $curPhase=''
for ($idx=0; $idx -lt $rows.Count; $idx++) {
  $row = $rows[$idx]
  if ($row.ContainsKey('P')) {
    # find child range
    $cStart = $r+1; $cEnd=$r
    for ($k=$idx+1; $k -lt $rows.Count; $k++) { if ($rows[$k].ContainsKey('P')) { break }; $cEnd = $firstData+$k }
    $phaseRanges += @{Row=$r; Name=$row.Name; From=$cStart; To=$cEnd}
    $curPhase = $row.P
    $line = "<row r=`"$r`" ht=`"18`" customHeight=`"1`">"
    $line += (CellS "A$r" 6 $row.P)
    $line += (CellS "B$r" 6 $row.Name)
    $line += (CellE "C$r" 6)
    $line += (CellF "D$r" 12 "MIN(D$cStart`:D$cEnd)")
    $line += (CellF "E$r" 12 "MAX(E$cStart`:E$cEnd)")
    $line += (CellF "F$r" 13 "E$r-D$r+1")
    $line += (CellE "G$r" 6)
    for ($i=0; $i -lt $nW; $i++) { $line += (CellE "$(Col ($gStart+$i))$r" 8) }
    $line += '</row>'
  } else {
    $taskNo++
    $line = "<row r=`"$r`" ht=`"17`" customHeight=`"1`">"
    $line += (CellN "A$r" 5 $taskNo)
    $line += (CellS "B$r" 3 $row.N)
    $line += (CellS "C$r" 10 $curPhase)
    $line += (CellN "D$r" 4 (Serial (D $row.S)))
    $line += (CellN "E$r" 4 (Serial (D $row.E)))
    $line += (CellF "F$r" 5 "E$r-D$r+1")
    $line += (CellS "G$r" 14 $row.Note)
    for ($i=0; $i -lt $nW; $i++) { $line += (CellE "$(Col ($gStart+$i))$r" 8) }
    $line += '</row>'
  }
  [void]$sb.Append($line)
  $r++
}

# Summary block
$r += 1
[void]$sb.Append("<row r=`"$r`"><c r=`"A$r`" s=`"1`" t=`"inlineStr`"><is><t>Кезеңдер бойынша қорытынды</t></is></c></row>"); $r++
$sumHdr = @('№','Кезең','','Басталу','Аяқталу','Күн','Ескерту')
$line = "<row r=`"$r`" ht=`"18`" customHeight=`"1`">"
for ($i=0; $i -lt $sumHdr.Count; $i++) { $line += (CellS "$(Col ($i+1))$r" 2 $sumHdr[$i]) }
[void]$sb.Append($line + '</row>'); $r++
foreach ($p in $phaseRanges) {
  $line = "<row r=`"$r`">"
  $line += (CellS "A$r" 10 ($p.Name.Split('.')[0]))
  $line += (CellS "B$r" 3 ($p.Name.Substring($p.Name.IndexOf('.')+2)))
  $line += (CellE "C$r" 3)
  $line += (CellF "D$r" 4 "D$($p.Row)")
  $line += (CellF "E$r" 4 "E$($p.Row)")
  $line += (CellF "F$r" 5 "F$($p.Row)")
  $line += (CellE "G$r" 3)
  [void]$sb.Append($line + '</row>'); $r++
}
$line = "<row r=`"$r`">"
$line += (CellE "A$r" 6) + (CellS "B$r" 6 'ЖАЛПЫ ҚҰРЫЛЫС') + (CellE "C$r" 6)
$line += (CellF "D$r" 12 "MIN(D$firstData`:D$lastData)") + (CellF "E$r" 12 "MAX(E$firstData`:E$lastData)") + (CellF "F$r" 13 "E$r-D$r+1")
$line += (CellS "G$r" 6 'Мерзім: 15.08.2027')
[void]$sb.Append($line + '</row>'); $r++
$totalRow = $r-1
$line = "<row r=`"$r`">" + (CellS "B$r" 11 'Мерзімге дейін қалған күн (бүгіннен):') + (CellF "D$r" 5 "E$totalRow-TODAY()") + '</row>'
[void]$sb.Append($line); $r++
$line = "<row r=`"$r`">" + (CellS "B$r" 11 'Ескерту: мерзімдер орташа өндірістік нормалар бойынша қойылған; бригада саны мен материал жеткізіліміне қарай D–E бағаналарын өзгертіңіз — Гант пен ұзақтық өзі қайта есептеледі.') + '</row>'
[void]$sb.Append($line); $r++

[void]$sb.Append('</sheetData>')

# merges
$merges = @("A1:$gEndL`1","A2:$gEndL`2") + $monthMerges
[void]$sb.Append("<mergeCells count=`"$($merges.Count)`">")
foreach ($m in $merges) { [void]$sb.Append("<mergeCell ref=`"$m`"/>") }
[void]$sb.Append('</mergeCells>')

# conditional formatting on Gantt area
$gRange = "$gStartL$firstData`:$gEndL$lastData"
$tl = "$gStartL$firstData"
$cf  = "<conditionalFormatting sqref=`"$gRange`">"
$cf += "<cfRule type=`"expression`" dxfId=`"0`" priority=`"1`" stopIfTrue=`"1`"><formula>AND(ISTEXT(`$A$firstData),$gStartL`$$hdrRow&lt;=`$E$firstData,$gStartL`$$hdrRow+6&gt;=`$D$firstData)</formula></cfRule>"
$cf += "<cfRule type=`"expression`" dxfId=`"1`" priority=`"2`" stopIfTrue=`"1`"><formula>AND(ISNUMBER(`$A$firstData),$gStartL`$$hdrRow&lt;=`$E$firstData,$gStartL`$$hdrRow+6&gt;=`$D$firstData)</formula></cfRule>"
$cf += "<cfRule type=`"expression`" dxfId=`"2`" priority=`"3`"><formula>AND($gStartL`$$hdrRow&lt;=TODAY(),TODAY()&lt;$gStartL`$$hdrRow+7)</formula></cfRule>"
$cf += '</conditionalFormatting>'
[void]$sb.Append($cf)

[void]$sb.Append('<pageMargins left="0.4" right="0.4" top="0.5" bottom="0.5" header="0.3" footer="0.3"/>')
[void]$sb.Append('<pageSetup paperSize="8" orientation="landscape" fitToWidth="1" fitToHeight="0"/>')
[void]$sb.Append('</worksheet>')
$sheetXml = $sb.ToString()

$stylesXml = @'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<numFmts count="2"><numFmt numFmtId="164" formatCode="dd.mm.yyyy"/><numFmt numFmtId="165" formatCode="dd.mm"/></numFmts>
<fonts count="6">
<font><sz val="10"/><name val="Arial"/></font>
<font><b/><sz val="10"/><name val="Arial"/></font>
<font><b/><sz val="14"/><color rgb="FF1F4E78"/><name val="Arial"/></font>
<font><b/><sz val="8"/><color rgb="FFFFFFFF"/><name val="Arial"/></font>
<font><b/><sz val="10"/><color rgb="FFFFFFFF"/><name val="Arial"/></font>
<font><i/><sz val="9"/><color rgb="FF595959"/><name val="Arial"/></font>
</fonts>
<fills count="4">
<fill><patternFill patternType="none"/></fill>
<fill><patternFill patternType="gray125"/></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FF1F4E78"/><bgColor indexed="64"/></patternFill></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FFDDEBF7"/><bgColor indexed="64"/></patternFill></fill>
</fills>
<borders count="3">
<border><left/><right/><top/><bottom/><diagonal/></border>
<border><left style="thin"><color rgb="FF808080"/></left><right style="thin"><color rgb="FF808080"/></right><top style="thin"><color rgb="FF808080"/></top><bottom style="thin"><color rgb="FF808080"/></bottom><diagonal/></border>
<border><left style="hair"><color rgb="FFBFBFBF"/></left><right style="hair"><color rgb="FFBFBFBF"/></right><top style="hair"><color rgb="FFBFBFBF"/></top><bottom style="hair"><color rgb="FFBFBFBF"/></bottom><diagonal/></border>
</borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="15">
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
<xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0" applyFont="1"><alignment vertical="center"/></xf>
<xf numFmtId="0" fontId="4" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center" wrapText="1"/></xf>
<xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf>
<xf numFmtId="164" fontId="0" fillId="0" borderId="1" xfId="0" applyNumberFormat="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
<xf numFmtId="1" fontId="0" fillId="0" borderId="1" xfId="0" applyNumberFormat="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
<xf numFmtId="0" fontId="1" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="center"/></xf>
<xf numFmtId="165" fontId="3" fillId="2" borderId="1" xfId="0" applyNumberFormat="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center" textRotation="90"/></xf>
<xf numFmtId="0" fontId="0" fillId="0" borderId="2" xfId="0" applyBorder="1"/>
<xf numFmtId="0" fontId="1" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
<xf numFmtId="0" fontId="1" fillId="0" borderId="1" xfId="0" applyFont="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
<xf numFmtId="0" fontId="5" fillId="0" borderId="0" xfId="0" applyFont="1"><alignment vertical="center"/></xf>
<xf numFmtId="164" fontId="1" fillId="3" borderId="1" xfId="0" applyNumberFormat="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
<xf numFmtId="1" fontId="1" fillId="3" borderId="1" xfId="0" applyNumberFormat="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
<xf numFmtId="0" fontId="5" fillId="0" borderId="1" xfId="0" applyFont="1" applyBorder="1" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf>
</cellXfs>
<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
<dxfs count="3">
<dxf><fill><patternFill patternType="solid"><fgColor rgb="FF1F4E78"/><bgColor rgb="FF1F4E78"/></patternFill></fill></dxf>
<dxf><fill><patternFill patternType="solid"><fgColor rgb="FF5B9BD5"/><bgColor rgb="FF5B9BD5"/></patternFill></fill></dxf>
<dxf><fill><patternFill patternType="solid"><fgColor rgb="FFFFF2CC"/><bgColor rgb="FFFFF2CC"/></patternFill></fill></dxf>
</dxfs>
</styleSheet>
'@

$workbookXml = @'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<bookViews><workbookView xWindow="0" yWindow="0" windowWidth="28800" windowHeight="15000"/></bookViews>
<sheets><sheet name="График" sheetId="1" r:id="rId1"/></sheets>
<calcPr calcId="191029" fullCalcOnLoad="1"/>
</workbook>
'@
$wbRels = @'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>
'@
$rootRels = @'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>
'@
$contentTypes = @'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
</Types>
'@

# validate XML well-formedness
foreach ($x in @($sheetXml,$stylesXml,$workbookXml,$wbRels,$rootRels,$contentTypes)) { [void]([xml]$x) }

$dir = Split-Path $Out
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
if (Test-Path $Out) { Remove-Item $Out -Force }
$utf8 = New-Object System.Text.UTF8Encoding($false)
$zip = [System.IO.Compression.ZipFile]::Open($Out, [System.IO.Compression.ZipArchiveMode]::Create)
function AddEntry($zip,$name,$content) {
  $e = $zip.CreateEntry($name, [System.IO.Compression.CompressionLevel]::Optimal)
  $s = $e.Open(); $b = $utf8.GetBytes($content); $s.Write($b,0,$b.Length); $s.Dispose()
}
AddEntry $zip '[Content_Types].xml' $contentTypes
AddEntry $zip '_rels/.rels' $rootRels
AddEntry $zip 'xl/workbook.xml' $workbookXml
AddEntry $zip 'xl/_rels/workbook.xml.rels' $wbRels
AddEntry $zip 'xl/styles.xml' $stylesXml
AddEntry $zip 'xl/worksheets/sheet1.xml' $sheetXml
$zip.Dispose()
"OK: $Out  tasks=$taskNo weeks=$nW rows=$($rows.Count) gantt=$gRange"
