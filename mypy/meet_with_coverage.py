from mypy.meet import TypeMeetVisitor
from mypy.state import state
from mypy.types import DeletedType, ProperType, NoneType, UninhabitedType, TypeVarTupleType

branch_coverage_deleted_type = {
    "visit_NoneType": False,
    "visit_UninhabitedType": False,
    "visit_other_Type": False,
    "visit_strict_optional": False,
    "visit_non_strict_optional": False
}

branch_coverage_var_tuple = {
    "visit_tuple_same_id": False,
    "tuple.s_bigger_min": False,
    "tuple.t_bigger_equal_min": False,
    "visit_other_Type": False
}

def print_visit_deleted_coverage():
    print_coverage(branch_coverage_deleted_type)

def print_visit_var_tuple_coverage():
    print_coverage(branch_coverage_var_tuple)

def print_coverage(branch_coverage):
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
            branch_coverage_deleted_type["visit_NoneType"] = True
            if state.strict_optional:
                branch_coverage_deleted_type["visit_strict_optional"] = True
                return t
            else:
                branch_coverage_deleted_type["visit_non_strict_optional"] = True
                return self.s
        elif isinstance(self.s, UninhabitedType):
            branch_coverage_deleted_type["visit_UninhabitedType"] = True
            return self.s
        else:
            branch_coverage_deleted_type["visit_other_Type"] = True
            return t
        
    def visit_type_var_tuple(self, t: TypeVarTupleType) -> ProperType:
        if isinstance(self.s, TypeVarTupleType) and self.s.id == t.id:
            branch_coverage_var_tuple["visit_tuple_same_id"] = True
            if self.s.min_len > t.min_len:
                branch_coverage_var_tuple["tuple.s_bigger_min"] = True
                return self.s
            else:
                branch_coverage_var_tuple["tuple.t_bigger_equal_min"] = True
                return t
        else:
            branch_coverage_var_tuple["visit_other_Type"] = True
            return self.default(self.s)



