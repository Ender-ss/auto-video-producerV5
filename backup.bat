@echo off
echo 🔄 AUTO VIDEO PRODUCER - BACKUP SYSTEM
echo =====================================
echo.

:menu
echo Escolha o tipo de backup:
echo 1. Backup Completo (recomendado)
echo 2. Backup Rápido (apenas código)
echo 3. Restaurar Backup
echo 4. Sair
echo.
set /p choice="Digite sua escolha (1-4): "

if "%choice%"=="1" goto full_backup
if "%choice%"=="2" goto quick_backup
if "%choice%"=="3" goto restore
if "%choice%"=="4" goto exit
echo Opção inválida!
goto menu

:full_backup
echo.
echo 📦 Executando backup completo...
python backup_system.py
if %errorlevel% equ 0 (
    echo ✅ Backup completo realizado com sucesso!
) else (
    echo ❌ Erro no backup completo!
)
pause
goto menu

:quick_backup
echo.
echo ⚡ Executando backup rápido...
python quick_backup.py
if %errorlevel% equ 0 (
    echo ✅ Backup rápido realizado com sucesso!
) else (
    echo ❌ Erro no backup rápido!
)
pause
goto menu

:restore
echo.
echo 🔄 Executando restauração...
python restore_system.py
if %errorlevel% equ 0 (
    echo ✅ Restauração concluída!
) else (
    echo ❌ Erro na restauração!
)
pause
goto menu

:exit
echo.
echo 👋 Até logo!
exit /b 0
