import requests                          # life_expectancy unemployment
import json                              # life_expectancy weather
from pytrends.request import TrendReq    # trends
from datetime import datetime, timedelta # trends
from xml.dom import minidom              # weather
import urllib                            # weather


URL_WHATS_MY_IP = 'https://api.my-ip.io/ip'
BASE_URL_WEATHER_API = 'https://api.weatherapi.com/v1'
URL_GEOLOC = 'http://ip-api.com/json/'
######################### HELPER FUNCTIONS #########################

# Used in /trends
async def get_trends(phrase, start_date=None, end_date=None):
    trend = TrendReq(hl='en-US', tz=360)
    cat = 0
    geo = ''
    gprop = ''

    try: # Check optional parameters
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    except:
        # if dates not specified defaults to two weeks ago
        end_date = datetime.now()
        start_date = end_date - timedelta(days = 14)
    
    timeframe = f"{start_date.strftime('%Y-%m-%d')} {end_date.strftime('%Y-%m-%d')}"
    
    # Use asynchronous calls to the external services
    totalTrend = await get_totalTrend(trend, phrase, cat, timeframe, geo, gprop)
    return {'interest': totalTrend[phrase].to_list()}

# Used in /get_ternds
# Use asynchronous calls to the external services
async def get_totalTrend(trend, phrase, cat, timeframe, geo, gprop):
    trend.build_payload([phrase], cat=cat, timeframe=timeframe, geo=geo, gprop=gprop)
    totalTrend = trend.interest_over_time()
    return totalTrend


# Used in /get_weather
# https://stackoverflow.com/a/28165957/3865092
async def geoloc():
    ip = requests.get(URL_WHATS_MY_IP).text # What is my ip?
    url = URL_GEOLOC + ip # Geoloc service
    req = urllib.request.Request(url)
    bjson = urllib.request.urlopen(req).read() 
    out = json.loads(bjson)
    return out["city"]


# Used in /get_weather
# Use asynchronous calls to the external services
async def get_xml(url):
    xml_str = urllib.request.urlopen(url).read()
    return xml_str


# Used in /weather
async def get_weather(api_key_weather):
    # collect and prepare query parameters
    CITY = await geoloc()
    end_date = datetime.now()
    start_date = end_date - timedelta(days = 6)
    API_ENDDT = f"{end_date.strftime('%Y-%m-%d')}"
    API_DT = f"{start_date.strftime('%Y-%m-%d')}"
    API_QUERY = f"/history.xml?key={api_key_weather}&dt={API_DT}&q={CITY}&end_dt={API_ENDDT}"

    # Retrieve data for the last 7 days as XML
    # Use asynchronous calls to the external services
    xml_str = await get_xml(f"{BASE_URL_WEATHER_API}{API_QUERY}")
    xmldoc = minidom.parseString(xml_str)

    # Extract relevant info for our JSON schema
    # Output schema inspired by: https://www.eltiempo.es/malaga.html
    name = xmldoc.getElementsByTagName('name')[0].firstChild.nodeValue
    country = xmldoc.getElementsByTagName('country')[0].firstChild.nodeValue
    days = xmldoc.getElementsByTagName('forecastday')

    # Extract the desired info for each of the 7 days 
    data = [] # root of our json
    for day in days:
        current_date_json = {}
        current_date = day.firstChild.firstChild.nodeValue # 2022-07-01
        hours = day.getElementsByTagName('hour') # All 24 hours
        current_date_json["date"] = current_date

        # Get only this hours: 8:00  14:00  20:00 
        for desc, h in [('morning', 8), ('afternoon', 14), ('evening', 20)]:
            current_date_json[desc] = {
                    'time': hours[h].childNodes[1].firstChild.nodeValue.split(" ")[-1],
                    'temp_c': hours[h].childNodes[2].firstChild.nodeValue,
                    'description': hours[h].childNodes[5].firstChild.firstChild.nodeValue,
                    'icon': hours[h].childNodes[5].firstChild.nextSibling.firstChild.nodeValue,
            }
        data.append(current_date_json)

    output = {
        'location': name, 
        'country': country,
        'data': data
    }
    return output


html_content = """
    <html>
        <head>
            <title>Fortris - Tech assignment</title>
            
<style>
body            
{
    margin:auto;
    width:1024px;
    padding:100px;
    background-color:#ebebeb;
    font-size:14px;
    font-family:Verdana;
}
ul {
    counter-reset: index;  
    padding: 0;
    max-width: 400px;
  }
  
  /* List element */
  li {
    counter-increment: index; 
    display: flex;
    align-items: center;
    padding: 12px 0;
    box-sizing: border-box;
  }
  
  
  /* Element counter */
  li::before {
    content: counters(index, ".", decimal-leading-zero);
    font-size: 1.5rem;
    text-align: right;
    font-weight: bold;
    min-width: 50px;
    padding-right: 12px;
    font-variant-numeric: tabular-nums;
    align-self: flex-start;
    background-image: linear-gradient(to bottom, aquamarine, blue);
    background-attachment: fixed;
    -webkit-background-clip: text;01
    -webkit-text-fill-color: transparent;
  }
  
  
  /* Element separation */
  li + li {
    border-top: 1px solid rgba(0,0,0,0.2);
  }
  
  @use postcss-preset-env {
    stage: 0;
    autoprefixer: {
      grid: true;
    }
    browsers: last 2 versions
  }
  
</style>
            
        </head>
        <body>
            <h3>The goal of this challenge is to build an integration API service with five endpoints.</h3>
            <h5>Visit the autogenerated <a href='/docs'>FASTAPI doc</a> for fine-tunning or click on this hardcoded samples</h5>
            <ul>
                <li><a href='/life_expectancy/Female/White/2013'>Life expectancy</a></li>
                <li><a href='/unemployment/california'>Unemployment</a></li>
                <li><a href='/trends?phrase=bitcoin&start_date=2022-01-01&end_date=2022-01-31'>Google Trends</a></li>
                <li><a href='/weather'>Weather</a></li>
                <li><a href='/trends_weather?phrase=bitcoin'>Google Trend and Weather (async)</a></li>
            </ul>
        </body>
    </html>
    """