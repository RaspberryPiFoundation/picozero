from inspect import getmembers, isfunction
import sys
from uio import StringIO

def get_test_functions(module):
    test_functions = []
    
    members = getmembers(module)
    
    for member in members:
    
        if isfunction(member[1]) and member[0][0:4] == "test":
            test_functions.append(member)
    
    return test_functions

def get_exception(e):
    # get the exception
    s = StringIO()
    sys.print_exception(e, s)
    
    # format the exception
    s = "   " + s.getvalue()
    s = s.replace("\n", "\n    ")
    s = s.strip()
    
    return s
    
def run_test(test_func_name, test_func):

    try:
        test_func()
        print("SUCCESS -", test_func_name)
    except Exception as e:
        print("FAIL -", test_func_name, "\n", get_exception(e))
        
    
def run_tests(path):
    
    test_funcs = get_test_functions(__import__(path))
    
    for test_func_name, test_func in test_funcs:
        run_test(test_func_name, test_func)
    
path = "/tests/test_picozero"
run_tests(path)

