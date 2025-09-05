@echo off
setlocal enabledelayedexpansion

echo ====================================
echo   Focus Blocker Pro Installation
echo ====================================
echo.

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This installer requires administrator privileges.
    echo Please right-click this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo [1/5] Checking required files...
if not exist "FocusBlockerPro.exe" (
    echo ERROR: FocusBlockerPro.exe not found in current directory
    pause
    exit /b 1
)

if not exist "FocusBlocker-Setup.exe" (
    echo ERROR: FocusBlocker-Setup.exe not found in current directory
    pause
    exit /b 1
)

if not exist "Certificates\" (
    echo ERROR: Certificates folder not found in current directory
    pause
    exit /b 1
)

echo [2/5] Creating application directory...
set "INSTALL_DIR=%PROGRAMFILES%\FocusBlockerPro"
if exist "%INSTALL_DIR%" (
    echo Removing existing installation...
    rmdir /s /q "%INSTALL_DIR%" 2>nul
)
mkdir "%INSTALL_DIR%" 2>nul
if %errorLevel% neq 0 (
    echo ERROR: Failed to create installation directory
    pause
    exit /b 1
)

echo [3/5] Copying application files...
copy "FocusBlockerPro.exe" "%INSTALL_DIR%\" >nul
if %errorLevel% neq 0 (
    echo ERROR: Failed to copy FocusBlockerPro.exe
    pause
    exit /b 1
)

copy "FocusBlocker-Setup.exe" "%INSTALL_DIR%\" >nul
if %errorLevel% neq 0 (
    echo ERROR: Failed to copy FocusBlocker-Setup.exe
    pause
    exit /b 1
)

mkdir "%INSTALL_DIR%\Certificates" 2>nul
xcopy "Certificates\*" "%INSTALL_DIR%\Certificates\" /y /q >nul
if %errorLevel% neq 0 (
    echo ERROR: Failed to copy certificates
    pause
    exit /b 1
)

echo [4/5] Creating desktop shortcut...
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%USERPROFILE%\Desktop\Focus Blocker Pro.lnk');$s.TargetPath='%INSTALL_DIR%\FocusBlockerPro.exe';$s.WorkingDirectory='%INSTALL_DIR%';$s.IconLocation='%INSTALL_DIR%\FocusBlockerPro.exe';$s.Description='AI-Powered Focus and Productivity App';$s.Save()" 2>nul

echo [5/5] Creating start menu entry...
set "START_MENU_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Focus Blocker Pro"
mkdir "%START_MENU_DIR%" 2>nul
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%START_MENU_DIR%\Focus Blocker Pro.lnk');$s.TargetPath='%INSTALL_DIR%\FocusBlockerPro.exe';$s.WorkingDirectory='%INSTALL_DIR%';$s.IconLocation='%INSTALL_DIR%\FocusBlockerPro.exe';$s.Description='AI-Powered Focus and Productivity App';$s.Save()" 2>nul

REM Create uninstaller
echo [BONUS] Creating uninstaller...
(
echo @echo off
echo echo Uninstalling Focus Blocker Pro...
echo.
echo REM Stop any running processes
echo taskkill /f /im FocusBlockerPro.exe 2^>nul
echo taskkill /f /im FocusBlocker-Setup.exe 2^>nul
echo.
echo REM Remove shortcuts
echo del "%%USERPROFILE%%\Desktop\Focus Blocker Pro.lnk" 2^>nul
echo rmdir /s /q "%%APPDATA%%\Microsoft\Windows\Start Menu\Programs\Focus Blocker Pro" 2^>nul
echo.
echo REM Remove application directory
echo rmdir /s /q "%%PROGRAMFILES%%\FocusBlockerPro" 2^>nul
echo.
echo echo Focus Blocker Pro has been uninstalled.
echo pause
) > "%INSTALL_DIR%\uninstall.bat"

echo.
echo ====================================
echo   Installation Complete!
echo ====================================
echo.
echo Focus Blocker Pro has been installed to:
echo %INSTALL_DIR%
echo.
echo Shortcuts created:
echo - Desktop: Focus Blocker Pro
echo - Start Menu: Programs ^> Focus Blocker Pro
echo.
echo To uninstall, run: %INSTALL_DIR%\uninstall.bat
echo.
pause 