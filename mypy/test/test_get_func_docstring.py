import sys
from mypy.test.helpers import Suite
from mypy.nodes import FuncDef, Block, Statement, ExpressionStmt, StrExpr
from mypy.stubgen import ASTStubGenerator, print_get_func_docstring


class GetFuncDocstringsSuite(Suite):
    def test_get_func_docstring(self):
        original_stdout = sys.stdout
        with open('test_get_func_docstring.txt', 'w') as f:
            sys.stdout = f
            try:

                print("# Test 1")
                statement = StrExpr("I don't know what to write here.")
                sxpression_stmt = ExpressionStmt(statement)
                block = Block(body=[sxpression_stmt])
                func_def = FuncDef(body=None)
                generator = ASTStubGenerator()
                result = generator._get_func_docstring(func_def)
                assert result is None, "Expected None, got %s" % result
                print("Test 1 passed.")

                print("# Test 2")
                statement = StrExpr("I don't know what to write here.")
                sxpression_stmt = ExpressionStmt(statement)
                block = Block(body=[sxpression_stmt])
                func_def = FuncDef(body=block)
                generator = ASTStubGenerator()
                result = generator._get_func_docstring(func_def)
                assert func_def.body.body is not None, "Expected not None, got %s" % func_def.body.body
                print("Test 2 passed.")

                print("# Test 3")
                statement = StrExpr("I don't know what to write here.")
                sxpression_stmt = ExpressionStmt(statement)
                block = Block(body=[sxpression_stmt])
                func_def = FuncDef(body=block)
                generator = ASTStubGenerator()
                result = generator._get_func_docstring(func_def)
                expr = func_def.body.body[0]
                assert result == expr.expr.value, "Expected %s, got %s" % (expr.expr.value, result)
                print("Test 3 passed.")

                print("# Test 4")
                statement = Statement("I don't know what to write here.")
                sxpression_stmt = ExpressionStmt(statement)
                block = Block(body=[sxpression_stmt])
                func_def = FuncDef(body=block)
                generator = ASTStubGenerator()
                result = generator._get_func_docstring(func_def)
                assert result is None, "Expected None, got %s" % result
                print("Test 4 passed.")

                print("# Test 5")
                statement = Statement("I don't know what to write here.")
                block = Block(body=[statement])
                func_def = FuncDef(body=block)
                generator = ASTStubGenerator()
                result = generator._get_func_docstring(func_def)
                assert result is None, "Expected None, got %s" % result
                print("Test 5 passed.")

                print("\nAll tests passed.\n") 
                print("Coverage results:\n")
                print_get_func_docstring()
            finally:
                sys.stdout = original_stdout
