import serial
import time
from Adafruit_IO import Client

# Configurações do Adafruit IO
ADAFRUIT_AIO_USERNAME = "ibastos"
ADAFRUIT_AIO_KEY = "adicionar key"
aio = Client(ADAFRUIT_AIO_USERNAME, ADAFRUIT_AIO_KEY)

# Configuração da porta serial
serial_port = "COM3"  # Substitua pelo nome da porta correta no seu PC
baud_rate = 9600

try:
    ser = serial.Serial(serial_port, baud_rate)
    print(f"Conectado à porta serial: {serial_port}")
except Exception as e:
    print(f"Erro ao conectar na porta serial: {e}")
    exit()

# Variáveis de controle
alert_active = False
last_sent_time = time.time()
last_sent_value = None  # Último valor estabilizado enviado
previous_limpidez = None
stability_threshold = 5  # Diferença máxima para considerar o valor estável
stability_count = 0  # Contador de leituras consecutivas estáveis
stability_required = 3  # Leituras consecutivas necessárias para considerar o valor estável

def parse_data(data):
    """Extrai os valores do texto recebido pela serial."""
    try:
        parts = data.split(", ")
        sensor_val = int(parts[0].split(": ")[1])
        voltage = float(parts[1].split(": ")[1])
        limpidez = float(parts[2].split(": ")[1])
        return sensor_val, voltage, limpidez
    except Exception as e:
        
        return None

def is_stable(current_value, previous_value):
    """Verifica se o valor atual é estável comparado ao anterior."""
    return abs(current_value - previous_value) <= stability_threshold

while True:
    if ser.in_waiting > 0:
        try:
            # Recebe os dados do Arduino
            line = ser.readline().decode('utf-8').strip()
            print(f"Recebido: {line}")
            parsed = parse_data(line)

            if parsed:
                sensor_val, voltage, limpidez = parsed
                current_time = time.time()

                if previous_limpidez is None:
                    # Inicializa o valor anterior
                    previous_limpidez = limpidez

                # Verifica estabilidade
                if is_stable(limpidez, previous_limpidez):
                    stability_count += 1
                else:
                    stability_count = 0

                # Define como estável se atingir o número necessário de leituras consecutivas
                stable = stability_count >= stability_required

                # Condições de envio:
                # 1. Diferença maior que 5 pontos em relação ao último valor enviado
                # 2. Tempo desde o último envio é superior a 60 segundos
                significant_change = last_sent_value is None or abs(limpidez - last_sent_value) > stability_threshold
                time_elapsed = current_time - last_sent_time > 60

                # Envia apenas se o valor estiver estável e houver uma alteração significativa ou tempo maior que 60s
                if stable and (significant_change or time_elapsed):
                    # Envia os dados para o Adafruit IO
                    aio.send("limpidez", limpidez)
                    print(f"Dados enviados para o Adafruit IO! Limpidez: {limpidez}")

                    # Atualiza variáveis de controle
                    last_sent_time = current_time
                    last_sent_value = limpidez

                    # Gerencia alertas
                    if limpidez < 60 and not alert_active:
                        aio.send("alerta", "Limpidez baixa")
                        alert_active = True
                        print("Alerta enviado ao Adafruit IO!")
                    elif limpidez >= 60 and alert_active:
                        aio.send("alerta", "Limpidez normalizada")
                        alert_active = False
                        print("Alerta removido e dados atualizados para o Adafruit IO!")

                # Atualiza o valor anterior
                previous_limpidez = limpidez

        except Exception as e:
            print(f"Erro durante envio ou leitura: {e}")

    time.sleep(0.5)
