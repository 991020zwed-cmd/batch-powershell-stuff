# Windows Compilation Instructions

## Option 1: Compiling on Windows with MinGW

### Prerequisites
1. Install MinGW-w64 (includes GCC for Windows)
   - Download from: https://www.mingw-w64.org/
   - Or install via MSYS2: https://www.msys2.org/

2. Add MinGW bin directory to your PATH
   - Example: `C:\mingw64\bin`

### Compilation Steps

Open Command Prompt or PowerShell in the project directory and run:

```cmd
gcc -Wall -Wextra -std=c99 -O2 -c main.c
gcc -Wall -Wextra -std=c99 -O2 -c interpreter.c
gcc -Wall -Wextra -std=c99 -O2 -c lexer.c
gcc -Wall -Wextra -std=c99 -O2 -c utils.c
gcc -Wall -Wextra -std=c99 -O2 -c commands.c
gcc -Wall -Wextra -std=c99 -O2 -c executor.c
gcc -Wall -Wextra -std=c99 -O2 -o interpreter.exe main.o interpreter.o lexer.o utils.o commands.o executor.o
```

Or use the provided `Makefile.win`:

```cmd
make -f Makefile.win
```

This will create `interpreter.exe` which you can run:

```cmd
interpreter.exe script.bet
interpreter.exe
```

### Clean Build Artifacts

```cmd
make -f Makefile.win clean
```

Or manually:
```cmd
del *.o interpreter.exe
```

## Option 2: Compiling on Windows with Visual Studio

### Prerequisites
1. Install Visual Studio (Community Edition is free)
2. Install "Desktop development with C++" workload

### Compilation Steps

Open "Developer Command Prompt for VS" and run:

```cmd
cl /W4 /O2 /std:c11 /Fe:interpreter.exe main.c interpreter.c lexer.c utils.c commands.c executor.c
```

This will create `interpreter.exe`.

## Option 3: Cross-Compiling from Linux to Windows

### Prerequisites
Install MinGW cross-compiler on Linux:

**Ubuntu/Debian:**
```bash
sudo apt-get install mingw-w64
```

**Fedora:**
```bash
sudo dnf install mingw64-gcc
```

### Compilation Steps

```bash
x86_64-w64-mingw32-gcc -Wall -Wextra -std=c99 -O2 -c main.c
x86_64-w64-mingw32-gcc -Wall -Wextra -std=c99 -O2 -c interpreter.c
x86_64-w64-mingw32-gcc -Wall -Wextra -std=c99 -O2 -c lexer.c
x86_64-w64-mingw32-gcc -Wall -Wextra -std=c99 -O2 -c utils.c
x86_64-w64-mingw32-gcc -Wall -Wextra -std=c99 -O2 -c commands.c
x86_64-w64-mingw32-gcc -Wall -Wextra -std=c99 -O2 -c executor.c
x86_64-w64-mingw32-gcc -Wall -Wextra -std=c99 -O2 -o interpreter.exe main.o interpreter.o lexer.o utils.o commands.o executor.o
```

Or use the cross-compilation Makefile:

```bash
make -f Makefile.cross
```

This will create a Windows-compatible `interpreter.exe` that can be run on Windows systems.

## Testing the .exe

Once compiled, you can run the interpreter:

```cmd
REM Run a script file
interpreter.exe examples\hello.bet

REM Interactive mode
interpreter.exe

REM Show help
interpreter.exe --help
```

## Troubleshooting

### "gcc is not recognized"
- Ensure MinGW bin directory is in your PATH
- Restart Command Prompt after installing MinGW

### "Cannot find interpreter.exe"
- Check that compilation completed without errors
- Look for .exe in the current directory

### Runtime errors
- Ensure all .c files were compiled
- Check that all .o files are linked together
- Verify Windows line endings if copying scripts from Linux (use `dos2unix` or text editor)

## Distribution

To distribute the interpreter:
1. Copy `interpreter.exe` to destination
2. Include example `.bet` scripts
3. Include `README.md` and `QUICKREF.md` documentation
4. No additional DLLs required (statically linked)
