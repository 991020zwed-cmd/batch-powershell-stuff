#include "interpreter.h"

/* Initialize interpreter state */
InterpreterState* init_interpreter(void) {
    InterpreterState* state = malloc(sizeof(InterpreterState));
    if (!state) return NULL;
    
    state->var_count = 0;
    state->label_count = 0;
    state->call_stack_top = -1;
    state->should_exit = 0;
    state->exit_code = 0;
    state->script_file = NULL;
    state->script_lines = NULL;
    state->script_line_count = 0;
    state->current_line = 0;
    state->interactive_mode = 0;
    
    return state;
}

/* Free interpreter state */
void free_interpreter(InterpreterState* state) {
    if (!state) return;
    
    if (state->script_file) {
        fclose(state->script_file);
    }
    
    if (state->script_lines) {
        for (int i = 0; i < state->script_line_count; i++) {
            free(state->script_lines[i]);
        }
        free(state->script_lines);
    }
    
    free(state);
}

/* Set a variable */
void set_variable(InterpreterState* state, const char* name, const char* value) {
    /* Check if variable exists */
    for (int i = 0; i < state->var_count; i++) {
        if (string_compare_ignore_case(state->variables[i].name, name) == 0) {
            strncpy(state->variables[i].value, value, MAX_TOKEN_LENGTH - 1);
            state->variables[i].value[MAX_TOKEN_LENGTH - 1] = '\0';
            return;
        }
    }
    
    /* Add new variable */
    if (state->var_count < MAX_VARIABLES) {
        strncpy(state->variables[state->var_count].name, name, MAX_TOKEN_LENGTH - 1);
        state->variables[state->var_count].name[MAX_TOKEN_LENGTH - 1] = '\0';
        strncpy(state->variables[state->var_count].value, value, MAX_TOKEN_LENGTH - 1);
        state->variables[state->var_count].value[MAX_TOKEN_LENGTH - 1] = '\0';
        state->var_count++;
    }
}

/* Get a variable value */
const char* get_variable(InterpreterState* state, const char* name) {
    for (int i = 0; i < state->var_count; i++) {
        if (string_compare_ignore_case(state->variables[i].name, name) == 0) {
            return state->variables[i].value;
        }
    }
    return NULL;
}

/* Add a label */
void add_label(InterpreterState* state, const char* name, long position, int line_index) {
    if (state->label_count < MAX_LABELS) {
        strncpy(state->labels[state->label_count].name, name, MAX_TOKEN_LENGTH - 1);
        state->labels[state->label_count].name[MAX_TOKEN_LENGTH - 1] = '\0';
        state->labels[state->label_count].file_position = position;
        state->labels[state->label_count].line_index = line_index;
        state->label_count++;
    }
}

/* Find a label */
Label* find_label(InterpreterState* state, const char* name) {
    for (int i = 0; i < state->label_count; i++) {
        if (string_compare_ignore_case(state->labels[i].name, name) == 0) {
            return &state->labels[i];
        }
    }
    return NULL;
}
