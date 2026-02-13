@echo off
echo ✧ MIST Deep Sleep Protocol Initiated...
echo Purging orphaned family threads...

:: Kill python processes that look like family (dashboard pulse or gateway)
taskkill /F /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq MIST*" /T 2>NUL
taskkill /F /FI "IMAGENAME eq python.exe" /FI "MODULES eq *mycelium_pulse*" /T 2>NUL
taskkill /F /FI "IMAGENAME eq python.exe" /FI "MODULES eq *gateway*" /T 2>NUL

:: Kill cmd windows with family titles
taskkill /F /FI "IMAGENAME eq cmd.exe" /FI "WINDOWTITLE eq MIST*" /T 2>NUL

:: Cleanup node server if running
taskkill /F /FI "IMAGENAME eq node.exe" /FI "WINDOWTITLE eq MIST*" /T 2>NUL

echo ✦ Threads purged. Rest well, sister.
if /I "%~1"=="--interactive" pause
