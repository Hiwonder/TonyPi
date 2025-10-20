#!/usr/bin/env python3
# encoding: utf-8
# @Author: Aiden
# @Date: 2024/09/21
import time
import smbus
from hiwonder.display import TM1640
from hiwonder.number_model import render_number


class AHT10:
    CONFIG = [0x08, 0x00]
    MEASURE = [0x33, 0x00]

    def __init__(self, bus=1, addr=0x38):
        self.bus = smbus.SMBus(bus)
        self.addr = addr
        time.sleep(0.2) 

    def getData(self):
        byte = self.bus.read_byte(self.addr)
        self.bus.write_i2c_block_data(self.addr, 0xAC, self.MEASURE)
        time.sleep(0.5)
        data = self.bus.read_i2c_block_data(self.addr, 0x00)
        temp = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
        ctemp = ((temp*200) / 1048576) - 50
        hum = ((data[1] << 16) | (data[2] << 8) | data[3]) >> 4
        chum = int(hum * 100 / 1048576)
        
        return (ctemp, chum)


if __name__ == '__main__':
    aht10 = AHT10()
    display = TM1640(dio=22, clk=24)
    display.clear()
    while True:
        # 提取温度
        tempture = str(round(aht10.getData()[0], 1))

        # 提取出三个数字
        num1, num2, num3 = tempture[0], tempture[1], tempture[3]

        display.display_buf = render_number(num1, num2, ".", num3)
        display.update_display()

        time.sleep(2)

        #提取湿度
        humidity = str(round(aht10.getData()[1], 1))

        # 提取出两个数字
        num1, num2 = humidity[0], humidity[1]

        display.display_buf = render_number(num1, num2, "%", "%")
        
        time.sleep(2)
