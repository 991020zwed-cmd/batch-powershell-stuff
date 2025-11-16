#ifndef INTERPRETER_H
#define INTERPRETER_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_LINE_LENGTH 1024
#define MAX_VARIABLES 256
#define MAX_LABELS 256
#define MAX_CALL_STACK 64
#define MAX_TOKEN_LENGTH 256

/* Token types */
typedef enum {
    TOKEN_ECKO,      /* ECHO command */
    TOKEN_SEP,       /* SET command */
    TOKEN_IZ,        /* IF command */
    TOKEN_GOTA,      /* GOTO command */
    TOKEN_COLL,      /* CALL command */
    TOKEN_RIM,       /* REM comment */
    TOKEN_PAUS,      /* PAUSE command */
    TOKEN_EXIS,      /* EXIT command */
    TOKEN_LABEL,     /* Label (starts with :) */
    TOKEN_STRING,    /* String/text */
    TOKEN_VARIABLE,  /* Variable reference %VAR% */
    TOKEN_EQUALS,    /* = operator */
    TOKEN_EQUAL,     /* == comparison */
    TOKEN_NOT_EQUAL, /* != comparison */
    TOKEN_NEWLINE,   /* End of line */
    TOKEN_EOF        /* End of file */
} TokenType;

/* Token structure */
typedef struct {
    TokenType type;
    char value[MAX_TOKEN_LENGTH];
} Token;

/* Variable storage */
typedef struct {
    char name[MAX_TOKEN_LENGTH];
    char value[MAX_TOKEN_LENGTH];
} Variable;

/* Label storage */
typedef struct {
    char name[MAX_TOKEN_LENGTH];
    long file_position;  /* Position in file for GOTO */
    int line_index;      /* Line index for in-memory scripts */
} Label;

/* Call stack entry */
typedef struct {
    long return_position;
    int return_line;
} CallStackEntry;

/* Interpreter state */
typedef struct {
    Variable variables[MAX_VARIABLES];
    int var_count;
    Label labels[MAX_LABELS];
    int label_count;
    CallStackEntry call_stack[MAX_CALL_STACK];
    int call_stack_top;
    int should_exit;
    int exit_code;
    FILE* script_file;
    char** script_lines;  /* For in-memory scripts (interactive mode) */
    int script_line_count;
    int current_line;
    int interactive_mode;
} InterpreterState;

/* Function prototypes */
InterpreterState* init_interpreter(void);
void free_interpreter(InterpreterState* state);
void set_variable(InterpreterState* state, const char* name, const char* value);
const char* get_variable(InterpreterState* state, const char* name);
void add_label(InterpreterState* state, const char* name, long position, int line_index);
Label* find_label(InterpreterState* state, const char* name);
int execute_line(InterpreterState* state, const char* line);
int execute_file(InterpreterState* state, const char* filename);
void execute_interactive(InterpreterState* state);
char* expand_variables(InterpreterState* state, const char* input);

/* Lexer functions */
Token* tokenize_line(const char* line, int* token_count);
void free_tokens(Token* tokens);

/* Command execution functions */
int execute_ecko(InterpreterState* state, Token* tokens, int token_count);
int execute_sep(InterpreterState* state, Token* tokens, int token_count);
int execute_iz(InterpreterState* state, Token* tokens, int token_count);
int execute_gota(InterpreterState* state, Token* tokens, int token_count);
int execute_coll(InterpreterState* state, Token* tokens, int token_count);
int execute_paus(InterpreterState* state);
int execute_exis(InterpreterState* state, Token* tokens, int token_count);

/* Utility functions */
void trim_whitespace(char* str);
int string_compare_ignore_case(const char* s1, const char* s2);

#endif /* INTERPRETER_H */
