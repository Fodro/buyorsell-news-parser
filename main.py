import requests
from bs4 import BeautifulSoup

url_to_parse = "https://meduza.io/news/2021/07/06/na-byvshego-gubernatora-kirovskoy-oblasti-nikitu-belyh-zaveli-delo-o-prevyshenii-polnomochiy"

def parse_meduza(url_to_parse):
	html_page = requests.get(url_to_parse)

	soup = BeautifulSoup(html_page.content, 'html.parser')

	page_header = soup.find('div', class_='GeneralMaterial-materialHeader')

	news_header = page_header.find('h1')
	news_time = page_header.find('div').find('time')

	news_source = page_header.find('div').find('a')

	news_content = soup.find('div', class_='GeneralMaterial-article')
	news_text = news_content.find_all('p')
	text = ""
	for paragraph in news_text:
		text += paragraph.text + "\n"
	response = {
		"header": news_header.text,
		"text": text.replace('\xa0', " "),
		"datetime": news_time.text,
		"tags": [],
		"source": news_source,
		"author": "",
	}
	return response


