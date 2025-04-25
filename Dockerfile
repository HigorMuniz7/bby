
FROM python:3.11-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg2 fonts-liberation libnss3 libxss1 libasound2 libatk1.0-0 \
    libatk-bridge2.0-0 libcups2 libdbus-1-3 libdrm2 libgbm1 libnspr4 \
    libxcomposite1 libxdamage1 libxrandr2 xdg-utils && \
    rm -rf /var/lib/apt/lists/*

# Instala o Google Chrome (versão estável atual)
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb

# Instala o ChromeDriver fixo compatível (v122)
RUN CHROMEDRIVER_VERSION=122.0.6261.111 && \
    wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin && \
    rm /tmp/chromedriver.zip

# Cria diretório do app
WORKDIR /app

# Copia os arquivos do projeto
COPY . .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Comando para rodar o bot
CMD ["python", "bot.py"]
