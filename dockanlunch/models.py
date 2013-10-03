import abc
from urllib2 import urlopen
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
    

def get_all(cache):
    return (Stereo(cache), DOCItaliano(cache))
