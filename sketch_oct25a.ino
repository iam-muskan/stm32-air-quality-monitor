#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <DHT.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define SCREEN_ADDRESS 0x3D

#define DHT_PIN PA1
#define DHT_TYPE DHT22

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
  Wire.begin();
  
  if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    while(1);
  }
  
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println(F("DHT22 Sensor"));
  display.println(F("Initializing..."));
  display.display();
  delay(2000);
}

void loop() {
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println(F("Sensor Error!"));
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println(F("Check wiring"));
    display.display();
    delay(2000);
    return;
  }
  
  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println(F("DHT22 Sensor"));
  display.drawLine(0, 10, 128, 10, SSD1306_WHITE);
  
  display.setCursor(0, 16);
  display.print(F("Temp: "));
  display.setTextSize(2);
  display.setCursor(0, 26);
  display.print(temperature, 1);
  display.print(F(" C"));
  
  display.setTextSize(1);
  display.setCursor(0, 46);
  display.print(F("Humidity: "));
  display.print(humidity, 1);
  display.print(F(" %"));
  
  display.display();
  delay(2000);
}

