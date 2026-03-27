class TokenType:
    LET = "LET"
    IDENT = "IDENT"
    INT = "INT"
    ASSIGN = "ASSIGN"
    PLUS = "PLUS"
    MINUS = "MINUS"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    COMMA = "COMMA"
    SEMICOLON = "SEMICOLON"
    FN = "FN"
    IF = "IF"
    RETURN = "RETURN"
    PRINT = "PRINT"
    LTE = "LTE"
    LT = "LT"
    GTE = "GTE"
    GT = "GT"
    EQ = "EQ"
    NEQ = "NEQ"
    STRING = "STRING"
    EOF = "EOF"


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = text[0]

    def advance(self):
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None

    def error(self):
        raise Exception("Invalid character")

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def readNumbers(self):
        result = ""
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def readIdent(self):
        result = ""
        while self.current_char is not None and self.current_char.isalnum():
            result += self.current_char
            self.advance()
        return result

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos >= len(self.text):
            return None
        return self.text[peek_pos]

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char.isdigit():
                return Token(TokenType.INT, self.readNumbers())
            if self.current_char.isalpha():
                readIn = self.readIdent()
                if readIn == "let":
                    return Token(TokenType.LET)
                elif readIn == "fn":
                    return Token(TokenType.FN)
                elif readIn == "if":
                    return Token(TokenType.IF)
                elif readIn == "return":
                    return Token(TokenType.RETURN)
                elif readIn == "print":
                    return Token(TokenType.PRINT)
                return Token(TokenType.IDENT, readIn)
            if self.current_char == "+":
                self.advance()
                return Token(TokenType.PLUS)
            if self.current_char == "-":
                self.advance()
                return Token(TokenType.MINUS)
            if self.current_char == "(":
                self.advance()
                return Token(TokenType.LPAREN)
            if self.current_char == ")":
                self.advance()
                return Token(TokenType.RPAREN)
            if self.current_char == "{":
                self.advance()
                return Token(TokenType.LBRACE)
            if self.current_char == "}":
                self.advance()
                return Token(TokenType.RBRACE)
            if self.current_char == ",":
                self.advance()
                return Token(TokenType.COMMA)
            if self.current_char == ";":
                self.advance()
                return Token(TokenType.SEMICOLON)
            if self.current_char == "<" and self.peek() == "=":
                self.advance()
                self.advance()
                return Token(TokenType.LTE)
            if self.current_char == ">" and self.peek() == "=":
                self.advance()
                self.advance()
                return Token(TokenType.GTE)
            if self.current_char == "=" and self.peek() == "=":
                self.advance()
                self.advance()
                return Token(TokenType.EQ)
            if self.current_char == "!" and self.peek() == "=":
                self.advance()
                self.advance()
                return Token(TokenType.GTE)
            if self.current_char == ">":
                self.advance()
                return Token(TokenType.GT)
            if self.current_char == "<":
                self.advance()
                return Token(TokenType.LT)
            if self.current_char == "=":
                self.advance()
                return Token(TokenType.ASSIGN)
            if self.current_char == '"':
                self.advance()
                result = ""
                while self.current_char is not None and self.current_char != '"':
                    result += self.current_char
                    self.advance()
                self.advance()
                return Token(TokenType.STRING, result)
            self.error()
        return Token(TokenType.EOF, None)


class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"


class AST:
    pass

class Expr(AST):
    pass

class Stmt(AST):
    pass

class Program(AST):
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Program({self.statements})"


class Number(Expr):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def __repr__(self):
        return f"Number({self.value})"


class StringLiteral(Expr):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def __repr__(self):
        return f"StringLiteral({self.value!r})"


class Identifier(Expr):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def __repr__(self):
        return f"Identifier({self.value})"


class Binary(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"Binary({self.left}, {self.operator.type}, {self.right})"


class Call(Expr):
    def __init__(self, callee, arguments):
        self.callee = callee
        self.arguments = arguments

    def __repr__(self):
        return f"Call({self.callee}, {self.arguments})"


class Let(Stmt):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"Let({self.name}, {self.value})"


class Function(Stmt):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

    def __repr__(self):
        return f"Function({self.name}, {self.params}, {self.body})"


class Return(Stmt):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Return({self.value})"


class Print(Stmt):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Print({self.value})"


class If(Stmt):
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def __repr__(self):
        return f"If({self.condition}, {self.then_branch}, {self.else_branch})"


class Block(Stmt):
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Block({self.statements})"


class ExprStmt(Stmt):
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"ExprStmt({self.expr})"


class Parser:
    PRECEDENCE = {
        TokenType.EQ: 1,
        TokenType.NEQ: 1,
        TokenType.LT: 2,
        TokenType.LTE: 2,
        TokenType.GT: 2,
        TokenType.GTE: 2,
        TokenType.PLUS: 3,
        TokenType.MINUS: 3,
    }

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos]

    def error(self, msg="Invalid syntax"):
        raise Exception(msg)

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def expect(self, type_):
        if self.current_token is not None and self.current_token.type == type_:
            token = self.current_token
            self.advance()
            return token
        got = None if self.current_token is None else self.current_token.type
        self.error(f"Expected {type_} but got {got}")

    def match(self, *types):
        if self.current_token is not None and self.current_token.type in types:
            token = self.current_token
            self.advance()
            return token
        return None

    def consume_optional_semicolon(self):
        self.match(TokenType.SEMICOLON)

    def peek(self):
        next_pos = self.pos + 1
        if next_pos < len(self.tokens):
            return self.tokens[next_pos]
        return None

    def is_at_end(self):
        return self.current_token is None or self.current_token.type == TokenType.EOF

    def parse(self):
        statements = []
        while not self.is_at_end():
            statements.append(self.statement())
        # print("\n\n\n------------statements")
        # print(statements)
        return Program(statements)

    def statement(self):
        t = self.current_token.type
        if t == TokenType.LET:
            return self.parse_let()
        if t == TokenType.FN:
            return self.parse_function()
        if t == TokenType.RETURN:
            return self.parse_return()
        if t == TokenType.PRINT:
            return self.parse_print()
        if t == TokenType.IF:
            return self.parse_if()
        return self.expr_statement()

    def parse_let(self):
        self.expect(TokenType.LET)
        name = self.expect(TokenType.IDENT)
        self.expect(TokenType.ASSIGN)
        value = self.expr()
        self.consume_optional_semicolon()
        return Let(name.value, value)

    def parse_function(self):
        self.expect(TokenType.FN)
        name = self.expect(TokenType.IDENT)
        self.expect(TokenType.LPAREN)
        params = []
        if self.current_token.type != TokenType.RPAREN:
            params.append(self.expect(TokenType.IDENT).value)
            while self.match(TokenType.COMMA):
                params.append(self.expect(TokenType.IDENT).value)
        self.expect(TokenType.RPAREN)
        body = self.parse_block()
        return Function(name.value, params, body)

    def parse_return(self):
        self.expect(TokenType.RETURN)
        value = self.expr()
        self.consume_optional_semicolon()
        return Return(value)

    def parse_print(self):
        self.expect(TokenType.PRINT)
        self.expect(TokenType.LPAREN)
        value = self.expr()
        self.expect(TokenType.RPAREN)
        self.consume_optional_semicolon()
        return Print(value)

    def parse_if(self):
        self.expect(TokenType.IF)
        if self.match(TokenType.LPAREN):
            condition = self.expr()
            self.expect(TokenType.RPAREN)
        else:
            condition = self.expr()
        then_branch = self.parse_block()
        return If(condition, then_branch)

    def parse_block(self):
        self.expect(TokenType.LBRACE)
        statements = []
        while self.current_token.type != TokenType.RBRACE:
            statements.append(self.statement())
        self.expect(TokenType.RBRACE)
        return Block(statements)

    def expr_statement(self):
        expr = self.expr()
        self.consume_optional_semicolon()
        return ExprStmt(expr)

    def expr(self, min_precedence=1):
        left = self.postfix()
        while self.current_token is not None:
            op_type = self.current_token.type
            precedence = self.PRECEDENCE.get(op_type)
            if precedence is None or precedence < min_precedence:
                break
            op = self.current_token
            self.advance()
            right = self.expr(precedence + 1)
            left = Binary(left, op, right)
        return left

    def postfix(self):
        expr = self.primary()
        while self.current_token is not None and self.current_token.type == TokenType.LPAREN:
            self.advance()
            args = []
            if self.current_token.type != TokenType.RPAREN:
                args.append(self.expr())
                while self.match(TokenType.COMMA):
                    args.append(self.expr())
            self.expect(TokenType.RPAREN)
            expr = Call(expr, args)
        return expr

    def primary(self):
        t = self.current_token.type
        if t == TokenType.INT:
            token = self.current_token
            self.advance()
            return Number(token)
        if t == TokenType.STRING:
            token = self.current_token
            self.advance()
            return StringLiteral(token)
        if t == TokenType.IDENT:
            token = self.current_token
            self.advance()
            return Identifier(token)
        if t == TokenType.LPAREN:
            self.advance()
            node = self.expr()
            self.expect(TokenType.RPAREN)
            return node
        self.error(f"Unexpected token: {self.current_token}")




def format_expression(node):
    if isinstance(node, Number):
        return f"Literal({node.value})"
    if isinstance(node, StringLiteral):
        return f'String("{node.value}")'
    if isinstance(node, Identifier):
        return f'Ident("{node.value}")'
    if isinstance(node, Binary):
        return (
            f"BinOp({node.operator.type}, "
            f"{format_expression(node.left)}, {format_expression(node.right)})"
        )
    if isinstance(node, Call):
        if isinstance(node.callee, Identifier):
            callee_name = node.callee.value
        else:
            callee_name = format_expression(node.callee)
        args = ", ".join(format_expression(arg) for arg in node.arguments)
        return f'Call("{callee_name}", [{args}])'
    return repr(node)


def ast_lines(node, prefix="", is_last=True):
    # print("\n--------------Node-----------")
    # print(node)
    # print("\n--------------Prefix-----------")
    # print(prefix)
    connector = "\\-- " if is_last else "|-- "
    lines = []
    
    if isinstance(node, Program):
        lines.append("Program")
        count = len(node.statements)
        for index, statement in enumerate(node.statements):
            child_prefix = prefix + ("    " if index == count - 1 else "|   ")
            lines.extend(ast_lines(statement, child_prefix, index == count - 1))
        # print(lines)
        return lines

    if isinstance(node, Function):
        lines.append(f'{prefix}{connector}FunctionDecl("{node.name}", params={node.params})')
        count = len(node.body.statements)
        for index, statement in enumerate(node.body.statements):
            child_prefix = prefix + ("    " if is_last else "|   ")
            child_prefix += "    " if index == count - 1 else "|   "
            lines.extend(ast_lines(statement, child_prefix[:-4], index == count - 1))
        return lines

    if isinstance(node, If):
        lines.append(
            f"{prefix}{connector}IfStatement(condition={format_expression(node.condition)})"
        )
        body_statements = node.then_branch.statements
        count = len(body_statements)
        base_prefix = prefix + ("    " if is_last else "|   ")
        for index, statement in enumerate(body_statements):
            lines.extend(ast_lines(statement, base_prefix, index == count - 1))
        return lines

    if isinstance(node, Return):
        lines.append(f"{prefix}{connector}ReturnStmt({format_expression(node.value)})")
        return lines

    if isinstance(node, Let):
        lines.append(
            f'{prefix}{connector}LetDecl("{node.name}", {format_expression(node.value)})'
        )
        return lines

    if isinstance(node, Print):
        lines.append(f"{prefix}{connector}PrintStmt({format_expression(node.value)})")
        return lines

    if isinstance(node, ExprStmt):
        lines.append(f"{prefix}{connector}ExprStmt({format_expression(node.expr)})")
        return lines

    lines.append(f"{prefix}{connector}{node}")
    return lines


def format_ast(node):
    return "\n".join(ast_lines(node))



class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.values = {}

    def define(self, name, value):
        self.values[name] = value

    def get(self, name):
        if name in self.values:
            return self.values[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise Exception(f"Undefined variable '{name}'")


class UserFunction:
    def __init__(self, declaration, closure):
        self.declaration = declaration
        self.closure = closure

    def call(self, interpreter, arguments):
        env = Environment(self.closure)
        for param, arg in zip(self.declaration.params, arguments):
            env.define(param, arg)
        try:
            interpreter.execute_block(self.declaration.body, env)
        except ReturnSignal as signal:
            return signal.value
        return None


class Interpreter:
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self.globals.define("str", lambda value: str(value))

    def interpret(self, program):
        for statement in program.statements:
            # print("Statement: " + str(statement))
            self.execute(statement)

    def execute(self, stmt):
        if isinstance(stmt, Let):
            self.environment.define(stmt.name, self.evaluate(stmt.value))
            return
        if isinstance(stmt, Function):
            self.environment.define(stmt.name, UserFunction(stmt, self.environment))
            return
        if isinstance(stmt, Return):
            raise ReturnSignal(self.evaluate(stmt.value))
        if isinstance(stmt, Print):
            print(self.evaluate(stmt.value))
            return
        if isinstance(stmt, If):
            if self.is_truthy(self.evaluate(stmt.condition)):
                self.execute_block(stmt.then_branch, Environment(self.environment))
            return
        if isinstance(stmt, Block):
            self.execute_block(stmt, Environment(self.environment))
            return
        if isinstance(stmt, ExprStmt):
            self.evaluate(stmt.expr)
            return
        raise Exception(f"Unsupported statement: {stmt}")

    def execute_block(self, block, environment):
        previous = self.environment
        self.environment = environment
        try:
            for statement in block.statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def evaluate(self, expr):
        if isinstance(expr, Number):
            return expr.value
        if isinstance(expr, StringLiteral):
            return expr.value
        if isinstance(expr, Identifier):
            return self.environment.get(expr.value)
        if isinstance(expr, Binary):
            left = self.evaluate(expr.left)
            right = self.evaluate(expr.right)
            op = expr.operator.type
            if op == TokenType.PLUS:
                return left + right
            if op == TokenType.MINUS:
                return left - right
            if op == TokenType.LT:
                return left < right
            if op == TokenType.LTE:
                return left <= right
            if op == TokenType.GT:
                return left > right
            if op == TokenType.GTE:
                return left >= right
            if op == TokenType.EQ:
                return left == right
            if op == TokenType.NEQ:
                return left != right
            raise Exception(f"Unsupported operator: {op}")
        if isinstance(expr, Call):
            callee = self.evaluate(expr.callee)
            arguments = [self.evaluate(arg) for arg in expr.arguments]
            if isinstance(callee, UserFunction):
                if len(arguments) != len(callee.declaration.params):
                    raise Exception("Argument count mismatch")
                return callee.call(self, arguments)
            if callable(callee):
                return callee(*arguments)
            raise Exception("Can only call functions")
        raise Exception(f"Unsupported expression: {expr}")

    @staticmethod
    def is_truthy(value):
        return bool(value)



def collect_tokens(source):
    lexer = Lexer(source)
    tokens = []
    while True:
        token = lexer.get_next_token()
        tokens.append(token)
        if token.type == TokenType.EOF:
            return tokens


def format_token(token):
    if token.value is None:
        return token.type
    if token.type == TokenType.INT:
        return f"{token.type}({token.value})"
    return f'{token.type}("{token.value}")'



# code = """fn fibonacci(n) {
# if n <= 1 { return n }
# return fibonacci(n - 1) + fibonacci(n - 2)
# }
# let result = fibonacci(10)
# print("Fibonacci(10) = " + str(result))
# """
code = """ let x = 10; let y = 20; fn add(a, b) { return a + b; } fn compare(n) { if (n <= 10) { print("less or equal"); } if (n >= 20) { print("greater or equal"); } if (n == 15) { print("equal"); } if (n != 0) { print("not zero"); } if (n < 5) { print("less"); } if (n > 5) { print("greater"); } return n; } let result = compare(add(x, y)); print("Result: " + str(result)); """

# code = """ let x = 10;
# let y = 20;
# let z = x + y;
# print(z); """
print("\n\n\n===---------------- Source Code (MiniLang) -----------===")
print(code.strip())

tokens = collect_tokens(code)
print("\n\n\n===----------- Lexer Output ---------------===")
print("[" + ", ".join(format_token(token) for token in tokens) + "]")

parser = Parser(tokens)
ast = parser.parse()
print("\n\n\n=== ----------------AST ------------------ ===")
print(ast)

print("\n\n\n=== ----------------AST (abbreviated)------------------ ===")
print(format_ast(ast))


print("\n\n\n=== --------------------Interpreter Output ------------------===")
Interpreter().interpret(ast)
