def format_port_label(port):
    """Return a port label that pairs its device path with its product name."""
    device = port.device
    product = getattr(port, "product", None)
    if product:
        product = product.strip()
        if product:
            return f"{device}\n{product}"

    description = getattr(port, "description", None)
    if description:
        description = description.strip()
        if description and description.casefold() != device.casefold():
            return f"{device}\n{description}"

    return device
