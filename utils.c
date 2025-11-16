#include "interpreter.h"

/* Trim leading and trailing whitespace from a string */
void trim_whitespace(char* str) {
    if (!str) return;
    
    /* Trim leading whitespace */
    char* start = str;
    while (*start && isspace(*start)) start++;
    
    /* Trim trailing whitespace */
    char* end = start + strlen(start) - 1;
    while (end > start && isspace(*end)) end--;
    
    /* Move trimmed string to beginning */
    size_t len = end - start + 1;
    memmove(str, start, len);
    str[len] = '\0';
}

/* Case-insensitive string comparison */
int string_compare_ignore_case(const char* s1, const char* s2) {
    while (*s1 && *s2) {
        char c1 = tolower(*s1);
        char c2 = tolower(*s2);
        if (c1 != c2) {
            return c1 - c2;
        }
        s1++;
        s2++;
    }
    return tolower(*s1) - tolower(*s2);
}

/* Expand variables in a string (replace %VAR% with values) */
char* expand_variables(InterpreterState* state, const char* input) {
    static char result[MAX_LINE_LENGTH];
    char var_name[MAX_TOKEN_LENGTH];
    int res_idx = 0;
    const char* ptr = input;
    
    result[0] = '\0';
    
    while (*ptr && res_idx < MAX_LINE_LENGTH - 1) {
        if (*ptr == '%') {
            /* Found variable reference */
            ptr++;
            int var_idx = 0;
            
            /* Extract variable name */
            while (*ptr && *ptr != '%' && var_idx < MAX_TOKEN_LENGTH - 1) {
                var_name[var_idx++] = *ptr++;
            }
            var_name[var_idx] = '\0';
            
            if (*ptr == '%') ptr++;
            
            /* Get variable value */
            const char* value = get_variable(state, var_name);
            if (value) {
                /* Copy value to result */
                while (*value && res_idx < MAX_LINE_LENGTH - 1) {
                    result[res_idx++] = *value++;
                }
            }
        } else {
            /* Regular character */
            result[res_idx++] = *ptr++;
        }
    }
    
    result[res_idx] = '\0';
    return result;
}
