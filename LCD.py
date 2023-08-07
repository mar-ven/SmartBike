# LCD
# Created at 2021-05-06 07:11:45.689767

import i2c
import streams
streams.serial()

#commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00

# flags for backlight control
LCD_BACKLIGHT = 0x08
LCD_NOBACKLIGHT = 0x00

En = 0b00000100 # Enable bit
Rw = 0b00000010 #Read/Write bit
Rs = 0b00000001 #Register select bit

class LCD:
    _backlightval=LCD_NOBACKLIGHT
    _displaymode=LCD_4BITMODE
    _displayfunction=LCD_DISPLAYON
    _displaycontrol=LCD_DISPLAYON
    
    def __init__(self, addr, cols, rows, port, autobegin = True):
        self._addr = addr
        self._cols = cols
        self._rows = rows
        self._backlightval = LCD_NOBACKLIGHT
        self.init(i2c.I2C(port, addr), autobegin)
        
    def init(self, port, autobegin):
        self._port = port
        self._displayfunction = LCD_4BITMODE | LCD_1LINE | LCD_5x8DOTS
        self._port.start()
        if autobegin:
            self.begin(16, 2, 1)
        
    def begin(self, cols, lines, dotsize):
        if lines > 1:
            self._displayfunction |= LCD_2LINE
        self._numlines = lines
        if (dotsize != 0 and lines == 1):
            self._displayfunction |= LCD_5x10DOTS
        sleep(50)
        self.expanderWrite(self._backlightval)
        sleep(1)
        self.write4bits(0x03 << 4)
        # we start in 8bit mode, try to set 4 bit mode
        self.write4bits(0x03 << 4);
        sleep(5) #wait min 4.1ms
           
        # second try
        self.write4bits(0x03 << 4);
        sleep(5) #wait min 4.1ms
        # third go!
        self.write4bits(0x03 << 4); 
        sleep(1);
           
        #finally, set to 4-bit interface
        self.write4bits(0x02 << 4); 
        self.command(LCD_FUNCTIONSET | self._displayfunction)
        self._displaycontrol = LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF
        self.display()
        self.clear()
        self._displaymode = LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT
        self.command(LCD_ENTRYMODESET | self._displaymode)
        self.home()
    
    def clear(self):
        self.command(LCD_CLEARDISPLAY)
        sleep(2)
    
    def home(self):
        self.command(LCD_RETURNHOME)
        sleep(2)
    
    def setCursor(self, col, row):
        self.row_offsets = [0x00, 0x40, 0x14, 0x54]
        if row > self._numlines:
            row = self._numlines - 1
        self.command(LCD_SETDDRAMADDR | (col + self.row_offsets[row]))
    
    def noDisplay(self):
        self._displaycontrol &= ~LCD_DISPLAYON
        self.command(LCD_DISPLAYCONTROL | self._displaycontrol)
    
    def display(self):
        self._displaycontrol |= LCD_DISPLAYON
        self.command(LCD_DISPLAYCONTROL | self._displaycontrol)
        
    def noCursor(self):
        self._displaycontrol &= ~LCD_CURSORON
        self.command(LCD_DISPLAYCONTROL | self._displaycontrol)
    
    def cursor(self):
        self._displaycontrol |= LCD_CURSORON
        self.command(LCD_DISPLAYCONTROL | self._displaycontrol)
    
    def noBlink(self):
        self._displaycontrol &= ~LCD_BLINKON
        self.command(LCD_DISPLAYCONTROL | self._displaycontrol)
    
    def blink(self):
        self._displaycontrol |= LCD_BLINKON
        self.command(LCD_DISPLAYCONTROL | self._displaycontrol)
        
    def scrollDisplayLeft(self):
        self.command(LCD_CURSORSHIFT | LCD_DISPLAYMOVE | LCD_MOVELEFT)
    
    def scrollDisplayRight(self):
        self.command(LCD_CURSORSHIFT | LCD_DISPLAYMOVE | LCD_MOVERIGHT)
        
    def leftToRight(self):
        self._displaymode |= LCD_ENTRYLEFT
        self.command(LCD_ENTRYMODESET | self._displaymode)

    def rightToLeft(self):
        self._displaymode &= ~LCD_ENTRYLEFT
        self.command(LCD_ENTRYMODESET | self._displaymode)

    def autoscroll(self):
        self._displaymode |= LCD_ENTRYSHIFTINCREMENT
        self.command(LCD_ENTRYMODESET | self._displaymode)

    def noAutoscroll(self):
        self._displaymode &= ~LCD_ENTRYSHIFTINCREMENT
        self.command(LCD_ENTRYMODESET | self._displaymode)
    
    def createchar(self, location, charmap):
        self.location &= 0x7  
        self.command(LCD_SETCGRAMADDR | (self.location << 3))
        for i in range(0, 8):
            self.write(charmap[i])
    
    def write(self, value):
        self.send(value, Rs)
        return 1
    
    def noBacklight(self):
        self._backlightval = LCD_NOBACKLIGHT
        self.expanderWrite(0)
    
    def backlight(self):
        self._backlightval = LCD_BACKLIGHT
        self.expanderWrite(0)
    
    def command(self, value):
        self.send(value, 0)
    
    def send(self, value, mode):
        self.highnib = value & 0xf0
        self.lownib = (value << 4) & 0xf0
        self.write4bits((self.highnib) | mode)
        self.write4bits((self.lownib) | mode)
    
    def write4bits(self, value):
        self.expanderWrite(value)
        self.pulseEnable(value)
    
    def expanderWrite(self, _data):
        self._port.write([int(_data | self._backlightval)])
    
    def pulseEnable(self, _data):
        self.expanderWrite(_data | En)
        sleep(1)
        self.expanderWrite( _data & ~En)
        sleep(1)
    
    def cursor_on(self):
        self.cursor()
        
    def cursor_off(self):
        self.noCursor()
    
    def blink_on(self):
        self.blink()
    
    def blink_off(self):
        self.noBlink()
    
    def load_custom_character(self, char_num, rows):
        self.create_char(char_num, rows)
    
    def setBacklight(self, new_val):
        if new_val:
            self.backlight()
        else:
            self.noBacklight()

    def printString(self, str):
        for character in str:
            self.write(ord(character))
    
    def stop(self):
        self._port.stop()