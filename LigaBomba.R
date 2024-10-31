# Instalar pacotes necessários (se ainda não estiverem instalados)
# install.packages("DBI") # nolint
# install.packages("RJDBC") # nolint
# install.packages("dplyr")
# install.packages("ggplot2")

# Carregar bibliotecas necessárias
library(DBI)
library(RJDBC)
library(dplyr)
library(ggplot2)

# Definir o caminho para o arquivo PNG onde o gráfico será salvo
GRAPH_PATH <- "/Users/pedrosof/Documents/FIAP/Trabalhos/Fase3_Cap1/LigaBomba.png"  # Ajuste o caminho conforme necessário

# Definir o caminho para o driver JDBC do Oracle (ajuste conforme necessário)
drv <- JDBC(driverClass = "oracle.jdbc.OracleDriver", 
            classPath = "/Users/pedrosof/Downloads/instantclient_23_3/ojdbc8.jar")  # Ajuste o caminho para o driver JDBC

# Função para conectar ao banco de dados usando RJDBC
conectar_banco <- function() {
  # Conectar ao banco de dados Oracle usando JDBC
  con <- dbConnect(drv, 
                   "jdbc:oracle:thin:@//oracle.fiap.com.br:1521/ORCL",  # URL de conexão
                   "rm560665",  # Usuário do banco
                   "280678")    # Senha do banco
  return(con)
}

# Função para carregar os dados de sensor_data e condicoes_climaticas
carregar_dados <- function(con) {
  # Query SQL para buscar os dados
  sensor_data_query <- "SELECT * FROM sensor_data"
  condicoes_climaticas_query <- "SELECT * FROM condicoes_climaticas"
  
  # Carregar os dados em dataframes
  sensor_data <- dbGetQuery(con, sensor_data_query)
  condicoes_climaticas <- dbGetQuery(con, condicoes_climaticas_query)
  
  # Renomear a coluna "READING_DATE" para "DATA_COLETA"
  colnames(sensor_data)[colnames(sensor_data) == "READING_DATE"] <- "DATA_COLETA"

  # Mesclar as tabelas com base na coluna "DATA_COLETA"
  merged_data <- merge(sensor_data, condicoes_climaticas, by = "DATA_COLETA", all = TRUE)
  
  return(merged_data)
}

# Função para criar a variável 'irrigar' e ajustar o modelo de regressão
analise_irrigacao <- function(merged_data) {
  # Remover linhas com valores ausentes
  merged_data <- na.omit(merged_data)
  
  # Criar a variável 'irrigar' com base nas condições ajustadas
  merged_data <- merged_data %>%
    mutate(irrigar = ifelse(
      (CLIMA %in% c("ensolarado", "nublado", "nuvens esparsas") & 
         TEMPERATURA > 20 &   # Relaxamos de 25 para 20
         UMIDADE < 50 &       # Relaxamos de 40 para 50
         TEMPERATURE < 35 &   # Relaxamos de 30 para 35
         HUMIDITY < 50), 1, 0))  # Relaxamos de 30 para 50
  
  return(merged_data)
}

# Função para calcular o volume de água com base na umidade do solo, do clima e nas temperaturas
calcular_volume_agua <- function(merged_data) {
  # Normalizar a umidade do solo para ajustar o cálculo do volume de água
  min_humidity_solo <- min(merged_data$HUMIDITY, na.rm = TRUE)  # Umidade mínima registrada no solo
  max_humidity_solo <- max(merged_data$HUMIDITY, na.rm = TRUE)  # Umidade máxima registrada no solo
  
  # Fatores de ajuste para necessidade de irrigação com base nas condições climáticas
  # Quanto mais úmido o clima (ex.: chuva ou neblina), menor o volume de água necessário
  fator_clima <- case_when(
    merged_data$CLIMA %in% c('chuva leve', 'chuva moderada', 'chuva intensa', 'chuva extrema') ~ 0.3,  # Reduz para 30%
    merged_data$CLIMA %in% c('névoa', 'neblina', 'fumaça') ~ 0.7,  # Reduz para 70%
    merged_data$CLIMA %in% c('nublado', 'nuvens quebradas') ~ 0.9,  # Reduz para 90%
    TRUE ~ 1  # Climas secos ou "céu limpo" mantêm o volume em 100%
  )
  
  # Ajuste da necessidade de água com base na temperatura do solo
  # Cada grau acima de 20°C aumenta a necessidade em 1%
  fator_temp_solo <- 1 + (merged_data$TEMPERATURE - 20) / 100
  # Ajuste adicional para temperatura ambiente (clima)
  fator_temp_clima <- 1 + (merged_data$TEMPERATURA - 20) / 100
  
  # Obter umidade do solo e do clima do dia anterior
  # Considera valores médios se o valor do dia anterior não estiver disponível
  umidade_solo_anterior <- lag(merged_data$HUMIDITY, 1, default = mean(merged_data$HUMIDITY, na.rm = TRUE))
  umidade_clima_anterior <- lag(merged_data$UMIDADE, 1, default = mean(merged_data$UMIDADE, na.rm = TRUE))
  
  # Redução na necessidade de irrigação com base na umidade do dia anterior
  # Se a umidade do solo ou do clima do dia anterior for alta (> 60%), reduz o volume em 30%
  fator_umidade_anterior <- ifelse((umidade_solo_anterior > 60 | umidade_clima_anterior > 60), 0.7, 1)

  # Cálculo final do volume de água
  # A fórmula multiplica fatores ajustados pelo fator climático e de umidade
  # A base de cálculo do volume é 15 litros, reduzido dinamicamente pela umidade do solo atual
  merged_data <- merged_data %>%
    mutate(volume_agua = fator_umidade_anterior * fator_clima * fator_temp_solo * fator_temp_clima * 
                         (15 - 10 * ((HUMIDITY - min_humidity_solo) / (max_humidity_solo - min_humidity_solo))))
  
  return(merged_data)
}

# Função para gerar o gráfico com volume de água e salvar em PNG com melhor qualidade
gerar_grafico_png <- function(merged_data, file_name = GRAPH_PATH) {
  # Definir o dispositivo gráfico para PNG com alta resolução
  png(file_name, width = 1600, height = 1200, res = 300)  # Aumente a largura, altura e resolução para melhor qualidade
  
  # Verificar se os dados estão disponíveis para a criação do gráfico
  if (!is.null(merged_data) && nrow(merged_data) > 0) {
    # Gerar o gráfico de volume de água para irrigação (gráfico de linha)
    plot <- ggplot(merged_data, aes(x = DATA_COLETA, y = volume_agua)) +
      geom_line(color = "blue") +  # Gráfico de linha para volume de água
      labs(title = "Volume de Água para Irrigação por Metro Quadrado", 
           x = "Data", 
           y = "Volume de Água (litros)") +
      theme_minimal()
    
    # Imprimir o gráfico no PNG
    print(plot)
  } else {
    print("Nenhum dado disponível para gerar o gráfico.")
  }
  
  # Fechar o dispositivo gráfico, salvando o arquivo PNG
  dev.off()
  
  print(paste("Gráfico salvo em:", file_name))
}

# Função para filtrar o dataframe com base no intervalo de datas
filtrar_por_data <- function(merged_data, start_date, end_date) {
  # Converter as colunas de data para o tipo Date
  merged_data$DATA_COLETA <- as.Date(merged_data$DATA_COLETA)
  
  # Filtrar os dados com base no intervalo de datas
  filtered_data <- merged_data %>%
    filter(DATA_COLETA >= as.Date(start_date) & DATA_COLETA <= as.Date(end_date))
  
  return(filtered_data)
}

# Função principal para executar o script com intervalo de datas como parâmetro
main <- function(start_date, end_date) {
  # Conectar ao banco de dados
  con <- conectar_banco()
  
  # Carregar todas as datas já existentes na tabela 'irrigacao' dentro do intervalo fornecido
  query <- sprintf("SELECT data_irrigacao FROM irrigacao WHERE data_irrigacao BETWEEN TO_DATE('%s', 'YYYY-MM-DD') AND TO_DATE('%s', 'YYYY-MM-DD')",
                   start_date, end_date)
  datas_existentes <- dbGetQuery(con, query)
  datas_existentes <- as.Date(datas_existentes$DATA_IRRIGACAO)  # Converter para o formato Date

  # Carregar e processar os dados necessários
  merged_data <- carregar_dados(con)
  merged_data <- analise_irrigacao(merged_data)
  merged_data <- filtrar_por_data(merged_data, start_date, end_date)
  merged_data <- calcular_volume_agua(merged_data)
  
  # Converter DATA_COLETA de merged_data para Date
  merged_data$DATA_COLETA <- as.Date(merged_data$DATA_COLETA)

  # Criar uma cópia filtrada de merged_data para inserções no banco de dados
  merged_data_filtrado <- merged_data[!merged_data$DATA_COLETA %in% datas_existentes, ]
  
  # Inserir apenas as datas que faltam no banco de dados
  if (nrow(merged_data_filtrado) > 0) {
    for (i in 1:nrow(merged_data_filtrado)) {
      data_irrigacao <- as.character(merged_data_filtrado$DATA_COLETA[i])
      volume_agua <- merged_data_filtrado$volume_agua[i]
      salvar_dados_irrigacao(con, data_irrigacao, volume_agua)
    }
  } else {
    print("Todas as datas do intervalo já têm dados de irrigação.")
  }

  # Gerar e salvar o gráfico em PNG com os dados completos de `merged_data`
  gerar_grafico_png(merged_data, GRAPH_PATH)

  # Fechar a conexão
  dbDisconnect(con)
}


# Função para salvar dados de irrigação no banco
salvar_dados_irrigacao <- function(con, data_irrigacao, volume_agua) {
  query <- sprintf("INSERT INTO irrigacao (data_irrigacao, volume_agua)
                    VALUES (TO_DATE('%s', 'YYYY-MM-DD'), %f)", 
                    data_irrigacao, volume_agua)
  dbSendUpdate(con, query)
  print(paste("Dados de irrigação inseridos para a data:", data_irrigacao))
}

# Capturar os argumentos da linha de comando (start_date e end_date)
args <- commandArgs(trailingOnly = TRUE)

# Verificar se as datas foram fornecidas como argumentos
if (length(args) != 2) {
  stop("Erro: Você precisa fornecer as datas de início e fim no formato YYYY-MM-DD.")
}

# Definir as variáveis start_date e end_date a partir dos argumentos
start_date <- args[1]
end_date <- args[2]

# Executar o script principal passando as datas de início e fim
main(start_date, end_date)

