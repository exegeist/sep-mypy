import sys

from mypy.test.helpers import Suite
from mypy.report import should_skip_path, print_skip_path_coverage



class SkipPathSuite(Suite):
    def test_skip_path(self):
        original_stdout = sys.stdout
        with open('test_skip_path.txt', 'w') as f:
            sys.stdout = f
            try:
                assert should_skip_path("some/dir/abc.pyi") == True     #Test special module path
                assert should_skip_path("some/dir/typing.pyi") == True 
                assert should_skip_path("some/dir/builtins.pyi") == True 

                assert should_skip_path("..some_path") == True          #Test parent directory path
                assert should_skip_path("path/test/stubs") == True      #Test path with stubs
                assert should_skip_path("normal_path") == False         #Test normal path 
              

                print("\nAll tests passed.\n") 
                print("Coverage results:\n")
                print_skip_path_coverage()
            finally:
                sys.stdout = original_stdout