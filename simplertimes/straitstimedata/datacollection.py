import requests
from bs4 import BeautifulSoup
import csv
import re
import html

urls = [
    'https://www.straitstimes.com/singapore/transport/construction-of-the-johor-bahru-singapore-rts-link-45-completed-on-the-s-pore-side-iswaran',
    'https://www.straitstimes.com/business/ubs-agrees-to-buy-credit-suisse-as-global-regulators-reassure-markets',
    'https://www.straitstimes.com/business/banking/singapore-bank-stocks-hit-by-credit-suisse-crisis-us-bank-failures',
    'https://www.straitstimes.com/world/europe/putin-says-china-s-proposal-could-be-basis-for-peace-in-ukraine-after-meeting-with-xi',
    'https://www.straitstimes.com/sport/football/football-south-korea-blow-lead-to-give-klinsmann-debut-draw-against-colombia',
    'https://www.straitstimes.com/asia/east-asia/hk-socialite-s-headless-body-found-6-other-gruesome-murders-that-shocked-the-city',
    'https://www.straitstimes.com/singapore/courts-crime/man-accused-of-killing-felicia-teo-loses-appeal-to-be-completely-cleared-of-murder-charge',
    'https://www.straitstimes.com/singapore/transport/construction-of-jurong-region-mrt-line-begins-stations-to-open-in-three-stages-from-2027-to-2029',
    'https://www.straitstimes.com/world/europe/ukraine-claims-russian-forces-left-kherson-region-town',
    'https://www.straitstimes.com/sport/football/football-arsenal-draw-at-sporting-roma-beat-sociedad-in-europa-league',
    'https://www.straitstimes.com/singapore/commercial-tech-gaining-ground-in-military-domain-lawrence-wong',
    'https://www.straitstimes.com/tech/tech-news/microsoft-to-bring-openai-s-chatbot-technology-to-the-office',
    'https://www.straitstimes.com/singapore/politics/president-halimah-gives-assent-to-govt-spending-plans-under-budget-2023',
    'https://www.straitstimes.com/singapore/politics/singapore-came-through-pandemic-well-without-spending-excessively-lawrence-wong',
    'https://www.straitstimes.com/singapore/environment/nea-free-reusable-containers-green-habits-cut-plastic-waste-sustainability',
    'https://www.straitstimes.com/world/171-trillion-pieces-of-plastic-trash-now-clog-the-world-s-oceans',
    'https://www.straitstimes.com/singapore/vaccination-strategy-kept-covid-19-death-rates-low-migrant-worker-outbreak-could-have-been-disastrous',
    'https://www.straitstimes.com/business/s-pore-insurers-to-retain-covid-19-coverage-such-as-for-vaccine-side-effects-in-post-pandemic-era',
    'https://www.straitstimes.com/world/united-states/how-tiktok-became-a-us-china-national-security-issue',
    'https://www.straitstimes.com/world/united-states/youtube-restores-donald-trumps-channel']

headers = {
    'Accept-Encoding': 'gzip, deflate, br',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
}


def clean_text(text):
    text = re.sub(r'REUTERS|[^\x00-\x7F]+', '', text)
    text = html.unescape(text)
    return text


def scrape_text(url):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        article = soup.find('div', {
            'class': 'clearfix text-formatted field field--name-field-paragraph-text field--type-text-long field--label-hidden field__item'})

        if article:
            text = ' '.join(p.get_text() for p in article.find_all('p'))
            cleaned_text = clean_text(text)
            return cleaned_text
    return None


with open('straitstimes_text.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['URL', 'article'])

    for url in urls:
        text = scrape_text(url)
        if text:
            print(f'Successfully scraped text from: {url}')
            csv_writer.writerow([url, text])
        else:
            print(f'Failed to scrape text from: {url}')
