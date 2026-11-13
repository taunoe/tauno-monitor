import errno


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


def lookup_usb_names(vid, pid, usb_db):
    """Return (vendor name, product name) for hexadecimal VID/PID strings.

    pyserial reports IDs in upper case while the bundled database uses
    lower-case keys, so the lookup is case-insensitive. Unknown entries
    are returned as None.
    """
    vendor = usb_db.get(vid.strip().lower(), {})
    vendor_name = vendor.get("name")
    product_name = vendor.get("products", {}).get(pid.strip().lower())
    return (
        vendor_name.strip() if vendor_name else None,
        product_name.strip() if product_name else None,
    )


def describe_open_error(port, error):
    """Return a short, user-facing reason why a serial port did not open."""
    code = getattr(error, "errno", None)
    if code == errno.EACCES:
        return f"No permission to open {port}. See Guide in the menu."
    if code == errno.ENOENT:
        return f"{port} not found. Is the device connected?"
    if code == errno.EBUSY:
        return f"{port} is in use by another program"
    return f"Could not open {port}: {error}"
