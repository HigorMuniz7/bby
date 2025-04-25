import os
import time
import asyncio
import threading
from dotenv import load_dotenv
from telegram import Bot
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

# ========== CONFIG ==========

load_dotenv()

EMAIL = os.getenv("EMAIL") or "higor242@gmail.com"
SENHA = os.getenv("SENHA") or "leads123#"
TOKEN = os.getenv("TOKEN") or "7836456161:AAGUi37b9PcqMOTOUI9wCj6_WXqnE-9l7-s"
CHAT_ID = os.getenv("CHAT_ID") or "@yurimartinsbacbo"
URL = "https://lotogreen.bet.br/play/6286"

bot = Bot(token=TOKEN)

limite_ = '''
PP=B
BB=P
PT=B
BT=P
PBP=B
BPB=P
PBT=B
BPT=P
'''
limite = limite_.strip().split()

entrada = True
green = False
gale = False
red = False
quantidade = 0
gales = 2

estrategy = []
aposta_ = ''
resultados = []
check_resultados = []

# ========== ABRE NAVEGADOR ==========

def iniciar_driver():
    options = Options()
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(options=options)
    driver.get(URL)
    return driver

# ========== LOGIN AUTOMÁTICO ==========

def login_bacbo(driver, email, senha):
    wait = WebDriverWait(driver, 15)

    try:
        idade_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Sim')]")))
        driver.execute_script("arguments[0].click();", idade_btn)
        print("✅ Idade confirmada")
    except TimeoutException:
        print("⚠️ Botão de idade não encontrado")

    try:
        cookies_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Aceitar todos')]")))
        driver.execute_script("arguments[0].click();", cookies_btn)
        print("🍪 Cookies aceitos")
    except TimeoutException:
        print("Nenhum popup de cookies.")

    try:
        entrar_div = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Entrar') and contains(@class, 'cursor-pointer')]")))
        driver.execute_script("arguments[0].click();", entrar_div)
        print("🟢 Botão central 'Entrar' clicado com JavaScript.")
    except Exception as e:
        print("❌ Nenhum botão 'Entrar' encontrado:", e)
        return False

    try:
        email_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Email ou CPF']")))
        senha_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Senha']")))
        print("🔐 Campos de login carregados.")
    except TimeoutException:
        print("Erro: campos de login não carregaram.")
        driver.quit()
        return False

    email_input.send_keys(email)
    senha_input.send_keys(senha)

    try:
        login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@id='legitimuz-action-send-analisys']")))
        driver.execute_script("arguments[0].click();", login_btn)
        print("🔓 Login enviado.")
    except Exception as e:
        print("Erro ao clicar em login:", e)
        driver.quit()
        return False

    time.sleep(5)
    print("✅ Login finalizado com sucesso!")
    return True

# ========== MANTER SESSÃO ATIVA ==========

def simular_atividade(driver):
    def clicar_periodicamente():
        while True:
            try:
                driver.switch_to.default_content()
                iframe_1 = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/main/div/div[1]/div[2]/div/div/section/div[1]/div/div[1]/iframe')
                driver.switch_to.frame(iframe_1)
                iframe_2 = driver.find_element(By.XPATH, '/html/body/div[5]/div[2]/iframe')
                driver.switch_to.frame(iframe_2)

                # Obtém a largura e altura da janela para calcular o centro
                largura = driver.execute_script("return window.innerWidth")
                altura = driver.execute_script("return window.innerHeight")

                centro_x = largura // 2
                centro_y = altura // 2

                ActionChains(driver).move_by_offset(centro_x, centro_y).click().perform()
                ActionChains(driver).move_by_offset(-centro_x, -centro_y).perform()  # Volta para a posição original do mouse

                print("👆 Clique no centro da tela para manter sessão ativa.")
                driver.switch_to.default_content()
            except Exception as e:
                print("⚠️ Erro ao simular clique:", e)
            time.sleep(30)

    threading.Thread(target=clicar_periodicamente, daemon=True).start()

# ========== BUSCAR RESULTADOS ==========

def buscar_resultados(driver):
    driver.switch_to.window(driver.window_handles[0])

    while len(driver.find_elements(By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/main/div/div[1]/div[2]/div/div/section/div[1]/div/div[1]/iframe')) == 0:
        time.sleep(2)

    iframe_1 = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/main/div/div[1]/div[2]/div/div/section/div[1]/div/div[1]/iframe')
    driver.switch_to.frame(iframe_1)

    while len(driver.find_elements(By.XPATH, '/html/body/div[5]/div[2]/iframe')) == 0:
        time.sleep(2)

    iframe_2 = driver.find_element(By.XPATH, '/html/body/div[5]/div[2]/iframe')
    driver.switch_to.frame(iframe_2)

    while len(driver.find_elements(By.XPATH, '/html/body/div[4]/div/div/div[2]/div[6]/div/div[1]/div/div/div')) == 0:
        time.sleep(2)

    resultado = driver.find_element(
        By.XPATH,
        '/html/body/div[4]/div/div/div[2]/div[6]/div/div[1]/div/div/div'
    ).text.split()[::-1][:10]

    return resultado

# ========== ESTRATÉGIA ==========

async def enviar_mensagem(texto):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=texto, parse_mode='Markdown')
    except Exception as e:
        print("❌ Erro ao enviar mensagem:", e)

async def estrategia(results):
    global entrada, green, gale, red, estrategy, aposta_, quantidade

    if entrada:
        for linha in limite:
            estrategy = list(linha.split('=')[0])
            aposta_ = linha.split('=')[1]

            if results[:len(estrategy)] == estrategy:
                aposta_formatada = "🟥 BANKER" if aposta_ == "B" else "🟦 PLAYER"
                msg = (
                    "🎲 *ENTRADA CONFIRMADA!*\n"
                    "🎲 [Cadastre-se na LotoGreen!](https://go.aff.lotogreen.com/a6peveba)\n"
                    f"💰 Aposte em: *{aposta_formatada}*\n"
                    "🟨 Faça cobertura no *TIE*\n"
                    "💸 [Os sinais funcionam apenas na LotoGreen](https://go.aff.lotogreen.com/a6peveba)"
                )
                await enviar_mensagem(msg)
                print(f'📌 ENTRADA EM: {aposta_}')
                entrada = False
                green = True
                gale = True
                return

    elif results[0] == aposta_ and green:
        await enviar_mensagem("✅✅✅ *GREEN!* ✅✅✅\n💸 Mais um vento no bolso!")
        print('✅✅✅ DEU GREEN! 💸💸💸')
        quantidade = 0
        entrada = True
        green = False
        gale = False
        red = False
        return

    elif results[0] == 'T' and green:
        await enviar_mensagem("✅✅✅ *GREEN - EMPATE* 💸💸💸\n💸 Mais um vento no bolso!")
        print('✅✅✅ GREEN - EMPATE 💸💸💸')
        quantidade = 0
        entrada = True
        green = False
        gale = False
        red = False
        return

    elif results[0] != 'T' and results[0] != aposta_ and gale:
        quantidade += 1
        msg = f"⚠️ *GALE {quantidade} Ativado!*\n⚠️ Continuamos com a mesma aposta."
        await enviar_mensagem(msg)
        print(msg)
        if quantidade >= gales:
            gale = False
            red = True
        return

    elif results[0] != 'T' and results[0] != aposta_ and red:
        await enviar_mensagem("❌❌❌ *RED!* ❌❌❌\n💥💥💥 Sequência encerrada. 💥💥💥")
        print('❌❌❌ RED ❌❌❌')
        quantidade = 0
        entrada = True
        green = False
        gale = False
        red = False
        return

# ========== LOOP PRINCIPAL ==========

async def main():
    await enviar_mensagem("🤖 Robô Yuri Martins Bac Bo - Iniciado com sucesso!")
    driver = iniciar_driver()
    if not login_bacbo(driver, EMAIL, SENHA):
        return

    simular_atividade(driver)

    global resultados, check_resultados

    while True:
        resultados = buscar_resultados(driver)

        if resultados != check_resultados:
            check_resultados = resultados.copy()
            print("🎲 Resultados:", resultados)
            await estrategia(resultados)

        time.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
