import ast
import typing

from masmod.symbols import GlobalContext
from masmod.functional import exp


class HppTranslator:

    def __init__(self, source_code: str, global_context: GlobalContext) -> None:
        self._source_code_lines = source_code.splitlines()
        self._global_context = global_context.as_dict()

    def translate(self, statements: typing.List[ast.stmt]) -> str:
        return ""

    def translate_statement(self, statement: ast.stmt) -> typing.List[str]:
        translated: typing.List[str] = []
        translated.append(f"// {self._source_code_lines[statement.lineno].strip()}")

        if isinstance(statement, ast.Assign):
            translated.extend(self.translate_assign(statement))
        else:
            raise NotImplementedError()
        return translated

    def translate_assign(self, assign: ast.Assign) -> typing.List[str]:
        translated: typing.List[str] = []
        targets = assign.targets

        if len(targets) != 1:
            raise ValueError()

        target = self.translate_expr(targets[0])
        value = self.translate_expr(assign.value)
        translated.append(f"{target} = {value};")
        return translated

    def translate_expr(self, expr: ast.expr) -> str:
        if isinstance(expr, ast.Name):
            return expr.id

        if isinstance(expr, ast.Attribute):
            value = self.translate_expr(expr.value)
            return f"{value}.{expr.attr}"

        if isinstance(expr, ast.Call):
            func = self.translate_expr(expr.func)
            if func == "exp":
                pass
            else:
                func_obj = eval(func, self._global_context, {})
                if id(func_obj) == id(exp):
                    pass
            # if func == "exp" or func

        raise NotImplementedError()
