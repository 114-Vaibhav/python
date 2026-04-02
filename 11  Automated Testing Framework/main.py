import os
import importlib.util
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

        # Ignore parametrized argument names here; only unresolved names should be treated as fixtures.
        if name in excluded_params:
            continue

        if name not in _fixture_registry:
            raise Exception(f"No fixture found for parameter '{name}'")

        fixture_info = _fixture_registry[name]

        # 🔹 SESSION scope
        if fixture_info["scope"] == "session":
            if fixture_info["cached"] is None:
                fixture_info["cached"] = fixture_info["func"]()
            value = fixture_info["cached"]

        # 🔹 MODULE scope
        elif fixture_info["scope"] == "module":
            if name not in module_cache:
                module_cache[name] = fixture_info["func"]()
            value = module_cache[name]

        # 🔹 FUNCTION scope
        else:
            value = fixture_info["func"]()

        fixture_kwargs[name] = value

    return fixture_kwargs


def build_test_units(tests):
    test_units = []

    for module in tests:
        module_name = module["name"]

        for test in module["functions"]:
            func = test["function"]
            name = test["name"]

            # PARAMETRIZED
            if hasattr(func, "_parametrize"):
                param_data = func._parametrize
                param_names = param_data.get("names", [])

                for values in param_data["values"]:
                    if not isinstance(values, tuple):
                        values = (values,)

                    param_dict = dict(zip(param_names, values))

                    test_units.append({
                        "module": module_name,
                        "function_name": name,
                        "param_dict": param_dict,
                    })
            else:
                test_units.append({
                    "module": module_name,
                    "function_name": name,
                    "param_dict": {},
                })

    return test_units

def worker_run(test_unit):
    import importlib
    import time
    import traceback
    from decoraters import _fixture_registry
    from main import resolve_fixtures  # reuse your function

    module_name = test_unit["module"]
    func_name = test_unit["function_name"]
    param_dict = test_unit["param_dict"]

    try:
        module = importlib.import_module(module_name)
        func = getattr(module, func_name)

        start = time.time()

        # skip check
        if hasattr(func, "_skip") and func._skip:
            return {
                "module": module_name,
                "name": func_name,
                "status": "SKIP",
                "reason": getattr(func, "_skip_reason", ""),
                "time": 0
            }

        # resolve fixtures
        fixture_kwargs = resolve_fixtures(func, module_cache={}, excluded_params=param_dict.keys())

        all_kwargs = {**fixture_kwargs, **param_dict}

        func(**all_kwargs)

        return {
            "module": module_name,
            "name": func_name,
            "status": "PASS",
            "time": time.time() - start,
            "params": param_dict
        }

    except AssertionError as e:
        return {
            "module": module_name,
            "name": func_name,
            "status": "FAIL",
            "error": str(e),
            "trace": traceback.format_exc(limit=1),
            "params": param_dict
        }

    except Exception as e:
        return {
            "module": module_name,
            "name": func_name,
            "status": "ERROR",
            "error": str(e),
            "trace": traceback.format_exc(limit=1),
            "params": param_dict
        }

passed = 0
failed = 0
skip = 0
error = 0
# 🔹 Total timing
total_start = time.time()

if __name__ == "__main__":
        
    print("------------- Test Discovery -----------------")
    tests,testCount = discovery_tests("tests")

    test_units = build_test_units(tests)
    print("Found", testCount, "tests and ", len(tests), "modules  \n")
    print("------------- Loading Fixtures -----------------")


    for name, fixture in _fixture_registry.items():
        if fixture["scope"] == "session" and fixture["cached"] is None:
            fixture["cached"] = fixture["func"]()
    fixture_info = []

    for name, fixture in _fixture_registry.items():
        fixture_info.append(f"{name} ({fixture['scope']})")

    print("Fixtures loaded:", ", ".join(fixture_info))

    parallel_workers = 4  # later from CLI

    if parallel_workers > 1:
        with Pool(parallel_workers) as pool:
            results = pool.map(worker_run, test_units)
    else:
        results = [worker_run(t) for t in test_units]

    passed = failed = skip = error = 0
    print(f"\n=== Execution ({parallel_workers} workers) ===\n")
    

    grouped = defaultdict(list)

    for res in results:
        grouped[res["module"]].append(res)
    for module, module_tests in grouped.items():
        print(module.replace(".", "/") + ".py")

        for res in module_tests:
            name = res["name"]
            status = res["status"]
            params = res.get("params", {})

            param_str = ""
            if params:
                param_str = "[" + ", ".join(f"{k}={v}" for k, v in params.items()) + "]"

            # aligned formatting
            label = f"{name}{param_str}"
            label = label.ljust(50)

            if status == "PASS":
                passed += 1
                print(f"PASS  {label} [{res['time']:.4f}s]")

            elif status == "FAIL":
                failed += 1
                print(f"FAIL  {label} [{res.get('time',0):.4f}s]")
                print(res["trace"])

            elif status == "ERROR":
                error += 1
                print(f"ERROR {label} -> {res['error']}")
                print(res["trace"])

            elif status == "SKIP":
                skip += 1
                print(f"SKIP  {label} (skipped: {res.get('reason','')})")

        print()  # spacing between modules

    #FIXTURE CLEANUP
    for name, fixture in _fixture_registry.items():
        if fixture["scope"] == "session" and fixture["cached"]:
            if fixture["teardown"]:
                fixture["teardown"](fixture["cached"])

    # 🔹 Total execution time
    total_time = time.time() - total_start

    print("\n=== Summary ===")
    print(f"{passed+failed+skip+error} tests | {passed} passed | {failed} failed | {skip} skipped | {error} errors")

    print(f"Total time: {total_time:.2f}s (parallel across {parallel_workers} workers)")


# without multiprocessing

# for module in tests:
#     module_name = module["name"]
#     print(f"\n--- Running {module_name}---")

#     module_cache = {}  # 🔹 for module scoped fixtures

#     for test in module["functions"]:
#         func = test["function"]
#         name = test["name"]

#         if hasattr(func, "_skip") and func._skip:
#             reason = getattr(func, "_skip_reason", "")
#             print(f"SKIP {name} ({reason})")
#             skip += 1
#             continue

#         start = time.time()

#         try:
#             # 🔹 PARAMETRIZED TEST
#             if hasattr(func, "_parametrize"):
#                 param_data = func._parametrize
#                 # Support both metadata shapes used in this project: "names" and "argnames".
#                 param_names = param_data.get("names") or [
#                     name.strip() for name in param_data.get("argnames", "").split(",") if name.strip()
#                 ]

#                 for values in param_data["values"]:
#                     if not isinstance(values, tuple):
#                         values = (values,)

#                     t_start = time.time()

#                     try:
                       
#                         # func(*fixture_args, *values)
#                         param_dict = dict(zip(param_names, values))

#                         fixture_kwargs = resolve_fixtures(func, module_cache, excluded_params=param_names)

#                         all_kwargs = {**fixture_kwargs, **param_dict}

#                         func(**all_kwargs)
#                         # merge args: fixtures first, then params (by keyword)
#                         # func(*fixture_args, **param_dict)
                        

#                         # print(f"PASS {name}{values} ({time.time()-t_start:.4f}s)")
#                         param_str = ", ".join(f"{k}={v}" for k, v in zip(param_names, values))
#                         print(f"PASS {name}[{param_str}] ({time.time()-t_start:.4f}s)")
#                         passed += 1

#                     except AssertionError as e:
#                         print(f"FAIL {name}")
#                         print("AssertionError:", e)
#                         print(traceback.format_exc(limit=1))
#                         failed += 1

#                     except Exception as e:
#                         # print(f"ERROR {name}{values} -> {e}")
#                         param_str = ", ".join(f"{k}={v}" for k, v in param_dict.items())
#                         print(f"ERROR {name}[{param_str}] -> {e}")
#                         error += 1

#                 continue
 
#             # 🔹 NORMAL TEST
#             fixture_kwargs = resolve_fixtures(func, module_cache)
#             func(**fixture_kwargs)
#             print(f"PASS {name} ({time.time()-start:.4f}s)")
#             passed += 1

#         except AssertionError:
#             print(f"FAIL {name}")
#             print("AssertionError:", e)
#             print(traceback.format_exc(limit=1))
#             failed += 1

#         except Exception as e:
#             print(f"ERROR {name} -> {e}")
#             print(traceback.format_exc(limit=2))
#             error += 1
