import requests
from bs4 import BeautifulSoup
import csv
import re
import html

urls = [
    'https://www.straitstimes.com/singapore/transport/construction-of-the-johor-bahru-singapore-rts-link-45-completed-on-the-s-pore-side-iswaran',
    'https://www.straitstimes.com/world/united-states/ftxs-bankman-fried-pleads-not-guilty-to-campaign-finance-china-bribery-charges',
    'https://www.straitstimes.com/asia/east-asia/beijing-may-allow-foreign-financial-firms-to-list-in-china-ex-finance-minister-lou-jiwei',
    'https://www.straitstimes.com/asia/east-asia/taiwan-faces-choice-of-peace-and-war-ex-president-ma-ying-jeou-says-after-china-trip',
    'https://www.straitstimes.com/sport/football/football-south-korea-blow-lead-to-give-klinsmann-debut-draw-against-colombia',
    'https://www.straitstimes.com/sport/para-champion-pistorius-up-for-parole-in-girlfriends-murder',
    'https://www.straitstimes.com/singapore/courts-crime/man-accused-of-killing-felicia-teo-loses-appeal-to-be-completely-cleared-of-murder-charge',
    'https://www.straitstimes.com/singapore/transport/construction-of-jurong-region-mrt-line-begins-stations-to-open-in-three-stages-from-2027-to-2029',
    'https://www.straitstimes.com/world/europe/ukraine-claims-russian-forces-left-kherson-region-town',
    'https://www.straitstimes.com/sport/football/football-arsenal-draw-at-sporting-roma-beat-sociedad-in-europa-league',
    'https://www.straitstimes.com/world/united-states/microsoft-co-founder-bill-gates-says-calls-to-pause-ai-won-t-solve-challenges-posed-by-new-technology',
    'https://www.straitstimes.com/world/europe/italy-blocks-ai-chatbot-chatgpt-over-data-privacy-failings',
    'https://www.straitstimes.com/singapore/politics/president-halimah-gives-assent-to-govt-spending-plans-under-budget-2023',
    'https://www.straitstimes.com/world/europe/britain-s-hunt-pledges-reform-to-spur-slow-economy-in-budget-speech',
    'https://www.straitstimes.com/business/banking/only-37-of-smes-surveyed-have-a-clear-road-map-on-how-to-achieve-their-sustainability-goals',
    'https://www.straitstimes.com/world/171-trillion-pieces-of-plastic-trash-now-clog-the-world-s-oceans',
    'https://www.straitstimes.com/world/europe/china-holds-the-key-to-understanding-covid-19-origins-who-chief',
    'https://www.straitstimes.com/singapore/courts-crime/jail-for-man-who-tried-extorting-mbs-staff-by-threatening-to-expose-alleged-covid-19-rule-breach',
    'https://www.straitstimes.com/world/europe/britain-watchdog-fines-tiktok-21m-for-misusing-children-s-data',
    'https://www.straitstimes.com/world/united-states/youtube-restores-donald-trumps-channel']

headers = {
    'Accept-Encoding': 'gzip, deflate, br',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
}


def clean_text(text):
    text = re.sub(r'REUTERS|AFP|BLOOMBERG|[^\x00-\x7F]+', '', text)
    text = html.unescape(text)
    return text


def scrape_text(url):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        article = soup.find('div', {
            'class': 'ds-wrapper article-content-rawhtml'})

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
