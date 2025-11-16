#include "interpreter.h"

/* Execute ECKO command (echo) */
int execute_ecko(InterpreterState* state, Token* tokens, int token_count) {
    /* Skip the ECKO command token */
    for (int i = 1; i < token_count; i++) {
        if (tokens[i].type == TOKEN_VARIABLE) {
            const char* value = get_variable(state, tokens[i].value);
            if (value) {
                printf("%s", value);
            }
        } else if (tokens[i].type == TOKEN_STRING) {
            /* Expand variables in string */
            char* expanded = expand_variables(state, tokens[i].value);
            printf("%s", expanded);
        } else {
            printf("%s", tokens[i].value);
        }
        
        /* Add space between tokens except last one */
        if (i < token_count - 1) {
            printf(" ");
        }
    }
    printf("\n");
    return 0;
}

/* Execute SEP command (set) */
int execute_sep(InterpreterState* state, Token* tokens, int token_count) {
    if (token_count < 3) {
        fprintf(stderr, "Error: SEP requires variable name and value\n");
        return 1;
    }
    
    /* SEP VAR = VALUE */
    if (tokens[1].type != TOKEN_STRING && tokens[1].type != TOKEN_VARIABLE) {
        fprintf(stderr, "Error: Invalid variable name\n");
        return 1;
    }
    
    if (tokens[2].type != TOKEN_EQUALS) {
        fprintf(stderr, "Error: Expected '=' after variable name\n");
        return 1;
    }
    
    /* Collect all remaining tokens as the value (or empty string if no value) */
    char value[MAX_LINE_LENGTH] = "";
    for (int i = 3; i < token_count; i++) {
        if (tokens[i].type == TOKEN_VARIABLE) {
            const char* var_val = get_variable(state, tokens[i].value);
            if (var_val) {
                strcat(value, var_val);
            }
        } else {
            strcat(value, tokens[i].value);
        }
        if (i < token_count - 1) {
            strcat(value, " ");
        }
    }
    
    set_variable(state, tokens[1].value, value);
    return 0;
}

/* Execute IZ command (if) */
int execute_iz(InterpreterState* state, Token* tokens, int token_count) {
    if (token_count < 4) {
        fprintf(stderr, "Error: IZ requires condition\n");
        return 1;
    }
    
    /* IZ value1 == value2 command */
    /* IZ value1 != value2 command */
    
    /* Get first value */
    char value1[MAX_TOKEN_LENGTH];
    if (tokens[1].type == TOKEN_VARIABLE) {
        const char* val = get_variable(state, tokens[1].value);
        strncpy(value1, val ? val : "", MAX_TOKEN_LENGTH - 1);
    } else {
        strncpy(value1, tokens[1].value, MAX_TOKEN_LENGTH - 1);
    }
    value1[MAX_TOKEN_LENGTH - 1] = '\0';
    
    /* Check operator */
    TokenType op_type = tokens[2].type;
    if (op_type != TOKEN_EQUAL && op_type != TOKEN_NOT_EQUAL) {
        fprintf(stderr, "Error: IZ requires == or != operator\n");
        return 1;
    }
    
    /* Get second value */
    char value2[MAX_TOKEN_LENGTH];
    if (tokens[3].type == TOKEN_VARIABLE) {
        const char* val = get_variable(state, tokens[3].value);
        strncpy(value2, val ? val : "", MAX_TOKEN_LENGTH - 1);
    } else {
        strncpy(value2, tokens[3].value, MAX_TOKEN_LENGTH - 1);
    }
    value2[MAX_TOKEN_LENGTH - 1] = '\0';
    
    /* Evaluate condition */
    int condition_met = 0;
    if (op_type == TOKEN_EQUAL) {
        condition_met = (string_compare_ignore_case(value1, value2) == 0);
    } else {
        condition_met = (string_compare_ignore_case(value1, value2) != 0);
    }
    
    /* If condition is met, execute the rest of the line as a command */
    if (condition_met && token_count > 4) {
        /* Execute remaining tokens as a new command */
        Token* sub_tokens = &tokens[4];
        int sub_count = token_count - 4;
        
        if (sub_tokens[0].type == TOKEN_ECKO) {
            return execute_ecko(state, sub_tokens, sub_count);
        } else if (sub_tokens[0].type == TOKEN_SEP) {
            return execute_sep(state, sub_tokens, sub_count);
        } else if (sub_tokens[0].type == TOKEN_GOTA) {
            return execute_gota(state, sub_tokens, sub_count);
        } else if (sub_tokens[0].type == TOKEN_COLL) {
            return execute_coll(state, sub_tokens, sub_count);
        } else if (sub_tokens[0].type == TOKEN_PAUS) {
            return execute_paus(state);
        } else if (sub_tokens[0].type == TOKEN_EXIS) {
            return execute_exis(state, sub_tokens, sub_count);
        }
    }
    
    return 0;
}

/* Execute GOTA command (goto) */
int execute_gota(InterpreterState* state, Token* tokens, int token_count) {
    if (token_count < 2) {
        fprintf(stderr, "Error: GOTA requires label name\n");
        return 1;
    }
    
    Label* label = find_label(state, tokens[1].value);
    if (!label) {
        fprintf(stderr, "Error: Label '%s' not found\n", tokens[1].value);
        return 1;
    }
    
    /* Jump to label */
    if (state->script_file) {
        fseek(state->script_file, label->file_position, SEEK_SET);
    } else {
        state->current_line = label->line_index;
    }
    
    return 0;
}

/* Execute COLL command (call) */
int execute_coll(InterpreterState* state, Token* tokens, int token_count) {
    if (token_count < 2) {
        fprintf(stderr, "Error: COLL requires label name\n");
        return 1;
    }
    
    Label* label = find_label(state, tokens[1].value);
    if (!label) {
        fprintf(stderr, "Error: Label '%s' not found\n", tokens[1].value);
        return 1;
    }
    
    /* Push return position to call stack */
    if (state->call_stack_top >= MAX_CALL_STACK - 1) {
        fprintf(stderr, "Error: Call stack overflow\n");
        return 1;
    }
    
    state->call_stack_top++;
    if (state->script_file) {
        state->call_stack[state->call_stack_top].return_position = ftell(state->script_file);
    }
    state->call_stack[state->call_stack_top].return_line = state->current_line;
    
    /* Jump to label */
    if (state->script_file) {
        fseek(state->script_file, label->file_position, SEEK_SET);
    } else {
        state->current_line = label->line_index;
    }
    
    return 0;
}

/* Execute PAUS command (pause) */
int execute_paus(InterpreterState* state) {
    (void)state;  /* Unused but required for function signature consistency */
    printf("Press Enter to continue...");
    fflush(stdout);
    getchar();
    return 0;
}

/* Execute EXIS command (exit) */
int execute_exis(InterpreterState* state, Token* tokens, int token_count) {
    state->should_exit = 1;
    
    /* Optional exit code */
    if (token_count > 1) {
        state->exit_code = atoi(tokens[1].value);
    } else {
        state->exit_code = 0;
    }
    
    return 0;
}
