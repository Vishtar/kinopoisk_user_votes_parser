Штука для сбора оценок с Кинопоиска, также собирает фильмы из раздела "Просмотры".

Сделано для частного использования.

Можете попробовать запустить сами, для этого необходимо:
1. Указать ваш Кинопоиск ID (https://www.kinopoisk.ru/user/<ЦИФРЫ_ВАШЕГО_ID>/) в [main.py] в переменной **USER_ID**.
2. Там же поменять путь до **webdriver**'а (/usr/bin/chromedriver). На Windows, полагаю, можете скачать какой-нибудь chromedriver.exe и, положив в папку со скриптом, указать путь типа "./chromedriver.exe".
3. После этого запускаем main.py, по необходимости запонляем капчу в открывающемся после запуска браузере.
4. Результат в виде json-объекта должен собраться в папке со скриптом в файл [movies.json].

Pull Requests и форки приветствуются.
