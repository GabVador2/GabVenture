@echo off
setlocal

:: Chemin vers l'installeur Python (le fichier doit être dans le même répertoire que le script)
set "PYTHON_INSTALLER=python-3.11.9.exe"

:: Vérifie si Python est installé globalement
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python n'est pas installé globalement.

    :: Vérifie si WinPython est installé en recherchant un chemin connu
    set "WINPYTHON_PATH=I:\python\WPy64-31241\python-3.12.4.exe"  :: Remplacez ce chemin par le chemin d'installation de WinPython

    if exist "%WINPYTHON_PATH%" (
        echo WinPython détecté, utilisation de WinPython...
        set "PYTHONPATH=%WINPYTHON_PATH%"
    ) else (
        echo WinPython non détecté.

        :: Téléchargez Python si le fichier d'installation n'est pas disponible localement
        if not exist "%PYTHON_INSTALLER%" (
            echo Téléchargement de Python...
            powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9.exe' -OutFile '%PYTHON_INSTALLER%'"
        )

        :: Installer Python de manière silencieuse
        echo Installation de Python en cours...
        "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

        :: Vérifie à nouveau si Python est installé correctement
        where python >nul 2>&1
        if %errorlevel% neq 0 (
            echo Echec de l'installation de Python. Veuillez l'installer manuellement.
            exit /b 1
        )
        
        :: Définir le chemin vers le Python installé après installation
        set "PYTHONPATH=python"
    )
) else (
    :: Si Python est installé globalement, l'utiliser
    set "PYTHONPATH=python"
)

:: Exécuter le script Python
echo Exécution de l'application Python...
"%PYTHONPATH%" app\main.py