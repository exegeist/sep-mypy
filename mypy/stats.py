"""Utilities for calculating and reporting statistics about types."""

from __future__ import annotations

import os
from collections import Counter
from contextlib import contextmanager
from typing import Final, Iterator

from mypy import nodes
from mypy.argmap import map_formals_to_actuals
from mypy.nodes import (
    AssignmentExpr,
    AssignmentStmt,
    BreakStmt,
    BytesExpr,
    CallExpr,
    ClassDef,
    ComparisonExpr,
    ComplexExpr,
    ContinueStmt,
    EllipsisExpr,
    Expression,
    ExpressionStmt,
    FloatExpr,
    FuncDef,
    Import,
    ImportAll,
    ImportFrom,
    IndexExpr,
    IntExpr,
    MemberExpr,
    MypyFile,
    NameExpr,
    Node,
    OpExpr,
    PassStmt,
    RefExpr,
    StrExpr,
    TypeApplication,
    UnaryExpr,
    YieldFromExpr,
)
from mypy.traverser import TraverserVisitor
from mypy.typeanal import collect_all_inner_types
from mypy.types import (
    AnyType,
    CallableType,
    FunctionLike,
    Instance,
    TupleType,
    Type,
    TypeOfAny,
    TypeQuery,
    TypeVarType,
    get_proper_type,
    get_proper_types,
)
from mypy.util import correct_relative_import

TYPE_EMPTY: Final = 0
TYPE_UNANALYZED: Final = 1  # type of non-typechecked code
TYPE_PRECISE: Final = 2
TYPE_IMPRECISE: Final = 3
TYPE_ANY: Final = 4

precision_names: Final = ["empty", "unanalyzed", "precise", "imprecise", "any"]


class StatisticsVisitor(TraverserVisitor):
    def __init__(
        self,
        inferred: bool,
        filename: str,
        modules: dict[str, MypyFile],
        typemap: dict[Expression, Type] | None = None,
        all_nodes: bool = False,
        visit_untyped_defs: bool = True,
    ) -> None:
        self.inferred = inferred
        self.filename = filename
        self.modules = modules
        self.typemap = typemap
        self.all_nodes = all_nodes
        self.visit_untyped_defs = visit_untyped_defs

        self.num_precise_exprs = 0
        self.num_imprecise_exprs = 0
        self.num_any_exprs = 0

        self.num_simple_types = 0
        self.num_generic_types = 0
        self.num_tuple_types = 0
        self.num_function_types = 0
        self.num_typevar_types = 0
        self.num_complex_types = 0
        self.num_any_types = 0

        self.line = -1

        self.line_map: dict[int, int] = {}

        self.type_of_any_counter: Counter[int] = Counter()
        self.any_line_map: dict[int, list[AnyType]] = {}

        # For each scope (top level/function), whether the scope was type checked
        # (annotated function).
        #
        # TODO: Handle --check-untyped-defs
        self.checked_scopes = [True]

        self.output: list[str] = []

        TraverserVisitor.__init__(self)

    def visit_mypy_file(self, o: MypyFile) -> None:
        self.cur_mod_node = o
        self.cur_mod_id = o.fullname
        super().visit_mypy_file(o)

    def visit_import_from(self, imp: ImportFrom) -> None:
        self.process_import(imp)

    def visit_import_all(self, imp: ImportAll) -> None:
        self.process_import(imp)

    def process_import(self, imp: ImportFrom | ImportAll) -> None:
        import_id, ok = correct_relative_import(
            self.cur_mod_id, imp.relative, imp.id, self.cur_mod_node.is_package_init_file()
        )
        if ok and import_id in self.modules:
            kind = TYPE_PRECISE
        else:
            kind = TYPE_ANY
        self.record_line(imp.line, kind)

    def visit_import(self, imp: Import) -> None:
        if all(id in self.modules for id, _ in imp.ids):
            kind = TYPE_PRECISE
        else:
            kind = TYPE_ANY
        self.record_line(imp.line, kind)

    def visit_func_def(self, o: FuncDef) -> None:
        with self.enter_scope(o):
            self.line = o.line
            if len(o.expanded) > 1 and o.expanded != [o] * len(o.expanded):
                if o in o.expanded:
                    print(
                        "{}:{}: ERROR: cycle in function expansion; skipping".format(
                            self.filename, o.line
                        )
                    )
                    return
                for defn in o.expanded:
                    assert isinstance(defn, FuncDef)
                    self.visit_func_def(defn)
            else:
                if o.type:
                    assert isinstance(o.type, CallableType)
                    sig = o.type
                    arg_types = sig.arg_types
                    if sig.arg_names and sig.arg_names[0] == "self" and not self.inferred:
                        arg_types = arg_types[1:]
                    for arg in arg_types:
                        self.type(arg)
                    self.type(sig.ret_type)
                elif self.all_nodes:
                    self.record_line(self.line, TYPE_ANY)
                if not o.is_dynamic() or self.visit_untyped_defs:
                    super().visit_func_def(o)

    @contextmanager
    def enter_scope(self, o: FuncDef) -> Iterator[None]:
        self.checked_scopes.append(o.type is not None and self.checked_scopes[-1])
        yield None
        self.checked_scopes.pop()

    def is_checked_scope(self) -> bool:
        return self.checked_scopes[-1]

    def visit_class_def(self, o: ClassDef) -> None:
        self.record_line(o.line, TYPE_PRECISE)  # TODO: Look at base classes
        # Override this method because we don't want to analyze base_type_exprs (base_type_exprs
        # are base classes in a class declaration).
        # While base_type_exprs are technically expressions, type analyzer does not visit them and
        # they are not in the typemap.
        for d in o.decorators:
            d.accept(self)
        o.defs.accept(self)

    def visit_type_application(self, o: TypeApplication) -> None:
        self.line = o.line
        for t in o.types:
            self.type(t)
        super().visit_type_application(o)

    def visit_assignment_stmt(self, o: AssignmentStmt) -> None:
        self.line = o.line
        if isinstance(o.rvalue, nodes.CallExpr) and isinstance(
            o.rvalue.analyzed, nodes.TypeVarExpr
        ):
            # Type variable definition -- not a real assignment.
            return
        if o.type:
            self.type(o.type)
        elif self.inferred and not self.all_nodes:
            # if self.all_nodes is set, lvalues will be visited later
            for lvalue in o.lvalues:
                if isinstance(lvalue, nodes.TupleExpr):
                    items = lvalue.items
                else:
                    items = [lvalue]
                for item in items:
                    if isinstance(item, RefExpr) and item.is_inferred_def:
                        if self.typemap is not None:
                            self.type(self.typemap.get(item))
        super().visit_assignment_stmt(o)

    def visit_expression_stmt(self, o: ExpressionStmt) -> None:
        if isinstance(o.expr, (StrExpr, BytesExpr)):
            # Docstring
            self.record_line(o.line, TYPE_EMPTY)
        else:
            super().visit_expression_stmt(o)

    def visit_pass_stmt(self, o: PassStmt) -> None:
        self.record_precise_if_checked_scope(o)

    def visit_break_stmt(self, o: BreakStmt) -> None:
        self.record_precise_if_checked_scope(o)

    def visit_continue_stmt(self, o: ContinueStmt) -> None:
        self.record_precise_if_checked_scope(o)

    def visit_name_expr(self, o: NameExpr) -> None:
        if o.fullname in ("builtins.None", "builtins.True", "builtins.False", "builtins.Ellipsis"):
            self.record_precise_if_checked_scope(o)
        else:
            self.process_node(o)
            super().visit_name_expr(o)

    def visit_yield_from_expr(self, o: YieldFromExpr) -> None:
        if o.expr:
            o.expr.accept(self)

    def visit_call_expr(self, o: CallExpr) -> None:
        self.process_node(o)
        if o.analyzed:
            o.analyzed.accept(self)
        else:
            o.callee.accept(self)
            for a in o.args:
                a.accept(self)
            self.record_call_target_precision(o)

    def record_call_target_precision(self, o: CallExpr) -> None:
        """Record precision of formal argument types used in a call."""
        if not self.typemap or o.callee not in self.typemap:
            # Type not available.
            return
        callee_type = get_proper_type(self.typemap[o.callee])
        if isinstance(callee_type, CallableType):
            self.record_callable_target_precision(o, callee_type)
        else:
            pass  # TODO: Handle overloaded functions, etc.

    def record_callable_target_precision(self, o: CallExpr, callee: CallableType) -> None:
        """Record imprecision caused by callee argument types.

        This only considers arguments passed in a call expression. Arguments
        with default values that aren't provided in a call arguably don't
        contribute to typing imprecision at the *call site* (but they
        contribute at the function definition).
        """
        assert self.typemap
        typemap = self.typemap
        actual_to_formal = map_formals_to_actuals(
            o.arg_kinds,
            o.arg_names,
            callee.arg_kinds,
            callee.arg_names,
            lambda n: typemap[o.args[n]],
        )
        for formals in actual_to_formal:
            for n in formals:
                formal = get_proper_type(callee.arg_types[n])
                if isinstance(formal, AnyType):
                    self.record_line(o.line, TYPE_ANY)
                elif is_imprecise(formal):
                    self.record_line(o.line, TYPE_IMPRECISE)

    def visit_member_expr(self, o: MemberExpr) -> None:
        self.process_node(o)
        super().visit_member_expr(o)

    def visit_op_expr(self, o: OpExpr) -> None:
        self.process_node(o)
        super().visit_op_expr(o)

    def visit_comparison_expr(self, o: ComparisonExpr) -> None:
        self.process_node(o)
        super().visit_comparison_expr(o)

    def visit_index_expr(self, o: IndexExpr) -> None:
        self.process_node(o)
        super().visit_index_expr(o)

    def visit_assignment_expr(self, o: AssignmentExpr) -> None:
        self.process_node(o)
        super().visit_assignment_expr(o)

    def visit_unary_expr(self, o: UnaryExpr) -> None:
        self.process_node(o)
        super().visit_unary_expr(o)

    def visit_str_expr(self, o: StrExpr) -> None:
        self.record_precise_if_checked_scope(o)

    def visit_bytes_expr(self, o: BytesExpr) -> None:
        self.record_precise_if_checked_scope(o)

    def visit_int_expr(self, o: IntExpr) -> None:
        self.record_precise_if_checked_scope(o)

    def visit_float_expr(self, o: FloatExpr) -> None:
        self.record_precise_if_checked_scope(o)

    def visit_complex_expr(self, o: ComplexExpr) -> None:
        self.record_precise_if_checked_scope(o)

    def visit_ellipsis(self, o: EllipsisExpr) -> None:
        self.record_precise_if_checked_scope(o)

    # Helpers

    def process_node(self, node: Expression) -> None:
        if self.all_nodes:
            if self.typemap is not None:
                self.line = node.line
                self.type(self.typemap.get(node))

    def record_precise_if_checked_scope(self, node: Node) -> None:
        if isinstance(node, Expression) and self.typemap and node not in self.typemap:
            kind = TYPE_UNANALYZED
        elif self.is_checked_scope():
            kind = TYPE_PRECISE
        else:
            kind = TYPE_ANY
        self.record_line(node.line, kind)

    def type(self, t: Type | None) -> None:
        t = get_proper_type(t)

        if not t:
            # If an expression does not have a type, it is often due to dead code.
            # Don't count these because there can be an unanalyzed value on a line with other
            # analyzed expressions, which overwrite the TYPE_UNANALYZED.
            self.record_line(self.line, TYPE_UNANALYZED)
            return

        if isinstance(t, AnyType) and is_special_form_any(t):
            # TODO: What if there is an error in special form definition?
            self.record_line(self.line, TYPE_PRECISE)
            return

        if isinstance(t, AnyType):
            self.log("  !! Any type around line %d" % self.line)
            self.num_any_exprs += 1
            self.record_line(self.line, TYPE_ANY)
        elif (not self.all_nodes and is_imprecise(t)) or (self.all_nodes and is_imprecise2(t)):
            self.log("  !! Imprecise type around line %d" % self.line)
            self.num_imprecise_exprs += 1
            self.record_line(self.line, TYPE_IMPRECISE)
        else:
            self.num_precise_exprs += 1
            self.record_line(self.line, TYPE_PRECISE)

        for typ in get_proper_types(collect_all_inner_types(t)) + [t]:
            if isinstance(typ, AnyType):
                typ = get_original_any(typ)
                if is_special_form_any(typ):
                    continue
                self.type_of_any_counter[typ.type_of_any] += 1
                self.num_any_types += 1
                if self.line in self.any_line_map:
                    self.any_line_map[self.line].append(typ)
                else:
                    self.any_line_map[self.line] = [typ]
            elif isinstance(typ, Instance):
                if typ.args:
                    if any(is_complex(arg) for arg in typ.args):
                        self.num_complex_types += 1
                    else:
                        self.num_generic_types += 1
                else:
                    self.num_simple_types += 1
            elif isinstance(typ, FunctionLike):
                self.num_function_types += 1
            elif isinstance(typ, TupleType):
                if any(is_complex(item) for item in typ.items):
                    self.num_complex_types += 1
                else:
                    self.num_tuple_types += 1
            elif isinstance(typ, TypeVarType):
                self.num_typevar_types += 1

    def log(self, string: str) -> None:
        self.output.append(string)

    def record_line(self, line: int, precision: int) -> None:
        self.line_map[line] = max(precision, self.line_map.get(line, TYPE_EMPTY))


def dump_type_stats(
    tree: MypyFile,
    path: str,
    modules: dict[str, MypyFile],
    inferred: bool = False,
    typemap: dict[Expression, Type] | None = None,
) -> None:
    if is_special_module(path):
        return
    print(path)
    visitor = StatisticsVisitor(inferred, filename=tree.fullname, modules=modules, typemap=typemap)
    tree.accept(visitor)
    for line in visitor.output:
        print(line)
    print("  ** precision **")
    print("  precise  ", visitor.num_precise_exprs)
    print("  imprecise", visitor.num_imprecise_exprs)
    print("  any      ", visitor.num_any_exprs)
    print("  ** kinds **")
    print("  simple   ", visitor.num_simple_types)
    print("  generic  ", visitor.num_generic_types)
    print("  function ", visitor.num_function_types)
    print("  tuple    ", visitor.num_tuple_types)
    print("  TypeVar  ", visitor.num_typevar_types)
    print("  complex  ", visitor.num_complex_types)
    print("  any      ", visitor.num_any_types)


def is_special_module(path: str) -> bool:
    return os.path.basename(path) in ("abc.pyi", "typing.pyi", "builtins.pyi")


def is_imprecise(t: Type) -> bool:
    return t.accept(HasAnyQuery())


class HasAnyQuery(TypeQuery[bool]):
    def __init__(self) -> None:
        super().__init__(any)

    def visit_any(self, t: AnyType) -> bool:
        return not is_special_form_any(t)


def is_imprecise2(t: Type) -> bool:
    return t.accept(HasAnyQuery2())


class HasAnyQuery2(HasAnyQuery):
    def visit_callable_type(self, t: CallableType) -> bool:
        # We don't want to flag references to functions with some Any
        # argument types (etc.) since they generally don't mean trouble.
        return False


def is_generic(t: Type) -> bool:
    t = get_proper_type(t)
    return isinstance(t, Instance) and bool(t.args)


def is_complex(t: Type) -> bool:
    t = get_proper_type(t)
    return is_generic(t) or isinstance(t, (FunctionLike, TupleType, TypeVarType))


def is_special_form_any(t: AnyType) -> bool:
    return get_original_any(t).type_of_any == TypeOfAny.special_form

get_original_any_branches = {
    "t_not_original_any" : False,
    "t_original_any" : False 
}


def get_original_any(t: AnyType) -> AnyType:
    if t.type_of_any == TypeOfAny.from_another_any:
        get_original_any_branches["t_not_original_any"] = True
        assert t.source_any
        assert t.source_any.type_of_any != TypeOfAny.from_another_any
        t = t.source_any
    else:
        get_original_any_branches["t_original_any"] = True
    return t


def print_get_original_any_coverage():
    print_coverage(get_original_any_branches)

def print_coverage(branch_coverage):
    total_branches = len(branch_coverage)
    print(f"Total number of branches: {total_branches}\n")
    print("Results:")
    for branch, hit in branch_coverage.items():
        print(f"{branch} was {'hit' if hit else 'not hit'}")
    num_branches_hit = sum(branch_coverage.values())
    print(f"\nNumber of branches hit: {num_branches_hit}")
    print(f"Total branch coverage: {num_branches_hit / total_branches * 100}%")