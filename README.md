
# FIAP - Faculdade de Informática e Administração Paulista
[![FIAP Logo](images/logo-fiap.png)](https://www.fiap.com.br)

## Fase 3 Cap 1 – Construindo uma máquina agrícola

### Grupo 10

👨‍🎓 **Integrantes**:
- [Fabio Marcos Pedroso Filho](https://www.linkedin.com/in/pedrosof/)

👩‍🏫 **Professores**:

**Tutor(a)**:
- [Lucas Gomes Moreira](https://www.linkedin.com/in/lucas-gomes-moreira-15a8452a/)

**Coordenador(a)**:
- [Andre Godoi, PhD](https://www.linkedin.com/in/profandregodoi/)

---

## 📜 Descrição

O objetivo deste projeto é a criação de um sistema de **monitoramento** e **análise de dados** de sensores de solo e condições climáticas, utilizando duas abordagens complementares: uma para a geração de um **dashboard interativo** e outra para os **cálculos de irrigação**.

### Primeiro Código: Python com Dash e R
Este código utiliza **Python** e a biblioteca **Dash** para criar um **dashboard interativo**, que permite visualizar dados de sensores de solo e condições climáticas. O sistema se conecta a um banco de dados Oracle para obter informações sobre **temperatura**, **umidade**, **pH do solo**, e dados climáticos como **temperatura**, **umidade**, e a **condição climática**. 

O código:
- Lê as configurações do banco de dados a partir de um arquivo de configuração.
- Executa uma consulta SQL para combinar dados de sensores e clima.
- Processa esses dados com **Pandas**.
- Exibe gráficos interativos no dashboard, que mostram a variação de diferentes variáveis como temperatura e eventos climáticos.
- Utiliza um script **R** para calcular o volume de água necessário para irrigação e exibe o gráfico gerado no dashboard.

### Segundo Código: R com Análise e Gráficos
O código em **R** conecta-se ao banco de dados Oracle, carrega dados de sensores de solo e condições climáticas, e calcula o volume de água necessário para irrigação. Ele utiliza ajustes baseados em fatores como **temperatura** e **umidade** para determinar **quando** e **quanto irrigar**.

Após realizar os cálculos, o código gera um gráfico de linha que mostra o volume de água necessário ao longo do tempo, salvando-o como um arquivo **PNG** que pode ser exibido no dashboard do primeiro código.

### Resumo Conjunto
Esses dois códigos trabalham juntos para construir um sistema completo de **monitoramento e análise de dados agrícolas**. O **Python** com **Dash** é utilizado para a visualização e interação com o usuário, enquanto o **R** faz os cálculos detalhados de irrigação. O sistema facilita a tomada de decisões sobre irrigação, visualizando tanto os dados de solo quanto as condições climáticas, além de gerar gráficos que mostram a quantidade de água necessária em diferentes cenários.

- **Dados Climáticos**: Obtidos através da API pública [OpenWeather](https://openweathermap.org/).
- **Dados do Solo**: Capturados por sensores desenvolvidos no site [Wokwi](https://wokwi.com/).
- **Projeto do Sensor**: O projeto do sensor criado está disponível em: [Wokwi Project](https://wokwi.com/projects/412014758291630081).

![Wokwi Sensor](images/wokwi.jpg)

---

## 📁 Estrutura de Pastas

- **config**: Arquivos de configuração.
- **README.md**: Este arquivo com a explicação geral sobre o projeto.
- **wokwi**: Código fonte e JSON do diagrama do sensor de solo.
- **images**: Imagens documentacionais.

---

## 🔧 Como Executar o Código

Para executar o código, siga os passos abaixo:

1. Tenha um banco de dados Oracle configurado e instalado.
2. Utilize Python 3.12.

### Scripts Principais:

- **Install.py**: Cria a estrutura do banco de dados.
- **Dashboard.py**: Exibe gráficos dos dados obtidos.
- **LigaBomba.R**: Calcula o volume de água necessário para irrigação.
- **SimulaEntradas.py**: Gera dados para o dia atual e entradas aleatórias para datas anteriores.

### Instalação:

Os scripts requerem a instalação do [Oracle Instant Client](https://www.oracle.com/br/database/technologies/instant-client.html).

Após a instalação, ajuste o caminho no script Python:

```python
cx_Oracle.init_oracle_client(lib_dir="/Path/to/Oracle/instantclient")
```

---

## 🗃 Histórico de Lançamentos

```markdown
- **0.1.0** – 17/10/2024: *Versão Inicial*
```

---

## 📋 Licença

Este projeto está licenciado sob os termos da licença **GPL**.
