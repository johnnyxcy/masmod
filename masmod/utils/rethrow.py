# _*_ coding: utf-8 _*_
############################################################
# File: masmod/masmod/utils/rethrow.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 12/05/2022 04:19 pm
#
# Last Modified: 12/06/2022 04:32 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################

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