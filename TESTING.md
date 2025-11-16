# Quick Test Guide - No Compilation Required!

This guide shows you how to download and test the interpreter **without compiling anything**.

## Step 1: Download the Executable

### Method A: From GitHub Actions (Recommended for Testing)

1. **Visit the Actions page**: Click [here](../../actions) or go to the "Actions" tab at the top of this repository
2. **Find the latest build**: Look for the most recent green checkmark (✓) for a workflow named "Build Interpreter"
3. **Click on it**: This opens the workflow run details
4. **Scroll down to "Artifacts"**: You'll see downloadable files
5. **Download your platform**:
   - Windows users: Download `interpreter-windows`
   - Linux users: Download `interpreter-linux`
   - Mac users: Download `interpreter-macos`

6. **Extract the ZIP file**: Your browser downloaded a .zip file. Extract it to get the executable.

### Method B: Direct Download (When Available)

If releases are available, go to the [Releases page](../../releases) and download the appropriate file directly.

## Step 2: Prepare the Executable

### Windows
- The extracted file will be named `interpreter.exe`
- Move it to a folder where you want to work (e.g., `C:\bat-interpreter\`)
- No additional setup needed!

### Linux/macOS
- The extracted file will be named `interpreter`
- Open Terminal and navigate to where you extracted it
- Make it executable: `chmod +x interpreter`

## Step 3: Create Your First Script

Create a new file called `test.bet` in the same folder as the interpreter:

```batch
RIM This is my first .bet script!
ECKO Hello from the Batch-Inspired Interpreter!
ECKO

SEP username = Alice
SEP greeting = Welcome
ECKO %greeting% %username%!
ECKO

SEP x = 10
SEP y = 10
IZ %x% == %y% ECKO x equals y!
IZ %x% != 5 ECKO x is not 5

ECKO
ECKO All tests passed!
```

## Step 4: Run Your Script

### Windows
Open Command Prompt in the folder and run:
```cmd
interpreter.exe test.bet
```

### Linux/macOS
Open Terminal in the folder and run:
```bash
./interpreter test.bet
```

**Expected output:**
```
Hello from the Batch-Inspired Interpreter!

Welcome Alice!

x equals y!
x is not 5

All tests passed!
```

## Step 5: Try Interactive Mode

Run the interpreter without any arguments:

### Windows
```cmd
interpreter.exe
```

### Linux/macOS
```bash
./interpreter
```

You'll see:
```
Batch-Inspired Interpreter v1.0
Commands: ECKO, SEP, IZ, GOTA, COLL, RIM, PAUS, EXIS
Type 'EXIS' to exit

>
```

Now try typing these commands one at a time:

```
ECKO Hello!
SEP name = YourName
ECKO My name is %name%
SEP a = 5
SEP b = 5
IZ %a% == %b% ECKO They are equal!
EXIS
```

## Try the Example Scripts

Want to see more? Download the examples:

1. **Download the repository**: Click the green "Code" button → "Download ZIP"
2. **Extract it**: Find the `examples` folder
3. **Copy the examples folder** to where your interpreter is
4. **Run the examples**:

**Windows:**
```cmd
interpreter.exe examples\hello.bet
interpreter.exe examples\variables.bet
interpreter.exe examples\conditionals.bet
interpreter.exe examples\labels.bet
interpreter.exe examples\demo.bet
```

**Linux/macOS:**
```bash
./interpreter examples/hello.bet
./interpreter examples/variables.bet
./interpreter examples/conditionals.bet
./interpreter examples/labels.bet
./interpreter examples/demo.bet
```

## Troubleshooting

### "Windows protected your PC"
- Click "More info" → "Run anyway"
- This is normal for unsigned executables

### "Permission denied" (Linux/macOS)
- Run: `chmod +x interpreter`

### "File not found"
- Make sure you're in the correct folder
- Use `dir` (Windows) or `ls` (Linux/macOS) to check

### Can't find the Actions tab?
- Make sure you're on the GitHub repository page
- The Actions tab is at the top: Code | Issues | Pull requests | **Actions**

### Still stuck?
- Check [DOWNLOAD.md](DOWNLOAD.md) for more detailed instructions
- Or compile from source using instructions in [README.md](README.md) or [WINDOWS_BUILD.md](WINDOWS_BUILD.md)

## Next Steps

Once you're comfortable:
- Read [QUICKREF.md](QUICKREF.md) for all available commands
- Check [README.md](README.md) for complete documentation
- Write your own .bet scripts!
- Share your scripts with others

Happy scripting! 🎉
