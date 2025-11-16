# Batch-Inspired Scripting Language Interpreter

A C-based interpreter for a batch-inspired scripting language with one-letter variations from standard batch commands. Uses the custom `.bet` (Batch Extended) file extension.

## Overview

This project implements a custom scripting language interpreter written in C that mimics Windows Batch scripting but with single-letter differences in command names. It supports script execution from files and an interactive REPL mode.

**File Extension:** `.bet` (Batch Extended)

## Building

### Prerequisites
- GCC or compatible C compiler
- Make

### Compilation
```bash
make
```

This will produce an executable named `interpreter`.

### Clean Build Artifacts
```bash
make clean
```

## Usage

### Running Scripts
```bash
./interpreter script.bet
```

### Interactive Mode (REPL)
```bash
./interpreter
```

In interactive mode, type commands one at a time and press Enter. Type `EXIS` to exit.

### Help
```bash
./interpreter --help
```

## Language Syntax

### Commands

| Command | Batch Equivalent | Description | Example |
|---------|------------------|-------------|---------|
| `ECKO` | `ECHO` | Output text to console | `ECKO Hello World` |
| `SEP` | `SET` | Set a variable | `SEP name = John` |
| `IZ` | `IF` | Conditional execution | `IZ %x% == 5 ECKO Five` |
| `GOTA` | `GOTO` | Jump to a label | `GOTA start` |
| `COLL` | `CALL` | Call a subroutine | `COLL function` |
| `RIM` | `REM` | Comment | `RIM This is a comment` |
| `PAUS` | `PAUSE` | Pause execution | `PAUS` |
| `EXIS` | `EXIT` | Exit the program | `EXIS 0` |

### Variables

Variables are defined using the `SEP` command and referenced using `%VAR%` syntax:

```batch
SEP username = Alice
SEP age = 30
ECKO Hello %username%, you are %age% years old
```

**Features:**
- Variables are case-insensitive
- Variable values can contain spaces
- Variables can be used in expressions and other commands
- Variable expansion happens at runtime

### Labels

Labels are defined with a colon prefix and used for control flow:

```batch
:start
ECKO This is a label
GOTA start
```

**Features:**
- Labels must start with `:`
- Label names are case-insensitive
- Labels can be targets for `GOTA` (goto) and `COLL` (call)

### Conditionals

The `IZ` command supports conditional execution with `==` (equals) and `!=` (not equals) operators:

```batch
SEP status = active
IZ %status% == active ECKO System is active
IZ %status% != inactive ECKO Not inactive
```

**Syntax:**
```batch
IZ value1 == value2 command
IZ value1 != value2 command
```

**Features:**
- Comparisons are case-insensitive
- Both values can be literals or variables
- The command after the condition executes only if condition is true

### Control Flow

#### GOTA (Goto)
Jump to a label unconditionally:

```batch
GOTA label_name
```

#### COLL (Call)
Call a subroutine and return:

```batch
COLL subroutine_name
```

**Note:** `COLL` is currently simplified in this implementation.

### Comments

Comments start with `RIM` and everything after is ignored:

```batch
RIM This is a comment
ECKO This will execute  RIM But this part is ignored
```

### Exit

Exit the program with an optional exit code:

```batch
EXIS          RIM Exit with code 0
EXIS 1        RIM Exit with code 1
```

## Example Scripts

### Hello World (`examples/hello.bet`)
```batch
RIM Hello World Example
ECKO Hello, World!
ECKO Welcome to the Batch-Inspired Scripting Language!
```

### Variables (`examples/variables.bet`)
```batch
RIM Variable Example
SEP name = Alice
SEP age = 25
ECKO Name: %name%
ECKO Age: %age%
```

### Conditionals (`examples/conditionals.bet`)
```batch
RIM Conditional Example
SEP value1 = hello
SEP value2 = hello
IZ %value1% == %value2% ECKO Values are equal
```

### Labels and Control Flow (`examples/labels.bet`)
```batch
RIM Labels Example
ECKO Starting program...
COLL subroutine
GOTA end

:subroutine
ECKO Inside subroutine
:end
ECKO Program finished!
```

### Comprehensive Demo (`examples/demo.bet`)
See `examples/demo.bet` for a comprehensive example demonstrating all features.

## Testing

Run the test scripts:
```bash
make test
```

Or run individual examples:
```bash
./interpreter examples/hello.bet
./interpreter examples/variables.bet
./interpreter examples/conditionals.bet
./interpreter examples/labels.bet
./interpreter examples/demo.bet
```

## Implementation Details

### Architecture

The interpreter consists of several components:

1. **Lexer** (`lexer.c`) - Tokenizes input lines into tokens
2. **Parser/Executor** (`executor.c`) - Parses and executes commands
3. **Command Handlers** (`commands.c`) - Individual command implementations
4. **State Management** (`interpreter.c`) - Manages variables, labels, and call stack
5. **Utilities** (`utils.c`) - Helper functions for string manipulation

### Data Structures

- **Variables**: Hash-like storage with name-value pairs (max 256 variables)
- **Labels**: Stores label positions for goto/call operations (max 256 labels)
- **Call Stack**: Supports nested calls (max depth 64)

### Features

- ✅ Command tokenization and parsing
- ✅ Variable storage and substitution
- ✅ Label support for control flow
- ✅ Conditional execution (IZ command)
- ✅ Comments (RIM command)
- ✅ Interactive REPL mode
- ✅ Script file execution
- ✅ Error handling
- ✅ Exit codes
- ✅ Custom .bet file extension

### Limitations

- Maximum line length: 1024 characters
- Maximum variables: 256
- Maximum labels: 256
- Maximum call stack depth: 64
- No expression evaluation (arithmetic operations)
- No file I/O operations
- Simplified COLL implementation (call stack for future enhancement)

## Development

### Project Structure
```
.
├── interpreter.h       # Header file with data structures
├── main.c             # Main program entry point
├── interpreter.c      # Interpreter state management
├── lexer.c           # Tokenization
├── executor.c        # Line execution and file parsing
├── commands.c        # Command implementations
├── utils.c           # Utility functions
├── Makefile          # Build configuration
└── examples/         # Example script files
    ├── hello.bet
    ├── variables.bet
    ├── conditionals.bet
    ├── labels.bet
    └── demo.bet
```

### Adding New Commands

1. Add token type to `TokenType` enum in `interpreter.h`
2. Add keyword recognition in `tokenize_line()` in `lexer.c`
3. Implement command handler in `commands.c`
4. Add function prototype to `interpreter.h`
5. Add case handler in `execute_line()` in `executor.c`

## File Extension: .bet

The `.bet` extension stands for "Batch Extended" and distinguishes this scripting language from standard Windows batch files. While the syntax is inspired by batch scripting, the one-letter command variations and custom file extension make it a distinct language.

## License

This project is provided as-is for educational purposes.

## Original Repository

This is part of the `batch-powershell-python-stuff` repository containing code using batch, powershell, or python.
