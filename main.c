******************************************************************************
  * @file           : main.c
  * @brief          : Air Pollution Detector with STM32F103C8T6
  * @author         : Your Name
  * @date           : 2025
  ******************************************************************************
  * Hardware:
  * - STM32F103C8T6 Blue Pill
  * - DHT22 (Temp/Humidity) - PA1
  * - MQ-135 (Air Quality) - PA0 (ADC)
  * - MQ-7 (CO Sensor) - PA2 (ADC)
  * - GP2Y1010 (Dust) - PA4 (ADC), PA3 (LED Control)
  * - SSD1306 OLED - PB6(SCL), PB7(SDA)
  * - Buzzer - PA8
  * - Red LED - PA9, Green LED - PA10
  ******************************************************************************
  */
/* USER CODE END Header */

/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "string.h"
#include "stdio.h"
#include "math.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
// Include OLED and DHT22 libraries (add these files to project)
// #include "ssd1306.h"
// #include "dht22.h"
/* USER CODE END Includes */

/* Private defines -----------------------------------------------------------*/
/* USER CODE BEGIN PD */
// Safety Thresholds (WHO/OSHA Standards)
#define TEMP_MIN 10.0f
#define TEMP_MAX 40.0f
#define HUMIDITY_MIN 20.0f
#define HUMIDITY_MAX 80.0f
#define CO_PPM_MAX 50.0f
#define CO2_PPM_MAX 1000.0f

// ADC Configuration
#define ADC_CHANNELS 3
#define ADC_BUFFER_SIZE 3

// Pin Definitions
#define DHT22_PIN GPIO_PIN_1
#define DHT22_PORT GPIOA
#define DUST_LED_PIN GPIO_PIN_3
#define DUST_LED_PORT GPIOA
#define BUZZER_PIN GPIO_PIN_8
#define BUZZER_PORT GPIOA
#define RED_LED_PIN GPIO_PIN_9
#define RED_LED_PORT GPIOA
#define GREEN_LED_PIN GPIO_PIN_10
#define GREEN_LED_PORT GPIOA

// Timing
#define SAMPLE_INTERVAL 2000  // 2 seconds between readings
#define BUZZER_BEEP_DURATION 200
/* USER CODE END PD */

/* Private variables ---------------------------------------------------------*/
ADC_HandleTypeDef hadc1;
DMA_HandleTypeDef hdma_adc1;

I2C_HandleTypeDef hi2c1;

TIM_HandleTypeDef htim1;

/* USER CODE BEGIN PV */
// ADC Data Buffer
uint16_t adc_buffer[ADC_BUFFER_SIZE];

// Sensor Readings
typedef struct {
    float temperature;
    float humidity;
    float co_ppm;
    float co2_ppm;
    float dust_density;
    uint8_t alert_status;  // 0=Safe, 1=Warning, 2=Critical
} SensorData_t;

SensorData_t sensor_data = {25.0f, 50.0f, 10.0f, 400.0f, 0.0f, 0};

// System Status
uint32_t cycle_count = 0;
uint32_t alert_count = 0;
uint32_t last_sample_time = 0;
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_DMA_Init(void);
static void MX_ADC1_Init(void);
static void MX_I2C1_Init(void);
static void MX_TIM1_Init(void);

/* USER CODE BEGIN PFP */
// Sensor Functions
void Read_DHT22(float *temperature, float *humidity);
float Read_MQ135_CO2(uint16_t adc_value);
float Read_MQ7_CO(uint16_t adc_value);
float Read_GP2Y1010_Dust(uint16_t adc_value);

// System Functions
void Update_Display(void);
void Check_Thresholds(void);
void Activate_Buzzer(uint8_t beeps);
void Set_LED_Status(uint8_t status);
void Delay_us(uint32_t us);
/* USER CODE END PFP */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */
  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/
  HAL_Init();
  SystemClock_Config();

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_DMA_Init();
  MX_ADC1_Init();
  MX_I2C1_Init();
  MX_TIM1_Init();

  /* USER CODE BEGIN 2 */
  // Initialize OLED Display
  // SSD1306_Init();
  // SSD1306_Clear();
  // SSD1306_GotoXY(0, 0);
  // SSD1306_Puts("Air Pollution", &Font_7x10, 1);
  // SSD1306_GotoXY(0, 12);
  // SSD1306_Puts("Detector v1.0", &Font_7x10, 1);
  // SSD1306_UpdateScreen();
  HAL_Delay(2000);
  
  // Start ADC with DMA
  HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adc_buffer, ADC_BUFFER_SIZE);
  
  // Initialize LEDs
  HAL_GPIO_WritePin(GREEN_LED_PORT, GREEN_LED_PIN, GPIO_PIN_SET);
  HAL_GPIO_WritePin(RED_LED_PORT, RED_LED_PIN, GPIO_PIN_RESET);
  
  last_sample_time = HAL_GetTick();
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    uint32_t current_time = HAL_GetTick();
    
    // Sample sensors every SAMPLE_INTERVAL milliseconds
    if ((current_time - last_sample_time) >= SAMPLE_INTERVAL) {
      last_sample_time = current_time;
      cycle_count++;
      
      // Read DHT22 (Temperature & Humidity)
      Read_DHT22(&sensor_data.temperature, &sensor_data.humidity);
      
      // Read MQ-135 (CO2/Air Quality) - ADC Channel 0 (PA0)
      sensor_data.co2_ppm = Read_MQ135_CO2(adc_buffer[0]);
      
      // Read MQ-7 (CO) - ADC Channel 2 (PA2)
      sensor_data.co_ppm = Read_MQ7_CO(adc_buffer[1]);
      
      // Read GP2Y1010 (Dust) - ADC Channel 4 (PA4)
      sensor_data.dust_density = Read_GP2Y1010_Dust(adc_buffer[2]);
      
      // Check safety thresholds
      Check_Thresholds();
      
      // Update display
      Update_Display();
    }
    
    /* USER CODE END WHILE */
    /* USER CODE BEGIN 3 */
    HAL_Delay(100);  // Small delay to reduce CPU load
  }
  /* USER CODE END 3 */
}

/* USER CODE BEGIN 4 */

/**
  * @brief  Read DHT22 Temperature and Humidity
  * @param  temperature: Pointer to store temperature
  * @param  humidity: Pointer to store humidity
  * @retval None
  */
void Read_DHT22(float *temperature, float *humidity)
{
  // DHT22 Protocol Implementation
  // Note: This is a simplified version. Use proper DHT22 library
  
  uint8_t data[5] = {0, 0, 0, 0, 0};
  uint8_t bit_count = 0;
  uint32_t timeout;
  
  // Send start signal
  HAL_GPIO_WritePin(DHT22_PORT, DHT22_PIN, GPIO_PIN_RESET);
  HAL_Delay(2);  // Hold low for 2ms
  HAL_GPIO_WritePin(DHT22_PORT, DHT22_PIN, GPIO_PIN_SET);
  Delay_us(30);
  
  // Wait for DHT22 response (simplified - needs proper timing)
  // For production, use dedicated DHT22 library
  
  // Placeholder: Return last valid readings if read fails
  // In actual implementation, parse 40-bit data from DHT22
  
  // Mock data for testing (replace with actual DHT22 read)
  *temperature = 25.0f + (float)(cycle_count % 10) * 0.5f;
  *humidity = 50.0f + (float)(cycle_count % 20) * 0.3f;
}

/**
  * @brief  Convert MQ-135 ADC to CO2 PPM
  * @param  adc_value: Raw ADC reading (0-4095)
  * @retval CO2 concentration in PPM
  */
float Read_MQ135_CO2(uint16_t adc_value)
{
  // MQ-135 Calibration Curve (approximate)
  // Vout = Vcc * (Rs / (Rs + RL))
  // Rs/R0 ratio varies with gas concentration
  
  float voltage = (adc_value / 4095.0f) * 3.3f;
  float rs_r0_ratio = (3.3f - voltage) / voltage;
  
  // CO2 PPM calculation (simplified exponential curve)
  // Based on datasheet: PPM = 116.6020682 * (rs/r0)^-2.769034857
  float ppm = 116.6f * powf(rs_r0_ratio, -2.769f);
  
  // Clamp to realistic range
  if (ppm < 300.0f) ppm = 300.0f;
  if (ppm > 5000.0f) ppm = 5000.0f;
  
  return ppm;
}

/**
  * @brief  Convert MQ-7 ADC to CO PPM
  * @param  adc_value: Raw ADC reading (0-4095)
  * @retval CO concentration in PPM
  */
float Read_MQ7_CO(uint16_t adc_value)
{
  // MQ-7 Calibration (approximate)
  float voltage = (adc_value / 4095.0f) * 3.3f;
  float rs_r0_ratio = (3.3f - voltage) / voltage;
  
  // CO PPM calculation: PPM = 98.322 * (rs/r0)^-1.458
  float ppm = 98.322f * powf(rs_r0_ratio, -1.458f);
  
  // Clamp to realistic range
  if (ppm < 0.0f) ppm = 0.0f;
  if (ppm > 500.0f) ppm = 500.0f;
  
  return ppm;
}

/**
  * @brief  Convert GP2Y1010 ADC to Dust Density
  * @param  adc_value: Raw ADC reading (0-4095)
  * @retval Dust density in µg/m³
  */
float Read_GP2Y1010_Dust(uint16_t adc_value)
{
  // Pulse LED
  HAL_GPIO_WritePin(DUST_LED_PORT, DUST_LED_PIN, GPIO_PIN_SET);
  Delay_us(280);  // Wait for stable reading
  
  // Take measurement (passed as parameter)
  float voltage = (adc_value / 4095.0f) * 3.3f;
  
  HAL_GPIO_WritePin(DUST_LED_PORT, DUST_LED_PIN, GPIO_PIN_RESET);
  
  // Convert to dust density: density = (Vout - 0.6) * 0.17 mg/m³
  float density = (voltage - 0.6f) * 170.0f;  // µg/m³
  
  if (density < 0.0f) density = 0.0f;
  if (density > 500.0f) density = 500.0f;
  
  return density;
}

/**
  * @brief  Check sensor thresholds and trigger alerts
  * @retval None
  */
void Check_Thresholds(void)
{
  uint8_t violations = 0;
  
  // Check temperature
  if (sensor_data.temperature < TEMP_MIN || sensor_data.temperature > TEMP_MAX) {
    violations++;
  }
  
  // Check humidity
  if (sensor_data.humidity < HUMIDITY_MIN || sensor_data.humidity > HUMIDITY_MAX) {
    violations++;
  }
  
  // Check CO
  if (sensor_data.co_ppm > CO_PPM_MAX) {
    violations++;
  }
  
  // Check CO2
  if (sensor_data.co2_ppm > CO2_PPM_MAX) {
    violations++;
  }
  
  // Set alert status
  if (violations >= 2) {
    sensor_data.alert_status = 2;  // CRITICAL
    alert_count++;
    Set_LED_Status(2);
    Activate_Buzzer(3);  // 3 beeps
  } else if (violations >= 1) {
    sensor_data.alert_status = 1;  // WARNING
    alert_count++;
    Set_LED_Status(1);
    Activate_Buzzer(2);  // 2 beeps
  } else {
    sensor_data.alert_status = 0;  // SAFE
    Set_LED_Status(0);
  }
}

/**
  * @brief  Update OLED display with sensor data
  * @retval None
  */
void Update_Display(void)
{
  char buffer[32];
  
  // Clear display
  // SSD1306_Clear();
  
  // Line 0: Temperature & Humidity
  // sprintf(buffer, "T:%4.1fC H:%4.1f%%", sensor_data.temperature, sensor_data.humidity);
  // SSD1306_GotoXY(0, 0);
  // SSD1306_Puts(buffer, &Font_7x10, 1);
  
  // Line 1: CO PPM
  // sprintf(buffer, "CO: %6.1f PPM", sensor_data.co_ppm);
  // SSD1306_GotoXY(0, 12);
  // SSD1306_Puts(buffer, &Font_7x10, 1);
  
  // Line 2: CO2 PPM
  // sprintf(buffer, "CO2:%6.1f PPM", sensor_data.co2_ppm);
  // SSD1306_GotoXY(0, 24);
  // SSD1306_Puts(buffer, &Font_7x10, 1);
  
  // Line 3: Status
  // SSD1306_GotoXY(0, 36);
  // if (sensor_data.alert_status == 2) {
  //   SSD1306_Puts("CRITICAL!", &Font_7x10, 1);
  // } else if (sensor_data.alert_status == 1) {
  //   SSD1306_Puts("WARNING", &Font_7x10, 1);
  // } else {
  //   SSD1306_Puts("ALL OK", &Font_7x10, 1);
  // }
  
  // Line 4: Cycle count
  // sprintf(buffer, "Cycle: %lu", cycle_count);
  // SSD1306_GotoXY(0, 48);
  // SSD1306_Puts(buffer, &Font_7x10, 1);
  
  // Update screen
  // SSD1306_UpdateScreen();
}

/**
  * @brief  Activate buzzer with specified beep pattern
  * @param  beeps: Number of beeps (1-3)
  * @retval None
  */
void Activate_Buzzer(uint8_t beeps)
{
  for (uint8_t i = 0; i < beeps; i++) {
    HAL_GPIO_WritePin(BUZZER_PORT, BUZZER_PIN, GPIO_PIN_SET);
    HAL_Delay(BUZZER_BEEP_DURATION);
    HAL_GPIO_WritePin(BUZZER_PORT, BUZZER_PIN, GPIO_PIN_RESET);
    if (i < beeps - 1) {
      HAL_Delay(100);  // Pause between beeps
    }
  }
}

/**
  * @brief  Set LED status based on alert level
  * @param  status: 0=Safe (Green), 1=Warning (Red blink), 2=Critical (Red solid)
  * @retval None
  */
void Set_LED_Status(uint8_t status)
{
  if (status == 0) {
    HAL_GPIO_WritePin(GREEN_LED_PORT, GREEN_LED_PIN, GPIO_PIN_SET);
    HAL_GPIO_WritePin(RED_LED_PORT, RED_LED_PIN, GPIO_PIN_RESET);
  } else if (status == 1) {
    HAL_GPIO_WritePin(GREEN_LED_PORT, GREEN_LED_PIN, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(RED_LED_PORT, RED_LED_PIN, GPIO_PIN_SET);
  } else {
    HAL_GPIO_WritePin(GREEN_LED_PORT, GREEN_LED_PIN, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(RED_LED_PORT, RED_LED_PIN, GPIO_PIN_SET);
  }
}

/**
  * @brief  Microsecond delay using TIM1
  * @param  us: Delay in microseconds
  * @retval None
  */
void Delay_us(uint32_t us)
{
  __HAL_TIM_SET_COUNTER(&htim1, 0);
  HAL_TIM_Base_Start(&htim1);
  while (__HAL_TIM_GET_COUNTER(&htim1) < us);
  HAL_TIM_Base_Stop(&htim1);
}

/* USER CODE END 4 */

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
  RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};

  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL9;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
  PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_ADC;
  PeriphClkInit.AdcClockSelection = RCC_ADCPCLK2_DIV6;
  if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
  {
    Error_Handler();
  }
}

static void MX_ADC1_Init(void)
{
  ADC_ChannelConfTypeDef sConfig = {0};

  hadc1.Instance = ADC1;
  hadc1.Init.ScanConvMode = ADC_SCAN_ENABLE;
  hadc1.Init.ContinuousConvMode = ENABLE;
  hadc1.Init.DiscontinuousConvMode = DISABLE;
  hadc1.Init.ExternalTrigConv = ADC_SOFTWARE_START;
  hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
  hadc1.Init.NbrOfConversion = 3;
  if (HAL_ADC_Init(&hadc1) != HAL_OK)
  {
    Error_Handler();
  }

  sConfig.Channel = ADC_CHANNEL_0;
  sConfig.Rank = ADC_REGULAR_RANK_1;
  sConfig.SamplingTime = ADC_SAMPLETIME_55CYCLES_5;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }

  sConfig.Channel = ADC_CHANNEL_2;
  sConfig.Rank = ADC_REGULAR_RANK_2;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }

  sConfig.Channel = ADC_CHANNEL_4;
  sConfig.Rank = ADC_REGULAR_RANK_3;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
}

static void MX_I2C1_Init(void)
{
  hi2c1.Instance = I2C1;
  hi2c1.Init.ClockSpeed = 100000;
  hi2c1.Init.DutyCycle = I2C_DUTYCYCLE_2;
  hi2c1.Init.OwnAddress1 = 0;
  hi2c1.Init.Ad