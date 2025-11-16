# Quick Reference Guide

## Batch-Inspired Scripting Language (.bet files)

### Command Summary

| Command | Syntax | Description |
|---------|--------|-------------|
| `ECKO` | `ECKO text` | Print text to console |
| `SEP` | `SEP var = value` | Set variable |
| `IZ` | `IZ val1 == val2 cmd` | Execute cmd if condition true |
| `GOTA` | `GOTA label` | Jump to label |
| `COLL` | `COLL label` | Call subroutine (simplified: works like GOTA) |
| `RIM` | `RIM comment` | Comment line |
| `PAUS` | `PAUS` | Wait for Enter key |
| `EXIS` | `EXIS [code]` | Exit with optional code |

### Variable Syntax
- Define: `SEP varname = value`
- Reference: `%varname%`
- Variables are case-insensitive
- Can contain spaces
- Empty values allowed

### Label Syntax
- Define: `:labelname`
- Must be on own line
- Case-insensitive

### Conditional Operators
- `==` - Equal to
- `!=` - Not equal to
- Case-insensitive comparison

### Examples

#### Hello World
```
ECKO Hello, World!
```

#### Variables
```
SEP name = Alice
SEP age = 30
ECKO Hello %name%, you are %age% years old
```

#### Conditionals
```
SEP status = active
IZ %status% == active ECKO System is running
IZ %status% != stopped ECKO Not stopped
```

#### Labels & Control Flow
```
:start
ECKO In loop
GOTA start

:exit
ECKO Done
EXIS 0
```

### Running Scripts

**File mode:**
```bash
./interpreter script.bet
```

**Interactive mode:**
```bash
./interpreter
> ECKO Hello!
> SEP x = 5
> ECKO x = %x%
> EXIS
```

### Differences from Batch

| Batch | .bet | Notes |
|-------|------|-------|
| ECHO | ECKO | One letter difference |
| SET | SEP | One letter difference |
| IF | IZ | One letter difference |
| GOTO | GOTA | One letter difference |
| CALL | COLL | One letter difference |
| REM | RIM | One letter difference |
| PAUSE | PAUS | One letter difference |
| EXIT | EXIS | One letter difference |
| .bat | .bet | Batch Extended extension |

### Tips

1. Use RIM for comments
2. Variables expand in ECKO automatically
3. Labels can be anywhere in the file
4. GOTA can jump forward or backward
5. IZ can chain commands after condition
6. Empty variables are valid
7. Interactive mode for quick testing
8. Exit codes: 0 = success, >0 = error

### Limitations

- Max line length: 1024 chars
- Max variables: 256
- Max labels: 256
- No arithmetic operations
- No file I/O
- COLL doesn't return (works like GOTA)
- No string functions
- No loops (use GOTA for loops)

### Build from Source

```bash
make          # Build
make clean    # Clean build artifacts
make test     # Run example scripts
```
