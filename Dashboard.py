# Importação das bibliotecas necessárias
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

    # Verificar se a seção [Database] existe
    if 'Database' not in config:
        print("Seção [Database] não encontrada no arquivo de configuração.")
    else:
        # Configurar parâmetros de conexão com o banco de dados
        db_username = config.get('Database', 'username')
        db_password = config.get('Database', 'password')
        db_host = config.get('Database', 'host')
        db_port = config.get('Database', 'port')
        db_service_name = config.get('Database', 'service_name')

        # Construir a string de conexão com o Oracle
        connection_string = f'oracle+cx_oracle://{db_username}:{db_password}@{db_host}:{db_port}/?service_name={db_service_name}'

        # Inicializar o cliente Oracle e criar o engine SQLAlchemy
        cx_Oracle.init_oracle_client(lib_dir="/Users/pedrosof/Downloads/instantclient_23_3")
        engine = create_engine(connection_string)

# Consulta SQL para coletar dados do sensor e condições climáticas
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

# Ler os dados resultantes em um DataFrame do pandas
df = pd.read_sql(query, con=engine)

# Renomear colunas para melhor compreensão
df.rename(columns={
    'temperature': 'temperatura',
    'humidity': 'umidade',
    'clima_temperatura': 'clima_temperatura',
    'clima_umidade': 'clima_umidade'
}, inplace=True)

# Ajustar `reading_date` para valores nulos, usando `data_coleta` nesses casos
df['reading_date'] = df['reading_date'].fillna(df['data_coleta'])

# Inicializar o aplicativo Dash
app = dash.Dash(__name__)

# Layout do Dashboard
app.layout = html.Div(children=[
    html.H1(children='Dashboard de Monitoramento de Sensores e Condições Climáticas'),

    # DatePicker para selecionar intervalo de datas
    dcc.DatePickerRange(
        id='date-picker-range',
        start_date=df['reading_date'].min(),
        end_date=df['reading_date'].max(),
        display_format='YYYY-MM-DD',
        style={'margin-bottom': '20px'}
    ),

    # Primeira linha de gráficos
    html.Div([
        html.Div([dcc.Graph(id='graph-button-presses')], style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'}),
        html.Div([dcc.Graph(id='graph-temp-hum')], style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'}),
    ]),

    # Segunda linha de gráficos
    html.Div([
        html.Div([dcc.Graph(id='graph-ph')], style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'}),
        html.Div([dcc.Graph(id='graph-climate')], style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'}),
    ]),

    # Terceira linha de gráficos
    html.Div([
        html.Div([dcc.Graph(id='graph-weather-events')], style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'}),
        html.Div([html.Img(id='graph-irrigation', style={'width': '100%', 'display': 'inline-block'})], style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'})
    ]),

    # Quarta linha: gráfico de dispersão e heatmap para condições climáticas
    html.Div([
        html.Div([dcc.Graph(id='graph-climate-scatter')], style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'}),
        html.Div([dcc.Graph(id='graph-climate-heatmap')], style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'}),
    ]),

    # Quinta linha: gráfico de pizza das condições climáticas
    html.Div([
        html.Div([dcc.Graph(id='graph-climate-pie')], style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'}),
    ])
])


# Callback para atualizar gráficos com base no intervalo de datas
@app.callback(
    [Output('graph-irrigation', 'src'),
     Output('graph-button-presses', 'figure'),
     Output('graph-temp-hum', 'figure'),
     Output('graph-ph', 'figure'),
     Output('graph-climate', 'figure'),
     Output('graph-weather-events', 'figure'),
     Output('graph-climate-heatmap', 'figure'),
     Output('graph-climate-pie', 'figure'),
     Output('graph-climate-scatter', 'figure')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)

def update_graphs(start_date, end_date):
    # Convertendo as datas para o tipo datetime
    df['reading_date'] = pd.to_datetime(df['reading_date'])
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Executar o script R com o intervalo de datas como parâmetros
    subprocess.run([RSCRIPT_PATH, SCRIPT_R_PATH, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')])

    # Verificar se o arquivo de gráfico foi gerado e retornar a URL para exibição
    if os.path.exists(GRAPH_PATH):
        graph_irrigation_src = f"data:image/png;base64,{base64.b64encode(open(GRAPH_PATH, 'rb').read()).decode()}"
    else:
        graph_irrigation_src = ""

    # Filtrar os dados pelo intervalo selecionado
    filtered_df = df[(df['reading_date'] >= start_date) & (df['reading_date'] <= end_date)]

    if filtered_df.empty:
        return graph_irrigation_src, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    ## Gráfico de Pizza para proporção de pressionamentos de P e K
    button_data_pie = pd.DataFrame({
        'Botão': ['P', 'K'],
        'Pressionamentos': [filtered_df['button_p_pressed'].sum(), filtered_df['button_k_pressed'].sum()]
    })
    fig_button_presses = px.pie(button_data_pie, names='Botão', values='Pressionamentos', 
                                title="Proporção de Pressionamentos dos Botões P e K")

    # Gráfico de Temperatura e Umidade do Solo ao longo do Tempo
    df_melted = pd.melt(filtered_df, id_vars=['reading_date'], value_vars=['temperatura', 'umidade'], var_name='Tipo', value_name='Valores')
    fig_temp_hum = px.line(df_melted, x='reading_date', y='Valores', color='Tipo', title="Temperatura e Umidade do Solo ao Longo do Tempo")

    # Gráfico de Nível de pH do Solo ao longo do Tempo
    fig_ph = px.line(filtered_df, x='reading_date', y='ph_value', title="Nível de pH do Solo ao Longo do Tempo")

    # Gráfico de Condições Climáticas (Temperatura e Umidade)
    df_climate_melted = pd.melt(filtered_df, id_vars=['reading_date'], value_vars=['clima_temperatura', 'clima_umidade'], var_name='Tipo', value_name='Valores')
    fig_climate = px.line(df_climate_melted, x='reading_date', y='Valores', color='Tipo', title="Temperatura e Umidade Climática ao longo do Tempo")

    # Gráfico de Dispersão para Condições Climáticas (Temperatura vs Umidade)
    fig_climate_scatter = px.scatter(
        filtered_df, 
        x='clima_temperatura', 
        y='clima_umidade', 
        color='condicao_clima',  # Diferencia por condição climática
        title="Dispersão de Temperatura e Umidade para Condições Climáticas",
        labels={'clima_temperatura': 'Temperatura (°C)', 'clima_umidade': 'Umidade (%)'},
        hover_data=['reading_date']  # Mostra a data no hover
    )
    # Gráfico de Heatmap para Condições Climáticas ao longo do Tempo
    climate_heatmap_data = filtered_df[['reading_date', 'condicao_clima']].copy()
    climate_heatmap_data['count'] = 1  # Adiciona uma coluna auxiliar para contagem
    climate_heatmap_data = climate_heatmap_data.groupby(['reading_date', 'condicao_clima']).count().reset_index()

    fig_climate_heatmap = px.density_heatmap(
        climate_heatmap_data, 
        x='reading_date', 
        y='condicao_clima', 
        z='count', 
        color_continuous_scale="Viridis",
        title="Frequência de Condições Climáticas ao Longo do Tempo",
        labels={'count': 'Frequência'}
    )

    # Gráfico de Pizza para Proporção das Condições Climáticas
    climate_counts = filtered_df['condicao_clima'].value_counts().reset_index()
    climate_counts.columns = ['Condicao', 'Frequência']

    fig_climate_pie = px.pie(
        climate_counts, 
        names='Condicao', 
        values='Frequência', 
        title="Proporção das Condições Climáticas"
    )

    # Gráfico de totalização de eventos de clima
    weather_event_counts = filtered_df['condicao_clima'].value_counts()
    fig_weather_events = px.bar(x=weather_event_counts.index, y=weather_event_counts.values, labels={'x': 'Condição Climática', 'y': 'Total de Eventos'}, title="Totalização de Eventos Climáticos no Período")

    return (graph_irrigation_src, fig_button_presses, fig_temp_hum, fig_ph, 
        fig_climate, fig_weather_events, fig_climate_heatmap, fig_climate_pie,
        fig_climate_scatter)

# Iniciar o servidor Dash
if __name__ == '__main__':
    app.run_server(debug=True)
