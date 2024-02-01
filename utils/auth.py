import os
import logging


def check_auth():
    session_folder = "./sessions/"
    auth_file = os.path.join(session_folder, "isAuth")

    if not os.path.exists(auth_file):
        print("\nСессия не найдена\nОтсканируйте QR-код")
        logging.info("\nSession not found.\nScan the QR code.")
        confirm = input("\nПосле сканирования введите Y: ").lower()
        if confirm == "y":
            print("Сессия успешно сохранена")
            logging.info("Session successfully saved.")
            with open(auth_file, "w") as auth_flag:
                auth_flag.write("Authenticated")
            return True
        else:
            print("Отмена сохранения сессии")
            logging.info("Session saving canceled.")
            return False
    else:
        print("\nСессия уже существует")
        logging.info("\nSession already exists.")
        return True


def authenticate(browser):
    browser.get("https://web.whatsapp.com/")
    logging.info("User chose option: [1] Authenticate")
    return check_auth()
