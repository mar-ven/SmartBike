import i2c
import streams
import math
streams.serial()

MPU6050_ADDRESS_AD0_LOW = 0x68
MPU6050_ADDRESS_AD0_HIGH = 0x69
MPU6050_DEFAULT_ADDRESS = MPU6050_ADDRESS_AD0_LOW
MPU6050_RA_XG_OFFS_TC = 0x00
MPU6050_RA_YG_OFFS_TC = 0x01
MPU6050_RA_ZG_OFFS_TC = 0x02
MPU6050_RA_X_FINE_GAIN = 0x03 
MPU6050_RA_Y_FINE_GAIN = 0x04   
MPU6050_RA_Z_FINE_GAIN = 0x05
MPU6050_RA_XA_OFFS_H    =    0x06 
MPU6050_RA_XA_OFFS_L_TC  =   0x07
MPU6050_RA_YA_OFFS_H     =  0x08 
MPU6050_RA_YA_OFFS_L_TC  =   0x09
MPU6050_RA_ZA_OFFS_H     =   0x0A
MPU6050_RA_ZA_OFFS_L_TC  =   0x0B
MPU6050_RA_SELF_TEST_X    =  0x0D
MPU6050_RA_SELF_TEST_Y   =   0x0E
MPU6050_RA_SELF_TEST_Z   =   0x0F
MPU6050_RA_SELF_TEST_A   =   0x10
GRAVITIY_MS2 = 9.80665



# dictionary of accel full-scale ranges
accel_fullscale = {
    '2': 0,
    '4': 1,
    '8': 2,
    '16': 3
}

# Scale Modifiers
ACCEL_SENSITIVITY_2G = 16384.0
ACCEL_SENSITIVITY_4G = 8192.0
ACCEL_SENSITIVITY_8G = 4096.0
ACCEL_SENSITIVITY_16G = 2048.0

# list of accel sensitivity
accel_sensitivity = [
    ACCEL_SENSITIVITY_2G,
    ACCEL_SENSITIVITY_4G,
    ACCEL_SENSITIVITY_8G,
    ACCEL_SENSITIVITY_16G
]

# dictionary of gyro full-scale ranges
gyro_fullscale = {
    '250': 0,
    '500': 1,
    '1000': 2,
    '2000': 3
}

GYRO_SENSITIVITY_250DPS = 131.0
GYRO_SENSITIVITY_500DPS = 65.5
GYRO_SENSITIVITY_1000DPS = 32.8
GYRO_SENSITIVITY_2000DPS = 16.4
# list of gyro sensitivity
gyro_sensitivity = [
    GYRO_SENSITIVITY_250DPS,
    GYRO_SENSITIVITY_500DPS,
    GYRO_SENSITIVITY_1000DPS,
    GYRO_SENSITIVITY_2000DPS
]

class ACCEL:
    def __init__(self, I2Cname, address = 0x68):
        self.port = i2c.I2C(I2Cname, address)
        self.port.start()
        self.setClockSource()
        self.setFullScaleGyroRange(250)
        self.setFullScaleAccelRange(16)
        
        self.set_dlpf_mode(0)
        
        self.set_sleep_mode(False)
        
    def setClockSource(self):
        self.port.write(0x6B)
        self.port.write(0x00)
        value = self.port.write_read(0x6B, n=1)[0]
        value &= 0b11111000
        value |=  1
        self.port.write_bytes(0x6B, value)
    
    def setFullScaleGyroRange(self, full_scale):
        self.port.write_bytes(0x1B, 0x00)
        full_scale = gyro_fullscale[str(full_scale)]
        value = self.port.write_read(0x1B, n=1)[0]
        value &= 0b11100111
        value |= (full_scale << 3)
        self.port.write_bytes(0x1B, value)
    
    def  setFullScaleAccelRange(self, full_scale):
        self.port.write_bytes(0x1C, 0x00)
        full_scale = accel_fullscale[str(full_scale)]
        value = self.port.write_read(0x1C, n=1)[0]
        value &= 0b11100111
        value |= (2 << 3)
        self.port.write_bytes(0x1C, value)
     
    def set_dlpf_mode(self, dlpf):
        value = self.port.write_read(0x1A, n=1)[0]
        value &= 0b11111000
        value |= dlpf
        self.port.write_bytes(0x1A, value)
        
    def set_sleep_mode(self, state):
        value = self.port.write_read(0x6B, n=1)[0]
        if (state):
            value |= (1 << 6)
        else: 
            value &= ~(1 << 6)
        self.port.write_bytes(0x6B, value)
    
    def _tc(self, v, n_bit=16):
        mask = 2**(n_bit - 1)
        return -(v & mask) + (v & ~mask)
    
    def get_accel_fullscale(self):
        # Get the raw value
        raw_data = self.port.write_read(0x1C, n=1)[0]
        raw_data &= 0b00011000
        raw_data >>= 3
    
        # get accel full-scale
        values = ['2', '4', '8', '16']
        for i in range(4):
            if (raw_data == accel_fullscale[values[i]]):
                return values[i]
        return -1
     
    def getTemperature(self):
        temp = self.port.write_read(0x41, 2)
        return (self._tc((temp[0] << 8) | temp[1]) /340 ) + 36.53
       
    def get_accel_values(self, g = False):
    
        
        data = self.port.write_read(0x3B, n=6)
        x = self._tc(data[0] << 8 | data[1]) 
        y = self._tc(data[2] << 8 | data[3]) 
        z = self._tc(data[4] << 8 | data[5]) 
    
        full_scale = self.get_accel_fullscale()
    
        
        accel_sensitivity = ACCEL_SENSITIVITY_2G
    
        
        values = ['2', '4', '8', '16']
        for i in range(len(values)):
            if (full_scale == accel_fullscale[values[i]]):
                accel_sensitivity = accel_sensitivity[i]
    
        x = x / accel_sensitivity
        y = y / accel_sensitivity
        z = z / accel_sensitivity
    
        if g is True:
            return (x, y, z)
        elif g is False:
            x = x * GRAVITIY_MS2
            y = y * GRAVITIY_MS2
            z = z * GRAVITIY_MS2
            return (x, y, z)
