import logging
import time, os, re
from datetime import datetime, timedelta
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, UnexpectedAlertPresentException
from alright import WhatsApp
from utils.auth import authenticate

def is_time_old(time_str, months=2):
    message_time = datetime.strptime(time_str, '%d.%m.%Y')

    time_difference = datetime.now() - message_time

    return time_difference > timedelta(days=months * 30)

def get_chat_message(messages):

    if not len(messages):
        return False

    else:
        return True


def get_list_of_messages(browser):

    messages = browser.find_elements(By.XPATH, '//div[@class="copyable-text"][@data-pre-plain-text]')

    return messages

def check_alert(browser, internet_speed):
    popup_xpath = "//div[@data-animate-modal-popup]"

    try:
        popup_element = WebDriverWait(browser, 15 + internet_speed).until(EC.presence_of_element_located((By.XPATH, popup_xpath)))

        attribute_value = popup_element.get_attribute("data-animate-modal-popup")

        if attribute_value and attribute_value.lower() == "true":
            return True
        else:
            return False


    except TimeoutException:
        logging.error("TimeoutException: Element not found within the specified timeout.")
        return False

def send_file(browser, file_path, internet_speed):
    file_name = os.path.realpath(file_path)

    clipButton = WebDriverWait(browser, 60 + internet_speed).until(
                        EC.presence_of_element_located(
                            (
                                By.XPATH,
                                '//*[@id="main"]/footer//*[@data-icon="attach-menu-plus"]/..',
                            )
                        )
                    )
    clipButton.click()

    # document_button = WebDriverWait(browser, 60 + internet_speed).until(
    #                     EC.presence_of_element_located(
    #                         (
    #                             By.XPATH,
    #                             '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[1]/div[2]/div/span/div/ul/div/div[1]/li/div/input',
    #                         )
    #                     )
    #                 )

    document_button = WebDriverWait(browser, 60 + internet_speed).until(
                            EC.presence_of_element_located(
                                (
                                    By.XPATH,
                                    '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[1]/div/div/span/div/ul/div/div[1]/li/div/input',
                                )
                            )
                        )
    document_button.send_keys(file_name)
    time.sleep(5)
    browser.find_element(By.CSS_SELECTOR, 'span[data-icon="send"]').click()
    time.sleep(5)

def send_message(browser, messenger, phone_number, internet_speed):
    try:
        texts = [
            "Доброе утро/день/вечер!",
            f"Вы интересовались определителем телефонных номеров посетителей вашего сайта - на нашем сервисе {phone_number['link']}",
            "Меня зовут Артем, отвечу на ваши вопросы",
            "Можете спрашивать голосовым сообщением. Я вам так же отвечу :)",
            "Также мы умеем определять номера посетителей сайтов ваших конкурентов."
        ]

        current_time = datetime.now().time()

        if current_time < datetime.strptime("12:00:00", "%H:%M:%S").time():
            texts[0] = "Доброе утро!"
        elif current_time < datetime.strptime("18:00:00", "%H:%M:%S").time():
            texts[0] = "Добрый день!"
        else:
            texts[0] = "Добрый вечер!"

        for text in texts:
            try:
                messenger.send_message(text)
            except Exception as e:
                logging.error(f"Failed to send text '{text}' to {phone_number['phone']}. Exception: {str(e)}")
                print(f"Не удалось отправить текст '{text}' на {phone_number['phone']}. Подробности см. в логах.")
                return

        time.sleep(1)
        send_file(browser, "./data/Определитель номеров для сайта.pdf", internet_speed)

        append_to_file(phone_number['phone'], "./data/temp_numbers.txt")

    except NoSuchElementException:
        logging.error(f"Failed to find the input field for {phone_number['phone']}.")
        print(f"Не удалось найти поле ввода для {phone_number['phone']}.")

    except TimeoutException:
        logging.error(f"Failed to make the input field for {phone_number['phone']} clickable within one minute.")
        print(f"Не удалось сделать поле ввода для {phone_number['phone']} кликабельным в течение минуты.")
    except Exception as e:
        logging.error(f"Failed to send text '{text}' to {phone_number['phone']}. Exception: {str(e)}")
        print(f"Не удалось отправить текст '{text}' на {phone_number['phone']}. Подробности см. в логах.")

def find_unique_phones(array1, array2):
    unique_numbers = set()
    unique_array = []

    for item in array1:
        phone_number = item.get("phone")
        link = item.get("link")

        if phone_number and phone_number not in unique_numbers and phone_number not in array2:
            unique_numbers.add(phone_number)
            unique_array.append({"phone": phone_number, "link": link})

    return unique_array


def send_messages(browser, internet_speed, create_browser=None):
    logging.info("User selected option: [2] Send Message")

    logging.info("Authenticating user...")
    is_auth = authenticate(browser)

    if is_auth:
        logging.info("Making an API request to get phone numbers...")

        while True:
            try:
                print("Выполнение запроса API для получения номеров телефонов...")
                api_url = "https://vmi458761.contaboserver.net/rept?token=ac7fa63332a1c87238af2cad5e8beae5"
                api_response = make_api_request(api_url)

                if api_response:
                    phone_numbers = extract_phone_numbers(api_response)
                    # phone_numbers = [{"phone": "+79037180516", "link": "vse-klienty.ru"}]

                    existing_numbers = set(read_from_file("./data/temp_numbers.txt").split('\n'))
                    updated_numbers = find_unique_phones(phone_numbers, existing_numbers)

                    for phone_number in updated_numbers:
                        if phone_number['phone'] in existing_numbers:
                            logging.info(f"Skipping message to {phone_number['phone']} as it already exists in the file.")
                            continue

                        browser.quit()
                        browser = create_browser()
                        browser.get("https://web.whatsapp.com/")

                        messenger = WhatsApp(browser)

                        print("Выходим и заходим в браузер")
                        logging.info("Выходим и заходим в браузер")
                        messenger.find_user(phone_number['phone'])
                        try:
                            WebDriverWait(browser, 20 + internet_speed).until(
                                EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/footer/div/div/span[2]/div/div[2]/div/div/div'))
                            )

                        except TimeoutException:
                            logging.error("TimeoutException: Element not found within the specified timeout.")
                            alert_status = check_alert(browser, internet_speed)

                            if alert_status:
                                append_to_file(f"{phone_number['phone']}, {phone_number['link']}", "./data/user_rechecks.txt")
                                logging.info(f"Failed to send message because number not found: {phone_number['phone']}")
                                print(f"\nОтправка сообщения на номер не удалась потому что номер не найден: {phone_number['phone']}\n")

                                continue
                        try:
                            time.sleep(5)
                            print(f"\nПроверка номера на диалог время ожидание ({15 + internet_speed}): {phone_number['phone']}\n")
                            messages = get_list_of_messages(browser)
                            is_to_months_ago = get_chat_message(messages)

                            if not is_to_months_ago:
                                send_message(browser, messenger, phone_number, internet_speed)
                                continue
                            else:
                                logging.info(f"Failed to send message because number not found: {phone_number['phone']}")
                                print(f"\nОтправка сообщения на номер не удалась потому как последние сообщение 2 месяца назад: {phone_number['phone']}\n")
                                append_to_file(phone_number['phone'], "./data/temp_numbers.txt")
                                continue

                        except TimeoutException:
                            logging.error("TimeoutException: Element not found within the specified timeout.")
                            print(f"\nДиалог с пользователем не найден продолжаем отправку: {phone_number['phone']}\n")
                            send_message(browser, messenger, phone_number, internet_speed)
                            continue

                logging.info(f"Mailing completed. Re-sending in 5 minutes.")
                print("Рассылка завершена. Повторная рассылка через 5 минут.")

                time.sleep(300)

                logging.info(f"We are sending again.")
                print("Делаем повторную рассылку.")

            except Exception as e:
                logging.error(f"An error occurred: {str(e)}", exc_info=True)
                browser.quit()
                print("Выходим и заходим в браузер")
                logging.info("Выходим и заходим в браузер")
                browser.get("https://web.whatsapp.com/")


    else:
        logging.warning("Authentication failed. Please authenticate first.")
        print("Аутентификация не удалась. Пожалуйста, пройдите аутентификацию перед отправкой сообщения.")

def send_rechecks_message(browser, internet_speed):
    logging.info("User selected option: [3] Send Message")

    logging.info("Authenticating user...")
    is_auth = authenticate(browser)

    MAX_ATTEMPTS = 7
    TIME_INTERVALS = [3600, 7200, 86400, 259200, 604800, 2592000, 15552000]

    if is_auth:
        phone_numbers = set(read_from_file("./data/user_rechecks.txt").split('\n'))
        messenger = WhatsApp(browser)

        for entry in phone_numbers.copy():
            if entry:
                parts = entry.split(',')
                phone_number = parts[0]
                link = parts[1]

                print(f"Текущий номер телефона: {phone_number}")
                messenger.find_user(phone_number)
                time.sleep(5 + internet_speed)

                for attempt in range(1, MAX_ATTEMPTS + 1):
                    alert_status = check_alert(browser, internet_speed)
                    if alert_status:
                        print(f"Попытка {attempt} для номера телефона {phone_number} не удалась. Повтор через {TIME_INTERVALS[attempt - 1]} секунд.")
                        time.sleep(TIME_INTERVALS[attempt - 1])
                    else:
                        send_message(browser, messenger, {"phone": phone_number, "link": link}, internet_speed)
                        print(f"\nСообщение успешно отправлено на номер {phone_number}.\n")

                        phone_numbers.remove(entry)
                        write_to_file("./data/user_rechecks.txt", '\n'.join(phone_numbers))

                        break

                if alert_status:
                    print(f"Все попытки для номера телефона {phone_number} не удалась. Переход к следующему номеру.")
    else:
        logging.warning("Authentication failed. Please authenticate first.")
        print("Аутентификация не удалась. Пожалуйста, пройдите аутентификацию перед отправкой сообщения.")

def make_api_request(api_url):
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            return response.text
        else:
            logging.error(f"API request failed with status code {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Failed to make API request. Exception: {str(e)}")
        return None

def extract_phone_numbers(api_response):
    phone_numbers = []
    lines = api_response.split('\n')[1:]
    for line in lines:
        if line:
            parts = line.split(';')
            phone_numbers.append({"phone": parts[0], "link": parts[1].rstrip('\r')})
    return phone_numbers

def append_to_file(new_data, file_path):
    try:
        with open(file_path, 'a', encoding='utf-8') as file:
            file.write('\n' + new_data)

    except Exception as e:
        print(f"Ошибка при обработке файла {file_path}: {str(e)}")

def read_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = file.read()

        return data

    except Exception as e:
        print(f"Ошибка при чтении файла {file_path}: {str(e)}")
        return None



def write_to_file(file_path, data):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(data)
    except Exception as e:
        print(f"Ошибка при записи данных в файл: {e}")
