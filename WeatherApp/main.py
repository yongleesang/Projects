# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import requests
import bs4
import collections

WeatherReport = collections.namedtuple('WeatherReport',
                                       'cond, temp, scale, loc')

def main():
    # print the header
    print_the_header()
    state = input("What US state do you want the weather for (e.g. OR)? ")
    city = input("What city in {} (e.g. Portland)? ")
    html = get_html_from_web(state, city)
    # parse the html

    report = get_weather_from_html(html)
    print('The temp in {} is {} {} and {}'.format(
        report.loc,
        report.temp,
        report.scale,
        report.cond,
    ))
    # get zipcode
    # get html from web


def print_the_header():
    print("------------------")
    print("         WEATHER APP")
    print("------------------")
    print()


def get_html_from_web(state, city):
    url = "https://www.wunderground.com/weather/us/{}/{}".format(state.lower().strip(), city.lower().strip())
    #print(url)
    response = requests.get(url)
    # print(response.status_code)
    return response.text


def cleanup_text(text: str):
    if not text:
        return text

    text = text.strip()
    return text


def find_city_and_state_from_location(loc: str):
    parts = loc.split(',')
    city = parts[0]
    parts_state = parts[1].strip().split(' ')
    state = parts_state[0]
    city_state = city + ' ' + state
    return city_state.strip()


def get_weather_from_html(html):
    soup = bs4.BeautifulSoup(html, 'html.parser')
    loc = soup.find(class_='city-header').find('h1').find('span').get_text()
    condition = soup.find(class_='conditions-extra').find(class_='condition-icon').find('p').get_text()
    temp = soup.find(class_='wu-value wu-value-to').get_text()
    scale = soup.find(class_='wu-label').get_text()

    loc = cleanup_text(loc)
    loc = find_city_and_state_from_location(loc)
    condition = cleanup_text(condition)
    temp = cleanup_text(temp)
    scale = cleanup_text(scale)

    report = WeatherReport(cond=condition, temp=temp, scale=scale, loc=loc)
    return report


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

