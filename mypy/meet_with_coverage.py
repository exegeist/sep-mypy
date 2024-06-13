from mypy.meet import TypeMeetVisitor
from mypy.state import state
from mypy.types import DeletedType, ProperType, NoneType, UninhabitedType

branch_coverage = {
    "visit_NoneType": False,
    "visit_UninhabitedType": False,
    "visit_other_Type": False,
    "visit_strict_optional": False,
    "visit_non_strict_optional": False
}

def print_coverage():
    for branch, hit in branch_coverage.items():
        print(f"{branch} was {'hit' if hit else 'not hit'}")

class TestTypeMeetVisitor(TypeMeetVisitor):
    def visit_deleted_type(self, t: DeletedType) -> ProperType:
        if isinstance(self.s, NoneType):
            print("NoneType")
            branch_coverage["visitNoneType"] = True
            if state.strict_optional:
                print("Strict NoneType")
                branch_coverage["visit_strict_optional"] = True
                return t
            else:
                print("Non Strict NoneType")
                branch_coverage["visit_non_strict_optional"] = True
                return self.s
        elif isinstance(self.s, UninhabitedType):
            print("UninhabitedType")
            branch_coverage["visitUninhabitedType"] = True
            return self.s
        else:
            print("Other Type")
            branch_coverage["visit_other_Type"] = True
            return t



