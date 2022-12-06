# _*_ coding: utf-8 _*_
############################################################
# File: masmod/masmod/utils/mask.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 11/30/2022 11:26 am
#
# Last Modified: 12/06/2022 04:32 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################


def mask_self_attr(attr_name: str) -> str:
    """重命名 self 的 属性"""
    return f"self__{attr_name}"


def mask_variable(variable_name: str) -> str:
    return f"{variable_name}_"