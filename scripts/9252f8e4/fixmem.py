p = r'C:\Users\beka\.claude\projects\R--\memory\project-kasymova-hotel.md'
b = open(p, 'rb').read()
bad = b'Kasymova\r\nevit' + bytes([92])
good = b'Kasymova' + bytes([92]) + b'revit' + bytes([92])
n = b.count(bad)
b = b.replace(bad, good)
t = b.decode('utf-8')
i = t.index('description:'); j = t.index('\r\n', i)
print('fixed', n, '| old description:', t[i:j])
t = t[:i] + 'description: Гостиница Касымова 25 (Маке) — ЛИРА: Расчет\\Kasymova.lir = v10 (пайдаланушы 16.11 22:30 өзгерткен v9; v10 есебі 17.11 BEKA-2-де), v9 есептелді (CSV res_v9); Revit BI моделі (rvbi) + ескі КЖ альбомы; файл жолдары мен күйі' + t[j:]
add = '''
## ЛИРА v9 есебі және пайдаланушының v10 өзгерісі (17.11.2026, BEKA-2)
- v9 есептелді (нормативные): FESolver 73 мин, ArmaDA 98 мин (14:37–16:16), қате жоқ. Модальды масса < 90 % (X ≈ 83 %, Y ≈ 87–88 %, Z 66–74 %), v3-тегідей. CSV: `D:\\_claude_work\\Kasymova\\res_v9\\` (plates_tbl02.32_2.csv, bars_tbl01.31_1.csv), экспорт `v9\\tbl9.ps1`.
- КЕЙІН АНЫҚТАЛДЫ: `R:\\От Маке\\Қасымова\\Расчет\\Kasymova.lir` 16.11 22:30:56-да пайдаланушы өзгерткен (BEKA-2 ЛИРА-сының MRU тізімінде бар; 22:31-де BEKA-1-ге «қазіргі күйімен армирование жаса» деген). Бұл = **v10**, жергілікті көшірмесі `D:\\_claude_work\\Kasymova\\Kasymova_v10.lir` (md5 бірдей).
- v10 − v9 (`v10\\diff_v10.py`, барлық құжат):
  - +195 ригель (жесткость 7) x=51.0, y 5.0→12.0, 13 деңгей (−3.700…+44.300; ST2 шахтасы шетінде);
  - y=34.0 фасадында −0.100…+4.100 стенасы (26 ұяшық, x 29.25–34.75) алынып, +4.100-де ригель (12) мен x=32.0 консолі 0.5 м (1) қойылған;
  - жүктеме/E×0.5 ригельдікімен бірдей, қалғаны (жесткость, C1, АЖТ, тірек, подзадача) өзгеріссіз.
- Нөмірлеу: v9 1–17857 сол күйі, кейінгісі −26-ға дейін ығысқан, жаңа 182295–182502. `v10\\map_v9_v10.csv`, `v10\\added_v10.csv`.
- v10 есебі 17.11 16:26-да BEKA-2 ЛИРА-сында (pid 18280) басталды; нәтиже `res_v10\\`-ке. BI сессиясына хабарланды. R:-дағы файлға тиіспедім (ол v10 өзі).
- Сабақ: [[lira-keep-user-edits]] — есеп алдында R:-дағы канон файлды жергілікті көшірмемен салыстыр; .lir-ді ЛИРА-сыз салыстыру [[lira-lir-binary-diff]].
'''.replace('\n', '\r\n')
t = t.rstrip('\r\n') + '\r\n' + add
out = t.encode('utf-8')
open(p, 'wb').write(out)
print('ok; lone CR:', out.count(b'\r') - out.count(b'\r\n'), '; revit paths:', out.count(good))
