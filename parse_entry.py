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
            faste_udtryk_soup = self.soup.find(id="content-faste-udtryk")
            self.faste_udtryk = self.parse_definitions(faste_udtryk_soup)
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
        dividers = pronunciation_soup.find_all(class_="dividerDouble")
        for d in dividers:
            d.replace_with("|")
        pronunciations = repr(pronunciation_soup).split("|")
        for v in pronunciations:
            p = BeautifulSoup(v, "html.parser")
            item = {}
            item["text"] = p.getText().strip().replace("Udtale\n", "")
            item["transcriptions"] = []
            for q in p.find_all(class_="lydskrift"):
                variant = {}
                variant["transcription"] = q.getText().strip()
                if q.find("audio"):
                    variant["audio"] = q.find("audio").a["href"]
                item["transcriptions"].append(variant)
            pronunciation["json"].append(item)
        return pronunciation

    def parse_definitions(self, definition_soup):
        definition = {}
        definition["html"] = definition_soup
        definition["json"] = []
        definitions = definition_soup.find_all(class_="definition")
        for d in definitions:
            item = {}
            parent = None
            for p in d.parents:
                if p.get("class") == ["definitionIndent"]:
                    parent = p
                    break
            if parent is None:
                continue
            item["definition"] = parent.find(class_="definition").getText()
            synonyms_div = parent.find(class_="onym")
            if synonyms_div:
                synonyms = synonyms_div.find_all("a")
                if synonyms:
                    item["synonyms"] = []
                    for s in synonyms:
                        item["synonyms"].append(s.getText())
            grammar = parent.find(class_="grammatik")
            if grammar:
                item["grammar"] = grammar.find(class_="inlineList").getText()
            definition["json"].append(item)
            quotes = parent.find_all(class_="citat")
            if quotes:
                item["quotes"] = []
                for e in quotes:
                    item["quotes"].append(e.getText())
            examples_span = parent.find(text="Eksempler")
            if examples_span:
                examples = examples_span.parent.parent.find(class_="inlineList")
                if examples:
                    item["examples"] = examples.getText()
        return definition
