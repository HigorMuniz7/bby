FROM python:3.10-slim

# Instala dependências
RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg ca-certificates \
    fonts-liberation libnss3 libxss1 libappindicator3-1 libasound2 \
    libatk-bridge2.0-0 libgtk-3-0 libu2f-udev libvulkan1 xdg-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Instala versão específica do Chrome e ChromeDriver (compatíveis entre si)
RUN wget -q https://storage.googleapis.com/chrome-for-testing-public/122.0.6261.111/linux/x64/chrome-linux64.zip && \
    unzip chrome-linux64.zip && \
    mv chrome-linux64 /opt/chrome && \
    ln -s /opt/chrome/chrome /usr/bin/google-chrome && \
    rm chrome-linux64.zip

RUN wget -q https://storage.googleapis.com/chrome-for-testing-public/122.0.6261.111/linux/x64/chromedriver-linux64.zip && \
    unzip chromedriver-linux64.zip && \
    mv chromedriver-linux64/chromedriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf chromedriver-linux64.zip chromedriver-linux64

# Variáveis de ambiente para o Chrome
ENV CHROME_BIN=/usr/bin/google-chrome
ENV PATH="/usr/local/bin:${PATH}"

# Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código
COPY . .

CMD ["python", "bot.py"]
