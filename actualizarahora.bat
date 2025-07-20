@echo off
REM ================================
REM BAT PARA GENERAR Y SUBIR HISTÓRICO A GITHUB
REM ================================

REM Cambiar a la carpeta del proyecto
cd /d "C:\Users\marti\Desktop\RED"

echo Ejecutando main.py para actualizar el historico...
python main.py

REM Confirmar si se generó correctamente
IF EXIST VENTAS_HISTORICO.DBF (
    echo ✅ Historico generado correctamente.
) ELSE (
    echo ⚠ No se encontro VENTAS_HISTORICO.DBF, revisa main.py
    pause
    exit /b
)

REM Preparar commit automático con fecha/hora
for /f "tokens=1-4 delims=/ " %%i in ("%date%") do (
    for /f "tokens=1-2 delims=: " %%a in ("%time%") do (
        set COMMIT_MSG=Actualizando historico %%i-%%j-%%k %%a-%%b
    )
)

REM Subir a GitHub
git add .
git commit -m "%COMMIT_MSG%"
git push origin main

echo.
echo ✅ Subida completada correctamente.
pause
