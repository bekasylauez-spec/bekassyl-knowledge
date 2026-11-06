---
name: acad-job-isolation
description: "AutoCAD generator robustness (06.11 БДМ Б3 ригели): unique job/temp names, one runner, restart per sheet, integrity check + rollback, work on D:, C: disk full corrupts DWGs"
metadata:
  node_type: memory
  type: feedback
  originSessionId: e9612f51-585b-4296-9d8b-098919c9d634
  modified: 2026-11-06T13:00:21.150Z
---

06.11.2026, БДМ Блок 3 ригели: DWG бірнеше рет «поврежденный файл» болды, AutoCAD құлады. Себептері:
1. **C: диск толып қалған** (0 МБ): сақтау кезінде файл бүлінеді. Пайдаланушы: «Д дискті қолдан». Жұмыс файлдары, тапсырма папкасы, ops/log/map — `D:\_claude_work\<объект>` ішінде, %TEMP%-те емес (пайдаланушы %TEMP%-ті тазалап, жұмыс DWG-м өшкен).
2. Бір тыңдаушыға екі генератор жазған (ескі python жабылмаған) — бір ғана runner; тоқтатқанда тек өз pid-ім (командалық жолы бойынша), «run_all» үлгісімен жаппа — колонна сессиясының процесін жаптым.
3. Тапсырма папкасы/ops/map аттары әр сессияда бөлек (b3_*, acadjob_b3).
4. AutoCAD қайта қосылғаннан кейінгі бірінші парақ тез (25 с), келесілері баяу → әр парақтан кейін қайта қос; сақтап бірден kill жасама, тексерілген _good көшірмеден қайта аш.
5. Әр парақтан кейін accoreconsole-да ашылуын тексер (integrity), бүлінсе соңғы _good-қа қайт. Қатса 60 с-та жаб (пайдаланушы: «қатып қалса бірден жауып қайта ашып жалғастыр»).
6. Layout: CreateLayout → CurrentLayout=name (paper viewport пайда болады) → сосын өз viewport-ыңды қос, On=true; live плот бос шығады, accoreconsole `-PLOT _N <layout>` (PDF үшін «файлға жазу?» сұрағы жоқ).
Related: [[bdm-block3-rigels]], [[cad-dedicated-instance]], [[acad-eatmaxreaders]]
