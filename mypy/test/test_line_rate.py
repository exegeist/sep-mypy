import sys

from mypy.test.helpers import Suite
from mypy.report import get_line_rate, print_line_rate_coverage



class LineRateSuite(Suite):
    def test_get_line_rate(self):
        original_stdout = sys.stdout
        with open('test_line_rate.txt', 'w') as f:
            sys.stdout = f
            try:
                
                assert get_line_rate(0,0) == "1.0"      #Test both = 0
                assert get_line_rate(2,0) == "1.0"      #Test total_lines = 0
                assert get_line_rate(0,2) == "0.0000"   #Test covered_lines = 0  
                assert get_line_rate(1,1) == "1.0000"   #Test both <> 0
                assert get_line_rate(1,2) == "0.5000"   #Test covered_lines < total_lines
                assert get_line_rate(2,1) == "2.0000"   #Test covered_lines > total_lines


                print("\nAll tests passed.\n") 
                print("Coverage results:\n")
                print_line_rate_coverage()
            finally:
                sys.stdout = original_stdout

