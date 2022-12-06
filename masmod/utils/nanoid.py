# _*_ coding: utf-8 _*_
############################################################
# File: masmod/masmod/utils/nanoid.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 11/29/2022 09:19 am
#
# Last Modified: 12/06/2022 04:32 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################

from __future__ import division, unicode_literals

import math
import os

DEFAULT_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
DEFAULT_SIZE = 8


def _do_generate(random_bytes: int) -> bytearray:
    return bytearray(os.urandom(random_bytes))


def generate_nanoid(size: int = DEFAULT_SIZE) -> str:
    """生成短 uuid

    Args:
        size (int, optional): 生成 nanoid 的长度. Defaults to DEFAULT_SIZE.

    Returns:
        str
    """
    alphabet = DEFAULT_ALPHABET
    alphabet_len = len(alphabet)

    mask = 1
    if alphabet_len > 1:
        mask = (2 << int(math.log(alphabet_len - 1) / math.log(2))) - 1
    step = int(math.ceil(1.6 * mask * size / alphabet_len))

    id: str = ""

    while True:
        random_bytes = _do_generate(step)

        for i in range(step):
            random_byte = random_bytes[i] & mask
            if random_byte < alphabet_len:
                if alphabet[random_byte]:
                    id += alphabet[random_byte]

                    if len(id) == size:
                        return id
