"""Simulated stand-ins for two benchtop VNAs.

Neither class talks to an instrument: each prints the SCPI command a real
driver would send and returns a fixed five-point S21 trace in dB.
"""

import time

from prototypes.base_instrument import AbstractVNA


class SimulatedKeysightVNA(AbstractVNA):
    """Simulated Keysight E5080B: no instrument I/O, fixed trace."""

    def connect(self) -> bool:
        print(f"[DRV-KEYSIGHT] Opening VISA session to {self.resource_address}")
        self.is_connected = True
        return True

    def set_if_bandwidth(self, bandwidth_hz: int) -> None:
        if not self.is_connected:
            raise ConnectionError("Instrument session is not open.")
        print(f"[DRV-KEYSIGHT] Transmitting SCPI: SENS:BAND {bandwidth_hz}")

    def capture_s21_trace(self) -> list:
        print("[DRV-KEYSIGHT] Querying: CALC:DATA? SDATA (Executing Sweep...)")
        time.sleep(0.05)
        return [-0.5, -1.2, -2.1, -3.4, -4.8]


class SimulatedAnritsuVNA(AbstractVNA):
    """Simulated Anritsu VectorStar: no instrument I/O, fixed trace."""

    def connect(self) -> bool:
        print(
            f"[DRV-ANRITSU] Initializing TCP/IP Socket interface to {self.resource_address}"
        )
        self.is_connected = True
        return True

    def set_if_bandwidth(self, bandwidth_hz: int) -> None:
        if not self.is_connected:
            raise ConnectionError("Instrument session is not open.")
        print(f"[DRV-ANRITSU] Transmitting SCPI: SENS:CH1:IFBW {bandwidth_hz}")

    def capture_s21_trace(self) -> list:
        print("[DRV-ANRITSU] Querying: TRAC:DATA? 1 (Executing Wave Sweep...)")
        time.sleep(0.05)
        return [-0.4, -1.1, -1.9, -3.2, -4.5]
