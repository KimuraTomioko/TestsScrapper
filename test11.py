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
from bs4 import BeautifulSoup

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

def clean_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup.find_all(['div', 'label']):
        tag.unwrap()
    for element in soup.find_all(class_=True):
        del element['class']
    for element in soup.find_all(style=True):
        del element['style']
    for element in soup.find_all(id=True):
        del element['id']
    return str(soup)

def collect_data(driver, question_count):
    data_dict = {}
    try:
        question = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.d-flex.p-3.overflow-auto"))
        )
        question_html = question.get_attribute('outerHTML').strip()
        question_text = clean_html(question_html)

        answers = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div ul.answers"))
        )
        answer_items = answers.find_elements(By.TAG_NAME, 'li')
        answers_text = []
        correct_answer = None

        for item in answer_items:
            answer_html = item.get_attribute('outerHTML').strip()
            answer_text = clean_html(answer_html)

            if 'border-success' in item.get_attribute('class'):
                correct_answer = f"<strong>{answer_text}</strong>"
            else:
                correct_answer = answer_text

            if 'Correct' in answer_text:
                answer_text = answer_text.replace('Correct', '').strip()

            answers_text.append(answer_text)

        explanation = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.card.my-2.border-info div.explanation"))
        ).get_attribute('outerHTML').strip()
        explanation_text = clean_html(explanation)

        data_dict[f"Вопрос {question_count}"] = f"<p>{question_text}</p>"
        data_dict[f"Варианты ответа {question_count}"] = f"<ul>{''.join([f'<li>{answer}</li>' for answer in answers_text])}</ul>"
        data_dict[f"Правильный ответ {question_count}"] = correct_answer if correct_answer else 'Не найден'
        data_dict[f"Объяснение {question_count}"] = f"<p>{explanation_text}</p>"

        return data_dict
    except Exception as e:
        print(f"Ошибка при сборе данных: {e}")
        return None

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
                
                # Проверка наличия кнопки "Start Test"
                try:
                    start_test_button = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.LINK_TEXT, "Start Test"))
                    )
                    start_test_button.click()
                    print("Кнопка 'Start Test' нажата")
                except Exception as e:
                    print(f"Ошибка при нажатии кнопки 'Start Test': {e}")
                    no_button.write(url + '\n')
                    continue
                
                # Переключаемся на iframe с указанным классом
                try:
                    iframe = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "cboxIframe"))
                    )
                    driver.switch_to.frame(iframe)
                    print("Переключились на iframe по классу")
                except Exception as e:
                    print(f"Ошибка при переключении на iframe: {e}")
                    problems.write(url + '\n')
                    continue

                # Ждем, пока кнопка "Start" станет доступной и кликаем по ней
                try:
                    start_button = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Start']"))
                    )
                    start_button.click()
                    print("Кнопка 'Start' нажата")
                except Exception as ex:
                    print(f"Ошибка при нажатии кнопки 'Start': {ex}")
                    problems.write(url + '\n')
                    continue

                time.sleep(5)

                # Ждем, пока кнопка "Finish" станет доступной и кликаем по ней
                try:
                    finish_button = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-secondary.form-control"))
                    )
                    finish_button.click()
                    print("Кнопка 'Finish' нажата")
                except Exception as ex:
                    print(f"Ошибка при нажатии кнопки 'Finish': {ex}")
                    problems.write(url + '\n')
                    continue

                time.sleep(5)

                # Ждем, пока модальное окно с подтверждением загрузится
                try:
                    modal_finish_button = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.btn-primary.finish"))
                    )
                    modal_finish_button.click()
                    print("Кнопка 'Finish' в модальном окне нажата")
                except Exception as ex:
                    print(f"Ошибка при нажатии кнопки 'Finish' в модальном окне: {ex}")
                    problems.write(url + '\n')
                    continue

                time.sleep(10)

                question_count = 1
                data_dict = {}

                # Сбор данных первого вопроса перед нажатием кнопки "Next"
                data = collect_data(driver, question_count)
                if data:
                    data_dict.update(data)

                # Цикл для нажатия кнопки "Next" до тех пор, пока она не станет неактивной
                while True:
                    try:
                        next_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.next.btn-primary"))
                        )
                        next_button.click()
                        print("Кнопка 'Next' нажата")
                        time.sleep(2)  # Небольшая задержка перед следующей попыткой

                        # Сбор данных после нажатия кнопки "Next"
                        question_count += 1
                        data = collect_data(driver, question_count)
                        if data:
                            data_dict.update(data)
                    except Exception as e:
                        print("Кнопка 'Next' неактивна или произошла ошибка:", e)
                        break

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