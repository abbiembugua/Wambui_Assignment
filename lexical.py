import re

def tokenize_simple_script(code):
    """
    Lexical Analyzer for SimpleScript
    Reads the input source code and returns a list of tokens.
    """
    # Token Patterns
    token_specification = [
        ('KEYWORD', r'\b(if|else|while|return|function)\b'),  # Keywords
        ('IDENTIFIER', r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),         # Identifiers
        ('NUMBER', r'\b\d+(\.\d+)?\b'),                     # Integer and Float Numbers
        ('OPERATOR', r'[+\-*/=<>!&|]{1,2}'),                    # Operators
        ('STRING', r'".*?"|\'.*?\''),                        # String Literals
        ('DELIMITER', r'[(){};,]'),                              # Delimiters
        ('WHITESPACE', r'\s+'),                                 # Whitespace
        ('MISMATCH', r'.')                                       # Any other character (error)
    ]

    token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
    tokens = []
    
    for match in re.finditer(token_regex, code):
        kind = match.lastgroup
        value = match.group(kind)
        if kind == 'WHITESPACE':
            continue  # Ignore whitespace
        elif kind == 'MISMATCH':
            raise SyntaxError(f'Unrecognized token: {value}')
        tokens.append((kind, value))
    
    return tokens

# Example SimpleScript Code
simple_script_code = 'function greet() { return "That is amazing, Wambui."; }'

# Tokenizing the SimpleScript code
tokens = tokenize_simple_script(simple_script_code)
for token in tokens:
    print(token)