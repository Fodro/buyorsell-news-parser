import requests
import os
import json
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup

url_to_start = "https://meduza.io/"


def parse_meduza(url_to_parse):
    html_page = requests.get(url_to_parse)

    soup = BeautifulSoup(html_page.content, 'html.parser')

    page_header = soup.find('div', class_='GeneralMaterial-materialHeader')

    news_header = page_header.find('h1')
    news_time = soup.find('time')
    try:
        news_source = page_header.find('div').find('a')
        source = news_source.text
    except:
        source = "meduza"
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
        "source": source,
        "author": "",
    }
    return response


def crawl_meduza(url_to_start):
    links = []
    opts = FirefoxOptions()
    opts.add_argument('--headless')
    driver = webdriver.Firefox(options=opts)
    actions = ActionChains(driver)
    print("check")
    driver.get(url_to_start)
    gdpr_panel_dismiss = driver.find_element_by_class_name("GDPRPanel-dismiss")
    gdpr_panel_dismiss.click()
    switch = driver.find_element_by_tag_name("input")
    switch.click()
    while True:
        data = []
        news = driver.find_elements_by_class_name("ChronologyItem-link")
        for item in news:
            link = item.get_attribute('href')
            print(link)
            if link not in links:
                links.append(link)
                if "/feature/" in link or "/news/" in link:
                    content = parse_meduza(link)
                    data.append(content)
                else:
                    continue
        dump_into_json("meduza", data)
        resume = driver.find_element_by_css_selector(
            "button[class^='Button-module_root']")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        footer = driver.find_element_by_class_name("Footer-giphy")
        actions.move_to_element(footer).perform()
        resume.click()


def dump_into_json(site, data):
    counter = 0
    while os.path.isfile(site + "-" + str(counter) + ".json"):
        counter += 1
    with open(site + "-" + str(counter) + ".json", "w", encoding='utf8') as file:
        json.dump(data, file, ensure_ascii=False)


crawl_meduza(url_to_start)
