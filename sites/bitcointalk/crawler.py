import urllib2
import time
import re
import os
from validateAddress import *
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint
from sets import Set

postUrlList = []
idSet = Set()
__delayTime = 0.2
__debug = 1

dataPrefix = "./data/"
currentUrl = ""
currentPage = ""

urlMap = {
"https://bitcointalk.org/index.php?board=5.":129,
"https://bitcointalk.org/index.php?board=53.":256,
"https://bitcointalk.org/index.php?board=56.":104,
"https://bitcointalk.org/index.php?board=52.":218
}

class MyHTMLMainPageParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.__tmpFlag = False
        
    def handle_starttag(self, tag, attrs):
        global postUrlList
        if tag == "span":
            if attrs[0][0] == "id":
                self.__tmpFlag = True
        if tag == "a":
            for attr in attrs:
                if self.__tmpFlag:
                    postUrlList.append(attr[1])
    def handle_endtag(self, tag):
        if tag == "span":
            self.__tmpFlag = False
        

class MyHTMLPostParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.__tmpFlag = False
        self.__currentUserStatus = False
        self.__currentUser = ""
        self.__currentUserUrl = ""
        
    def handle_starttag(self, tag, attrs):
        if tag == "div":
            if len(attrs) > 0:
                if attrs[0][0] == "class":
                    if attrs[0][1] == "post":
                        self.__tmpFlag = True
                    if attrs[0][1][:9] == "signature":
                        self.__tmpFlag = True
        
        if tag == "a":
            if len(attrs) == 2:
                if attrs[1][1].startswith("View the profile of"):
                    self.__currentUserUrl = attrs[0][1]
                    self.__currentUserStatus = True

    def handle_endtag(self, tag):
        if tag == "div":
            self.__tmpFlag = False
        if tag == "a":
            self.__currentUserStatus = False
            
    def handle_data(self, data):
        global currentUrlG, dataPrefix
        if self.__tmpFlag:
            p = re.compile('[13][a-km-zA-HJ-NP-Z0-9]{26,33}', re.DOTALL)
            result = p.findall(data)
            if len(result) > 0:
                if self.__currentUser+","+result[0] not in idSet:
                    if validate(result[0]) != False:
                        idSet.add(self.__currentUser + "," + result[0])
                        if not os.path.exists(dataPrefix + result[0]):
                            os.mkdir(dataPrefix + result[0])
                        f = open(dataPrefix + result[0] + "/" + self.__currentUser, 'w')
                        f.write(currentUrlG + "\n")
                        f.write(self.__currentUserUrl + "\n")
                        f.write(data + "\n")
                        f.write(currentPage + "\n")
                        f.close()
            
        if self.__currentUserStatus:
            self.__currentUser = data
            #print "User", data


def main():
    global postUrlList, currentUrlG, currentPage
    parserMain = MyHTMLMainPageParser()
    parserPost = MyHTMLPostParser()
    for currentUrl in urlMap:
        for i in range(urlMap[currentUrl]):
            url = currentUrl + str(i * 40)
            if __debug:
                print "currentModule", url
            try:
                content = urllib2.urlopen(url).read().decode("iso-8859-1").encode("utf8")
                time.sleep(__delayTime)
                parserMain.feed(content)
            except:
                print "Error in", url
                continue
            
            for pageUrl in postUrlList:
                if __debug:
                    print "currentPage", pageUrl
                parserPost = MyHTMLPostParser()
                currentUrlG = pageUrl + ";all"
                try:
                    content = urllib2.urlopen(pageUrl + ";all").read().decode("iso-8859-1").encode("utf8")
                    currentPage = content;
                    time.sleep(__delayTime)
                    parserPost.feed(content)
                except:
                    print "Error in", currentUrlG
                    continue
                        
            postUrlList = []


if not os.path.exists(dataPrefix):
    os.mkdir(dataPrefix)
main()

