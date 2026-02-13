@echo off
echo Finding empty directories in C:\Users\nator\clawd
echo =================================================
echo This script identifies empty directories but does NOT delete them.
echo Review the list below and decide which (if any) you want to delete manually.
echo.

for /f "usebackq" %%i in (`dir /ad /b /s "C:\Users\nator\clawd" ^| sort /r`) do (
    if "%%~zi" == "0" (
        echo Empty directory found: %%i
    )
)

echo.
echo Review the list above. To delete any empty directories, navigate to them manually
echo and confirm they contain nothing important before deletion.
echo Remember: It's safer to manually delete directories after verifying contents.
pause