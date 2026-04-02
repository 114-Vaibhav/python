#Without multiprocessing
import inspect
import time
from decoraters import _fixture_registry
from discovery import discovery_tests
import traceback
from multiprocessing import Pool
from collections import defaultdict

def resolve_fixtures(func, module_cache, excluded_params=None):
    sig = inspect.signature(func)
   
    excluded_params = set(excluded_params or [])
    fixture_kwargs = {}

    for param in sig.parameters.values():
        name = param.name

        if name in excluded_params:
            continue

        if name not in _fixture_registry:
            raise Exception(f"No fixture found for parameter '{name}'")

        fixture_info = _fixture_registry[name]

        
        if fixture_info["scope"] == "session":
            if fixture_info["cached"] is None:
                fixture_info["cached"] = fixture_info["func"]()
            value = fixture_info["cached"]

        
        elif fixture_info["scope"] == "module":
            if name not in module_cache:
                module_cache[name] = fixture_info["func"]()
            value = module_cache[name]

        
        else:
            value = fixture_info["func"]()

        fixture_kwargs[name] = value

    return fixture_kwargs

passed = 0
failed = 0
skip = 0
error = 0

total_start = time.time()
print("------------- Test Discovery -----------------")
tests,testCount = discovery_tests("tests")

print("Found", testCount, "tests and ", len(tests), "modules  \n")
print("------------- Loading Fixtures -----------------")


for name, fixture in _fixture_registry.items():
    if fixture["scope"] == "session" and fixture["cached"] is None:
        fixture["cached"] = fixture["func"]()
fixture_info = []

for name, fixture in _fixture_registry.items():
    fixture_info.append(f"{name} ({fixture['scope']})")

print("Fixtures loaded:", ", ".join(fixture_info))

for module in tests:
    module_name = module["name"]
    print(f"\n--- Running {module_name}---")

    module_cache = {} 

    for test in module["functions"]:
        func = test["function"]
        name = test["name"]

        if hasattr(func, "_skip") and func._skip:
            reason = getattr(func, "_skip_reason", "")
            print(f"SKIP {name} ({reason})")
            skip += 1
            continue

        start = time.time()

        try:
            
            if hasattr(func, "_parametrize"):
                param_data = func._parametrize
                
                param_names = param_data.get("names") or [
                    name.strip() for name in param_data.get("argnames", "").split(",") if name.strip()
                ]

                for values in param_data["values"]:
                    if not isinstance(values, tuple):
                        values = (values,)

                    t_start = time.time()

                    try:
                       
                        
                        param_dict = dict(zip(param_names, values))

                        fixture_kwargs = resolve_fixtures(func, module_cache, excluded_params=param_names)

                        all_kwargs = {**fixture_kwargs, **param_dict}

                        func(**all_kwargs)
                        
                        param_str = ", ".join(f"{k}={v}" for k, v in zip(param_names, values))
                        print(f"PASS {name}[{param_str}] ({time.time()-t_start:.4f}s)")
                        passed += 1

                    except AssertionError as e:
                        print(f"FAIL {name}")
                        print("AssertionError:", e)
                        print(traceback.format_exc(limit=1))
                        failed += 1

                    except Exception as e:
                        
                        param_str = ", ".join(f"{k}={v}" for k, v in param_dict.items())
                        print(f"ERROR {name}[{param_str}] -> {e}")
                        error += 1

                continue
 
            # 🔹 NORMAL TEST
            fixture_kwargs = resolve_fixtures(func, module_cache)
            func(**fixture_kwargs)
            print(f"PASS {name} ({time.time()-start:.4f}s)")
            passed += 1

        except AssertionError:
            print(f"FAIL {name}")
            print("AssertionError:", e)
            print(traceback.format_exc(limit=1))
            failed += 1

        except Exception as e:
            print(f"ERROR {name} -> {e}")
            print(traceback.format_exc(limit=2))
            error += 1

print("\n=== Summary ===")
print(f"{passed+failed+skip+error} tests | {passed} passed | {failed} failed | {skip} skipped | {error} errors")

print(f"Total time: {time.time()-total_start:.4f}s )")
