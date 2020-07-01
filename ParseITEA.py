import requests, re
from html.parser import HTMLParser
from collections import defaultdict
import codecs
from ast import literal_eval

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

    def get_output(self):
        #print("Title: " + self.title)
        # print(self.h1)
        # print(self.start_date)
        # print(self.end_date)
        # print(self.description)
        # print(self.h5)

        partners = []
        for i in range(0, len(self.h5), 3):
            p = self.h5[i]
            if "'" not in self.h5[i]:
                p = literal_eval("b'{}'".format(p)).decode('utf-8')
            u, c = self.h5[i+1], self.h5[i+2]
            partners.append((p, u, c))

        return {
            'acronym' : self.h1[0],
            'title' : self.h1[1],
            'start_date' : self.start_date,
            'end_date' : self.end_date,
            'description' : self.description,
            'partners' : partners
        }


class ITEAParser:

    def __init__(self):
        self.out_file = open("out.csv", 'w', encoding='utf-8')

        self.headers = ["acronym", 'title', 'start_date', 'end_date', 'description', 'partners']
        for h in self.headers:
            self.out_file.write(h.title() + ";")

        self.out_file.write("Partner Link;Partner Country;")
        self.out_file.write("\n")

        self.partner_count = defaultdict(int)
        self.country_count = defaultdict(int)

    def __del__(self):

        self.out_file.close()


    def write_partner_count(self):
        with open("partner_count.csv", 'w', encoding='utf-8') as f:

            f.write("Partner;Times in Projects\n")
            for k in sorted(self.partner_count, key=self.partner_count.get, reverse=True):
                f.write(k + ";" + str(self.partner_count[k]) + "\n")

    def write_country_count(self):
        with open("country_count.csv", 'w', encoding='utf-8') as f:

            f.write("Country;Times in Projects\n")
            for k in sorted(self.country_count, key=self.country_count.get, reverse=True):
                f.write(k + ";" + str(self.country_count[k]) + "\n")


    def parse(self, url):
        if url.startswith("#"):
            return

        print(url)

        r = requests.get(url, allow_redirects=True)

        mhp = MyHTMLParser()
        mhp.feed(str(r.content))

        content = mhp.get_output()
        print(content)

        for h in self.headers:
            if h == "partners":
                continue

            self.out_file.write(str(content[h]) + ";")
        self.out_file.write("\n")

        for p in content["partners"]:
            for i in range(len(self.headers) - 1):
                self.out_file.write(";")
            self.out_file.write(p[0] + ";" + p[1] + ";" + p[2] + "\n")

            self.partner_count[p[0]] += 1
            self.country_count[p[2]] += 1

if __name__ == "__main__":

    ITEAP = ITEAParser()
    with open("ITEA_projects.txt") as f:
        for line in f:
            ITEAP.parse(line.strip())

    ITEAP.write_partner_count()
    ITEAP.write_country_count()
