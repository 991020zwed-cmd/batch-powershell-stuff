#include "interpreter.h"

/* Tokenize a line of script */
Token* tokenize_line(const char* line, int* token_count) {
    Token* tokens = malloc(sizeof(Token) * MAX_LINE_LENGTH);
    *token_count = 0;
    
    if (!tokens) {
        return NULL;
    }
    
    const char* ptr = line;
    
    /* Skip leading whitespace */
    while (*ptr && isspace(*ptr)) ptr++;
    
    /* Empty line or comment */
    if (!*ptr || *ptr == '\n') {
        tokens[0].type = TOKEN_NEWLINE;
        tokens[0].value[0] = '\0';
        *token_count = 1;
        return tokens;
    }
    
    /* Check for label */
    if (*ptr == ':') {
        ptr++;
        int i = 0;
        while (*ptr && !isspace(*ptr) && *ptr != '\n' && i < MAX_TOKEN_LENGTH - 1) {
            tokens[0].value[i++] = *ptr++;
        }
        tokens[0].value[i] = '\0';
        tokens[0].type = TOKEN_LABEL;
        *token_count = 1;
        return tokens;
    }
    
    /* Parse tokens */
    while (*ptr) {
        /* Skip whitespace between tokens */
        while (*ptr && isspace(*ptr) && *ptr != '\n') ptr++;
        
        if (!*ptr || *ptr == '\n') break;
        
        Token* current = &tokens[*token_count];
        int idx = 0;
        
        /* Check for variable reference %VAR% */
        if (*ptr == '%') {
            ptr++;
            while (*ptr && *ptr != '%' && *ptr != '\n' && idx < MAX_TOKEN_LENGTH - 1) {
                current->value[idx++] = *ptr++;
            }
            if (*ptr == '%') ptr++;
            current->value[idx] = '\0';
            current->type = TOKEN_VARIABLE;
            (*token_count)++;
            continue;
        }
        
        /* Check for operators */
        if (*ptr == '=') {
            if (*(ptr + 1) == '=') {
                current->type = TOKEN_EQUAL;
                strcpy(current->value, "==");
                ptr += 2;
            } else {
                current->type = TOKEN_EQUALS;
                strcpy(current->value, "=");
                ptr++;
            }
            (*token_count)++;
            continue;
        }
        
        if (*ptr == '!' && *(ptr + 1) == '=') {
            current->type = TOKEN_NOT_EQUAL;
            strcpy(current->value, "!=");
            ptr += 2;
            (*token_count)++;
            continue;
        }
        
        /* Check for quoted strings */
        if (*ptr == '"') {
            ptr++;
            while (*ptr && *ptr != '"' && *ptr != '\n' && idx < MAX_TOKEN_LENGTH - 1) {
                current->value[idx++] = *ptr++;
            }
            if (*ptr == '"') ptr++;
            current->value[idx] = '\0';
            current->type = TOKEN_STRING;
            (*token_count)++;
            continue;
        }
        
        /* Parse word token */
        while (*ptr && !isspace(*ptr) && *ptr != '\n' && *ptr != '=' && *ptr != '%' && idx < MAX_TOKEN_LENGTH - 1) {
            current->value[idx++] = *ptr++;
        }
        current->value[idx] = '\0';
        
        /* Determine token type based on keyword */
        if (string_compare_ignore_case(current->value, "ECKO") == 0) {
            current->type = TOKEN_ECKO;
        } else if (string_compare_ignore_case(current->value, "SEP") == 0) {
            current->type = TOKEN_SEP;
        } else if (string_compare_ignore_case(current->value, "IZ") == 0) {
            current->type = TOKEN_IZ;
        } else if (string_compare_ignore_case(current->value, "GOTA") == 0) {
            current->type = TOKEN_GOTA;
        } else if (string_compare_ignore_case(current->value, "COLL") == 0) {
            current->type = TOKEN_COLL;
        } else if (string_compare_ignore_case(current->value, "RIM") == 0) {
            current->type = TOKEN_RIM;
        } else if (string_compare_ignore_case(current->value, "PAUS") == 0) {
            current->type = TOKEN_PAUS;
        } else if (string_compare_ignore_case(current->value, "EXIS") == 0) {
            current->type = TOKEN_EXIS;
        } else {
            current->type = TOKEN_STRING;
        }
        
        (*token_count)++;
        
        /* Stop after command if it's RIM (rest of line is comment) */
        if (current->type == TOKEN_RIM) {
            /* Store rest of line as comment */
            idx = 0;
            while (*ptr && *ptr != '\n' && idx < MAX_TOKEN_LENGTH - 1) {
                ptr++;
            }
            break;
        }
    }
    
    return tokens;
}

void free_tokens(Token* tokens) {
    free(tokens);
}
