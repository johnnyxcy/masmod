# _*_ coding: utf-8 _*_
############################################################
# File: masmod/masmod/translator/__init__.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 11/30/2022 09:13 am
#
# Last Modified: 12/06/2022 04:31 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################

from masmod.translator.cc_trans import CCTranslator
from masmod.translator.sympy_ast_trans import ASTSympyTranslator

__all__ = ["CCTranslator", "ASTSympyTranslator"]