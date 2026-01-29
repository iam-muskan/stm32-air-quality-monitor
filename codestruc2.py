"""
Wearable Pollution Detector - Complete Serial Input Version
Takes sensor values via serial/console input and displays on OLED
Shows: Temperature, Humidity, CO, CO2/PPM
Triggers buzzer when any parameter exceeds safety thresholds
COMPLETE COPY-PASTE READY CODE
"""

import time
from enum import Enum
from datetime import datetime

# ============================================================================
# SAFETY THRESHOLDS & CONFIGURATION
# ============================================================================

# WHO/OSHA Safety Standards
THRESHOLDS = {
    'temperature_min': 10.0,      # °C
    'temperature_max': 40.0,      # °C
    'humidity_min': 20.0,         # %
    'humidity_max': 80.0,         # %
    'co_ppm_max': 50.0,           # PPM (OSHA 8-hour TWA)
    'co2_ppm_max': 1000.0,        # PPM (NIOSH Recommended Exposure Limit)
    'mq135_adc_max': 400,         # ADC (CO2 proxy)
    'dust_adc_min': 300,          # ADC (inverted logic)
}

NORMAL_COLOR = "\033[92m"      # Green
WARNING_COLOR = "\033[93m"     # Yellow
CRITICAL_COLOR = "\033[91m"   # Red
RESET_COLOR = "\033[0m"

class AlarmStatus(Enum):
    SAFE = 0
    WARNING = 1
    CRITICAL = 2

# ============================================================================
# OLED DISPLAY SIMULATION (128x64, 8 rows x 16 cols)
# ============================================================================

class SimulatedOLED:
    """Simulate SSD1306 0.96" OLED 128x64"""
    
    def __init__(self):
        self.width = 16
        self.height = 8
        self.frame_buffer = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        self.update_count = 0
        self.last_update_time = time.time()
        
    def fill(self, color=0):
        """Clear display"""
        self.frame_buffer = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
    def puts(self, text, row=0, truncate=True):
        """
        Place text at specified row
        row: 0-7 (each row ~7-8 pixels high)
        """
        if row >= self.height:
            return
        
        if truncate and len(text) > self.width:
            text = text[:self.width]
        else:
            text = text.ljust(self.width)[:self.width]
        
        self.frame_buffer[row] = list(text)
        
    def update_screen(self):
        """Refresh display (called via I2C)"""
        self.update_count += 1
        self.last_update_time = time.time()
        
    def display(self, title="POLLUTION MONITOR"):
        """Print current display to console"""
        print("\n" + "="*20)
        print(f"  {title}")
        print("="*20)
        for row in self.frame_buffer:
            print("|" + "".join(row) + "|")
        print("="*20)
        print(f"Updates: {self.update_count}\n")


# ============================================================================
# BUZZER & LED ALERT SYSTEM
# ============================================================================

class AlertSystem:
    """Buzzer and LED control"""
    
    def __init__(self):
        self.buzzer_active = False
        self.red_led_active = False
        self.green_led_active = False
        self.alarm_status = AlarmStatus.SAFE
        self.beep_count = 0
        self.beep_pattern = []
        
    def evaluate_alert(self, readings):
        """
        Evaluate sensor readings against thresholds
        Returns: (alarm_status, violated_params)
        """
        violations = []
        
        # Check temperature
        if readings['temperature'] < THRESHOLDS['temperature_min'] or \
           readings['temperature'] > THRESHOLDS['temperature_max']:
            violations.append('TEMP')
        
        # Check humidity
        if readings['humidity'] < THRESHOLDS['humidity_min'] or \
           readings['humidity'] > THRESHOLDS['humidity_max']:
            violations.append('HUM')
        
        # Check CO
        if readings['co_ppm'] > THRESHOLDS['co_ppm_max']:
            violations.append('CO')
        
        # Check CO2
        if readings['co2_ppm'] > THRESHOLDS['co2_ppm_max']:
            violations.append('CO2')
        
        # Determine alarm status
        if len(violations) >= 2:
            status = AlarmStatus.CRITICAL
        elif len(violations) >= 1:
            status = AlarmStatus.WARNING
        else:
            status = AlarmStatus.SAFE
        
        self.alarm_status = status
        return status, violations
    
    def activate_alarm(self, violations):
        """Activate buzzer and LED based on violations"""
        self.buzzer_active = True
        self.red_led_active = True
        self.green_led_active = False
        
        if len(violations) >= 2:
            # Critical: 3 beeps
            self.beep_pattern = [0.2, 0.1, 0.2, 0.1, 0.2]
        else:
            # Warning: 2 beeps
            self.beep_pattern = [0.15, 0.1, 0.15]
        
        self.beep_count = len([x for x in self.beep_pattern if x > 0.12])
        
    def deactivate_alarm(self):
        """Turn off alert systems"""
        self.buzzer_active = False
        self.red_led_active = False
        self.green_led_active = True
        self.beep_pattern = []
        self.beep_count = 0
    
    def trigger_buzzer(self):
        """Simulate buzzer beeps"""
        if self.buzzer_active and self.beep_pattern:
            beeps = self.beep_count
            beep_duration = 0.2
            print(f"\n{CRITICAL_COLOR}🔊 BUZZER BEEPING... ({beeps} beep{'s' if beeps > 1 else ''}){RESET_COLOR}")
            for i in range(beeps):
                print(f"   [BEEP {i+1}/{beeps}] ● ●●●● ●●●●●")
                time.sleep(beep_duration)
            print()
    
    def status_string(self):
        """Return LED status string"""
        if self.alarm_status == AlarmStatus.CRITICAL:
            return "🔴 CRITICAL"
        elif self.alarm_status == AlarmStatus.WARNING:
            return "🟡 WARNING"
        else:
            return "🟢 SAFE"


# ============================================================================
# SERIAL INPUT HANDLER
# ============================================================================

class SerialInputHandler:
    """Handle user input for sensor simulation"""
    
    def __init__(self):
        self.last_readings = {
            'temperature': 25.0,
            'humidity': 50.0,
            'co_ppm': 10.0,
            'co2_ppm': 400.0,
            'mq135_adc': 150,
            'dust_adc': 500,
            'timestamp': datetime.now()
        }
        
    def get_sensor_input(self):
        """Get sensor values from user via serial/console"""
        print("\n" + "="*60)
        print("  ENTER SENSOR VALUES")
        print("="*60)
        
        try:
            # Temperature
            while True:
                try:
                    temp = float(input(f"Temperature (°C) [{self.last_readings['temperature']:.1f}]: ").strip() or self.last_readings['temperature'])
                    if -50 <= temp <= 80:
                        self.last_readings['temperature'] = temp
                        break
                    else:
                        print("  ❌ Please enter value between -50 to 80°C")
                except ValueError:
                    print("  ❌ Invalid input. Enter a number.")
            
            # Humidity
            while True:
                try:
                    humid = float(input(f"Humidity (%) [{self.last_readings['humidity']:.1f}]: ").strip() or self.last_readings['humidity'])
                    if 0 <= humid <= 100:
                        self.last_readings['humidity'] = humid
                        break
                    else:
                        print("  ❌ Please enter value between 0 to 100%")
                except ValueError:
                    print("  ❌ Invalid input. Enter a number.")
            
            # CO PPM
            while True:
                try:
                    co = float(input(f"CO (PPM) [{self.last_readings['co_ppm']:.1f}]: ").strip() or self.last_readings['co_ppm'])
                    if 0 <= co <= 500:
                        self.last_readings['co_ppm'] = co
                        break
                    else:
                        print("  ❌ Please enter value between 0 to 500 PPM")
                except ValueError:
                    print("  ❌ Invalid input. Enter a number.")
            
            # CO2 PPM
            while True:
                try:
                    co2 = float(input(f"CO2 (PPM) [{self.last_readings['co2_ppm']:.1f}]: ").strip() or self.last_readings['co2_ppm'])
                    if 0 <= co2 <= 5000:
                        self.last_readings['co2_ppm'] = co2
                        break
                    else:
                        print("  ❌ Please enter value between 0 to 5000 PPM")
                except ValueError:
                    print("  ❌ Invalid input. Enter a number.")
            
            self.last_readings['timestamp'] = datetime.now()
            return self.last_readings.copy()
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Input cancelled by user.")
            return None


# ============================================================================
# MAIN POLLUTION DETECTOR SYSTEM
# ============================================================================

class PollutionDetectorSerial:
    """Main system with serial input"""
    
    def __init__(self):
        self.oled = SimulatedOLED()
        self.alert_system = AlertSystem()
        self.input_handler = SerialInputHandler()
        
        self.cycle_count = 0
        self.total_alerts = 0
        self.readings_history = []
        
    def initialize(self):
        """Initialize system"""
        print("\n" + "="*60)
        print("  ⚙️  WEARABLE POLLUTION DETECTOR - INITIALIZING")
        print("="*60)
        print("  [✓] STM32F103C8T6 Blue Pill initialized")
        print("  [✓] HAL drivers loaded")
        print("  [✓] I2C1 configured (PB6/SCL, PB7/SDA)")
        print("  [✓] ADC1 configured (PA0, PA2)")
        print("  [✓] GPIO configured (PA1, PA8, PA9)")
        print("  [✓] OLED SSD1306 detected at 0x3C")
        print("  [✓] MQ-135 sensor ready")
        print("  [✓] GP2Y1010 dust sensor ready")
        print("  [✓] DHT22 sensor ready")
        print("  [✓] All systems operational")
        print("="*60)
        print("\n📋 SAFETY THRESHOLDS:")
        print(f"   Temperature:  {THRESHOLDS['temperature_min']}°C to {THRESHOLDS['temperature_max']}°C")
        print(f"   Humidity:     {THRESHOLDS['humidity_min']}% to {THRESHOLDS['humidity_max']}%")
        print(f"   CO:           0 to {THRESHOLDS['co_ppm_max']} PPM (OSHA standard)")
        print(f"   CO2:          0 to {THRESHOLDS['co2_ppm_max']} PPM (NIOSH standard)\n")
        
    def process_readings(self, readings):
        """Process sensor readings and update display"""
        if readings is None:
            return
        
        self.cycle_count += 1
        self.readings_history.append(readings.copy())
        
        # Evaluate alerts
        status, violations = self.alert_system.evaluate_alert(readings)
        
        print(f"\n{'='*60}")
        print(f"CYCLE #{self.cycle_count} | {readings['timestamp'].strftime('%H:%M:%S')}")
        print(f"{'='*60}")
        
        # Display raw readings
        print(f"\n📊 SENSOR READINGS:")
        temp_color = CRITICAL_COLOR if readings['temperature'] < THRESHOLDS['temperature_min'] or \
                                       readings['temperature'] > THRESHOLDS['temperature_max'] else NORMAL_COLOR
        humid_color = CRITICAL_COLOR if readings['humidity'] < THRESHOLDS['humidity_min'] or \
                                        readings['humidity'] > THRESHOLDS['humidity_max'] else NORMAL_COLOR
        co_color = CRITICAL_COLOR if readings['co_ppm'] > THRESHOLDS['co_ppm_max'] else NORMAL_COLOR
        co2_color = CRITICAL_COLOR if readings['co2_ppm'] > THRESHOLDS['co2_ppm_max'] else NORMAL_COLOR
        
        print(f"   {temp_color}Temperature:   {readings['temperature']:.1f}°C{RESET_COLOR}")
        print(f"   {humid_color}Humidity:      {readings['humidity']:.1f}%{RESET_COLOR}")
        print(f"   {co_color}CO:             {readings['co_ppm']:.1f} PPM{RESET_COLOR}")
        print(f"   {co2_color}CO2:            {readings['co2_ppm']:.1f} PPM{RESET_COLOR}")
        
        # OLED Display Update
        self.oled.fill()
        self.oled.puts(f"T:{readings['temperature']:6.1f}C H:{readings['humidity']:5.1f}%", row=0)
        self.oled.puts(f"CO: {readings['co_ppm']:6.1f}PPM", row=1)
        self.oled.puts(f"CO2:{readings['co2_ppm']:6.1f}PPM", row=2)
        self.oled.puts("", row=3)
        self.oled.puts(self.alert_system.status_string(), row=4)
        
        if violations:
            violation_str = " | ".join(violations)
            self.oled.puts(f"Alert: {violation_str}", row=5)
            print(f"\n⚠️  VIOLATIONS: {violation_str}")
        else:
            self.oled.puts("Status: ALL OK", row=5)
            print(f"\n✅ All parameters within safe limits")
        
        self.oled.puts("", row=6)
        self.oled.puts(f"Cycle: {self.cycle_count}", row=7)
        self.oled.update_screen()
        
        # Display OLED
        self.oled.display()
        
        # Alert logic
        if violations:
            self.total_alerts += 1
            print(f"\n🚨 ALERT TRIGGERED! ({len(violations)} violation{'s' if len(violations) > 1 else ''})")
            self.alert_system.activate_alarm(violations)
            self.alert_system.trigger_buzzer()
        else:
            self.alert_system.deactivate_alarm()
            print(f"\n✅ System operating normally. LEDs: {self.alert_system.status_string()}")
        
    def print_summary(self):
        """Print system summary"""
        print("\n" + "="*60)
        print("  📈 SYSTEM SUMMARY")
        print("="*60)
        print(f"Total cycles:            {self.cycle_count}")
        print(f"Total alerts triggered:  {self.total_alerts}")
        print(f"Readings stored:         {len(self.readings_history)}")
        
        if self.readings_history:
            temps = [r['temperature'] for r in self.readings_history]
            humids = [r['humidity'] for r in self.readings_history]
            cos = [r['co_ppm'] for r in self.readings_history]
            co2s = [r['co2_ppm'] for r in self.readings_history]
            
            print(f"\nTemperature Range:   {min(temps):.1f}°C to {max(temps):.1f}°C (Avg: {sum(temps)/len(temps):.1f}°C)")
            print(f"Humidity Range:      {min(humids):.1f}% to {max(humids):.1f}% (Avg: {sum(humids)/len(humids):.1f}%)")
            print(f"CO Range:            {min(cos):.1f} to {max(cos):.1f} PPM (Avg: {sum(cos)/len(cos):.1f} PPM)")
            print(f"CO2 Range:           {min(co2s):.1f} to {max(co2s):.1f} PPM (Avg: {sum(co2s)/len(co2s):.1f} PPM)")
        
        print("="*60 + "\n")
    
    def run(self):
        """Main execution loop"""
        self.initialize()
        
        try:
            while True:
                # Get input from user
                readings = self.input_handler.get_sensor_input()
                
                if readings is None:
                    break
                
                # Process and display
                self.process_readings(readings)
                
                # Ask for another reading
                cont = input("\n➤ Enter another reading? (y/n): ").strip().lower()
                if cont != 'y':
                    break
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Program interrupted by user.")
        
        self.print_summary()
        print("🏁 System shutdown complete.\n")


# ============================================================================
# MAIN EXECUTION - START HERE
# ============================================================================

if __name__ == "__main__":
    detector = PollutionDetectorSerial()
    detector.run()