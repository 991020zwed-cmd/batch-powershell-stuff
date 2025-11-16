@echo off
REM Build script for Windows
REM Requires MinGW GCC to be installed and in PATH

echo Compiling Batch-Inspired Interpreter for Windows...
echo.

REM Check if gcc is available
where gcc >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: GCC not found in PATH
    echo Please install MinGW-w64 and add it to your PATH
    echo Download from: https://www.mingw-w64.org/
    echo.
    pause
    exit /b 1
)

echo Compiling source files...
gcc -Wall -Wextra -std=c99 -O2 -c main.c
if %errorlevel% neq 0 goto error

gcc -Wall -Wextra -std=c99 -O2 -c interpreter.c
if %errorlevel% neq 0 goto error

gcc -Wall -Wextra -std=c99 -O2 -c lexer.c
if %errorlevel% neq 0 goto error

gcc -Wall -Wextra -std=c99 -O2 -c utils.c
if %errorlevel% neq 0 goto error

gcc -Wall -Wextra -std=c99 -O2 -c commands.c
if %errorlevel% neq 0 goto error

gcc -Wall -Wextra -std=c99 -O2 -c executor.c
if %errorlevel% neq 0 goto error

echo Linking executable...
gcc -Wall -Wextra -std=c99 -O2 -o interpreter.exe main.o interpreter.o lexer.o utils.o commands.o executor.o
if %errorlevel% neq 0 goto error

echo.
echo Build successful! Created interpreter.exe
echo.
echo You can now run:
echo   interpreter.exe examples\hello.bet
echo   interpreter.exe
echo.
goto end

:error
echo.
echo ERROR: Compilation failed!
echo.
pause
exit /b 1

:end
pause
