@echo off
rem Instalador del Despacho Pessoa para Windows: doble clic aqui.
rem Ejecuta instalar.ps1 sin cambiar la politica de ejecucion del equipo.
if not exist "%~dp0instalar.ps1" (
  echo.
  echo Primero descomprime el ZIP: clic derecho ^> Extraer todo, y abre instalar.cmd desde la carpeta extraida.
  echo.
  pause
  exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0instalar.ps1" %*
echo.
pause
