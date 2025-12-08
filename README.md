<p align="center">
  <img src="banner.png" width="100%">
</p>

<h1 align="center">💹 CRYPTO MONITOR</h1>

<p align="center">
  <img src="logo.png" width="180">
</p>

<p align="center">
  <a><img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python"></a>
  <a><img src="https://img.shields.io/badge/PyQt6-GUI-green?style=for-the-badge&logo=qt"></a>
  <a><img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge"></a>
</p>

---

# ⚠️ Aviso
**Status do Projeto:** Em desenvolvimento.

Aplicação desktop desenvolvida em **Python + PyQt6** para monitoramento em tempo real de **criptomoedas** utilizando **WebSockets da API oficial da Binance**.  
O sistema exibe **preços atualizados**, **volume**, **variação percentual**, **máximas/mínimas**, e permite configurar **alertas personalizados**.

---

# ✅ Funcionalidades

### 📊 Monitoramento em tempo real
- Preços atualizados em tempo real (via WebSocket)
- Volume de mercado
- Variação percentual 24h
- Máximas e mínimas do dia

### 🔔 Sistema de Alertas
- Criação de alertas personalizados por preço
- Notificações visuais
- Histórico de alertas disparados

### 📈 Dashboard interativo
- Interface moderna criada com PyQt6
- Gráficos e indicadores
- Tabela dinâmica com preços

---

# 🛠️ Tecnologias Utilizadas

| Categoria | Tecnologia |
|----------|------------|
| **Linguagem** | Python |
| **GUI** | PyQt6 |
| **Comunicação** | WebSockets |
| **Banco de Dados** | SQLite |
| **Controle de Versão** | Git & GitHub |

---

# 🚀 Como executar o projeto

## 1️⃣ Clone o repositório
```bash
git clone https://github.com/MatheusPereiira/projeto-crypto-monitor.git
cd projeto-crypto-monitor
```

## 2️⃣ Crie um ambiente virtual
```bash
python -m venv venv
```

### Ativar ambiente:

**Windows:**
```bash
.\venv\Scripts\activate
```

**Linux/MacOS:**
```bash
source venv/bin/activate
```

## 3️⃣ Instale as dependências
```bash
pip install -r requirements.txt
```

## 4️⃣ Execute o aplicativo
```bash
python main.py
```

---

# 📂 Estrutura do Projeto

```bash
projeto_crypto/
├── core/               # Lógica principal e comunicação com API
├── ui/                 # Telas do PyQt6
├── resources/          # Arquivos JSON e dados
├── banner.png          # Banner mostrado no README
├── logo.png            # Logo do projeto
├── main.py             # Arquivo principal
├── requirements.txt    # Dependências
└── README.md
```

---

# 📄 Licença
Este projeto está licenciado sob a **MIT License**.  
Você pode usar, modificar e distribuir livremente.

---

# 👤 Autor
**Matheus Pereira**  
🔥 Apaixonado por Python, automação e desenvolvimento desktop.  
📬 GitHub: https://github.com/MatheusPereiira  

---

