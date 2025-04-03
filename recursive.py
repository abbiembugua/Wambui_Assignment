import re

class SimpleScriptParser:
    def __init__(self, tokens):
        """
        Initializes the parser with a list of tokens generated from the lexical analyzer.
        """
        self.tokens = tokens
        self.current_token = 0

    def match(self, expected_type, expected_value=None):
        """
        Checks if the current token matches the expected type (and optionally value), then moves to the next token.
        """
        if self.current_token < len(self.tokens):
            token_type, token_value = self.tokens[self.current_token]
            if token_type == expected_type and (expected_value is None or token_value == expected_value):
                self.current_token += 1
                return True
        return False

    def parse_program(self):
        """
        Parses a SimpleScript program by checking a sequence of statements.
        """
        while self.current_token < len(self.tokens):
            if not self.parse_statement():
                print(f"Syntax Error: Unexpected token {self.tokens[self.current_token]} at position {self.current_token}")
                return False
        return True

    def parse_statement(self):
        """
        Parses a valid SimpleScript statement (function declarations, variable declaration, expression, control structures).
        """
        if self.match("KEYWORD", "function"):
            return self.parse_function_decl()
        elif self.match("KEYWORD", "var"):
            return self.parse_var_decl()
        elif self.match("KEYWORD", "return"):
            return self.parse_return_stmt()
        elif self.match("KEYWORD", "if"):
            return self.parse_if_stmt()
        elif self.match("KEYWORD", "while"):
            return self.parse_while_stmt()
        elif self.match("IDENTIFIER"):
            return self.match("OPERATOR") and self.parse_expression() and self.match("DELIMITER", ";")  # Handle assignments like x = 10;
        return False

    def parse_function_decl(self):
        """
        Parses function declarations (e.g., function greet() { return "Hello"; }).
        """
        if not self.match("IDENTIFIER") or not self.match("DELIMITER", "(") or not self.match("DELIMITER", ")") or not self.match("DELIMITER", "{"):
            print("Syntax Error: Invalid function declaration.")
            return False
        while self.current_token < len(self.tokens) and self.tokens[self.current_token][1] != "}":
            if not self.parse_statement():
                return False
        return self.match("DELIMITER", "}")

    def parse_var_decl(self):
        """
        Parses variable declarations (e.g., var x = 10;).
        """
        if not self.match("IDENTIFIER") or not self.match("OPERATOR", "=") or not self.parse_expression() or not self.match("DELIMITER", ";"):
            print("Syntax Error: Invalid variable declaration.")
            return False
        return True

    def parse_expression(self):
        """
        Parses expressions involving numbers, identifiers, and arithmetic operations.
        """
        if self.match("NUMBER") or self.match("STRING") or self.match("IDENTIFIER"):
            while self.match("OPERATOR"):
                if not (self.match("NUMBER") or self.match("IDENTIFIER") or self.match("STRING")):
                    print("Syntax Error: Expected operand after operator.")
                    return False
            return True
        return False

    def parse_if_stmt(self):
        """
        Parses 'if' statements (e.g., if (x > 10) { return x; }).
        """
        if not self.match("DELIMITER", "(") or not self.parse_expression() or not self.match("DELIMITER", ")") or not self.match("DELIMITER", "{"):
            print("Syntax Error: Invalid 'if' statement.")
            return False
        while self.current_token < len(self.tokens) and self.tokens[self.current_token][1] != "}":
            if not self.parse_statement():
                return False
        return self.match("DELIMITER", "}")

    def parse_while_stmt(self):
        """
        Parses 'while' loops (e.g., while (x < 5) { x = x + 1; }).
        """
        return self.parse_if_stmt()  # 'if' and 'while' have similar structures

    def parse_return_stmt(self):
        """
        Parses 'return' statements (e.g., return x + 5;).
        """
        return self.parse_expression() and self.match("DELIMITER", ";")


# Example Tokenized Code (Function Definition with a Return Statement)
tokens = [
    ('KEYWORD', 'function'), ('IDENTIFIER', 'greet'), ('DELIMITER', '('), ('DELIMITER', ')'), 
    ('DELIMITER', '{'), ('KEYWORD', 'return'), ('STRING', '"That is amazing, Wambui."'), ('DELIMITER', ';'), ('DELIMITER', '}')
]

parser = SimpleScriptParser(tokens)
if parser.parse_program():
    print("Syntax Analysis: Program is syntactically correct.")
else:
    print("Syntax Analysis: Program has syntax errors.")
