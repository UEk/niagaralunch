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
        if hasattr(self, "name"):
            return self.name
        else:
            return self.__class__.__name__
    
    def get_courses(self):
        courses = self.cache.get(self.get_name())
        if courses is None:
            try:
                courses = self.fetch()
            except:
                return []
            if courses:
                self.cache.set(self.get_name(), courses, timeout=3600)
        return courses
    
    def day_range(self, forced_start_day = None):
        # Heroku doesn't have non-English locales installed...
        days = [u'måndag', u'tisdag', u'onsdag', u'torsdag', u'fredag',
                u'lördag', u'söndag']
        if forced_start_day is not None:
            d0 = forced_start_day
        else:
            d0 = datetime.now().weekday()
        d1 = (d0 + 1) % 7
        return {
            'today': {
                'i': d0,
                'name': days[d0]
            },
            'tomorrow': {
                'i': d1,
                'name': days[d1]
            }
        }
    
    def find_menu_text(self, container_text):
        d = self.day_range()
        t = container_text.lower()
        day_start = t.find(d['today']['name'])
        next_day_start = t.find(d['tomorrow']['name'])
        t = container_text[day_start:next_day_start]
        # Filter out unicode nbsp:
        t = t.replace(u"\xa0", u"")
        return t
    
    @abc.abstractmethod
    def fetch(self):
        return
    

class Stereo(Restaurant):
    url = "http://stereo-malmo.se/veckans-lunch/"
    
    def fetch(self):
        soup = BeautifulSoup(urlopen(self.url), "html5lib")
        start_el = soup.find("h5")
        container = start_el.parent
        # Remove from further text search
        start_el.extract()
        
        menu_text = self.find_menu_text(container.text)
        courses = menu_text.split("\n")[1:3]
        
        # Veg is special case, always last
        veg_start = container.text.find("Veckans Vegetariska")
        if veg_start:
            courses += container.text[veg_start:].split("\n")[1:2]
        
        return courses
    

class DOCItaliano(Restaurant):
    name = u"DOC Italiano"
    url = "http://www.docitaliano.se/"
    
    def fetch(self):
        soup = BeautifulSoup(urlopen(self.url), "html5lib")
        container = soup.find("div", class_ = "post_content")
        menu_text = self.find_menu_text(container.text)
        return menu_text.split("\n")[1:3]
    

class P2(Restaurant):
    url = "http://restaurangp2.se/lunch"
    
    def fetch(self):
        # Holy crap. New site actually uses classes `monday` - `friday`
        # to identify the respective days. However... If you don't close
        # your divs properly, and Thursday goes within Wednesday, you're
        # doing it wrong. So close!
        soup = BeautifulSoup(urlopen(self.url), "html5lib")
        day_name = datetime.now().strftime("%A").lower()
        day_container = soup.find("div", id = day_name)
        if day_container:
            courses = day_container.find_all("tr")
            return [c.get_text() for c in courses][:3]
    
    
class Arstiderna(Restaurant):
    name = u"Årstiderna By The Sea"
    url = "http://arstidernabythesea.se/?cat=21"
    
    def fetch(self):
        soup = BeautifulSoup(urlopen(self.url), "html5lib")
        container = soup.find("div", id="content-border")
        menu_text = self.find_menu_text(container.text)
        return [menu_text.split("\n")[3],]
    

class WhiteShark(Restaurant):
    name = "White Shark"
    
    def fetch(self):
        soup = BeautifulSoup(urlopen("http://gastrogate.com/restaurang/whiteshark/page/3/"),
                             "html5lib", from_encoding="UTF-8")
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
    return [r(cache) for r in (Stereo, DOCItaliano, P2, Arstiderna, WhiteShark)]

