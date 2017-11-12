@ECHO OFF

SET ScriptDir=%~dp0
SET ScriptDir=%ScriptDir:~0,-1%

PYTHON %ScriptDir%\pcsv-script.py %*
