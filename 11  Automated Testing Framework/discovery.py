
import os
import importlib.util
import inspect

def discovery_tests(test_dir="tests"):
    tests = []
    testsCount=0;
    for root, _, files in os.walk(test_dir):
        for file in files:
            temp = []
            if file.endswith(".py"):
                
                file_path = os.path.join(root, file)
                
                # module_name = file_path.replace("/", ".").replace("\\", ".")
                module_name = file_path.replace("\\", ".").replace("/", ".")
                module_name = module_name.replace(".py", "")
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                for name, obj in inspect.getmembers(module, inspect.isfunction):
                    if name.startswith("test_"):
                        testsCount+=1
                        temp.append({
                            "name": name,
                            "function": obj,
                            "parameters": inspect.signature(obj).parameters,
                        })
                tests.append({"name": module_name, "functions": temp})

    return tests,testsCount

