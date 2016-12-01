from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, parse_qs, urlencode

from abc import ABCMeta, abstractmethod


class Element(metaclass=ABCMeta):
    def __init__(self, soup):
        self.soup = soup
        if soup is None:
            self.json = {}
        else:
            self.json = self.parse(soup)

    @abstractmethod
    def parse(self, soup):
        return

    def __repr__(self):
        return str(self.json)


class Title(Element):
    def parse(self, soup):
        title = {}
        title_span = soup.find(class_="match")
        title["title"] = title_span.getText()
        title["attributes"] = soup.find(class_="tekstmedium").getText()
        return {"title": title}


class Pronunciations(Element):
    def parse(self, soup):
        pronunciations = []
        dividers = soup.find_all(class_="dividerDouble")
        for d in dividers:
            d.replace_with("|")
        pronunciations_soup = repr(soup).split("|")
        for v in pronunciations_soup:
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
            pronunciations.append(item)
        return {"pronunciations": pronunciations}


class Definitions(Element):
    def parse(self, soup):
        definitions = []
        definitions_soup = soup.find_all(class_="definition")
        for d in definitions_soup:
            item = {}
            parent = None
            for p in d.parents:
                if p.get("class") == ["definitionIndent"]:
                    parent = p
                    break
            if parent is None:
                continue
            item["definition"] = parent.find(class_="definition").getText()
            synonyms_div = parent.find(text="Synonym")
            if synonyms_div:
                synonyms = synonyms_div.parent.parent.find_all("a")
                if synonyms:
                    item["synonyms"] = []
                    for s in synonyms:
                        item["synonyms"].append(s.getText())
            grammar = parent.find(class_="grammatik")
            if grammar:
                item["grammar"] = grammar.find(class_="inlineList").getText()
            definitions.append(item)
            quotes = parent.find_all(class_="citat")
            if quotes:
                item["quotes"] = []
                for e in quotes:
                    item["quotes"].append(e.getText())
            examples_span = parent.find(text="Eksempler")
            if examples_span:
                examples = examples_span.parent.parent.find(
                    class_="inlineList")
                if examples:
                    item["examples"] = examples.getText()
        return {"definitions": definitions}


class Suggestions(Element):
    def parse(self, soup):
        suggestions = []
        for arrow in soup.find_all(class_="arrow-mini"):
            arrow.replace_with("→")
        suggestions_soup = soup.find_all("a")
        for s in suggestions_soup:
            item = {}
            item["text"] = s.getText().strip()
            href = urlparse(s.get("href"))
            qs = href.query
            item["query"] = parse_qs(qs)
            item["qs"] = qs
            suggestions.append(item)
        return {"suggestions": suggestions}


class Inflection(Element):
    def parse(self, soup):
        inflection = soup.find(class_="tekstmedium").getText()
        return {"inflection": inflection}


class Entry:
    def __init__(self, query, select=""):
        query_string = urlencode({"query": query, "select": select})
        url = "http://ordnet.dk/ddo/ordbog?{}".format(query_string)
        resp = requests.get(url)
        if resp.ok:
            html = resp.content
            self.soup = BeautifulSoup(html, 'html.parser')
            self.title = Title(
                self.soup.find(class_="definitionBoxTop")).json
            self.inflection = Inflection(
                self.soup.find(id="id-boj")).json
            self.pronunciations = Pronunciations(
                self.soup.find(id="id-udt")).json
            self.definitions = Definitions(
                self.soup.find(id="content-betydninger")).json
            self.faste_udtryk = Definitions(
                self.soup.find(id="content-faste-udtryk")).json
            self.suggestions = Suggestions(
                self.soup.find(class_="searchResultBox")).json
        else:
            raise ValueError

    def serialize(self):
        return {**self.title, **self.inflection, **self.pronunciations,
                **self.definitions, **self.faste_udtryk,
                **self.suggestions}

    def __repr__(self):
        return str(self.title)
