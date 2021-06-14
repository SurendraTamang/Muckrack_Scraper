import requests
from lxml import html
from lxml.html import HtmlElement
from lxml.etree import _ElementUnicodeResult as PageString
import json
from urls import URLS

DEV_MODE = False
ARTICAL_LIMIT = 125
class Muckrack:
    def __init__(self):
        self.config = {
            "rows": '//h4[@class="news-story-title"]/parent::div',
            "next_link": '//a[@class="endless_more"]/@href',
        }
        self.fields = {
            "title": ".//h4//text()",
            "time": './/a[@class="timeago"]/@title',
            "blurb": './/div[@class="news-story-body col-xs-12"]/a/following-sibling::text()',
            "url": './/div[@class="news-story-body col-xs-12"]/a/@href',
        }
        self.articles = []
        self.bio = {

        }
        self.bio_fields = {'name':'//h1[contains(@class,"profile")]/a/text()',
    'personal_title':"//div[contains(@class,'title')]/div/text()",
    'company':"//div[contains(@class,'title')]/div//a/text()",
    'company_link':"//div[contains(@class,'title')]/div//a/@href",
    'location':"//div[contains(@class,'location')]/div",
    'bio_summary':"//div[@class='mr-font-size-lg mr-font-family-2 top-sm']"
    
        }


    

    def parse_selectors(self, rows):
        """
        """
        print(f"Adding Articles: {len(self.articles)}")
        for row in rows:
            new_dict = {}
            for _k, _v in self.fields.items():
                raw_data = row.xpath(_v)
                if raw_data and raw_data[0].__class__ == PageString :
                    new_dict[_k] = raw_data[0].replace('\n','').replace('—','').strip()
                if raw_data and raw_data[0].__class__ == HtmlElement:
                    new_dict[_k] = raw_data[0].text_content().replace('\n','').strip()
            self.articles.append(new_dict)
    def parse_bio(self,page,url):
        '''
        For bio
        '''
        new_dict = {}
        for _k, _v in self.bio_fields.items():
            raw_data = page.xpath(_v)
            if raw_data:
                if raw_data and raw_data[0].__class__ == PageString :

                    new_dict[_k] = raw_data[0].replace('—','').strip()
                if raw_data and raw_data[0].__class__ == HtmlElement:
                    new_dict[_k] = raw_data[0].text_content().replace('\n','').strip()
            
        beats_list = page.xpath("//div[contains(@class,'beats')]/div/a")
        beats = {}
        for beat_ in beats_list:
            beats[beat_.xpath('./text()')[0]] = 'https://muckrack.com'+ beat_.xpath('./@href')[0]
        new_dict['beats'] = beats
        as_seen_url = url.split('/')[-2]
        url_as = f'https://muckrack.com/{as_seen_url}/as-seen-in.json'
        as_seen = self.get_response(url_as)
        new_dict['as_seen_in'] = as_seen.json()
        if 'media_link' in new_dict:
            new_dict['media_link'] = 'https://muckrack.com' + new_dict['media_link']
        self.bio['bio'] = (new_dict)


    def get_response(self,url):
        '''
        '''
        resp = requests.get(url)
        return resp

    def parse_url(self, url, first_page = True):
        """
        """
        if url.startswith("/"):
            url = "https://muckrack.com" + url
        resp = self.get_response(url)
        page = html.fromstring(resp.text)
        if first_page:
            print("Calling first time only")
            self.parse_bio(page,url)
        rows = page.xpath(self.config["rows"])
        self.parse_selectors(rows)
        next_links = page.xpath(self.config["next_link"])
        if DEV_MODE:
            if len(self.articles) > ARTICAL_LIMIT:
                return None
            
        if next_links:
            print(f"URL: {next_links[0]}")
            self.parse_url(next_links[0], first_page= False)

    def crawl(self, url):
        """
        """
        print(url)
        self.parse_url(url)
        self.close(url)

    def close(self,url):
        file_name = as_seen_url = url.split('/')[-2]
        with open(f"{file_name}.json", "w", encoding="utf-8") as fp:
            article = {'bio':self.bio['bio'], 'articles':self.articles}
            json.dump(article, fp, indent=2, ensure_ascii=False)
    


if __name__ == "__main__":
    #URLS = 
    for url in URLS:
        crawler = Muckrack()
        crawler.crawl(url)
