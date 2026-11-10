---
name: video-lessons-tts
description: Дауысты түсіндірме видео (MP4) жасау тәсілі — edge-tts kk-KZ-DauletNeural + PIL 3D кадрлар + imageio-ffmpeg
metadata:
  node_type: memory
  type: reference
  originSessionId: 43ab5924-eb64-446f-b8d7-8ab1e3112883
  modified: 2026-11-10T04:54:42.180Z
---

Пайдаланушы «видео жасап түсіндір» десе — дауыспен MP4 керек (3D бет емес; 10.11.2026 «дауыспен жасай алмайсың ба?» деді). Деңгейі — инженер/жобалаушы.

Жұмыс істейтін құрал (BEKA-2, 10.11.2026):
- Дауыс: `edge-tts` ≥7.3.1 (ескі нұсқа 403 береді), дауыс `kk-KZ-DauletNeural` (ер) / `kk-KZ-AigulNeural` (әйел), rate -4%; сахналарды кезекпен генерацияла (параллель → 403).
- ffmpeg: жүйеде жоқ → `pip install imageio-ffmpeg`, `imageio_ffmpeg.get_ffmpeg_exe()`.
- Кадрлар: Python PIL өз перспектива проекциясы (2× supersample), rawvideo → libx264 pipe; биіктік ×4 үлкейтіліп, кадрда жазылады.
- Үлгі скрипт: «Плита арматурасы» видеосы, `D:\РАБОЧКА\Видеосабақтар\` (scenes.py / tts.py / render.py).

Мазмұн пайдаланушы ережелерінен: фиксатор Ф-1 [[obsidian-first]] (08_Detailing_Fixators_Frames), стык тәртібі Онкоцентр 07 Плиты.
