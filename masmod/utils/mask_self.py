def mask_self_attr(attr_name: str) -> str:
    """重命名 self 的 属性"""
    return f"__self__{attr_name}"
