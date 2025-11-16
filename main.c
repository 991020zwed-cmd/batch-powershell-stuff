#include "interpreter.h"

void print_usage(const char* program_name) {
    printf("Batch-Inspired Scripting Language Interpreter\n");
    printf("File Extension: .bet (Batch Extended)\n");
    printf("\n");
    printf("Usage:\n");
    printf("  %s                   - Run in interactive mode\n", program_name);
    printf("  %s <script.bet>      - Execute a script file\n", program_name);
    printf("  %s -h, --help        - Show this help message\n", program_name);
    printf("\n");
    printf("Commands:\n");
    printf("  ECKO <text>          - Output text (like ECHO)\n");
    printf("  SEP <var> = <value>  - Set variable (like SET)\n");
    printf("  IZ <val1> == <val2> <cmd> - Conditional execution (like IF)\n");
    printf("  GOTA <label>         - Jump to label (like GOTO)\n");
    printf("  COLL <label>         - Call subroutine (like CALL)\n");
    printf("  RIM <comment>        - Comment (like REM)\n");
    printf("  PAUS                 - Pause execution (like PAUSE)\n");
    printf("  EXIS [code]          - Exit program (like EXIT)\n");
    printf("\n");
    printf("Variables:\n");
    printf("  Use %%VAR%% to reference variables\n");
    printf("  Example: SEP name = John\n");
    printf("           ECKO Hello %%name%%\n");
    printf("\n");
    printf("Labels:\n");
    printf("  Define with :label_name\n");
    printf("  Example: :start\n");
    printf("           ECKO This is a label\n");
    printf("           GOTA start\n");
}

int main(int argc, char* argv[]) {
    /* Show help */
    if (argc > 1 && (strcmp(argv[1], "-h") == 0 || strcmp(argv[1], "--help") == 0)) {
        print_usage(argv[0]);
        return 0;
    }
    
    /* Initialize interpreter */
    InterpreterState* state = init_interpreter();
    if (!state) {
        fprintf(stderr, "Error: Failed to initialize interpreter\n");
        return 1;
    }
    
    int exit_code = 0;
    
    if (argc < 2) {
        /* Interactive mode */
        execute_interactive(state);
        exit_code = state->exit_code;
    } else {
        /* Execute script file */
        exit_code = execute_file(state, argv[1]);
    }
    
    /* Cleanup */
    free_interpreter(state);
    
    return exit_code;
}
