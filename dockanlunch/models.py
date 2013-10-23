# coding: utf-8

import abc
from urllib2 import urlopen
from datetime import datetime
from bs4 import BeautifulSoup

class Restaurant:
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, cache):
        self.cache = cache
    
    def get_name(self):
        return self.__class__.__name__
    
    def get_courses(self):
        courses = self.cache.get(self.get_name())
        if courses is None:
            courses = self.fetch()
            if courses:
                self.cache.set(self.get_name(), courses, timeout=3600)
        return courses
    
    @abc.abstractmethod
    def fetch(self):
        return
    

class Stereo(Restaurant):
    def fetch(self):
        soup = BeautifulSoup(urlopen("http://stereo-malmo.se/"), "html5lib")
        content = soup.find("div", class_ = "circle")
        courses = [el.get_text() for el in content.find_all("li")]
        return courses
    

class DOCItaliano(Restaurant):
    def fetch(self):
        soup = BeautifulSoup(urlopen("http://www.docitaliano.se/"), "html5lib")
        content = soup.find("div", class_ = "post_content")
        strongs = content.find_all("strong")
        for i in xrange(len(strongs)):
            if "Dagens lunch" in strongs[i].get_text():
                return [
                    strongs[i+1].parent.get_text(),
                    strongs[i+1].parent.find_next("p").find_next("strong").parent.get_text()
                ]
    

class P2(Restaurant):
    def fetch(self):
        """Finds today's P2 courses by a text search, rather than
        looking for specific elements.
        """
        # Their site specifies `bizpart.se` - that is obviously a very bad product.
        # At least send the encoding of the document ffs.
        soup = BeautifulSoup(urlopen("http://www.restaurangp2.se/sv/sidor/176/171/lunchmeny.aspx"),
                             "html5lib", from_encoding="UTF-8")
        container = soup.find("div", id="MyBPControlLayout_Container_510_divContainer")
        t = container.get_text().lower()
        d0 = datetime.now().weekday()
        d1 = (d0+1) % 7
        # Heroku doesn't have non-English locales installed...
        days = [u'måndag', u'tisdag', u'onsdag', u'torsdag', u'fredag',
                     u'lördag', u'söndag']
        day_start = t.find(days[d0])
        next_day_start = t.find(days[d1])
        
        if day_start > 0 and next_day_start > day_start:
            courses_text = container.get_text()[day_start:next_day_start]
            # Remove non-braking spaces
            courses_text = courses_text.replace(u'\xa0', u' ')
            # Exclude day heading and empty line
            return courses_text.split(u'\n')[1:-1]
        return []
    

class WhiteShark(Restaurant):
    def fetch(self):
        soup = BeautifulSoup(urlopen("http://gastrogate.com/restaurang/whiteshark/page/3/"), "html5lib")
        container = soup.find("table", class_ = "lunch_menu")
        d = datetime.now().weekday()
        courses = []
        if d < 5:
            course_trs = container.find_all("tr", class_ = "no_divider")
            todays = course_trs[d].find("td", class_ = "td_title")
            if todays:
                courses.append(todays.get_text())
            alternative = course_trs[5].find("td", class_ = "td_title")
            if alternative:
                courses.append(alternative.get_text())
        return courses
    

def get_all(cache):
    return [r(cache) for r in (Stereo, DOCItaliano, P2, WhiteShark)]

