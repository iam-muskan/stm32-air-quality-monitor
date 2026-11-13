# STM32 Air Quality Monitor

Measures temperature, humidity, gas and dust and raises an alert when a reading passes a safety threshold. The firmware targets an STM32F103C8T6 (Blue Pill). The Python files are separate simulation and test programs you can run on a computer without the board.

## Files
- main.c - STM32 firmware. Pins in its header: DHT22 on PA1, MQ-135 on PA0, MQ-7 on PA2, GP2Y1010 dust sensor on PA4 (LED on PA3), SSD1306 OLED on PB6 and PB7, buzzer on PA8, LEDs on PA9 and PA10.
- final_code.ino - Arduino-style version with a DHT22, MQ-135, GP2Y1010 dust sensor and a 16x2 LCD. Serial output at 115200 baud.
- sketch_oct25a.ino - small test sketch for the DHT22 and an SSD1306 OLED. The .bin, .elf, .hex and .map files with the same name are its compiled output.
- pythonmpp.py - Python simulation of sensor readings and control logic.
- codestruc2.py - Python console program: type in sensor values and it shows them and triggers an alert past the thresholds.
- main.c.xlsx - a spreadsheet copy of main.c.

## Notes
- main.c and final_code.ino are different versions with different sensor sets (main.c has the MQ-7; final_code.ino does not).
