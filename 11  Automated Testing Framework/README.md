# Automated Testing Framework

A lightweight custom Python testing framework that demonstrates how to build core testing features from scratch without external libraries.

This project includes:

- Test discovery from a `tests/` directory
- Custom decorators for skipping and parametrizing tests
- Fixture injection with `function`, `module`, and `session` scope
- A serial test runner
- A multiprocessing test runner
- Console output with pass/fail/skip/error summaries

## Project Structure

```text
.
|-- decoraters.py
|-- discovery.py
|-- main.py
|-- mainW.py
|-- Output.txt
`-- tests/
    |-- test_auth.py
    |-- test_cart.py
    `-- test_fix.py
```

## Files Overview

- `decoraters.py`: Defines the custom decorators:
  - `@skip(...)`
  - `@parameter(...)`
  - `@fixture(scope=...)`
- `discovery.py`: Scans the `tests/` folder, imports test modules, and collects functions whose names start with `test_`.
- `mainW.py`: Runs tests without multiprocessing.
- `main.py`: Runs tests using a multiprocessing worker pool.
- `tests/`: Contains sample test modules using parametrization, skipping, and fixtures.
- `Output.txt`: Example output from both execution modes.

## Features

### 1. Test Discovery

The framework automatically walks through the `tests/` directory and loads all Python files. Any function whose name starts with `test_` is treated as a test.

### 2. Parametrized Tests

Use `@parameter(...)` to run the same test multiple times with different inputs.

Example:

```python
from decoraters import parameter

@parameter("user,passwd", [("user1", "pass1"), ("user2", "pass2")])
def test_login_valid_credentials(user, passwd):
    assert True
```

### 3. Skipped Tests

Use `@skip(...)` to mark a test as skipped.

Example:

```python
from decoraters import skip

@skip("Not implemented")
def test_payment():
    assert False
```

### 4. Fixtures

Fixtures are automatically injected into test functions by matching argument names.

Supported fixture scopes:

- `function`: a new value is created for each test
- `module`: the same value is reused within one module
- `session`: the same value is reused across the whole run

Example:

```python
from decoraters import fixture

@fixture(scope="session")
def db_connection():
    return {"conn": "DB_CONN"}

def test_db_connection(db_connection):
    assert db_connection["conn"] == "DB_CONN"
```

### 5. Parallel Execution

`main.py` builds individual test units and runs them across multiple processes using Python's `multiprocessing.Pool`.

This is useful for demonstrating how a basic test framework can scale beyond single-process execution.

## Requirements

- Python 3.8 or later
- No third-party dependencies are required

## How to Run

Open a terminal in the project folder and run one of the following commands.

### Run without multiprocessing

```bash
python mainW.py
```

### Run with multiprocessing

```bash
python main.py
```

## Example Output

The sample tests currently show:

- 22 total executed test cases
- 21 passed
- 1 skipped
- 0 failed
- 0 errors

See `Output.txt` for a captured example run.

## How Tests Are Written

Add new test files inside the `tests/` directory and name test functions with the `test_` prefix.

Example:

```python
def test_example():
    assert 1 + 1 == 2
```

You can also combine parametrization and fixtures:

```python
from decoraters import parameter, fixture

@fixture(scope="module")
def sample_data():
    return {"value": 10}

@parameter("x,y", [(1, 2), (2, 3)])
def test_sum(x, y, sample_data):
    assert x + y <= sample_data["value"]
```

## Learning Goals

This project is a good reference for understanding:

- how test discovery works
- how decorators store metadata on functions
- how fixtures can be resolved dynamically with `inspect.signature`
- how parametrized tests expand into multiple execution cases
- how multiprocessing can be used in a basic runner

## Notes

- The file name `decoraters.py` is used throughout the project and should stay unchanged unless imports are updated everywhere.
- `main.py` is the multiprocessing runner.
- `mainW.py` is the non-multiprocessing runner.
