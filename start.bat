@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

set PROJECT_ROOT=%~dp0
set PYTHON_DIR=%PROJECT_ROOT%python
set PYTHON_EXE=%PYTHON_DIR%\python.exe
set SCRIPTS_DIR=%PYTHON_DIR%\Scripts
set PIP_EXE=%SCRIPTS_DIR%\pip.exe
set PACKAGES_DIR=%PROJECT_ROOT%packages
set DEPS_INSTALLED_FLAG=%PROJECT_ROOT%deps_installed.flag

if not exist "%DEPS_INSTALLED_FLAG%" (
    echo Setting up the environment...

    if not exist "%PYTHON_DIR%" (
        echo Downloading and extracting Python...
        powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.4/python-3.12.4-embed-amd64.zip' -OutFile 'python.zip'; Expand-Archive -Path 'python.zip' -DestinationPath '%PYTHON_DIR%'; Remove-Item 'python.zip'}"
    )

    echo Creating python312._pth file...
    echo python312.zip> "%PYTHON_DIR%\python312._pth"
    echo .>> "%PYTHON_DIR%\python312._pth"
    echo Lib\site-packages>> "%PYTHON_DIR%\python312._pth"

    if not exist "%PROJECT_ROOT%get-pip.py" (
        echo Downloading get-pip.py...
        powershell -Command "& {Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%PROJECT_ROOT%get-pip.py'}"
    )

    echo Installing pip...
    "%PYTHON_EXE%" "%PROJECT_ROOT%get-pip.py" --no-warn-script-location
    if !errorlevel! neq 0 (
        echo Failed to install pip.
        pause
        exit /b 1
    )

    if not exist "%PACKAGES_DIR%" (
        mkdir "%PACKAGES_DIR%"
    )

    echo Downloading project dependencies...
    "%PYTHON_EXE%" -m pip download -r "%PROJECT_ROOT%requirements.txt" -d "%PACKAGES_DIR%"
    if !errorlevel! neq 0 (
        echo Failed to download project dependencies.
        pause
        exit /b 1
    )

    echo Installing project dependencies...
    "%PYTHON_EXE%" -m pip install --no-index --find-links="%PACKAGES_DIR%" -r "%PROJECT_ROOT%requirements.txt" --no-warn-script-location
    if !errorlevel! neq 0 (
        echo Failed to install project dependencies.
        pause
        exit /b 1
    )

    echo Dependencies installed successfully. > "%DEPS_INSTALLED_FLAG%"
) else (
    echo 已安装所需依赖
)

echo Running main.py...
cd /d "%PROJECT_ROOT%"
set PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%
"%PYTHON_EXE%" "%PROJECT_ROOT%main.py"

if !errorlevel! neq 0 (
    echo An error occurred while running main.py.
    pause
)
