from playwright.sync_api import sync_playwright #импорта класса и функции (автоматизация браузера)
from bs4 import BeautifulSoup #импорт класса, BeautifulSoup - библиотека для парсинга
import csv #встроенная библиотека для работы с CSV файлами


def parse_search(query): #функция парсинга, query - строка
    url = f"https://obuv-tut2000.ru/magazin/search?gr_smart_search=1&search_text={query}" #создание переменной с подстановкой поискового запроса
    products = [] #пустой список для хранения товаров

    with sync_playwright() as p: #контекстный менеджер, объект playwright для управления браузером
        browser = p.chromium.launch(headless=True) #вызов метода, Chrome в фоновом режиме
        page = browser.new_page() #вызов метода, новая вкладка
        page.goto(url, wait_until="domcontentloaded", timeout=60000) #вызов метода, переход по ссылке с ожиданием загрузки древовидной структуры объектов, котрую браузер создает после загрузки HTML (60 сек)

        # ждём карточки товаров
        page.wait_for_selector(
            ".shop2-product-item.product-item", timeout=20000) #вызов метода, ожидание появления карточек товаров (20 сек)

        soup = BeautifulSoup(page.content(), "html.parser") #создание объекта, объект soup для парсинга HTML содержимого страницы

        for card in soup.select(".shop2-product-item.product-item"): #цикл, итерация по найденным карточкам товаров
            name_tag = card.select_one(".gr-product-name a") #поиск элеменета, тег <a> с названием товара или Nоne если товар не найден
            price_tag = card.select_one(".product-price .price-current strong") #поиск элемента, тег <strong> с текущей ценой или None
            old_price_tag = card.select_one(".product-price .price-old strong") #Поиск элемента, Тег <strong> со старой ценой или None
            article_tag = card.select_one(".product-article") #Поиск элемента, Тег с артикулом товара или None
            vendor_tag = card.select_one(".gr-vendor-block") #Поиск элемента, Тег с производителем или None
            img_tag = card.select_one(".gr-product-image img") #Поиск элемента, Тег <img> с изображением товара или None
            #Создание словаря с данными товара
            products.append({ #Вызов метода списка, Добавление словаря в список products
                "name": name_tag.get_text(strip=True) if name_tag else None, #Тернарный оператор, Ключ "name" со значением (текст тега или None)
                "link": "https://obuv-tut2000.ru" + name_tag["href"] if name_tag else None, #Конкатенация строк + тернарный оператор, Ключ "link" с полным URL или None
                "price": price_tag.get_text(strip=True) if price_tag else None, #Тернарный оператор, Ключ "price" с текстом цены или None
                "old_price": old_price_tag.get_text(strip=True) if old_price_tag else None, #Тернарный оператор, Ключ "old_price" с текстом старой цены или None
                "article": article_tag.get_text(strip=True).replace("Артикул:", "").strip() if article_tag else None, #Цепочка методов + тернарный оператор, Ключ "article" с очищенным артикулом или None 
                "vendor": vendor_tag.get_text(strip=True) if vendor_tag else None, #Тернарный оператор, Ключ "vendor" с производителем или None
                "image": "https://obuv-tut2000.ru" + img_tag["src"] if img_tag else None #Конкатенация строк + тернарный оператор, Ключ "image" с полным URL изображения или None
            })

        browser.close() #Вызов метода, Закрытие браузера
    return products #Возврат значения, Возврат списка products из функции


def save_to_csv(products, filename): #Объявление функции, Функция save_to_csv с параметрами products (список) и filename (строка)
    with open(filename, "w", newline="", encoding="utf-8") as f: #Контекстный менеджер, Открытие файла для записи в кодировке UTF-8
        writer = csv.DictWriter(f, fieldnames=products[0].keys()) #Создание объекта, Объект writer для записи словарей в CSV
        writer.writeheader() #Вызов метода, Запись заголовков (ключи первого словаря)
        writer.writerows(products) #Вызов метода, Запись всех данных из списка products


if __name__ == "__main__": #Условие выполнения, Проверка, что скрипт запущен напрямую
    query = input("Введите поисковый запрос: ").strip() # Ввод данных + вызов метода, Строка query с пользовательским вводом (без пробелов по краям)
    products = parse_search(query) #Вызов функции, Список products с результатами парсинга

    if not products: #Условный оператор, Проверка, что список пустой
        print("Товары не найдены") #Вывод в консоль, Сообщение об отсутствии товаров
    else: #Условный оператор, Блок выполнения если товары найдены
        filename = f"{query}_products.csv" #Создание переменной, Строка filename с именем файла 
        save_to_csv(products, filename) #Вызов функции, Сохранение данных в CSV файл
        print(f"Найдено товаров: {len(products)}") #Форматированная строка, Вывод количества товаров (длина списка)
        print(f"Данные сохранены в файл: {filename}") #Форматированная строка, Вывод имени файла
