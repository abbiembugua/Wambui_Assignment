import re

class TACGenerator:
    def __init__(self):
        self.temp_count = 0  # Counter for temp variables (t1, t2, ...)
        self.label_count = 0  # Counter for labels (L1, L2, ...)
        self.tac_code = []  # Store generated TAC instructions
        self.label_stack = []  # Stack to keep track of labels for nested structures

    def new_temp(self):
        """ Generates a new temporary variable (e.g., t1, t2, ...) """
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        """ Generates a new label (e.g., L1, L2, ...) """
        self.label_count += 1
        return f"L{self.label_count}"

    def generate_tac(self, tokens):
        """ Converts tokenized SimpleScript expressions into TAC """
        i = 0
        while i < len(tokens):
            if i >= len(tokens):
                break
                
            token_type, token_value = tokens[i]

            if token_type == "KEYWORD" and token_value == "var":  
                # Handling variable declarations (e.g., var x = 10 + y;)
                var_name = tokens[i+1][1]  # Variable name
                i += 3  # Skip 'var x ='
                temp, i = self.parse_expression(tokens, i)
                self.tac_code.append(f"{var_name} = {temp}")
            
            elif token_type == "IDENTIFIER" and i+1 < len(tokens) and tokens[i+1][0] == "OPERATOR" and tokens[i+1][1] == "=":
                # Handling assignments (e.g., x = 10 + y;)
                var_name = token_value
                i += 2  # Skip 'x ='
                temp, i = self.parse_expression(tokens, i)
                self.tac_code.append(f"{var_name} = {temp}")
            
            elif token_type == "KEYWORD" and token_value == "if":
                # Handling 'if' conditionals (e.g., if (a > b) { ... })
                i += 2  # Skip 'if ('
                condition, i = self.parse_condition(tokens, i)
                label_true = self.new_label()
                label_end = self.new_label()
                
                self.tac_code.append(f"if {condition} goto {label_true}")
                self.tac_code.append(f"goto {label_end}")
                self.tac_code.append(f"{label_true}:")
                
                # Push end label to stack for when we encounter the closing '}'
                self.label_stack.append(("if_end", label_end))
                i += 1  # Skip past '{'
            
            elif token_type == "KEYWORD" and token_value == "while":
                # Handling 'while' loops
                start_label = self.new_label()
                end_label = self.new_label()
                
                self.tac_code.append(f"{start_label}:")
                i += 2  # Skip 'while ('
                condition, i = self.parse_condition(tokens, i)
                self.tac_code.append(f"if not {condition} goto {end_label}")
                
                # Push both labels to stack for when we encounter the closing '}'
                self.label_stack.append(("while", start_label, end_label))
                i += 1  # Skip past '{'
            
            elif token_type == "DELIMITER" and token_value == "}":
                # Handle end of block
                if self.label_stack:
                    block_type = self.label_stack[-1][0]
                    if block_type == "if_end":
                        # End of if block - add the end label
                        _, end_label = self.label_stack.pop()
                        self.tac_code.append(f"{end_label}:")
                    elif block_type == "while":
                        # End of while block - add jump back to condition and end label
                        _, start_label, end_label = self.label_stack.pop()
                        self.tac_code.append(f"goto {start_label}")
                        self.tac_code.append(f"{end_label}:")
                
            i += 1

    def parse_expression(self, tokens, i):
        """ Parses arithmetic expressions and generates TAC """
        operands = []
        operators = []
        
        # Define operator precedence
        precedence = {'+': 1, '-': 1, '*': 2, '/': 2}
        
        while i < len(tokens) and tokens[i][1] not in [";", ")"]:
            token_type, token_value = tokens[i]
            
            if token_type in ["NUMBER", "IDENTIFIER"]:
                operands.append(token_value)
            elif token_type == "OPERATOR":
                # Process operators based on precedence
                while (operators and operators[-1] in precedence and 
                       precedence.get(operators[-1], 0) >= precedence.get(token_value, 0)):
                    op = operators.pop()
                    if len(operands) < 2:
                        raise SyntaxError("Invalid expression: not enough operands for operator")
                    right = operands.pop()
                    left = operands.pop()
                    temp_var = self.new_temp()
                    self.tac_code.append(f"{temp_var} = {left} {op} {right}")
                    operands.append(temp_var)
                
                operators.append(token_value)
            
            i += 1
            
        # Process any remaining operators
        while operators:
            op = operators.pop()
            if len(operands) < 2:
                raise SyntaxError("Invalid expression: not enough operands for operator")
            right = operands.pop()
            left = operands.pop()
            temp_var = self.new_temp()
            self.tac_code.append(f"{temp_var} = {left} {op} {right}")
            operands.append(temp_var)
        
        if not operands:
            raise SyntaxError("Invalid expression: missing operands")
        
        return operands[-1], i

    def parse_condition(self, tokens, i):
        """ Parses boolean conditions in if/while statements """
        if i + 2 >= len(tokens):
            raise SyntaxError("Incomplete conditional expression")
        
        left = tokens[i][1]
        op = tokens[i+1][1]
        right = tokens[i+2][1]
        condition = f"{left} {op} {right}"
        return condition, i+3

    def print_tac(self):
        """ Prints the generated TAC code """
        print("\nThree-Address Code (TAC):")
        for line in self.tac_code:
            print(line)

# Example Tokenized SimpleScript Code
tokens = [
    ('KEYWORD', 'var'), ('IDENTIFIER', 'x'), ('OPERATOR', '='), ('NUMBER', '10'), ('OPERATOR', '+'), ('IDENTIFIER', 'y'), ('DELIMITER', ';'),
    ('KEYWORD', 'if'), ('DELIMITER', '('), ('IDENTIFIER', 'x'), ('OPERATOR', '>'), ('NUMBER', '5'), ('DELIMITER', ')'), ('DELIMITER', '{'),
    ('IDENTIFIER', 'x'), ('OPERATOR', '='), ('IDENTIFIER', 'x'), ('OPERATOR', '-'), ('NUMBER', '1'), ('DELIMITER', ';'), ('DELIMITER', '}'),
    ('KEYWORD', 'while'), ('DELIMITER', '('), ('IDENTIFIER', 'x'), ('OPERATOR', '<'), ('NUMBER', '20'), ('DELIMITER', ')'), ('DELIMITER', '{'),
    ('IDENTIFIER', 'x'), ('OPERATOR', '='), ('IDENTIFIER', 'x'), ('OPERATOR', '+'), ('NUMBER', '2'), ('DELIMITER', ';'), ('DELIMITER', '}')
]

# Run TAC Generator
tac_gen = TACGenerator()
tac_gen.generate_tac(tokens)
tac_gen.print_tac()