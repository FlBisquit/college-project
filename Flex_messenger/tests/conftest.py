import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URL = "http://localhost:5173/"

# Фикстура для создания и закрытия драйвера Chrome
@pytest.fixture
def driver():
    # Создание объекта Options для настройки браузера
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Запуск в фоновом режиме
    # chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = "/usr/bin/google-chrome"  # Путь к бинарному файлу Chrome

    # Создание экземпляра драйвера Chrome
    driver = webdriver.Chrome(options=chrome_options)
    yield driver  # Возвращаем драйвер для теста
    driver.quit()  # Закрываем драйвер после теста

