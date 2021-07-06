import requests
import os
import json
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException

url_to_start = "https://www.kommersant.ru/archive/news/"

def parse_commersant(url_to_parse):
    html_page = requests.get(url_to_parse)
    soup = BeautifulSoup(html_page.content, 'html.parser')

    news_body = soup.find("div", class_="lenta js-lenta").find("article")
    
    author = news_body.get("data-article-authors")
    
    header = news_body.find("header").find("div", class_="text").find("h1").text

    try:
        subheader = news_body.find("header").find("div", class_="text").find(
            "h1", class_="article_subheader").text
    except:
        subheader = ""

    rubric = news_body.get("data-article-categories")

    body = news_body.find(
        "div", class_="article_text_wrapper").find_all("p", class_="b-article__text")
    
    text = ""
    for item in body:
        text += item.text + "\n"
    
    datetime = soup.find("time", class_="title__cake").get("datetime")
    
    source = "commersant"
    response = {
        "header": header,
        "text": text,
        "rubric": rubric,
        "datetime": datetime,
        "subheader": subheader,
        "tags": [],
        "source": source,
    }
    return response


def dump_into_json(site, data):
    counter = 0
    while os.path.isfile(site + "-" + str(counter) + ".json"):
        counter += 1
    with open(site + "-" + str(counter) + ".json", "w", encoding='utf8') as file:
        json.dump(data, file, ensure_ascii=False)


def crawl_commersant(url_to_start):
    links = []
    opts = FirefoxOptions()
    opts.add_argument('--headless')
    driver = webdriver.Firefox(options=opts)
    actions = ActionChains(driver)
    print("check")
    driver.get(url_to_start)
    while True:
        data = []
        news = driver.find_elements_by_class_name("archive_date_result__item")
        for item in news:
            link = item.find_element_by_tag_name("a").get_attribute("href")
            print(link)
            if link not in links:
                links.append(link)
                content = parse_commersant(link)
                data.append(content)
        dump_into_json("commersant", data)
        try:
            resume = driver.find_element_by_class_name(
                "ui_button ui_button--load_content lazyload-button")
            actions.move_to_element(resume).perform()
            resume.click()
        except NoSuchElementException:
            change_page = driver.find_element_by_class_name("archive_date__arrow--prev")
            driver.get(change_page.get_attribute("href"))
        
crawl_commersant(url_to_start)
