import re


def strip_ansi_escape_codes(text):
    """Remove ANSI SGR sequences before text is written to a log."""
    return re.sub(r'\x1b\[[0-9;]*m', '', text)


def encode_tx_data(data, data_format):
    """Encode TX entry text as bytes using the selected representation."""
    if data_format == 'ASCII':
        return data.encode('utf-8')

    if data_format == 'HEX':
        compact = re.sub(r'[\s,]+', '', re.sub(r'0[xX]', '', data))
        if len(compact) % 2 or re.fullmatch(r'[0-9a-fA-F]*', compact) is None:
            raise ValueError("Enter hexadecimal bytes, for example: 48 65 6c 6c 6f")
        return bytes.fromhex(compact)

    if data_format == 'BIN':
        tokens = re.split(r'[\s,]+', data.strip()) if data.strip() else []
        bits = ''.join(tokens)
        if not bits:
            return b''
        if re.fullmatch(r'[01]+', bits) is None or len(bits) % 8:
            raise ValueError("Enter binary data in complete 8-bit bytes")
        return bytes(int(bits[index:index + 8], 2) for index in range(0, len(bits), 8))

    bases = {'DEC': 10, 'OCT': 8}
    if data_format not in bases:
        raise ValueError(f"Unsupported TX data format: {data_format}")

    tokens = re.split(r'[\s,]+', data.strip()) if data.strip() else []
    values = []
    for token in tokens:
        try:
            value = int(token, bases[data_format])
        except ValueError as error:
            raise ValueError(f"Invalid {data_format} byte: {token}") from error
        if not 0 <= value <= 255:
            raise ValueError(f"{data_format} byte must be between 0 and 255: {token}")
        values.append(value)
    return bytes(values)


def tx_line_ending(index):
    return {
        0: '\n',
        1: '\r',
        2: '\r\n',
        3: ';',
    }.get(index, '')
