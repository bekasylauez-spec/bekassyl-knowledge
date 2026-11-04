@echo off
rem Run on BEKA-2: asks for admin rights and links Claude memory to BEKA-1.
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-NoExit','-File','%~dp0lan-link-memory.ps1'"
