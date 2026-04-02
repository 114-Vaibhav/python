from decoraters import fixture
from decoraters import parameter
import tempfile

# 🔹 SESSION FIXTURE
@fixture(scope="session")
def db_connection():
    print("Setting up DB connection (session)")
    return {"conn": "DB_CONN"}


# 🔹 MODULE FIXTURE
@fixture(scope="module")
def module_data():
    print("Setting up module data")
    return {"module": "data"}


# 🔹 FUNCTION FIXTURE
@fixture(scope="function")
def temp_dir():
    dir_path = tempfile.mkdtemp()
    print("Creating temp dir:", dir_path)
    return dir_path


# 🔹 SIMPLE TEST
def test_db_connection(db_connection, temp_dir):
    assert db_connection["conn"] == "DB_CONN"


# 🔹 MODULE SCOPE TEST
def test_module(module_data):
    assert module_data["module"] == "data"



@parameter("x", [1, 2, 3])
def test_param(x, db_connection):
    assert x in [1, 2, 3]


# 🔹 COMBINED FIXTURE + PARAM
@parameter("x,y,z", [(1, 2,3), (2, 3,5)])
def test_combined(x, y,z, module_data, temp_dir):
    assert x + y == z