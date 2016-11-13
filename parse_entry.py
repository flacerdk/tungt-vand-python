from bs4 import BeautifulSoup
import requests


class Entry:
    def __init__(self, word):
        url = "http://ordnet.dk/ddo/ordbog?query={}".format(word)
        resp = requests.get(url)
        if resp.ok:
            html = resp.content
            self.soup = BeautifulSoup(html, 'html.parser')
            title_soup = self.soup.find(class_="definitionBoxTop")
            self.title = self.parse_title(title_soup)
            pronunciation_soup = self.soup.find(id="id-udt")
            self.pronunciations = self.parse_pronunciation(pronunciation_soup)
            definition_soup = self.soup.find(id="content-betydninger")
            self.definitions = self.parse_definitions(definition_soup)
        else:
            raise ValueError

    def parse_title(self, title_soup):
        title = {}
        title["html"] = title_soup
        title["title"] = title_soup.find(class_="match").getText()
        title["attributes"] = title_soup.find(class_="tekstmedium").getText()
        return title

    def parse_pronunciation(self, pronunciation_soup):
        pronunciation = {}
        pronunciation["html"] = pronunciation_soup
        pronunciation["json"] = []
        pronunciation_list = pronunciation_soup.find_all(class_="lydskrift")
        for p in pronunciation_list:
            item = {}
            item["transcription"] = p.getText().strip()
            if p.find("audio"):
                item["audio"] = p.find("audio").a["href"]
            pronunciation["json"].append(item)
        return pronunciation

    def parse_definitions(self, definition_soup):
        definition = {}
        definition["html"] = definition_soup
        definition["json"] = []
        definition_list = definition_soup.find_all(class_="definitionIndent")
        for d in definition_list:
            item = {}
            item["definition"] = d.find(class_="definition").getText()
            synonyms = d.find(class_="onym")
            if synonyms:
                item["synonyms"] = []
                for s in synonyms.find(class_="inlineList").find_all("a"):
                    item["synonyms"].append(s.getText())
            definition["json"].append(item)
        return definition
