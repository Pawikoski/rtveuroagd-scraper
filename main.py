import requests
from bs4 import BeautifulSoup
import json
from openpyxl import Workbook


class Scraper:
    def __init__(self):
        self.soup = BeautifulSoup(requests.get("https://www.euro.com.pl/telefony-komorkowe,_xiaomi.bhtml").text, 'html.parser')
        self.products_raw = self.scrap_offers()
        self.products = dict()

    def pages(self):
        return int(self.soup.findAll("a", {"class": "paging-number"})[-1].text)

    def scrap_offers(self):
        products = []
        for page in range(self.pages()):
            page += 1
            self.soup = BeautifulSoup(
                requests.get(f"https://www.euro.com.pl/telefony-komorkowe,_xiaomi,strona-{page}.bhtml").text,
                'html.parser')
            products.extend(self.soup.findAll("div", {"class": "product-row"}))

        return products

    def prepare_data(self):
        for product in self.products_raw:
            product_id = product.find("div", {"class": "selenium-product-code"})
            inner_div = product_id.div
            inner_div.decompose()
            product_id = product_id.text

            name_and_url = product.find("a", {"class": "js-save-keyword"})
            name = name_and_url.text
            url = name_and_url['href']

            price = product.find("div", {"class": "selenium-price-normal"}).text

            #   Product specs
            product_attributes = product.findAll("div", {"class": "attributes-row"})
            camera = None
            battery = None
            memory = None
            display = None
            operating_system = None
            cpu = None

            for attribute in product_attributes:
                if "aparaty" in attribute.text.lower():
                    camera = attribute.find("span", {"attribute-value"}).text
                elif "pojemność" in attribute.text.lower():
                    battery = attribute.find("span", {"attribute-value"}).text
                elif "pamięć" in attribute.text.lower():
                    memory = attribute.find("span", {"attribute-value"}).text
                elif "wyświetlacz" in attribute.text.lower():
                    display = attribute.find("span", {"attribute-value"}).text
                elif "system" in attribute.text.lower():
                    operating_system = attribute.find("span", {"attribute-value"}).text
                elif "procesor" in attribute.text.lower():
                    cpu = attribute.find("span", {"attribute-value"}).text

            self.products[product_id] = {
                "name": name,
                "url": url,
                "price": price,
                "camera": camera,
                "battery": battery,
                "memory": memory,
                "display": display,
                "os": operating_system,
                "cpu": cpu
            }

        with open("products.json", "w") as products_json:
            json.dump(self.products, products_json)


class Writer:
    def __init__(self):
        self.products = None

    def load_products(self):
        with open("products.json", "r") as products_json:
            self.products = json.load(products_json)

    def write_data(self):
        self.load_products()
        wb = Workbook()
        ws = wb.active
        ws.append(["Nr kat.", "Nazwa", "URL", "Cena", "Aparaty", "Bateria", "Pamięć", "Wyświetlacz", "System", "Procesor"])
        for product_id in self.products:
            ws.append([
                product_id,
                self.products[product_id]['name'],
                self.products[product_id]['url'],
                self.products[product_id]['price'],
                self.products[product_id]['camera'],
                self.products[product_id]['battery'],
                self.products[product_id]['memory'],
                self.products[product_id]['display'],
                self.products[product_id]['os'],
                self.products[product_id]['cpu']
            ])

        wb.save('data.xlsx')



if __name__ == "__main__":
    scraper = Scraper()
    scraper.prepare_data()

    writer = Writer()
    writer.write_data()
