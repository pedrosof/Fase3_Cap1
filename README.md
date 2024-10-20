
# FIAP - Faculdade de Informática e Administração Paulista
![FIAP Logo](images/logo-fiap.png)

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

O projeto tem como objetivo a análise de sensores de umidade, temperatura e pH do solo, além de umidade e temperatura do clima, para quantificar o volume de água necessário para irrigar 1 metro quadrado de plantação.

- **Dados Climáticos**: Obtidos através da API pública [OpenWeather](https://openweathermap.org/).
- **Dados do Solo**: Capturados por sensores desenvolvidos no site [Wokwi](https://wokwi.com/). 

O Projeto do Sensor criado está disponível em: [Wokwi Project](https://wokwi.com/projects/412014758291630081).

![Wokwi Sensor](images/wokwi.jpg)

---

## 📁 Estrutura de pastas

- **config**: Arquivos de configuração.
- **README.md**: Este arquivo de guia e explicações gerais sobre o projeto.
- **wokwi**: Código fonte e JSON do diagrama do sensor de solo.
- **images**: Imagens documentacionais.

---

## 🔧 Como executar o código

Para executar o código, siga os passos abaixo:

1. Tenha um banco de dados Oracle configurado e instalado.
2. Utilize Python 3.12.

Scripts principais:

- `Install.py`: Cria a estrutura do banco de dados.
- `Dashboard.py`: Exibe gráficos dos dados obtidos.
- `LigaBomba.R`: Calcula o volume de água necessário para irrigação.
- `SimulaEntradas.py`: Gera dados para o dia atual e entradas aleatórias em datas anteriores.

### Instalação:

Os scripts requerem a instalação do [Oracle Instant Client](https://www.oracle.com/br/database/technologies/instant-client.html).

Após a instalação, ajuste o caminho no script Python:

```python
cx_Oracle.init_oracle_client(lib_dir="/Path/to/Oracle/instantclient")
```

---

## 🗃 Histórico de lançamentos

```markdown
- **0.1.0** – 17/10/2024: *Versão Inicial*
```

---

## 📋 Licença

Este projeto está licenciado sob os termos da licença **GPL**.
