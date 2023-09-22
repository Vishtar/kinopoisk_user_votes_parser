import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from datetime import datetime
import json

USER_ID = '13600880'

VOTES_URL = f'https://www.kinopoisk.ru/user/{USER_ID}/votes/list/vs/vote/perpage/200/page/'
WATCHED_URL = f'https://www.kinopoisk.ru/user/{USER_ID}/votes/list/vs/novote/perpage/200/page/'

types_by_rus = {
    'фильм': 'movie',
    'сериал': 'series',
    'мини-сериал': 'miniseries',
}

def process_name_rus(name_rus):
    title, info = name_rus.split('(')
    info_split = info.replace(')', '').split(', ')
    type_ = types_by_rus.get(info_split.pop(0).strip(), 'movie') if len(info_split) == 2 else 'movie'
    years = info_split[0].split(' – ')
    year_to = ''
    if len(years) == 2:
        year_to = years[-1]
        if year_to == '...':
            year_to = None
        else:
            int(years[-1])
    year = int(years[0])
    
    return {
        'name_rus': title.strip(),
        'year': year,
        'year_to': year_to,
        'type': type_,
    }

def process_movie_elements(movie_elements):
    movies_data = {}
    
    for element in movie_elements:
        name_rus_div = element.find(class_='nameRus')
        if not name_rus_div:
            continue
        name_rus_element = name_rus_div.find('a')
        name_eng_element = element.find(class_='nameEng')
        rating_element = element.find(class_='rating').find('b')
        vote_container_element = element.find('span', class_='text-grey')
        duration_element = element.find_all('span', class_='text-grey')[-1]
        date_element = element.find(class_='date')
        vote_element = element.find(class_='vote')
        eye = vote_element.find(class_='eye')

        name_rus = name_rus_element.text.strip().replace(' ', ' ')
        name_eng = name_eng_element.text.strip() if name_eng_element else None
        kp_id = name_rus_element['href'].split('/')[-2]
        kp_rating = float(rating_element.text) if rating_element else None
        votes_match = vote_container_element.text.strip('()') if vote_container_element and kp_rating else None
        kp_votes = int(votes_match.replace(' ', '')) if votes_match else None
        duration_match = duration_element.text.strip()
        duration = int(duration_match.replace(' мин.', '')) if duration_match and kp_rating and duration_match.find('мин') != -1 else ''
        date_time = datetime.strptime(date_element.text.strip(), "%d.%m.%Y, %H:%M").strftime("%Y-%m-%dT%H:%M") if date_element else ''
        vote = int(vote_element.text) if vote_element and not eye else 0
        print(f'{vote} {name_rus}')

        if kp_id in movies_data:
            continue
        
        movies_data[kp_id] = {
            **process_name_rus(name_rus),
            'name_eng': name_eng,
            'datetime': date_time,
            'kp_id': kp_id,
            'kp_rating': kp_rating,
            'kp_votes': kp_votes,
            'duration': duration,
            'vote': vote,
        }
    
    return movies_data


chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-gpu")

service = Service(executable_path='/usr/bin/chromedriver')

# Browser init
driver = webdriver.Chrome(service=service, options=chrome_options)

movies = {}

current_url = VOTES_URL

for current_url in [VOTES_URL, WATCHED_URL]:
    current_page = 1
    max_page = 1

    while current_page <= max_page:
        print(f'{current_url}{current_page}')

        full_url = f'{current_url}{current_page}'
        driver.get(full_url)
        time.sleep(3)
        while driver.current_url.find(full_url) == -1:
            time.sleep(5)
        time.sleep(5)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        last_page_element = soup.find_all('li', class_='arr')[-1].find('a')
        last_page = last_page_element['href'].split('/')[-2]

        page_movies_data = process_movie_elements(soup.find_all(class_='item'))

        max_page = int(last_page)

        for movie_id in page_movies_data:
            if movie_id not in movies:
                movies[movie_id] = page_movies_data[movie_id]

        current_page += 1

# Закрываем браузер
driver.quit()

# Запись итогового объекта movies в файл
with open('movies.json', 'w', encoding='utf-8') as file:
    json.dump(movies, file, ensure_ascii=False, indent=2)
