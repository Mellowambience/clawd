@echo off
echo Running System Diagnostics for MIST Personal IDE
echo ==============================================

echo.
echo Checking Disk Space...
wmic logicaldisk get size,freespace,caption

echo.
echo Checking Installed Programs...
wmic product get name,version

echo.
echo Checking Running Processes...
tasklist /svc

echo.
echo Checking Ollama Models (if installed)...
ollama list 2>nul || echo Ollama not found or not in PATH

echo.
echo Checking System Uptime...
wmic computersystem get TotalPhysicalMemory
wmic OS get LastBootUpTime

echo.
echo Diagnostic complete. Review the information above to identify potential sources of system bloat.
echo Common areas to check:
echo - Large AI models (Ollama, etc.)
echo - Browser cache and temporary files
echo - Application logs and cached data
echo - Duplicate or unnecessary files

pause