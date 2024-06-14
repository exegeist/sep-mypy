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
    total_branches = len(branch_coverage)
    print(f"Total number of branches: {total_branches}\n")
    print("Results:")
    for branch, hit in branch_coverage.items():
        print(f"{branch} was {'hit' if hit else 'not hit'}")
    num_branches_hit = sum(branch_coverage.values())
    print(f"\nNumber of branches hit: {num_branches_hit}")
    print(f"Total branch coverage: {num_branches_hit / total_branches * 100}%")

class TestTypeMeetVisitor(TypeMeetVisitor):
    def visit_deleted_type(self, t: DeletedType) -> ProperType:
        if isinstance(self.s, NoneType):
            branch_coverage["visit_NoneType"] = True
            if state.strict_optional:
                branch_coverage["visit_strict_optional"] = True
                return t
            else:
                branch_coverage["visit_non_strict_optional"] = True
                return self.s
        elif isinstance(self.s, UninhabitedType):
            branch_coverage["visit_UninhabitedType"] = True
            return self.s
        else:
            branch_coverage["visit_other_Type"] = True
            return t



