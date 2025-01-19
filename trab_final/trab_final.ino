#include <Arduino.h>

int pinoSensor = A0;        // Pino do sensor
int n = 25;                 // Número de leituras para média

int sensorValor = 0;        // Valor bruto do sensor
float Vlimpo = 2.0;         // Valor de referência para água limpa
float voltage = 0.0;        // Voltagem calculada
float turbidez = 0.0;       // Turbidez calculada
float limpidez = 0.0;       // Limpidez calculada

int buttoncalib = 49;       // Pino do botão de calibração

float voltageValue(int read) {
  return read * (5.0 / 1023.0);
}

float turbidezValor(int read) {
  return 100.0 - (voltage / Vlimpo) * 100.0;
}

void setup() {
  pinMode(buttoncalib, INPUT_PULLUP);  // Configura o botão como entrada com pull-up
  Serial.begin(9600);                 // Inicia a comunicação serial
}

void loop() {
  int pushcalib = digitalRead(buttoncalib);

  // Calibração
  if (pushcalib == LOW) {
    int sensorCalib = 0;
    for (int i = 0; i < n; i++) {
      sensorCalib += analogRead(pinoSensor);
      delay(10);
    }
    sensorValor = sensorCalib / n;
    Vlimpo = voltageValue(sensorValor);

    Serial.print("Calibrado, Vlimpo: ");
    Serial.print(Vlimpo, 2);
    Serial.println(" V");
    delay(1000);
  } else {
    // Leituras do sensor
    int sensor = 0;
    for (int i = 0; i < n; i++) {
      sensor += analogRead(pinoSensor);
      delay(100);
    }
    sensorValor = sensor / n;
    voltage = voltageValue(sensorValor);

    // Garante que a voltagem não ultrapasse o limite calibrado
    if (voltage > Vlimpo) {
      voltage = Vlimpo;
    }

    // Calcula turbidez e limpidez
    turbidez = turbidezValor(sensorValor);
    limpidez = 100.0 - turbidez;

    // Exibição formatada no monitor serial
    Serial.print("Sensor: ");
    Serial.print(sensorValor);
    Serial.print(", Voltage: ");
    Serial.print(voltage, 2);
    Serial.print(", Limpidez: ");
    Serial.print(limpidez, 2);
    Serial.print(", Vlimpo: ");
    Serial.println(Vlimpo, 2);
    delay(1000);
  }
}
