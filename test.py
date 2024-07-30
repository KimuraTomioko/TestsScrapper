from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from gologin import GoLogin
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
chrome_options.add_argument("--start-maximized")  # Открытие браузера в полноэкранном режиме

# Запуск браузера
driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()), options=chrome_options)

driver.get('https://www.testprepreview.com/iaap.htm')

# Ждем, пока кнопка "Start Test" станет доступной и кликаем по ней
try:
    start_test_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Start Test"))
    )
    start_test_button.click()
    print("Кнопка 'Start Test' нажата")
except Exception as e:
    print(f"Ошибка при нажатии кнопки 'Start Test': {e}")

# Переключаемся на iframe с указанным классом
try:
    iframe = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "cboxIframe"))
    )
    driver.switch_to.frame(iframe)
    print("Переключились на iframe по классу")
except Exception as e:
    print(f"Ошибка при переключении на iframe: {e}")

# Ждем, пока кнопка "Start" станет доступной и кликаем по ней
try:
    start_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Start']"))
    )
    start_button.click()
    print("Кнопка 'Start' нажата")
except Exception as ex:
    print(f"Ошибка при нажатии кнопки 'Start': {ex}")

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

time.sleep(5)

# Цикл для нажатия кнопки "Next" до тех пор, пока она не станет неактивной
while True:
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.next.btn-primary"))
        )
        next_button.click()
        print("Кнопка 'Next' нажата")
        time.sleep(2)  # Небольшая задержка перед следующей попыткой
    except Exception as e:
        print("Кнопка 'Next' неактивна или произошла ошибка:", e)
        break

# Завершение работы браузера
driver.quit()
gl.stop()
