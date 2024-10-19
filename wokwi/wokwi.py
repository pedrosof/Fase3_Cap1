import machine
import dht
import time
from machine import ADC, Pin

# Configuração do sensor DHT22
dht_sensor = dht.DHT22(Pin(2))  # O DHT22 está conectado ao pino GPIO 2

# Configuração do sensor LDR
ldr = ADC(Pin(34))  # O LDR está conectado ao pino ADC (GPIO34)
ldr.atten(ADC.ATTN_11DB)  # Configura a atenuação para ler até 3.3V

# Configuração dos LEDs
led_temp = Pin(0, Pin.OUT)  # O LED de temperatura está conectado ao pino GPIO 16 (D0)
led_light = Pin(4, Pin.OUT)  # O LED de luminosidade está conectado ao pino GPIO 4 (D4)
led_humidity = Pin(25, Pin.OUT)  # O LED de umidade está conectado ao pino GPIO 25

# Configuração dos botões
button_p = Pin(26, Pin.IN, Pin.PULL_UP)  # Botão P conectado ao GPIO 26
button_k = Pin(27, Pin.IN, Pin.PULL_UP)  # Botão K conectado ao GPIO 27

# Limites para acender os LEDs
temp_threshold = 30  # Limiar para a temperatura (em graus Celsius)
humidity_threshold = 30  # Limiar para a umidade (em percentual)

# Definindo os limites de luminosidade
light_threshold_min = 1800  # Limiar inferior
light_threshold_max = 1950  # Limiar superior

# Função para mapear o valor de 0-4095 para 0-14
def mapear_ldr(valor, min_orig, max_orig, min_dest, max_dest):
    return (valor - min_orig) * (max_dest - min_dest) / (max_orig - min_orig) + min_dest

while True:
    try:
        # Lê os valores de temperatura e umidade do DHT22
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum = dht_sensor.humidity()
        print("Temperatura: {:.1f}°C".format(temp))
        print("Umidade: {:1f}%".format(hum))
        
        # Lê o valor do LDR (faixa de 0 a 4095)
        ldr_value = ldr.read()
        # Mapeia o valor do LDR para a faixa de 0 a 14
        ldr_mapeado = mapear_ldr(ldr_value, 0, 4095, 0, 14)
        print("pH:", ldr_mapeado)
        #print("LUZ:", ldr_value)
        
        # Acende o LED de temperatura se a temperatura for maior que o limite
        if temp > temp_threshold:
            led_temp.on()  # Acende o LED de temperatura
            #print("LED de Temperatura aceso")
        else:
            led_temp.off()  # Apaga o LED de temperatura
            #print("LED de Temperatura apagado")
        
        # Acende o LED de pH se o valor do LDR for menor que o limite (pouca luz)
        if ldr_value < light_threshold_min or ldr_value > light_threshold_max:
            led_light.on()  # Acende o LED de pH
            #print("LED de pH aceso")
        else:
            led_light.off()  # Apaga o LED de pH
            #print("LED de pH apagado")
        
        # Acende o LED de umidade se a umidade for menor que o limite
        if hum < humidity_threshold:
            led_humidity.on()  # Acende o LED de umidade
            #print("LED de Umidade aceso")
        else:
            led_humidity.off()  # Apaga o LED de umidade
            #print("LED de Umidade apagado")
        
        # Verifica se o botão P foi pressionado (GPIO 26)
        if not button_p.value():
            print("P")  # Mostra a letra P quando o botão é pressionado
            time.sleep(0.2)  # Debouncing simples
        
        # Verifica se o botão K foi pressionado (GPIO 27)
        if not button_k.value():
            print("K")  # Mostra a letra K quando o botão é pressionado
            time.sleep(0.2)  # Debouncing simples
        
    except OSError as e:
        print('Falha ao ler o sensor DHT!')

    # Aguardar 2 segundos antes da próxima leitura
    time.sleep(2)
