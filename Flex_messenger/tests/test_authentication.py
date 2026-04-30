import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .conftest import URL

# Тест функции входа 
def test_login(driver):
    # Определение URL страницы входа

    driver.get(URL)
    time.sleep(2)  # Задержка 2 секунды
    print(f"Текущий URL: {driver.current_url}")

    wait = WebDriverWait(driver, 10)
    username_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Login']")))
    time.sleep(2)  # Задержка 2 секунды
    print("Поле логина найдено")

    password_field = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Password']")
    time.sleep(2)  # Задержка 2 секунды
    print("Поле пароля найдено")

    login_button = driver.find_element(By.CLASS_NAME, "btn-arrow")
    time.sleep(2)  
    print("Кнопка входа найдена")

    username_field.send_keys("Daniil")
    time.sleep(2)
    print("Логин введён")

    password_field.send_keys("123")
    time.sleep(2)  # Задержка 2 секунды
    print("Пароль введён")

    login_button.click()
    time.sleep(4)  # Ждём 4 секунды для загрузки страницы или тестов
    print("Вход выполнен")

    print(f"После входа URL: {driver.current_url}")
    print(f"Заголовок страницы: {driver.title}")
    print("Тест завершён успешно")