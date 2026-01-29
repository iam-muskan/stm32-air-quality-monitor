"""
Wearable Pollution Detector - Python Simulation
Simulates all sensor readings and control logic
Testing platform before ARM7/C implementation on STM32
"""

import time
import random
from datetime import datetime
from enum import Enum

# ============================================================================
# CONFIGURATION & THRESHOLDS
# ============================================================================

MQ135_THRESHOLD_ADC = 400
DUST_THRESHOLD_ADC = 300
TEMP_MIN, TEMP_MAX = 15.0, 40.0
HUM_MIN, HUM_MAX = 30.0, 80.0

# ADC Resolution: 12-bit (0-4095)
ADC_MAX = 4095
ADC_RESOLUTION = 12

# Sensor calibration baseline (ppm equivalent)
MQ135_BASELINE_ADC = 100  # Clean air reference

class SensorStatus(Enum):
    GOOD = 0
    WARNING = 1
    CRITICAL = 2

# ============================================================================
# SENSOR SIMULATION CLASSES
# ============================================================================

class MQ135_Sensor:
    """MQ-135 CO2/Gas sensor simulation"""
    
    def __init__(self, baseline=MQ135_BASELINE_ADC):
        self.baseline = baseline
        self.current_adc = baseline
        self.readings_history = []
        self.warmup_time = 0  # seconds
        self.is_warmed_up = False
        
    def warmup(self, duration=3600):
        """Simulate 1 hour warmup (use 10s for testing)"""
        self.warmup_time = duration
        self.is_warmed_up = True
        print(f"[MQ-135] Warming up for {duration}s...")
        
    def read_adc(self, pollution_level=0.5):
        """
        Read ADC value
        pollution_level: 0.0-1.0 (0=clean, 1=very polluted)
        """
        if not self.is_warmed_up:
            self.current_adc = self.baseline + random.randint(-10, 10)
        else:
            noise = random.randint(-15, 15)
            self.current_adc = int(self.baseline + (pollution_level * 600) + noise)
            self.current_adc = max(0, min(ADC_MAX, self.current_adc))
        
        self.readings_history.append(self.current_adc)
        return self.current_adc
    
    def get_status(self):
        """Return sensor status based on threshold"""
        if self.current_adc > MQ135_THRESHOLD_ADC:
            return SensorStatus.CRITICAL
        elif self.current_adc > MQ135_THRESHOLD_ADC * 0.7:
            return SensorStatus.WARNING
        return SensorStatus.GOOD
    
    def get_moving_average(self, window=5):
        """Calculate exponential moving average (EMA)"""
        if not self.readings_history:
            return self.baseline
        recent = self.readings_history[-window:]
        return sum(recent) / len(recent)


class GP2Y1010_DustSensor:
    """Sharp GP2Y1010 optical dust sensor simulation"""
    
    def __init__(self):
        self.current_adc = 0
        self.readings_history = []
        self.led_pulse_count = 0
        
    def pulse_led_and_read(self, dust_concentration=0.3):
        """
        Simulate LED pulse and analog read
        dust_concentration: 0.0-1.0 (0=clean, 1=very dusty)
        Formula: V_out = V_ref - (sensitivity * dust_density)
        """
        self.led_pulse_count += 1
        
        # Simulate pulse timing and ADC read
        noise = random.randint(-20, 20)
        self.current_adc = int((1 - dust_concentration) * ADC_MAX * 0.6 + noise)
        self.current_adc = max(0, min(ADC_MAX, self.current_adc))
        
        self.readings_history.append(self.current_adc)
        return self.current_adc
    
    def adc_to_dust_density(self, adc_value):
        """Convert ADC reading to dust density (µg/m³)"""
        # Simplified calibration formula
        voltage = (adc_value / ADC_MAX) * 5.0  # Convert to voltage
        dust_density = (voltage - 0.9) / 0.005  # Example coefficients
        return max(0, dust_density)
    
    def get_status(self):
        """Return dust sensor status"""
        if self.current_adc < DUST_THRESHOLD_ADC:
            return SensorStatus.CRITICAL
        elif self.current_adc < DUST_THRESHOLD_ADC * 1.5:
            return SensorStatus.WARNING
        return SensorStatus.GOOD


class DHT22_TempHumiditySensor:
    """DHT22 temperature and humidity sensor simulation"""
    
    def __init__(self):
        self.temperature = 25.0
        self.humidity = 50.0
        self.last_read_time = 0
        
    def read(self):
        """
        Read temperature and humidity
        DHT22 requires ~2 seconds between reads
        """
        time_since_last = time.time() - self.last_read_time
        if time_since_last < 2.0:
            return self.temperature, self.humidity
        
        # Simulate environmental changes
        self.temperature += random.uniform(-0.5, 0.5)
        self.humidity += random.uniform(-2, 2)
        
        # Clamp values
        self.temperature = max(TEMP_MIN, min(TEMP_MAX, self.temperature))
        self.humidity = max(HUM_MIN, min(HUM_MAX, self.humidity))
        
        self.last_read_time = time.time()
        return self.temperature, self.humidity


class OLED_Display:
    """SSD1306 OLED display simulation (0.96" 128x64)"""
    
    def __init__(self):
        self.frame_buffer = [[' ' for _ in range(16)] for _ in range(8)]
        self.update_count = 0
        
    def fill(self):
        """Clear display"""
        self.frame_buffer = [[' ' for _ in range(16)] for _ in range(8)]
        
    def puts(self, text, row=0):
        """Place text at row"""
        if row < 8:
            self.frame_buffer[row] = list(text[:16].ljust(16))
        
    def update_screen(self):
        """Refresh display"""
        self.update_count += 1
        
    def display(self):
        """Print current display state to console"""
        print("\n" + "="*20)
        print("    OLED Display")
        print("="*20)
        for row in self.frame_buffer:
            print("|" + "".join(row) + "|")
        print("="*20 + "\n")


class BuzzerLED:
    """Active buzzer and LED alert system simulation"""
    
    def __init__(self):
        self.buzzer_state = False
        self.red_led_state = False
        self.green_led_state = False
        self.alert_count = 0
        
    def activate_alert(self):
        """Turn on buzzer and red LED"""
        self.buzzer_state = True
        self.red_led_state = True
        self.green_led_state = False
        self.alert_count += 1
        print("[ALERT] 🔴 RED LED ON | 🔊 BUZZER ON")
        
    def deactivate_alert(self):
        """Turn off alert systems"""
        self.buzzer_state = False
        self.red_led_state = False
        self.green_led_state = True
        print("[OK] 🟢 GREEN LED ON | 🔇 BUZZER OFF")
        
    def status(self):
        """Return current status"""
        return {
            'buzzer': self.buzzer_state,
            'red_led': self.red_led_state,
            'green_led': self.green_led_state
        }


# ============================================================================
# MAIN POLLUTION DETECTOR SYSTEM
# ============================================================================

class PollutionDetector:
    """Main system controller"""
    
    def __init__(self):
        self.mq135 = MQ135_Sensor()
        self.dust_sensor = GP2Y1010_DustSensor()
        self.temp_humid = DHT22_TempHumiditySensor()
        self.oled = OLED_Display()
        self.alert = BuzzerLED()
        
        self.loop_count = 0
        self.system_time = 0
        self.start_time = time.time()
        
    def initialize(self):
        """Initialize system"""
        print("\n" + "="*50)
        print("  WEARABLE POLLUTION DETECTOR - INITIALIZING")
        print("="*50)
        print("[INIT] Checking power rails...")
        print("[INIT] ✓ 3.3V rail OK")
        print("[INIT] ✓ 5V rail OK")
        print("[INIT] ✓ Common ground OK")
        print("[INIT] Starting I2C scan for OLED...")
        print("[INIT] ✓ OLED found at 0x3C")
        print("[INIT] ✓ All sensors detected")
        print("[INIT] Warming up MQ-135 (simulated)...")
        self.mq135.warmup(duration=10)  # 10s for simulation
        print("[INIT] System initialized successfully!\n")
        
    def read_all_sensors(self, pollution_level=0.5, dust_level=0.3):
        """
        Read all sensor values
        pollution_level: simulated pollution (0-1)
        dust_level: simulated dust (0-1)
        """
        mq135_adc = self.mq135.read_adc(pollution_level)
        dust_adc = self.dust_sensor.pulse_led_and_read(dust_level)
        temp, humid = self.temp_humid.read()
        
        return {
            'mq135_raw': mq135_adc,
            'mq135_ma': self.mq135.get_moving_average(),
            'dust_raw': dust_adc,
            'dust_density': self.dust_sensor.adc_to_dust_density(dust_adc),
            'temperature': temp,
            'humidity': humid
        }
        
    def check_thresholds(self, readings):
        """Evaluate alert conditions"""
        mq135_alert = readings['mq135_raw'] > MQ135_THRESHOLD_ADC
        dust_alert = readings['dust_raw'] < DUST_THRESHOLD_ADC
        
        return mq135_alert or dust_alert
        
    def update_display(self, readings):
        """Update OLED display"""
        self.oled.fill()
        self.oled.puts(f"Tmp:{readings['temperature']:.1f}C", row=0)
        self.oled.puts(f"Hum:{readings['humidity']:.1f}%", row=1)
        self.oled.puts(f"CO2:{readings['mq135_raw']:.0f}ADC", row=2)
        self.oled.puts(f"PM:{readings['dust_raw']:.0f}ADC", row=3)
        
        mq135_status = "GOOD" if readings['mq135_raw'] < MQ135_THRESHOLD_ADC else "ALERT"
        dust_status = "OK" if readings['dust_raw'] > DUST_THRESHOLD_ADC else "ALERT"
        
        self.oled.puts(f"MQ:{mq135_status}", row=4)
        self.oled.puts(f"DS:{dust_status}", row=5)
        self.oled.update_screen()
        
    def main_loop(self, pollution_level=0.5, dust_level=0.3, iterations=10):
        """Main control loop (1000ms cycle)"""
        print("\n[MAIN] Starting main loop...\n")
        
        for i in range(iterations):
            self.loop_count += 1
            self.system_time = time.time() - self.start_time
            
            print(f"\n--- CYCLE {self.loop_count} (Time: {self.system_time:.1f}s) ---")
            
            # Read sensors
            readings = self.read_all_sensors(pollution_level, dust_level)
            
            # Display readings
            print(f"MQ-135 Raw ADC:       {readings['mq135_raw']}")
            print(f"MQ-135 Moving Avg:    {readings['mq135_ma']:.1f}")
            print(f"Dust Sensor Raw ADC:  {readings['dust_raw']}")
            print(f"Dust Density:         {readings['dust_density']:.2f} µg/m³")
            print(f"Temperature:          {readings['temperature']:.1f}°C")
            print(f"Humidity:             {readings['humidity']:.1f}%")
            
            # Check thresholds and activate alerts
            if self.check_thresholds(readings):
                self.alert.activate_alert()
            else:
                self.alert.deactivate_alert()
            
            # Update display
            self.update_display(readings)
            self.oled.display()
            
            # Simulate 1-second cycle
            time.sleep(1)
        
    def print_summary(self):
        """Print system summary"""
        print("\n" + "="*50)
        print("  SYSTEM SUMMARY")
        print("="*50)
        print(f"Total cycles:         {self.loop_count}")
        print(f"Total alerts:         {self.alert.alert_count}")
        print(f"MQ-135 readings:      {len(self.mq135.readings_history)}")
        print(f"Dust readings:        {len(self.dust_sensor.readings_history)}")
        print(f"OLED updates:         {self.oled.update_count}")
        print(f"Total runtime:        {self.system_time:.1f}s")
        print("="*50 + "\n")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    detector = PollutionDetector()
    detector.initialize()
    
    # Run main loop with simulated pollution levels
    # Scenarios: pollution_level (0-1), dust_level (0-1)
    print("\n[TEST] Running normal operation test (5 cycles)...")
    detector.main_loop(pollution_level=0.3, dust_level=0.5, iterations=5)
    
    print("\n[TEST] Running high pollution scenario (3 cycles)...")
    detector.main_loop(pollution_level=0.8, dust_level=0.2, iterations=3)
    
    detector.print_summary()
    print("[COMPLETE] Python simulation finished successfully!")