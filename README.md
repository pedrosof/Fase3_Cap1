FIAP - Faculdade de Informática e Administração Paulista
![alt text](images/logo-fiap.png)

Fase 3 Cap 1 – Construindo uma máquina agrícola

Grupo 10

👨‍🎓 Integrantes:
•	Fabio Marcos Pedroso Filho

👩‍🏫 Professores:
Tutor(a)
•	Lucas Gomes Moreira
Coordenador(a)
•	Andre Godoi, PhD

📜 Descrição
O projeto tem como base a análise de sensores de umidade, temperatura e pH de solo e umidade e temperatura do clima para quantificar o volume de água necessário para irrigar 1 metro quadrado de plantação.

Os dados climáticos são obtidos através da API pública OpenWeather.

Os dados do Solo são obtidos através de Sensores criados no site Wokwi. 
O Projeto do Sensor criado está disponível em: https://wokwi.com/projects/412014758291630081

![alt text](images/wokwi.jpg)

📁 Estrutura de pastas
Dentre os arquivos e pastas presentes na raiz do projeto, definem-se:
•	config: Arquivos de configuração
•	README.md: arquivo que serve como guia e explicação geral sobre o projeto (o mesmo que você está lendo agora).
•	wokwi: Código fonte e JSON do diagrama do sensor de solo. 

🔧 Como executar o código
O código é de simples utilização. Você precisará de um banco de dados Oracle e python 3.12.

Install.py – Cria a estrutura do banco de dados.
Dashboard.py – Script que mostra gráficos dos dados obtidos.
LigaBomba.R – Script que faz o cálculo do volume de água necessário para irrigação.
SimulaEntradas.py – Script que gera dados para o dia de hoje e entradas aleatórios em datas anteriores.

Os scripts requerem a instalação do Oracle Instant Client https://www.oracle.com/br/database/technologies/instant-client.html

Depois de instalado, os script python precisam ser ajustados em:

cx_Oracle.init_oracle_client(lib_dir="/Path/to/Oracle/instantclient")

🗃 Histórico de lançamentos
•	0.4.0 – 19/10/2024 * Correção de bugs no Simulador.
•	0.3.0 – 19/10/2024 * Criação do Simulador
•	0.2.0 – 18/10/2024 * Criação do Dashboard
•	0.1.0 – 17/10/2024 * Versão Inicial

📋 Licença
GPL


