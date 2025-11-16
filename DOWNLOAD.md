# Downloading Pre-Built Executables

Don't want to compile from source? You can download pre-built executables from the GitHub Actions artifacts or releases.

## Option 1: Download from GitHub Actions (Latest Build)

1. Go to the [Actions tab](../../actions) in this repository
2. Click on the latest successful workflow run for your branch
3. Scroll down to "Artifacts" section
4. Download the appropriate artifact for your platform:
   - **interpreter-windows** - Windows executable (interpreter.exe)
   - **interpreter-linux** - Linux executable
   - **interpreter-macos** - macOS executable

5. Extract the downloaded zip file
6. On Linux/macOS, make it executable: `chmod +x interpreter`
7. Run the interpreter!

## Option 2: Download from Releases (Stable Versions)

When available, you can download stable releases:

1. Go to the [Releases page](../../releases)
2. Download the appropriate file for your platform:
   - **interpreter.exe** - Windows
   - **interpreter** (marked Linux) - Linux
   - **interpreter** (marked macOS) - macOS

3. On Linux/macOS, make it executable: `chmod +x interpreter`

## Quick Test

After downloading, test the interpreter:

**Windows:**
```cmd
interpreter.exe --help
```

**Linux/macOS:**
```bash
chmod +x interpreter
./interpreter --help
```

## Running Your First Script

Create a file called `test.bet`:

```batch
RIM My first script
ECKO Hello, World!
SEP name = YourName
ECKO Welcome %name%!
```

Then run it:

**Windows:**
```cmd
interpreter.exe test.bet
```

**Linux/macOS:**
```bash
./interpreter test.bet
```

## Interactive Mode

Run the interpreter without arguments for interactive mode:

**Windows:**
```cmd
interpreter.exe
```

**Linux/macOS:**
```bash
./interpreter
```

Type commands one at a time and see immediate results!

## Need Examples?

After downloading the interpreter, you can also download the example scripts:

1. Download the entire repository as a ZIP from GitHub
2. Extract and navigate to the `examples/` folder
3. Run any example:
   - `hello.bet` - Simple hello world
   - `variables.bet` - Variable demonstration
   - `conditionals.bet` - Conditional statements
   - `labels.bet` - Labels and control flow
   - `demo.bet` - Comprehensive demo

## Still Having Issues?

If you can't download or the executable doesn't work:

1. **Check your antivirus** - It might flag the executable as suspicious (false positive)
2. **Check file permissions** - On Linux/macOS, ensure the file is executable
3. **Windows SmartScreen** - Click "More info" → "Run anyway" if Windows blocks it
4. **Build from source** - See [WINDOWS_BUILD.md](WINDOWS_BUILD.md) or [README.md](README.md) for compilation instructions

## What Gets Built?

The GitHub Actions workflow automatically builds:
- **Windows .exe** using MinGW cross-compiler
- **Linux binary** using GCC on Ubuntu
- **macOS binary** using Clang on macOS

All builds are tested automatically to ensure they work correctly.
