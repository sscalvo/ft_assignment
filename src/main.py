from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests                          # life_expectancy unemployment
import json                              # life_expectancy weather
from bs4 import BeautifulSoup            # unemployment
from typing import Optional              # trends
from .helpers import get_trends, get_weather, html_content
import os

app  = FastAPI(title='Tech assignment',
            description='The goal of this challenge is to build an integration API service with five endpoints.',
            version='1.2')

app.api_key_weather = os.environ['KEY']


@app.get('/', response_class=HTMLResponse)
def index(api_key: Optional[str] = None):
    return HTMLResponse(content=html_content, status_code=200)


# 1 - Query data from: https://data.cdc.gov/resource/w9j2-ggv5.json
@app.get('/life_expectancy/{sex}/{race}/{year}')
async def life_expectancy(sex: str, race: str, year: int):
    sex = sex.title()
    race = race.title()
    JSON_URL = f'https://data.cdc.gov/resource/w9j2-ggv5.json?year={year}&sex={sex}&race={race}'
    response = {'average_life_expectancy': 'unknown'}
    data = json.loads(requests.get(JSON_URL).text)
    if data:
        ale =  data[0].get('average_life_expectancy', -1)
        if ale != -1: 
            response = {'average_life_expectancy': float(ale)}
    return response


# 2 - Retrieve and parse data from: https://www.bls.gov/web/laus/lauhsthl.htm
@app.get('/unemployment/{state}')
async def unemployment(state: str):
    URL = "https://www.bls.gov/web/laus/lauhsthl.htm"

    rate = 'unknown'

    data = requests.get(URL).text
    soup = BeautifulSoup(data, features="html.parser")

    table = soup.find(id='lauhsthl')
    tbody = table.tbody
    trs = tbody.find_all("tr")

    for tr in trs:
        iterablex = iter(tr.children)
        tmp_state = next(iterablex) # carrier return
        tmp_state = next(iterablex).contents[0].contents[0]
        
        tmp_rate = next(iterablex) # carrier return
        tmp_rate = next(iterablex).contents[0].contents[0]
        
        if tmp_state.upper() == state.upper():
            rate = float(tmp_rate)

    return { 'rate': rate }   


# 3 - Retrieve historical interest for the phrase for the period <start_date,
# end_date> from Google Trends.
@app.get('/trends')
async def trends(phrase: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
    return await get_trends(phrase, start_date, end_date)

# 4 - Retrieve historical weather for the last 7 days for the client location.
@app.get('/weather')
async def weather():
    return await get_weather(app.api_key_weather)


# 5 - Retrieve Google Trend interest and weather as for the /trends and /weather.
@app.get('/trends_weather')
async def weather(phrase: str):
    trends = await get_trends(phrase, None, None) # Last 7 days
    weather = await get_weather(app.api_key_weather)
    location = weather['location']
    country = weather['country']
    t = trends['interest']  # [ 100, 100, 78, ...]
    w = weather['data']  # [ {}, {}, {}, ...]
    response = []
    for i in range(7):
        response.append({
            'date': w[i]['date'],
            'interest': t[i],
            'weather': {
                "location": location,
                "country": country,
                'data': [ w[i] ], # mantain exercise 3 structure
            }
        })
    return response




