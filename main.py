# This is a sample Python script.
import json
import requests
from bs4 import BeautifulSoup
from typing import TypedDict, Literal

# typing
class EpeEventData(TypedDict):
    title: str
    description: str
    website: str
    address: str

class EpeWebsiteData(TypedDict):
    url: str
    events: list[EpeEventData]

class UrlSources:
    _epe: list[str] = [
        'https://vvvepe.nl/evenementen/maand',
        'https://vvvepe.nl/zien-doen/attracties-bezienswaardigheden',
    ]
    _hattem: list[str] = []

    def get_city(self, city: Literal['epe', 'hattem']) -> list[str]:
        city_name = f"_{city.strip()}"

        return getattr(self, city_name, [])


def preparation_script(name: str) -> None:
    print(f'Hi, {name}')
    print(f'This is a beautifulSoup project that scrapes URLs for fun events nearby!')

def make_soup(url: str) -> BeautifulSoup:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return BeautifulSoup(response.content, 'html.parser')
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return BeautifulSoup("", 'html.parser')

def parse_data_epe(soup: BeautifulSoup) -> list[EpeEventData]:
    # This function will parse the BeautifulSoup object and extract relevant data
    events: list[EpeEventData] = []
    event_list_el = []
    script_tag = soup.find('script', id='__NEXT_DATA__')

    # Process JSON data to extract event information
    if script_tag is not None:
        raw_data = script_tag.string

        if raw_data is not None:
            script_content = json.loads(raw_data)

            if 'atracties' in script_content['props']['pageProps']:
                # for URL: 'https://vvvepe.nl/zien-doen/attracties-bezienswaardigheden'
                event_list_el = script_content['props']['pageProps']['atracties']
            elif 'events' in script_content['props']['pageProps']:
                # for URL: https://vvvepe.nl/evenementen/maand'
                event_list_el = script_content['props']['pageProps']['events']

    if len(event_list_el) == 0 or not event_list_el:
        print('Aborting mission: No events found on this page!')
        return events

    for event_data in event_list_el:
        # Initialize the actual data!!
        title = 'Untitled Event'
        desc = 'No description available'
        website = 'Unknown Website'
        address = 'Unknown Address'

        title_el = event_data.get('what', {}).get('title', {}).get('value', None)
        desc_el = event_data.get('what', {}).get('shortdescription', {}).get('value', None)
        address_el: str = f"{event_data['location']['street']} {event_data['location'].get('housenr', '')} {event_data['location'].get('zipcode', '')}, {event_data['location']['city'].capitalize()}"
        website_el = None
        contact_info = event_data.get('contactinformation')

        # get the website!
        if contact_info is not None and isinstance(contact_info, dict):
            urls = contact_info.get('urls', [])
            if urls and isinstance(urls, list) and len(urls) >= 1:
                website_el = urls[0].get('value') if isinstance(urls[0], dict) else None

        if title_el is not None:
            title = title_el.strip()
        if desc_el is not None:
            desc = desc_el.strip()
        if website_el is not None:
            website = website_el.strip()
        if address_el is not None:
            address = address_el.strip()

        events.append({'title': title, 'description': desc, 'website': website, 'address': address})

    return events

def process_epe_events():
    result: list[EpeWebsiteData] = []
    url_sources = UrlSources().get_city('epe')

    print('Start processing events in Epe...')
    print('Scraping data from URLs...')

    for url in url_sources:
        print(f'Processing {url}...')
        soup = make_soup(url)
        events = parse_data_epe(soup)
        result.append({'url': url, 'events': events})

    print('Scraping completed!')
    print('Results:')

    for website in result:
        print(f"URL: {website['url']}")
        for event in website['events']:
            print(f"  Title: {event['title']}")
            print(f"  Description: {event['description']}")
            print(f"  Website: {event['website']}")
            print(f"  Address: {event['address']}")
            print('---')

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    preparation_script('Jeka')
    process_epe_events()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
