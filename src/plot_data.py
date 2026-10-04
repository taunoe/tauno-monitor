import math
import re
from collections import deque


class SerialPlotData:
    MAX_SAMPLES = 500
    MAX_LINE_BYTES = 256
    MAX_SERIES = 16
    SEPARATORS = (ord(','), ord('\n'), ord('\r'), ord(';'))
    READING_PATTERN = re.compile(
        r'^\s*(?P<label>.+?)(?:\s*[:=]\s*|\s+)'
        r'(?P<value>[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*$'
    )

    def __init__(self):
        self.series = {}
        self._reading = bytearray()
        self._discarding_reading = False

    def feed(self, data):
        updated = False
        for byte in data:
            if byte in self.SEPARATORS:
                if self._reading and not self._discarding_reading:
                    updated = self._append_reading() or updated
                self._reading.clear()
                self._discarding_reading = False
            elif not self._discarding_reading:
                if len(self._reading) >= self.MAX_LINE_BYTES:
                    self._reading.clear()
                    self._discarding_reading = True
                else:
                    self._reading.append(byte)
        return updated

    def _append_reading(self):
        try:
            reading = self._reading.decode('utf-8').strip()
        except UnicodeDecodeError:
            return False

        match = self.READING_PATTERN.fullmatch(reading)
        if match is None:
            return False

        label = match.group('label').strip()
        try:
            value = float(match.group('value'))
        except ValueError:
            return False

        if not label or not math.isfinite(value):
            return False
        if label not in self.series:
            if len(self.series) >= self.MAX_SERIES:
                return False
            self.series[label] = deque(maxlen=self.MAX_SAMPLES)
        self.series[label].append(value)
        return True

    def clear(self):
        self.series.clear()
        self._reading.clear()
        self._discarding_reading = False
