import logging
import shutil

from selenium import webdriver
import platform
from selenium.webdriver.chrome.options import Options

from utils import send_messages, auth

shutil.copy2('./logs/whatsapp_bot.log', './logs/whatsapp_bot_backup.log')
open('./logs/whatsapp_bot.log', 'w').close()

logging.basicConfig(filename='./logs/whatsapp_bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logging.info("Script started")

def create_browser():
    system_platform = platform.system()

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("user-data-dir=sessions/whatsapp") 
    chrome_options.add_argument("disable-gpu")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("disable-infobars"); 
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")

    if system_platform == "Windows":
        browser = webdriver.Chrome(options=chrome_options)
        return browser
    elif system_platform == "Linux":
        browser = webdriver.Chrome(options=chrome_options)
        return browser
    else:
        raise Exception("Unsupported operating system")



try:
    print("\n[1] Авторизация")
    print("[2] Отправка сообщений")
    print("[3] Повторная проверка и отправка сообщения\n")

    choice = input("Выберите вариант (1, 2 или 3): ")
    browser = create_browser()
    browser.get("https://web.whatsapp.com/")
    while True:
        print("")

    # if choice.isdigit():
    #     choice = int(choice)
    #     # if choice != 1:
    #        # browser.set_window_position(-10000, 0)

    #     if choice == 1:
    #         auth.authenticate(browser)

    #     elif choice == 2:
    #         send_messages.send_messages(browser)

    #     elif choice == 3:
    #         send_messages.send_rechecks_message(browser)

    #     else:
    #         print("\nНеверный вариант. Пожалуйста, выберите 1, 2 или 3.\n")
    #         logging.warning("User entered an invalid option")
    # else:
    #     print("\nНеверный ввод. Пожалуйста, введите число.\n")
    #     logging.warning("User entered a non-numeric input")

except Exception as e:
    logging.error(f"An error occurred: {str(e)}", exc_info=True)

finally:
    logging.info("Script ended")
