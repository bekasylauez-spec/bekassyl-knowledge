---
name: openjarvis-reference
description: "OpenJarvis — Стэнфордтың ашық, компьютердің өзінде жұмыс істейтін жеке ИИ-көмекші фреймворкі; сілтемелер, Windows орнату жолы, BEKA-1-дегі дайындық күйі (18.11.2026 — орнатылмаған)"
metadata:
  node_type: memory
  type: reference
  originSessionId: c737e7bd-4af6-4609-88ac-b70d424457a1
  modified: 2026-11-18T05:55:56.455Z
---

**OpenJarvis** («Personal AI, On Personal Devices») — жергілікті (local-first) жеке ИИ-агент фреймворкі: модель компьютердің өзінде жүреді, бұлтқа тек керек болғанда шығады. Stanford SAIL (Hazy Research + Scaling Intelligence Lab), лицензия Apache-2.0. Пайдаланушы 18.11.2026 «опен жарвисті өзіңе сохранит етіп алшы» деді — осы жазба сол үшін сақталды.

## Сілтемелер
- Репо: https://github.com/open-jarvis/OpenJarvis (тармақ `main`, ~87 МБ, 16,6 мың жұлдыз, 17.11.2026 жаңарған)
- Сайт: https://openjarvis.stanford.edu/ · Құжат: https://open-jarvis.github.io/OpenJarvis/
- Орнату беттері: `…/getting-started/installation/`, `…/getting-started/windows-native/`
- Релиз `desktop-v1.0.5` (11.11.2026): `OpenJarvis_x64-setup.exe` 17,2 МБ, MSI 23,6 МБ — https://github.com/open-jarvis/OpenJarvis/releases/latest

## Не істей алады (ресми құжаттан, 18.11.2026 оқылды)
- CLI `jarvis`: `init [--preset …]`, `ask "…"`, `chat`, `serve --port 8000`, `doctor`, `model list`, `gui`, `skill install …`, `connect gdrive`, `digest`.
- Пресеттер: chat-simple, deep-research, code-assistant, scheduled-monitor, morning-digest.
- Модульдер: channels (telegram, whatsapp, slack, discord …), connectors (obsidian, gmail, gdrive, notion …), mcp (client + server), speech (whisper, TTS), scheduler, memory (SQLite/FTS5), skills (agentskills.io форматы), agents ішінде `claude_code`.
- Қозғалтқыш: NVIDIA-да әдепкі Ollama; сондай-ақ llama.cpp, vLLM, SGLang. Бұлт (OpenAI/Anthropic) — `uv sync --extra inference-cloud`; баптау `~/.openjarvis/config.toml` (`[intelligence] default_model`).

## Windows-қа орнату (native, WSL-сіз)
- Талап: Windows 10 1809+/11, Python 3.11–3.13 (3.14 жарамайды), git PATH-та, `%LOCALAPPDATA%`-да ~5 ГБ.
- `irm https://open-jarvis.github.io/OpenJarvis/install.ps1 | iex` — uv орнатады, репоны `%LOCALAPPDATA%\OpenJarvis\src`-ке клондайды, `uv sync --extra desktop --group desktop-native` жасайды, автоқосылу қызметін (scheduled task) тіркеуді сұрайды (`-SkipService` — өткізу).
- Іске қосу: `cd "$env:LOCALAPPDATA\OpenJarvis\src"` → `uv run jarvis serve` → тексеру http://127.0.0.1:8000/health (тек 127.0.0.1, кілтсіз).
- Бастапқы кодтан/CLI жолына Rust керек (`uv run maturin develop -m rust/crates/openjarvis-python/Cargo.toml`); браузер UI-ға Node.js 22+; desktop қосымшасының алғашқы іске қосылуына Git, uv, Rust, VS Build Tools (x64 C++). Құжат WSL2 жолын «тегісірек» дейді.

## BEKA-1 күйі (18.11.2026 тексерілді)
- Бар: git, Python 3.13.14, uv; i7-14700F, 31,8 ГБ RAM, RTX 5060 Ti **8 ГБ** VRAM (драйвер 621.14); бос орын C: 87 ГБ, D: 278 ГБ.
- Жоқ: Ollama, Rust (cargo), Node.js, WSL дистрибутиві, `jarvis` командасы. **OpenJarvis орнатылмаған — тек осы анықтама сақталды.**
- Ұсынылатын жергілікті модель: VRAM × 0,9 ≈ 7,2 ГБ → «8 ГБ-қа дейін» → `qwen3.5:2b` (~1,1 ГБ жүктеу).
- `%LOCALAPPDATA%` C дискінде: [[disk-cleanup-rules]] және [[claude-data-on-d-junctions]] бойынша ауыр нәрсені (src, модельдер) D-ге қойған жөн. Орнату — жүктеу + сырттан скрипт іске қосу, сондықтан алдымен пайдаланушыдан рұқсат ал, `install.ps1`-ді іске қоспас бұрын оқып шық.

Шатастырма (менің байқағаным): 31.10 чаттарындағы «jarvis» — пайдаланушының Remote Control ортасының аты, OpenJarvis емес.
