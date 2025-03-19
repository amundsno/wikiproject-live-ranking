import logging
import requests
import time

from config import WIKIPEDIA_API_URL

def fetch_wikiprojects(title: str) -> list[str]:
    url = f'{WIKIPEDIA_API_URL}?action=query&format=json&prop=links&titles=Talk:{title}&formatversion=2&plnamespace=4&pllimit=100&pldir=descending'
    start_time = time.time_ns()
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        wikiprojects = extract_wikiprojects(data)

        elapsed_time = round((time.time_ns() - start_time)/10e6, 2)
        logging.info(f'Fetched {len(wikiprojects)} WikiProjects for {title} in {elapsed_time}ms')
        return wikiprojects

    except requests.exceptions.RequestException as e:
        logging.warning(f'Failed to fetch WikiProject data for {title}: {e}')
        return []

def extract_wikiprojects(data: dict) -> list[str]:
    pages = data.get('query', {}).get('pages', [])
    if not pages:
        return []

    links = pages[0].get('links', [])

    return [
        link['title'].split('Wikipedia:WikiProject ')[-1]
        for link in links
        if 'Wikipedia:WikiProject ' in link['title'] and '/' not in link['title']
        ]