from mypy.meet_with_coverage import TestTypeMeetVisitor, print_coverage
from mypy.state import state
from mypy.types import DeletedType, ProperType, NoneType, UninhabitedType
from mypy.test.helpers import Suite

class TestVisitDeletedSuite(Suite):
    def test_visit_deleted(self):
        t = DeletedType()

        with state.strict_optional_set(True):
            # Test visitNoneType and visit_strict_optional
            visitor = TestTypeMeetVisitor(NoneType())
            result = visitor.visit_deleted_type(t)
            assert result is t, "Test failed for NoneType with strict_optional=True"

            # Test visit_UninhabitedType
            visitor = TestTypeMeetVisitor(UninhabitedType())
            result = visitor.visit_deleted_type(t)
            assert result is visitor.s, "Test failed for UninhabitedType"

            # Test visit_other_Type (ProperType)
            visitor = TestTypeMeetVisitor(ProperType())
            result = visitor.visit_deleted_type(t)
            assert result is t, "Test failed for ProperType"


        with state.strict_optional_set(False):
            # Test visitNoneType and visit_non_strict_optional
            visitor = TestTypeMeetVisitor(NoneType())
            state.strict_optional_set(False)
            result = visitor.visit_deleted_type(t)
            assert result is visitor.s, "Test failed for NoneType with strict_optional=False"



        print("All tests passed.")
        print_coverage()  