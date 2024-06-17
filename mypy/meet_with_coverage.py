from mypy.meet import TypeMeetVisitor
from mypy.state import state
from mypy.types import DeletedType, ProperType, NoneType, UninhabitedType, TypeVarTupleType

class TestTypeMeetVisitor(TypeMeetVisitor):
    def visit_deleted_type(self, t: DeletedType) -> ProperType:
        if isinstance(self.s, NoneType):
            if state.strict_optional:
                return t
            else:
                return self.s
        elif isinstance(self.s, UninhabitedType):
            return self.s
        else:
            return t
        
    def visit_type_var_tuple(self, t: TypeVarTupleType) -> ProperType:
        if isinstance(self.s, TypeVarTupleType) and self.s.id == t.id:
            return self.s if self.s.min_len > t.min_len else t
        else:
            return self.default(self.s)