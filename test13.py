from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from gologin import GoLogin
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os

def setup_driver():
    # Настройка GoLogin
    gl = GoLogin({
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NmEyMzc1ZWJiMzQxZTQ3ZGIyMzRlZTQiLCJ0eXBlIjoiZGV2Iiwiand0aWQiOiI2NmE4YWQ3MTFiMDlkY2E2ZTM1YjNlOGIifQ.sRx1Kv7W5djGhdBfeSY3Rpx1js9Q3W5VhrGyCyknPA0",
        "profile_id": '66a8ab3168f8872d9bc3ab02'
    })
    
    # Запуск GoLogin профиля
    debugger_address = gl.start()
    
    # Настройка ChromeOptions
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("debuggerAddress", debugger_address)
    chrome_options.add_argument("--start-maximized")
    
    # Запуск браузера
    driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()), options=chrome_options)
    return driver, gl

def main():
    # Настройка браузера
    driver, gl = setup_driver()

    # Чтение ссылок из файла
    with open('links.txt', 'r') as f:
        links = f.readlines()
    
    no_button_file = 'no_button.txt'
    problems_file = 'problems.txt'
    
    # Открытие файлов для записи проблемных ссылок
    with open(no_button_file, 'w') as no_button, open(problems_file, 'w') as problems:
        for url in links:
            url = url.strip()
            if not url:
                continue
            
            print(f"Обрабатываем URL: {url}")
            try:
                driver.get(url)

                time.sleep(10)
                
                # Сбор названия теста
                try:
                    test_title_element = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "h1.entry-title"))
                    )
                    test_title = test_title_element.text.strip()
                    print(f"Название теста: {test_title}")
                except Exception as e:
                    print(f"Ошибка при сборе названия теста: {e}")
                    test_title = 'Не найден'

                # Сохранение данных
                data_dict = {
                    "Название теста": test_title,
                    "Ссылка на тест": url
                }

                # Преобразование словаря в DataFrame
                df_combined = pd.DataFrame([data_dict])

                # Путь к файлу Excel
                file_path = 'test_data.xlsx'

                # Проверка, существует ли файл и чтение существующих данных
                if os.path.exists(file_path):
                    df_existing = pd.read_excel(file_path)
                    df_combined = pd.concat([df_existing, df_combined], ignore_index=True)

                # Сохранение данных в Excel
                df_combined.to_excel(file_path, index=False)
                print(f"Данные сохранены в файл '{file_path}'")
                
            except Exception as e:
                print(f"Ошибка при обработке URL {url}: {e}")
                problems.write(url + '\n')

    # Завершение работы браузера
    driver.quit()
    gl.stop()

if __name__ == "__main__":
    main()