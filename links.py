import requests
from bs4 import BeautifulSoup

# URL страницы, с которой будем собирать ссылки
url = 'https://www.testprepreview.com/other_exams.htm'

# Выполняем HTTP-запрос к странице
response = requests.get(url)
response.raise_for_status()  # Проверяем, что запрос выполнен успешно

# Создаем объект BeautifulSoup для парсинга HTML
soup = BeautifulSoup(response.text, 'html.parser')

# Находим все <a> теги в <li> тегах
links = soup.find_all('li')

# Открываем файл для записи ссылок
with open('links.txt', 'w') as file:
    for li in links:
        a_tag = li.find('a')
        if a_tag and a_tag.get('href'):
            link = a_tag['href']
            file.write(link + '\n')

print('Ссылки успешно собраны и записаны в файл links.txt')
