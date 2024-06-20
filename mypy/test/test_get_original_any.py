import sys
from mypy.test.helpers import Suite
from mypy.stats import print_get_original_any_coverage, get_original_any
from mypy.types import AnyType

class GetOriginalAnySuite(Suite):
    def test_get_original_any(self):
        original_stdout = sys.stdout
        with open('test_get_original_any_output.txt', 'w') as f:
            sys.stdout = f
            try:
                
                # Test 1
                print("\nTest 1:")
                # Is 7 when it comes from interaction with another Any
                type2 = AnyType(9)
                type1 = AnyType(7, type2)
                result = get_original_any(type1)
                assert result == type1.source_any, f"Expected {type1.source_any}, but got {result}"
                print("Test 1 passed.")

                # Test 2
                print("\nTest 2:")
                type2 = AnyType(8)
                result = get_original_any(type2)
                assert result == type2, f"Expected {type2}, but got {result}"
                print("Test 2 passed.")

                print("\nAll tests passed.\n") 
                print("Coverage results:\n")
                print_get_original_any_coverage()
            finally:
                sys.stdout = original_stdout
    