import logging
import shutil
import os
import sys

from selenium import webdriver
import platform
from selenium.webdriver.chrome.options import Options

from utils import send_messages, auth


shutil.copy2('./logs/whatsapp_bot.log', './logs/whatsapp_bot_backup.log')
open('./logs/whatsapp_bot.log', 'w').close()

logging.basicConfig(filename='./logs/whatsapp_bot.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logging.info("Script started")


def create_browser(no_headless=False):
    system_platform = platform.system()

    chrome_options = Options()
    chrome_options.add_argument("disable-gpu")
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")

    # if no_headless:
    #     chrome_options.add_argument("--headless")

    full_path = os.path.abspath("sessions/whatsapp")
    chrome_options.add_argument(f"user-data-dir={full_path}")

    if system_platform == "Windows":
        browser = webdriver.Chrome(options=chrome_options)
        return browser
    elif system_platform == "Linux":
        browser = webdriver.Chrome(options=chrome_options)
        return browser
    else:
        raise Exception("Unsupported operating system")


print("\n[1] Быстрый интернет\n[2] Слабый интернет\n[3] Критичный интернет")
internet_choice = input("\nВыберите вариант (1, 2 или 3): ")
internet_speed = 0

if internet_choice.isdigit():
    internet_choice = int(internet_choice)
    if internet_choice == 1:
        print("[+] Дефолтные таймеры\n")

    elif internet_choice == 2:
        internet_speed += 60
        print("[+] 60 секунд к каждому таймеру\n")

    elif internet_choice == 3:
        internet_speed += 120
        print("[+] 120 секунд к каждому таймеру\n")

    else:
        logging.warning("User entered an invalid option")
        sys.exit("\nНеверный вариант. Пожалуйста, выберите 1, 2 или 3.\n")

else:
    logging.warning("User entered a non-numeric input")
    sys.exit("\nНеверный ввод. Пожалуйста, введите число.\n")


print("\n[1] Авторизация\n[2] Отправка сообщений\n[3] Повторная проверка и отправка сообщения\n")

choice = input("Выберите вариант (1, 2 или 3): ")

browser = create_browser()
browser.get("https://web.whatsapp.com/")

def run(choice):
    if choice.isdigit():
        choice = int(choice)
        # if choice != 1:
        # browser.set_window_position(-10000, 0)

        if choice == 1:
            auth.authenticate(browser)

        if choice == 2:

            send_messages.send_messages(browser, internet_speed, create_browser)

        elif choice == 3:
            send_messages.send_rechecks_message(browser, internet_speed)

        else:
            logging.warning("User entered an invalid option")
            sys.exit("\nНеверный вариант. Пожалуйста, выберите 1, 2 или 3.\n")
    else:
        logging.warning("User entered a non-numeric input")
        sys.exit("\nНеверный ввод. Пожалуйста, введите число.\n")


try:
    run(choice)
except Exception as e:
    logging.error(f"An error occurred: {str(e)}", exc_info=True)
    browser.refresh()
    run(choice)

    # sys.exit("Global error se more in logs")

# finally:
#     logging.info("Script ended")
