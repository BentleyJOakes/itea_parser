import requests, re
from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):

    def __init__(self):
        super(MyHTMLParser, self).__init__()

        self.attrs = None

        self.title = None
        self.title_next = False

        self.h1 = []
        self.h1_count = 0

        self.h5 = []
        self.h5_count = 0

        self.date_pattern = re.compile("(\w+\s20\d\d).n\s+-\s(\w+\s20\d\d)")
        self.start_date = ""
        self.end_date = ""

        self.description_count = 0
        self.description = ""

    def handle_starttag(self, tag, attrs):
        print("Encountered a start tag:", tag)
        if tag == "title":
            self.title_next = True
        elif tag == "h1":
            self.h1_count = 1
        elif tag == "h5":
            self.h5_count = 1

        self.attrs = {}
        for attr in attrs:
            self.attrs[attr[0]] = attr[1]

    def handle_endtag(self, tag):
        pass
        #print("Encountered an end tag :", tag)

    def handle_data(self, data):
        print("Encountered some data  :", data)

        if "20" in data:
            result = self.date_pattern.search(data)
            if result:
                self.start_date = result.group(1)
                self.end_date = result.group(2)

        if self.description_count == 0 and data.strip() == "Project description":
            self.description_count = 1
        elif self.description_count > 0:
            data = data.replace("\\n", "").strip()
            if data:
                self.description = data
                self.description_count = 0


        if self.title_next:
            #data = re.sub(r'\xc2\xb7', "-", data)
            self.title = data
            self.title_next = False
        elif self.h1_count > 0:
            data = data.replace("\\n", "").strip()
            if data:
                self.h1.append(data)

            self.h1_count += 1
            if self.h1_count == 4:
                self.h1_count = 0
        elif self.h5_count > 0:
            data = data.replace("\\n", "").strip()
            if data:
                self.h5.append(data)
                #print(self.attrs)
                if 'href' in self.attrs:
                    link = self.attrs['href']
                    self.h5.append(link)

            self.h5_count += 1
            if self.h5_count == 6:
                self.h5_count = 0

    def output(self):
        print("Title: " + self.title)
        print(self.h1)
        print(self.start_date)
        print(self.end_date)
        print(self.description)
        print(self.h5)

class ITEAParser:

    def __init__(self):
        pass

    def parse(self, url):
        if url.startswith("#"):
            return

        print(url)

        r = requests.get(url, allow_redirects=True)

        mhp = MyHTMLParser()
        mhp.feed(str(r.content))

        mhp.output()


if __name__ == "__main__":

    ITEAP = ITEAParser()
    with open("ITEA_projects.txt") as f:
        for line in f:
            ITEAP.parse(line.strip())