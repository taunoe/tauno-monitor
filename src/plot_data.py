import math
import re
from collections import deque


class SerialPlotData:
    MAX_SAMPLES = 800
    MAX_LINE_BYTES = 256
    MAX_SERIES = 16
    SEPARATORS = (ord(','), ord('\n'), ord('\r'), ord(';'))
    READING_PATTERN = re.compile(
        r'\s*(?P<label>.+?)(?:\s*[:=]\s*|\s+)'
        r'(?P<value>[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)(?=\s|$)'
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

        matches = list(self.READING_PATTERN.finditer(reading))
        if not matches:
            return False

        readings = []
        previous_end = 0
        for match in matches:
            if reading[previous_end:match.start()].strip():
                return False

            label = match.group('label').strip()
            try:
                value = float(match.group('value'))
            except ValueError:
                return False

            if not label or not math.isfinite(value):
                return False
            readings.append((label, value))
            previous_end = match.end()

        if reading[previous_end:].strip():
            return False

        updated = False
        for label, value in readings:
            if label not in self.series:
                if len(self.series) >= self.MAX_SERIES:
                    continue
                self.series[label] = deque(maxlen=self.MAX_SAMPLES)
            self.series[label].append(value)
            updated = True
        return updated

    def clear(self):
        self.series.clear()
        self._reading.clear()
        self._discarding_reading = False
