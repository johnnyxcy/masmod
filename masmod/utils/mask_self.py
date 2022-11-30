def mask_self_attr(attr_name: str) -> str:
    """重命名 self 的 属性"""
    return f"__self__{attr_name}"


def mask_self_get_data(col_name: str) -> str:
    if col_name.find(" ") != -1:
        raise ValueError("不允许包含空格的列名")
    return f"{mask_self_attr('get_data')}__{col_name}"