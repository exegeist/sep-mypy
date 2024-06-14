import sys
from mypy.meet_with_coverage import TestTypeMeetVisitor, print_visit_deleted_coverage
from mypy.state import state
from mypy.types import DeletedType, ProperType, NoneType, UninhabitedType
from mypy.test.helpers import Suite

class TestVisitDeletedSuite(Suite):
    def test_visit_deleted(self):
        original_stdout = sys.stdout
        with open('test_visit_deleted_output.txt', 'w') as f:
            sys.stdout = f
            try:
                t = DeletedType()

                with state.strict_optional_set(True):
                    # Test visit_NoneType and visit_strict_optional
                    visitor = TestTypeMeetVisitor(NoneType())
                    result = visitor.visit_deleted_type(t)
                    assert result is t, "Test failed for NoneType with strict_optional=True"
                    print("Passed Test: visit_NoneType and visit_strict_optional")

                    # Test visit_UninhabitedType
                    visitor = TestTypeMeetVisitor(UninhabitedType())
                    result = visitor.visit_deleted_type(t)
                    assert result is visitor.s, "Test failed for UninhabitedType"
                    print("Passed Test: visit_UninhabitedType")

                    # Test visit_other_Type (ProperType)
                    visitor = TestTypeMeetVisitor(ProperType())
                    result = visitor.visit_deleted_type(t)
                    assert result is t, "Test failed for other_Type (ProperType)"
                    print("Passed Test: visit_other_Type")


                with state.strict_optional_set(False):
                    # Test visitNoneType and visit_non_strict_optional
                    visitor = TestTypeMeetVisitor(NoneType())
                    state.strict_optional_set(False)
                    result = visitor.visit_deleted_type(t)
                    assert result is visitor.s, "Test failed for NoneType with strict_optional=False"
                    print("Passed Test: visit_NoneType and visit_non_strict_optional")



                print("\nAll tests passed.\n") 
                print("Coverage results:\n")
                print_visit_deleted_coverage()
            finally:
                sys.stdout = original_stdout
    