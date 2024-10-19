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

# Função para calcular o volume de água com base na umidade
# Função para calcular o volume de água com base na umidade do solo e do clima
# Função para calcular o volume de água com base na umidade do solo, do clima e nas temperaturas
calcular_volume_agua <- function(merged_data) {
  # Normalizar a umidade do solo e do clima para o cálculo do volume de água
  min_humidity_solo <- min(merged_data$HUMIDITY, na.rm = TRUE)
  max_humidity_solo <- max(merged_data$HUMIDITY, na.rm = TRUE)
  
  min_humidity_clima <- min(merged_data$UMIDADE, na.rm = TRUE)
  max_humidity_clima <- max(merged_data$UMIDADE, na.rm = TRUE)

  # Criar um fator de ajuste com base na temperatura
  fator_temp_solo <- 1 + (merged_data$TEMPERATURE - 20) / 100  # Quanto maior a temperatura do solo, maior o fator (aumenta em 1% para cada grau acima de 20°C)
  fator_temp_clima <- 1 + (merged_data$TEMPERATURA - 20) / 100  # Quanto maior a temperatura do clima, maior o fator (aumenta em 1% para cada grau acima de 20°C)
  
  # Fator clima para umidade alta reduzindo a necessidade de irrigação
  fator_clima <- ifelse(merged_data$UMIDADE > 60, 0.5, 1)  # Reduz a necessidade de irrigação em 50% se o clima estiver úmido
  
  # Cálculo do volume de água ajustado pela umidade e temperatura
  merged_data <- merged_data %>%
    mutate(volume_agua = fator_clima * fator_temp_solo * fator_temp_clima * 
                         (15 - 10 * ((HUMIDITY - min_humidity_solo) / (max_humidity_solo - min_humidity_solo))))
  
  return(merged_data)
}

# Função para gerar o gráfico com volume de água e salvar em PNG (gráfico de linha) # nolint: line_length_linter.
gerar_grafico_png <- function(merged_data, file_name = GRAPH_PATH) {
  # Definir o dispositivo gráfico para PNG
  png(file_name, width = 800, height = 600)
  
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
  
  # Carregar os dados
  merged_data <- carregar_dados(con)
  
  # Realizar a análise de irrigação e calcular o volume de água
  merged_data <- analise_irrigacao(merged_data)
  
  # Filtrar os dados com base no intervalo de datas
  merged_data <- filtrar_por_data(merged_data, start_date, end_date)
  
  # Calcular o volume de água necessário por metro quadrado
  merged_data <- calcular_volume_agua(merged_data)
  
  # Gerar e salvar o gráfico em PNG
  gerar_grafico_png(merged_data, GRAPH_PATH)
  
  # Fechar a conexão
  dbDisconnect(con)
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
