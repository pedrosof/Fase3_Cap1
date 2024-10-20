import cx_Oracle
import random
from datetime import datetime, timedelta
from configparser import ConfigParser
import argparse
import requests

# Inicializar o Oracle Instant Client (caso necessário)
cx_Oracle.init_oracle_client(lib_dir="/Users/pedrosof/Downloads/instantclient_23_3")

# Função para carregar as configurações do arquivo config.cfg
def carregar_configuracoes():
    config = ConfigParser()
    config.read('config/config.cfg')
    return config

# Função para gerar datas aleatórias
def random_date(start, end):
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))

# Função para conectar ao banco de dados Oracle
def conectar_banco():
    config = carregar_configuracoes()
    host = config.get('Database', 'host')
    port = config.get('Database', 'port')
    service_name = config.get('Database', 'service_name')
    user = config.get('Database', 'username')
    password = config.get('Database', 'password')

    dsn_tns = cx_Oracle.makedsn(host, port, service_name=service_name)
    conn = cx_Oracle.connect(user=user, password=password, dsn=dsn_tns)
    print("Conexão estabelecida com o banco de dados.")
    return conn

# Função para verificar se uma data já existe no banco de dados (somente data, ignorando hora) em ambas as tabelas
def verificar_data_existente(cursor, data):
    query_sensor = """
        SELECT COUNT(*) FROM sensor_data 
        WHERE TRUNC(reading_date) = TRUNC(:data)
    """
    query_climatic = """
        SELECT COUNT(*) FROM condicoes_climaticas 
        WHERE TRUNC(data_coleta) = TRUNC(:data)
    """
    
    cursor.execute(query_sensor, {'data': data})
    result_sensor = cursor.fetchone()[0]
    
    cursor.execute(query_climatic, {'data': data})
    result_climatic = cursor.fetchone()[0]
    
    # Se a data já existe em qualquer uma das tabelas, retornar True
    return result_sensor > 0 or result_climatic > 0

# Função para inserir dados na tabela sensor_data
def insert_data_sensor_data(cursor, conn, reading_date, temperature, humidity, ph_value, button_p, button_k):
    insert_sql = """
        INSERT INTO sensor_data (reading_date, temperature, humidity, ph_value, button_p_pressed, button_k_pressed)
        VALUES (:1, :2, :3, :4, :5, :6)
    """
    try:
        cursor.execute(insert_sql, (reading_date, temperature, humidity, ph_value, button_p, button_k))
        conn.commit()  # Commit após a inserção
        print(f"Nova entrada inserida:\n Data: {reading_date}, Temperatura: {temperature}, Umidade: {humidity}, PH: {ph_value}, Botão P: {button_p}, Botão K: {button_k}")
        return True  # Retorna True se o dado foi inserido com sucesso
    except cx_Oracle.IntegrityError as e:
        print(f"Erro de integridade ao inserir: {e}")
        return False  # Retorna False se houve violação de chave única (duplicata)

# Função para inserir dados na tabela condicoes_climaticas
def insert_data_condicoes_climaticas(cursor, conn, reading_date, temperatura, umidade, clima):
    insert_sql = """
        INSERT INTO condicoes_climaticas (data_coleta, temperatura, umidade, clima)
        VALUES (:1, :2, :3, :4)
    """
    try:
        cursor.execute(insert_sql, (reading_date, temperatura, umidade, clima))
        conn.commit()  # Commit após a inserção
        print(f"Condições climáticas inseridas:\n Data: {reading_date}, Temperatura: {temperatura}, Umidade: {umidade}, Clima: {clima}")
        return True  # Retorna True se o dado foi inserido com sucesso
    except cx_Oracle.IntegrityError as e:
        print(f"Erro de integridade ao inserir: {e}")
        return False  # Retorna False se houve violação de chave única (duplicata)

# Função para buscar condições climáticas usando a API OpenWeather
def buscar_condicoes_climaticas():
    config = carregar_configuracoes()
    api_key = config.get('OpenWeather', 'apikey')
    city = config.get('OpenWeather', 'city')
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=pt_br"
    
    try:
        print(f"Fazendo chamada para a API OpenWeather: {url}")
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            temperatura = data['main']['temp']
            umidade = data['main']['humidity']
            clima = data['weather'][0]['description']  # Descrição do clima (ex: "nuvens dispersas", "ensolarado")
            print(f"Condições climáticas recebidas: Temperatura: {temperatura}, Umidade: {umidade}, Clima: {clima}")
            return temperatura, umidade, clima
        else:
            print(f"Erro ao buscar condições climáticas: {response.status_code}")
            return None, None, None

    except Exception as e:
        print(f"Erro ao buscar condições climáticas: {e}")
        return None, None, None

# Função para gerar e inserir dados aleatórios entre um intervalo de datas
def gerar_e_inserir_dados(cursor, conn, start_date, end_date, ne=1):
    if ne is None:
        ne = 1  # Definir o padrão para 1 se não for passado

    insercoes_realizadas = 0  # Contador de inserções bem-sucedidas
    datas_geradas = set()  # Conjunto para armazenar datas já geradas
    tentativas_max = ne  # Limitar o número de tentativas ao valor de `ne`

    print(f"Gerando {ne} entradas entre {start_date.date()} e {end_date.date()}")

    while insercoes_realizadas < ne and tentativas_max > 0:
        current_date = random_date(start_date, end_date).date()  # Gerar apenas a parte da data

        # Verificar se a data já foi gerada nesta execução
        if current_date in datas_geradas:
            print(f"Data {current_date} já foi gerada anteriormente. Gerando nova data.")
            tentativas_max -= 1  # Diminuir o número de tentativas restantes
            continue

        # Verificar se a data já existe no banco (em ambas as tabelas)
        if verificar_data_existente(cursor, current_date):
            print(f"Data {current_date} já existe no banco. Gerando nova data.")
            tentativas_max -= 1  # Diminuir o número de tentativas restantes
            continue

        print(f"Gerando dados para a data: {current_date}")

        # Gerar dados para a tabela sensor_data
        temp_sensor = random.uniform(20, 40)
        hum_sensor = random.uniform(30, 70)
        ph_value = random.uniform(4, 8)
        button_p_state = random.choice([0, 1])
        button_k_state = random.choice([0, 1])

        # Inserir os dados na tabela sensor_data
        inserido = insert_data_sensor_data(cursor, conn, current_date, temp_sensor, hum_sensor, ph_value, button_p_state, button_k_state)
        if inserido:
            insercoes_realizadas += 1  # Incrementar apenas se a inserção for bem-sucedida
            datas_geradas.add(current_date)  # Adicionar a data ao conjunto de datas já geradas

            # Gerar condições climáticas aleatórias
            temp_climatic = random.uniform(10, 40)
            hum_climatic = random.uniform(20, 80)
            clima = random.choice(['Nublado', 'Chuvoso', 'Ensolarado', 'Nuvens Esparsas'])

            # Inserir dados de condições climáticas aleatórias
            insert_data_condicoes_climaticas(cursor, conn, current_date, temp_climatic, hum_climatic, clima)

        print(f"Inserções realizadas: {insercoes_realizadas}/{ne}")

        tentativas_max -= 1  # Diminuir o número de tentativas restantes

    if tentativas_max == 0:
        print("Limite de tentativas excedido. Não foi possível gerar mais inserções.")

# Função principal
if __name__ == "__main__":
    # Definir e processar argumentos da linha de comando
    parser = argparse.ArgumentParser(description="Script para gerar e inserir dados no Oracle.")
    parser.add_argument('-ne', type=int, help="Número de entradas a serem inseridas (opcional).", default=1)
    parser.add_argument('--start_date', type=lambda s: datetime.strptime(s, '%Y-%m-%d'), help="Data de início no formato YYYY-MM-DD.", default=datetime.now())
    parser.add_argument('--end_date', type=lambda s: datetime.strptime(s, '%Y-%m-%d'), help="Data de fim no formato YYYY-MM-DD.", default=datetime.now())
    args = parser.parse_args()

    # Conectar ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Gerar e inserir dados no banco de dados
    gerar_e_inserir_dados(cursor, conn, args.start_date, args.end_date, args.ne)

    # Fechar a conexão
    cursor.close()
    conn.close()
