#include <LiquidCrystal.h>
#include <DHT.h>

// ---------- Pin Definitions ----------
#define DHT_PIN PA1
#define DHT_TYPE DHT22

#define MQ135_PIN PA0         // MQ135 A0 → STM32 PA0 (analog in)
#define GP2Y_LED_PIN PA8      // GP2Y1010 IR LED control via 150Ω resistor
#define GP2Y_ANALOG_PIN PA2   // GP2Y1010 Vo → STM32 PA2 (analog in)

#define RS_PIN PA2
#define E_PIN  PA3
#define D4_PIN PA4
#define D5_PIN PA5
#define D6_PIN PA6
#define D7_PIN PA7

LiquidCrystal lcd(RS_PIN, E_PIN, D4_PIN, D5_PIN, D6_PIN, D7_PIN);
DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
  // Serial Monitor output via USB-to-TTL
  Serial.begin(115200);
  Serial.println("STM32 Environmental Station v1");

  lcd.begin(16, 2);
  lcd.clear();
  lcd.print("Env. Monitor");
  lcd.setCursor(0, 1);
  lcd.print("Init sensors...");
  delay(2000);
  lcd.clear();

  dht.begin();
  pinMode(GP2Y_LED_PIN, OUTPUT);
}

void loop() {
  // ---- Read DHT22 ----
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  // ---- Read MQ135 ----
  int airQualityRaw = analogRead(MQ135_PIN);
}
  // ---- Read
