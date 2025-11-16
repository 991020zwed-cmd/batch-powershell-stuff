#include "interpreter.h"

/* Execute a single line */
int execute_line(InterpreterState* state, const char* line) {
    int token_count = 0;
    Token* tokens = tokenize_line(line, &token_count);
    
    if (!tokens) {
        fprintf(stderr, "Error: Failed to tokenize line\n");
        return 1;
    }
    
    int result = 0;
    
    /* Handle empty lines and comments */
    if (token_count == 0 || tokens[0].type == TOKEN_NEWLINE || tokens[0].type == TOKEN_RIM) {
        free_tokens(tokens);
        return 0;
    }
    
    /* Handle labels (just skip, they're recorded in first pass) */
    if (tokens[0].type == TOKEN_LABEL) {
        free_tokens(tokens);
        return 0;
    }
    
    /* Execute commands */
    switch (tokens[0].type) {
        case TOKEN_ECKO:
            result = execute_ecko(state, tokens, token_count);
            break;
        case TOKEN_SEP:
            result = execute_sep(state, tokens, token_count);
            break;
        case TOKEN_IZ:
            result = execute_iz(state, tokens, token_count);
            break;
        case TOKEN_GOTA:
            result = execute_gota(state, tokens, token_count);
            break;
        case TOKEN_COLL:
            result = execute_coll(state, tokens, token_count);
            break;
        case TOKEN_PAUS:
            result = execute_paus(state);
            break;
        case TOKEN_EXIS:
            result = execute_exis(state, tokens, token_count);
            break;
        default:
            fprintf(stderr, "Error: Unknown command '%s'\n", tokens[0].value);
            result = 1;
            break;
    }
    
    free_tokens(tokens);
    return result;
}

/* First pass: scan for labels */
static void scan_labels(InterpreterState* state, FILE* file) {
    char line[MAX_LINE_LENGTH];
    long position;
    
    while (!feof(file)) {
        position = ftell(file);
        if (fgets(line, MAX_LINE_LENGTH, file) == NULL) break;
        
        /* Check if line starts with : (label) */
        char* ptr = line;
        while (*ptr && isspace(*ptr)) ptr++;
        
        if (*ptr == ':') {
            ptr++;
            char label_name[MAX_TOKEN_LENGTH];
            int i = 0;
            while (*ptr && !isspace(*ptr) && *ptr != '\n' && i < MAX_TOKEN_LENGTH - 1) {
                label_name[i++] = *ptr++;
            }
            label_name[i] = '\0';
            
            add_label(state, label_name, position, 0);
        }
    }
    
    /* Reset file position */
    rewind(file);
}

/* Execute a script file */
int execute_file(InterpreterState* state, const char* filename) {
    FILE* file = fopen(filename, "r");
    if (!file) {
        fprintf(stderr, "Error: Cannot open file '%s'\n", filename);
        return 1;
    }
    
    state->script_file = file;
    
    /* First pass: scan for labels */
    scan_labels(state, file);
    
    /* Second pass: execute */
    char line[MAX_LINE_LENGTH];
    int line_number = 0;
    
    while (!state->should_exit && !feof(file)) {
        if (fgets(line, MAX_LINE_LENGTH, file) == NULL) break;
        
        line_number++;
        
        /* Remove newline */
        size_t len = strlen(line);
        if (len > 0 && line[len - 1] == '\n') {
            line[len - 1] = '\0';
        }
        
        /* Execute line */
        if (execute_line(state, line) != 0) {
            fprintf(stderr, "Error at line %d\n", line_number);
        }
    }
    
    fclose(file);
    state->script_file = NULL;
    
    return state->exit_code;
}

/* Execute interactive mode (REPL) */
void execute_interactive(InterpreterState* state) {
    char line[MAX_LINE_LENGTH];
    
    state->interactive_mode = 1;
    
    printf("Batch-Inspired Interpreter v1.0\n");
    printf("Commands: ECKO, SEP, IZ, GOTA, COLL, RIM, PAUS, EXIS\n");
    printf("Type 'EXIS' to exit\n");
    printf("\n");
    
    while (!state->should_exit) {
        printf("> ");
        fflush(stdout);
        
        if (fgets(line, MAX_LINE_LENGTH, stdin) == NULL) {
            break;
        }
        
        /* Remove newline */
        size_t len = strlen(line);
        if (len > 0 && line[len - 1] == '\n') {
            line[len - 1] = '\0';
        }
        
        /* Skip empty lines */
        if (len <= 1) continue;
        
        /* Execute line */
        execute_line(state, line);
    }
    
    printf("\nExiting with code %d\n", state->exit_code);
}
