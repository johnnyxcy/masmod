def mask_self_attr(attr_name: str) -> str:
    """重命名 self 的 属性"""
    return f"self__{attr_name}"


def mask_variable(variable_name: str) -> str:
    return f"{variable_name}_"