from machine import I2C
import time

class BMP180:
    def __init__(self, i2c, addr=0x77):
        self.i2c = i2c
        self.addr = addr
        self._load_calibration()

    def _read16(self, reg):
        data = self.i2c.readfrom_mem(self.addr, reg, 2)
        return (data[0] << 8) + data[1]

    def _readS16(self, reg):
        val = self._read16(reg)
        if val > 32767:
            val -= 65536
        return val

    def _write8(self, reg, val):
        self.i2c.writeto_mem(self.addr, reg, bytes([val]))

    def _read8(self, reg):
        return self.i2c.readfrom_mem(self.addr, reg, 1)[0]

    def _load_calibration(self):
        self.AC1 = self._readS16(0xAA)
        self.AC2 = self._readS16(0xAC)
        self.AC3 = self._readS16(0xAE)
        self.AC4 = self._read16(0xB0)
        self.AC5 = self._read16(0xB2)
        self.AC6 = self._read16(0xB4)
        self.B1  = self._readS16(0xB6)
        self.B2  = self._readS16(0xB8)
        self.MB  = self._readS16(0xBA)
        self.MC  = self._readS16(0xBC)
        self.MD  = self._readS16(0xBE)

    def _read_raw_temp(self):
        self._write8(0xF4, 0x2E)
        time.sleep_ms(5)
        return self._read16(0xF6)

    def _read_raw_pressure(self):
        self._write8(0xF4, 0x34)
        time.sleep_ms(8)
        msb = self._read8(0xF6)
        lsb = self._read8(0xF7)
        xlsb = self._read8(0xF8)
        return ((msb << 16) + (lsb << 8) + xlsb) >> 8

    @property
    def temperature(self):
        UT = self._read_raw_temp()

        X1 = ((UT - self.AC6) * self.AC5) >> 15
        X2 = (self.MC << 11) // (X1 + self.MD)
        B5 = X1 + X2

        temp = (B5 + 8) >> 4
        return temp / 10.0

    @property
    def pressure(self):
        UT = self._read_raw_temp()
        UP = self._read_raw_pressure()

        X1 = ((UT - self.AC6) * self.AC5) >> 15
        X2 = (self.MC << 11) // (X1 + self.MD)
        B5 = X1 + X2

        B6 = B5 - 4000
        X1 = (self.B2 * (B6 * B6 >> 12)) >> 11
        X2 = (self.AC2 * B6) >> 11
        X3 = X1 + X2

        B3 = (((self.AC1 * 4 + X3) << 0) + 2) >> 2
        X1 = (self.AC3 * B6) >> 13
        X2 = (self.B1 * (B6 * B6 >> 12)) >> 16
        X3 = ((X1 + X2) + 2) >> 2

        B4 = (self.AC4 * (X3 + 32768)) >> 15
        B7 = (UP - B3) * 50000

        if B7 < 0x80000000:
            p = (B7 << 1) // B4
        else:
            p = (B7 // B4) << 1

        X1 = (p >> 8) * (p >> 8)
        X1 = (X1 * 3038) >> 16
        X2 = (-7357 * p) >> 16

        p = p + ((X1 + X2 + 3791) >> 4)

        return p  # Pa