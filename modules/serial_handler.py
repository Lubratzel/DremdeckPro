# modules/serial_handler.py
import time
import serial
import serial.tools.list_ports


class SerialHandler:
    def __init__(self, baud_rate: int = 115200, timeout: float = 0.5):
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.ser: serial.Serial | None = None
        self.device: str | None = None

    @property
    def is_connected(self) -> bool:
        return self.ser is not None and self.ser.is_open

    def disconnect(self) -> None:
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
        finally:
            self.ser = None
            self.device = None

    def scan_and_connect(self) -> tuple[str, str] | None:
        """
        Sucht nach Pico, sendet GET_CONFIG und erwartet 'CONFIG:...'
        Returns: (device, config_line) oder None
        """
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            try:
                test_ser = serial.Serial(p.device, self.baud_rate, timeout=self.timeout)
                time.sleep(0.5)
                test_ser.write(b"GET_CONFIG\n")
                res = test_ser.readline().decode(errors="ignore").strip()

                if res.startswith("CONFIG:"):
                    self.ser = test_ser
                    self.device = p.device
                    return (p.device, res)

                test_ser.close()
            except Exception:
                continue
        return None

    def send(self, cmd: str, idx: int | None, val) -> None:
        if not self.is_connected:
            return
        try:
            # idx kann bei globalen Befehlen auch 0 oder -1 sein – du nutzt aktuell selected_idx
            if idx is None:
                idx = 0
            self.ser.write(f"{cmd}:{idx}:{val}\n".encode())
        except Exception:
            # optional: disconnect bei Fehler
            pass
