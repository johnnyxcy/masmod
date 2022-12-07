# _*_ coding: utf-8 _*_
############################################################
# File: masmod/masmod/compiler/cc_compile.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 12/06/2022 04:47 pm
#
# Last Modified: 12/07/2022 01:28 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################
import pathlib
import platform
import tempfile
import subprocess
import typing
import dataclasses

from ..utils.nanoid import generate_nanoid


@dataclasses.dataclass
class CompileResult:
    target_file: pathlib.Path


CompilerToolchain = typing.Literal["gcc", "clang"]


class CCCompiler:

    def __init__(self, cc_source_code: str, temp_dir: pathlib.Path | None = None, uid: str | None = None) -> None:
        if temp_dir is None:
            temp_dir = pathlib.Path(tempfile.gettempdir())
        self._temp_dir = temp_dir
        self._source_code = cc_source_code

        if uid is None:
            uid = generate_nanoid()
        temp_file_cc = self._temp_dir.joinpath(f"{uid}.cc")

        with open(temp_file_cc, mode="w", encoding="utf-8") as f:
            f.write(cc_source_code)

        self._uid = uid
        self.temp_file_cc = temp_file_cc

        _toolchain: CompilerToolchain
        self.platform_system = platform.system()
        if self.platform_system == "Windows":
            # detect g++
            _toolchain = "gcc"
        elif self.platform_system == "Darwin":
            # detect clang
            _toolchain = "clang"
        else:
            raise NotImplementedError("Not Supported platform: {0}".format(self.platform_system))

        self.toolchain = _toolchain

        self._SRC_ROOT = pathlib.Path(__file__).parent.parent.parent.resolve()
        self._EIGEN_ROOT = self._SRC_ROOT.joinpath("vendor/eigen-3.4.0")

    def compile(self) -> CompileResult:
        obj_path = self._do_build_obj()
        dylib_path = self._do_build_dylib(obj_path)

        return CompileResult(target_file=dylib_path)

    def _do_build_obj(self) -> pathlib.Path:
        temp_file_obj = self._temp_dir.joinpath(f"{self._uid}.o")
        flags = [
            "-std=c++17",
            f"-I{self._SRC_ROOT.as_posix()}",
            f"-I{self._EIGEN_ROOT.as_posix()}",
            f"-c {self.temp_file_cc.as_posix()}",
            f"-o {temp_file_obj.as_posix()}",
        ]
        if self.toolchain == "gcc":
            self._exec(f"g++ {' '.join(flags)}")
        elif self.toolchain == "clang":
            self._exec(f"clang++ {' '.join(flags)}")
        else:
            raise NotImplementedError("不支持的 toolchain")

        return temp_file_obj

    def _do_build_dylib(self, obj_path: pathlib.Path) -> pathlib.Path:
        suffix: str
        if self.platform_system == "Windows":
            suffix = "dll"
        elif self.platform_system == "Darwin":
            suffix = "so"
        else:
            raise NotImplementedError
        temp_file_dylib = self._temp_dir.joinpath(f"{self._uid}.{suffix}")
        flags = [
            f"{obj_path.as_posix()}",
            "-shared",
            "-fPIC",
            f"-o {temp_file_dylib.as_posix()}",
        ]
        if self.toolchain == "gcc":
            self._exec(f"g++ {' '.join(flags)}")
        elif self.toolchain == "clang":
            self._exec(f"clang++ {' '.join(flags)}")
        else:
            raise NotImplementedError("不支持的 toolchain")

        return temp_file_dylib

    def _exec(self, cmd: str) -> str:
        try:
            output = subprocess.check_output(cmd, shell=True, encoding="utf-8")
        except Exception as e:
            raise RuntimeError(f"命令执行失败 \n $ {cmd}") from e

        return output
