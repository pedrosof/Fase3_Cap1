import cx_Oracle
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
from sqlalchemy import create_engine
import configparser
import os
import subprocess
import base64

# Definir o caminho do Rscript e do script R que será executado
RSCRIPT_PATH = "/usr/local/bin/Rscript"  # Ajuste conforme o local do Rscript no seu sistema
SCRIPT_R_PATH = "/Users/pedrosof/Documents/FIAP/Trabalhos/Fase3_Cap1/LigaBomba.R"  # Ajuste o caminho para o seu script R
GRAPH_PATH = "/Users/pedrosof/Documents/FIAP/Trabalhos/Fase3_Cap1/LigaBomba.png"  # Caminho para o arquivo PNG gerado pelo R

# Verificar o caminho do arquivo de configuração
config_path = 'config/config.cfg'

if not os.path.exists(config_path):
    print(f"Arquivo de configuração não encontrado: {config_path}")
else:
    # Ler o arquivo de configuração
    config = configparser.ConfigParser()
    config.read(config_path)

    if 'Database' not in config:
        print("Seção [Database] não encontrada no arquivo de configuração.")
    else:
        db_username = config.get('Database', 'username')
        db_password = config.get('Database', 'password')
        db_host = config.get('Database', 'host')
        db_port = config.get('Database', 'port')
        db_service_name = config.get('Database', 'service_name')

        connection_string = f'oracle+cx_oracle://{db_username}:{db_password}@{db_host}:{db_port}/?service_name={db_service_name}'

        cx_Oracle.init_oracle_client(lib_dir="/Users/pedrosof/Downloads/instantclient_23_3")
        engine = create_engine(connection_string)

# Consulta SQL corrigida
query = """
    SELECT reading_date, temperature, humidity, ph_value, button_p_pressed, button_k_pressed, clima_temperatura, clima_umidade, condicao_clima, data_coleta
    FROM (
        SELECT sd.reading_date, 
               sd.temperature, 
               sd.humidity, 
               sd.ph_value, 
               sd.button_p_pressed,  
               sd.button_k_pressed,  
               cc.temperatura AS clima_temperatura, 
               cc.umidade AS clima_umidade, 
               cc.clima AS condicao_clima,
               cc.data_coleta
        FROM sensor_data sd
        LEFT JOIN condicoes_climaticas cc 
        ON TRUNC(sd.reading_date) = TRUNC(cc.data_coleta)

        UNION ALL

        SELECT cc.data_coleta AS reading_date,
               NULL AS temperature,
               NULL AS humidity,
               NULL AS ph_value,
               NULL AS button_p_pressed,
               NULL AS button_k_pressed,
               cc.temperatura AS clima_temperatura,
               cc.umidade AS clima_umidade,
               cc.clima AS condicao_clima,
               cc.data_coleta
        FROM condicoes_climaticas cc
        WHERE NOT EXISTS (SELECT 1 FROM sensor_data sd WHERE TRUNC(sd.reading_date) = TRUNC(cc.data_coleta))
    )
    ORDER BY reading_date
"""

# Ler os dados em um DataFrame do pandas
df = pd.read_sql(query, con=engine)

# Renomear as colunas para facilitar o uso
df.rename(columns={
    'temperature': 'temperatura',
    'humidity': 'umidade',
    'clima_temperatura': 'clima_temperatura',
    'clima_umidade': 'clima_umidade'
}, inplace=True)

# Usar a coluna `data_coleta` como data se `reading_date` estiver nula
df['reading_date'] = df['reading_date'].fillna(df['data_coleta'])

# Inicializar o aplicativo Dash
app = dash.Dash(__name__)

# Layout do Dashboard com DatePicker no topo e gráficos organizados em 2 colunas
app.layout = html.Div(children=[
    html.H1(children='Dashboard de Monitoramento de Sensores e Condições Climáticas'),

    dcc.DatePickerRange(
        id='date-picker-range',
        start_date=df['reading_date'].min(),
        end_date=df['reading_date'].max(),
        display_format='YYYY-MM-DD',
        style={'margin-bottom': '20px'}
    ),

    # Colunas para os gráficos em layout 2 colunas
    html.Div([
        html.Div([
            dcc.Graph(id='graph-button-presses')  # Gráfico de colunas para botões P e K
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'}),
        
        html.Div([
            dcc.Graph(id='graph-temp-hum')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'}),
    ]),

    html.Div([
        html.Div([
            dcc.Graph(id='graph-ph')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'}),
        
        html.Div([
            dcc.Graph(id='graph-climate')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'}),
    ]),

    # Colunas para os gráficos de eventos climáticos em layout 2 colunas
    html.Div([
        html.Div([
            dcc.Graph(id='graph-weather-events')  # Gráfico de eventos climáticos
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'}),
        
        html.Div([
            html.Img(id='graph-irrigation', style={'width': '100%', 'display': 'inline-block'})
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'})
    ]),
])

# Callback para atualizar os gráficos e chamar o script R com base no intervalo de datas selecionado
@app.callback(
    [Output('graph-irrigation', 'src'),
     Output('graph-button-presses', 'figure'),
     Output('graph-temp-hum', 'figure'),
     Output('graph-ph', 'figure'),
     Output('graph-climate', 'figure'),
     Output('graph-weather-events', 'figure')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_graphs(start_date, end_date):
    # Convertendo para datetime para garantir que o tipo de dado esteja correto
    df['reading_date'] = pd.to_datetime(df['reading_date'])
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Chamar o script R passando as datas selecionadas como parâmetros
    subprocess.run([RSCRIPT_PATH, SCRIPT_R_PATH, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')])

    # Verificar se o arquivo de gráfico foi gerado e retornar sua URL
    if os.path.exists(GRAPH_PATH):
        graph_irrigation_src = f"data:image/png;base64,{base64.b64encode(open(GRAPH_PATH, 'rb').read()).decode()}"
    else:
        graph_irrigation_src = ""

    # Filtrar os dados com base no intervalo de datas selecionado
    filtered_df = df[(df['reading_date'] >= start_date) & (df['reading_date'] <= end_date)]

    if filtered_df.empty:
        return graph_irrigation_src, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Gráfico de Botões P e K
    button_p_count = filtered_df['button_p_pressed'].sum()
    button_k_count = filtered_df['button_k_pressed'].sum()

    button_data = pd.DataFrame({
        'Botão': ['P', 'K'],
        'Pressionamentos': [button_p_count, button_k_count]
    })

    fig_button_presses = px.bar(button_data, x='Botão', y='Pressionamentos', 
                                title="Total de Pressionamentos dos Botões P e K")

    # Gráfico de Temperatura e Umidade do Solo ao longo do Tempo
    df_melted = pd.melt(filtered_df, id_vars=['reading_date'], value_vars=['temperatura', 'umidade'], 
                        var_name='Tipo', value_name='Valores')
    fig_temp_hum = px.line(df_melted, x='reading_date', y='Valores', color='Tipo',
                           title="Temperatura e Umidade do Solo ao Longo do Tempo")

    # Gráfico de Nível de pH do Solo ao longo do Tempo
    fig_ph = px.line(filtered_df, x='reading_date', y='ph_value', 
                     title="Nível de pH do Solo ao Longo do Tempo")

    # Gráfico de Condições Climáticas (Temperatura e Umidade Climática)
    df_climate_melted = pd.melt(filtered_df, id_vars=['reading_date'], 
                                value_vars=['clima_temperatura', 'clima_umidade'], 
                                var_name='Tipo', value_name='Valores')
    fig_climate = px.line(df_climate_melted, x='reading_date', y='Valores', color='Tipo',
                          title="Temperatura e Umidade Climática ao longo do Tempo")

    # Gráfico de totalização de eventos de clima
    weather_event_counts = filtered_df['condicao_clima'].value_counts()
    fig_weather_events = px.bar(x=weather_event_counts.index, y=weather_event_counts.values,
                                labels={'x': 'Condição Climática', 'y': 'Total de Eventos'},
                                title="Totalização de Eventos Climáticos no Período")

    return graph_irrigation_src, fig_button_presses, fig_temp_hum, fig_ph, fig_climate, fig_weather_events

# Rodar o servidor do Dash
if __name__ == '__main__':
    app.run_server(debug=True)
