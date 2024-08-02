import pandas as pd

# Загрузка данных из файлов
file1 = "test_data.xlsx"
file2 = "testprepreview.xlsx"

df1 = pd.read_excel(file1)
df2 = pd.read_excel(file2)

# Извлечение колонок с URL
urls1 = df1["Ссылка на тест"].dropna().tolist()
urls2 = df2["URL"].dropna().tolist()

# Поиск уникальных URL
unique_urls = list(set(urls1).symmetric_difference(set(urls2)))

# Запись уникальных URL в файл
with open("links.txt", "w") as file:
    for url in unique_urls:
        file.write(url + "\n")

print(f"Найдено {len(unique_urls)} уникальных URL. Они сохранены в файл links.txt.")
