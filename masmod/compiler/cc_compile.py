# _*_ coding: utf-8 _*_
############################################################
# File: masmod/masmod/compiler/cc_compile.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 12/06/2022 04:47 pm
#
# Last Modified: 12/06/2022 05:07 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################
import pathlib
import subprocess
import typing
import dataclasses

from ..utils.nanoid import generate_nanoid


@dataclasses.dataclass
class CompileResult:
    target_file: pathlib.Path


class CCCompiler:

    def __init__(self, cc_source_code: str) -> None:
        self._source_code = cc_source_code
        self._uid = generate_nanoid()

    def compile(self, target: typing.Literal["dylib", "pyd"]) -> CompileResult:
        if target == "pyd":
            raise NotImplementedError("Compile as pyd is not Supported yet")

        elif target == "dylib":
            return CompileResult(target_file=self._do_compile_dylib())

        else:
            raise NotImplementedError("Unknown target {0}".format(target))

    def _do_compile_dylib(self) -> pathlib.Path:
        pass
