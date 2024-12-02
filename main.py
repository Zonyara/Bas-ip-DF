# -*- coding: utf-8 -*-
import os
import requests
from bs4 import BeautifulSoup


# Проверка и создание папки
def check_and_create_directory(directory_name):
    if os.path.exists(directory_name):
        if os.path.isdir(directory_name):
            print(f"Папка '{directory_name}' уже существует.")
            return True
        else:
            print(f"'{directory_name}' существует, но это не папка.")
            return False
    else:
        os.makedirs(directory_name)
        print(f"Папка '{directory_name}' была создана.")
        return True

# Проверка ссылки
def is_valid_url(url):
    if (url.startswith("https://cdn.bas-ip.com/firmware/manual/") and
            (len(url.split('/')[-1]) > 0 or url.endswith('/'))):
        return True
    return False


# Функция для загрузки файла
def download_file(url, directory):
    local_filename = os.path.join(directory, url.split('/')[-1])
    print(f"Начинается загрузка файла '{local_filename}'...")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"Файл '{local_filename}' загружен.")  # Сообщение о завершении загрузки





# Вывод инструкции
print("\nИнструкция\n1) Необходимо указать путь к папке для сохранения прошивок\n2) Будет произведена проверка названия папок с именами устройств Bas-ip (пример названия папки: AA-12fb)\n3) В случае отсутствия папки для указанного устройства, будет создана новая и загружены все версии прошивок под данное устройство\n4) В случае обнаружения папки для указанного устройства, будет произведена проверка наличия версий прошивок в папке и на сайте, если будут обнаружены новые версии прошивок на сайте, недостающие будут загружены в данную папку\n")

# Путь к папке для сохранения прошивок
while True:
    the_folder_to_save = input("Введите путь для сохранения: ")
    if os.path.exists(the_folder_to_save):
        break
    else:
        print(f"Путь '{the_folder_to_save}' не существует, укажите корректный путь")

# Проверка значения для количества устройств
while True:
    number_of_iterations = input("Укажите количество устройств для которых необходимо загрузить прошивки: ")
    try:
        number_of_iterations = int(number_of_iterations)
        if number_of_iterations <= 0:
            print("Число должно быть положительным и не равняться 0")
            continue
        break
    except ValueError:
        print("Количество устройств указано некорректно")

# Массив для хранения ссылок на прошивки от пользователя
user_data = []

# Запрос всех ссылок от пользователя
for i in range(number_of_iterations):
    while True:
        try:
            element = input(f"Укажите {i + 1} ссылку на прошивки для нужного устройства : ")
            if is_valid_url(element):
                user_data.append(element)
                element_parse = element.split('/')[-2]
                check_and_create_directory(os.path.join(the_folder_to_save, element_parse))
                response = requests.get(element)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    links = soup.find_all('a')
                    file_names = []
                    for link in links:
                        href = link.get('href')
                        if href and href.endswith('.img'):
                            file_names.append(href)


                    # Сравнение с локальными файлами и загрузка недостающих
                    local_files = os.listdir(os.path.join(the_folder_to_save, element_parse))
                    for file_name in file_names:
                        if file_name not in local_files:
                            # Загружаем файл, если его нет в локальной папке
                            file_url = os.path.join(element, file_name)  # Полный URL для загрузки
                            download_file(file_url, os.path.join(the_folder_to_save, element_parse))

                else:
                    print(f"Не удалось получить страницу. Код состояния: {response.status_code}")
                break
        except Exception as e:
            print(f"'{element}' не является действительным URL. Ошибка: {e}")

print("Загрузка всех прошивок завершена")