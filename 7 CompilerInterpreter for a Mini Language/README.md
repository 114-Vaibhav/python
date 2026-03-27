# MiniLang Compiler / Interpreter in Python

This project implements a small language called `MiniLang` in Python. It includes:

- a `Lexer` to convert source code into tokens
- an AST builder to represent program structure
- a `Parser` to turn tokens into AST nodes
- an `Interpreter` to execute the AST
- AST pretty-printing for easier debugging and learning

The project is useful for understanding the core stages of a simple compiler / interpreter pipeline.

## Features

The current implementation supports:

- variable declarations using `let`
- integer literals
- string literals
- identifiers
- binary operators: `+`, `-`, `<`, `<=`, `>`, `>=`, `==`
- function declarations with `fn`
- function calls
- recursion
- `if` statements
- `return` statements
- `print(...)`
- a built-in `str(...)` function
- AST output in normal and abbreviated tree format

## Project Flow

The program processes MiniLang source code in these stages:

1. Source code is read as a string.
2. The lexer converts it into a list of tokens.
3. The parser converts the tokens into an Abstract Syntax Tree (AST).
4. The AST is printed in full and abbreviated form.
5. The interpreter executes the AST and prints the result.

## MiniLang Syntax

### Variable Declaration

```txt
let x = 10
let y = 20
let z = x + y
```

Semicolons are also accepted:

```txt
let x = 10;
```

### Function Declaration

```txt
fn add(a, b) {
    return a + b
}
```

### Function Call

```txt
let result = add(10, 20)
```

### If Statement

Both styles are supported:

```txt
if n <= 1 { return n }
```

```txt
if (n <= 1) {
    return n;
}
```

### Print

```txt
print(result)
print("Answer = " + str(result))
```

## Example Program

```txt
fn fibonacci(n) {
if n <= 1 { return n }
return fibonacci(n - 1) + fibonacci(n - 2)
}

let result = fibonacci(10)
print("Fibonacci(10) = " + str(result))
```

Expected interpreter output:

```txt
Fibonacci(10) = 55
```

## How To Run

Make sure Python is installed, then run:

```bash
python main.py
```

## Sample Output Stages

When you run the program, it prints:

- source code
- lexer output
- full AST
- abbreviated AST tree
- interpreter output

## Main Components

- `TokenType`: defines token names
- `Token`: stores token type and value
- `Lexer`: breaks source code into tokens
- `AST` node classes: represent expressions and statements
- `Parser`: builds the program AST
- `Interpreter`: executes the AST
- formatting helpers: print tokens and AST cleanly

## File Structure

```txt
.
|-- main.py
|-- README.md
|-- Output.txt
```

## Notes

- The parser now supports both semicolon-based and newline/brace-based MiniLang style.
- Function calls such as `fibonacci(10)` and `str(result)` are supported.
- Recursive functions work correctly.
- The lexer/parser/interpreter are implemented in a single file for simplicity and learning purposes.

## Learning Goal

This project is a good starting point for studying:

- lexical analysis
- parsing
- abstract syntax trees
- interpreters
- function execution and environments
- recursion in language design

## Future Improvements

Possible next steps:

- add `else`
- add `*` and `/`
- add boolean literals
- add comments in the language
- move lexer, parser, AST, and interpreter into separate files
- improve error messages
- fix `!=` token handling inside the lexer
