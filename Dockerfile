FROM python:3.10-slim

# Instala Chrome e ChromeDriver fixos
RUN apt-get update && apt-get install -y wget unzip curl gnupg ca-certificates \
    fonts-liberation libnss3 libxss1 libappindicator3-1 libasound2 \
    libatk-bridge2.0-0 libgtk-3-0 libu2f-udev libvulkan1 xdg-utils && \
    wget -q https://storage.googleapis.com/chrome-for-testing-public/122.0.6261.111/linux/x64/chrome-linux64.zip && \
    unzip chrome-linux64.zip && mv chrome-linux64 /opt/chrome && ln -s /opt/chrome/chrome /usr/bin/google-chrome && \
    wget -q https://storage.googleapis.com/chrome-for-testing-public/122.0.6261.111/linux/x64/chromedriver-linux64.zip && \
    unzip chromedriver-linux64.zip && mv chromedriver-linux64/chromedriver /usr/local/bin/ && chmod +x /usr/local/bin/chromedriver && \
    apt-get clean && rm -rf /var/lib/apt/lists/* *.zip chromedriver-linux64

ENV CHROME_BIN=/usr/bin/google-chrome
ENV PATH="/usr/local/bin:${PATH}"

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
