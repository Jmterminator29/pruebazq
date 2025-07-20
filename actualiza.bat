@echo off
echo ==============================
echo   LIMPIANDO CARPETA DEL PROYECTO
echo ==============================

REM Mantendremos solo estos archivos
set FILES_TO_KEEP=main.py requirements.txt ZETH50T.DBF ZETH51T.DBF ZETH70.DBF

for %%f in (*) do (
    set keep=0
    for %%k in (%FILES_TO_KEEP%) do (
        if /I "%%f"=="%%k" set keep=1
    )
    if !keep!==0 (
        echo Eliminando %%f
        del /f /q "%%f"
    )
)

echo ==============================
echo   LIMPIEZA FINALIZADA
echo ==============================
pause
