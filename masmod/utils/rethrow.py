import typing
import ast


def locatable(token: ast.AST) -> bool:
    return hasattr(token, "lineno") and token.lineno is not None


def rethrow(source_code: str, token: ast.AST, error: BaseException) -> typing.NoReturn:
    if locatable(token):
        lineno = token.lineno
        col_offset = token.col_offset

        orig_code = source_code.splitlines()[lineno - 1]
        indicator_line = [" "] * len(orig_code)
        indicator_line[col_offset - 1] = "^"

        syntax_error_summary = "\n" + orig_code + "\n" + "".join(indicator_line)
    else:
        syntax_error_summary = ast.unparse(token)

    raise SyntaxError(syntax_error_summary) from error