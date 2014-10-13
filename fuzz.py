import sys
import requests
import bs4
from urllib.parse import urlparse

extensions = ['.html', '.jsp', '.php', '.asp', '.htm', '.css', '.js', '.dll']

pageurlparam = {}
pageforminput = {}

pages = []
urlinput = []
forminput = []

def discover(url, netloc, words, query, response):
    """
    Starts the discover process of fuzzing.
    """
    print("")
    print("================ FUZZ ROUND 1 - DISCOVER! ================")

    pageurlparam[url] = []
    pageforminput[url] = []

    scrapeLinks(response, url)
    guessLinks(url, words)
    scrapeInput(response, url)
    parseInput(query, url)
    scrapeCookies(response)

def authenticate(url, netloc, appname):
    """
    Hard-coded authentication for DVWA or BodgeIt. 
    """
    if appname == 'dvwa':
        payload = {
            'username': 'admin',
            'password': 'password',
            'Login':'Login'
        }

        with requests.Session() as s:
            s.post(netloc +'/login.php', data = payload)
            r = s.get(url, allow_redirects=False)
            return r

    elif appname == 'bodgeit':
        payload = {
            'username': 'dankrutz@rit.edu',
            'password1': 'password',
            'password2': 'password',
            'submit': 'submit'
        }

        with requests.Session() as s:
            s.post(netloc + '/register.jsp', data=payload)
            r = s.get(url, allow_redirects=False)
            return r


def scrapeLinks(response, url):
    """
    Parses the HTML to find all links.
    """
    soup = bs4.BeautifulSoup(response.text)
    anchors = soup.find_all('a')

    print("")
    print("================== Discovering Links... ==================")

    newURL = url
    if not url.endswith('/'):
        newURL = url + '/'

    count = 0
    for anchor in anchors:
        if anchor.has_attr('href') and anchor['href'] != '':
            link = anchor['href']

            if link.startswith('//'):
                link = 'http:' + link
            elif link.find('http://') < 0 and link.find('https://') < 0:
                link = newURL + link
                # pages.append(link)
                addLinkToDict(link, pageurlparam, pageforminput)

            print(link)
            count += 1

    print("================== " + str(count) + " Links Discovered ==================")


def guessLinks(url, words):
    """
    Attempts to guess valid links using the given list of common words.
    """
    print("")
    print("=================== Guessing Links... ===================")

    count = 0

    newURL = url
    if not url.endswith('/'):
        newURL = url + '/'

    for word in words:
        currURL = newURL + word

        response = requests.get(currURL)
        if (response.status_code == 200):
            count += 1
            # pages.append(currURL)
            addLinkToDict(currURL, pageurlparam, pageforminput)
            print(currURL)

        for ext in extensions:
            currURL = newURL + word + ext


            response = requests.get(currURL)
            if (response.status_code == 200):
                count += 1
                # pages.append(currURL)
                addLinkToDict(currURL, pageurlparam, pageforminput)
                print(currURL)

    print("==================== " + str(count) + " Links Guessed ====================")


def addLinkToDict(link, dict1, dict2):
    if link not in dict1:
        pageforminput[link] = []
    if link not in dict2:
        pageurlparam[link] = []


def scrapeInput(response, url):
    """
    Parses the HTML to find all input values and types.
    """
    soup = bs4.BeautifulSoup(response.text)

    print("\n================= Discovering Input... ==================") 
    
    count = 0

    inputs = soup.find_all('input')

    for inpt in inputs:
        value = inpt.get('name')
        input_type = inpt.get('type')

        if value:
            print(value + " : " + str(input_type))
        else:
            print("input has no name : " + input_type)

        # forminputs.append(value)
        if url in pageforminput:
            pageforminput[url].append(value)

        count += 1

    print("================== " + str(count) + " Inputs Discovered ==================")

def parseInput(query, url):
    """
    Parses input from the given URL.
    """
    print("\n=============== Parsing Input from URL... ===============")

    query = query.split('&')

    count = 0
    for elem in query:
        qvalues = elem.split('=')
        if len(qvalues) > 1:
            count += 1
            # urlinput.append(qvalues[0])
            if url in pageurlparam:
                pageurlparam[url].append(qvalues[0])

            print("Input: " + qvalues[0] + ", Value: " + qvalues[1])

    print("==================== " + str(count) + " Inputs Parsed ====================")

def scrapeCookies(response):
    """
    Discovers cookies for the given url"
    """
    # Get cookies
    cookies = response.cookies

    # Make a session
    session = requests.session()

    print("\n=============== Discovering Cookies... ==================")

    count = 0
    for cookie in requests.utils.dict_from_cookiejar(cookies):
        count += 1
        print(cookie + " : " + requests.utils.dict_from_cookiejar(cookies)[cookie])

    print("================= " + str(count) + " Cookies Discovered ==================")


def test(url, response, vectors, sensitive, slow, random):
    # print("")
    print("\n================= FUZZ ROUND 2 - TEST! ==================")

    checkSanitizedInput(url, vectors)
    # print(pageurlparam[url])


def checkSanitizedInput(url, vectors):
    print("\n============ Checking Input Sanitization... =============")

    inputs = pageforminput[url]
    unsanitized = []

    payload = {}
    for ipt in inputs:
        if ipt not in payload:
            payload[ipt] = ''

    for vector in vectors:
        for key in payload:
            payload[key] = vector

        with requests.Session() as s:
            r = s.post(url, data=payload)
            if vector in r.text and vector not in unsanitized:
                unsanitized.append(vector)

    for exploit in unsanitized:
        print(exploit + " - unsanitized on " + url)

    print("============ " + str(len(unsanitized)) + " Unsanitized Inputs Discovered ============")

def checkSensitiveData(sensitive):
    pass


def slowResponse(response, slow):
    """
    Discovers if the response message is being recieved to slow signaling
    a possible DOS attack.
    Returns true if the response was slower than our slow limit, and false
    if the response was fast enough.
    """
    respTime = response.elapsed.total_seconds()
    if (slow/1000 < respTime):
        return true
    return false


def badHTTPCode(response):
    """
    Checks the response status code to ensure everything is okay
    Returns true if there is a problem and false if the response was okay
    """
    if (response.status_code != requests.codes.ok):
        return true
    return false


def printErrorMessage():
    print("Please enter a command in the following format:")
    print("python fuzz.py [discover | test] url OPTIONS")   

def printDiscoverErrorMessage():
    print("Please enter a command to discover in the following format:")
    print("python fuzz.py discover url --common-words=file OPTIONS") 

def printTestErrorMessage():
    print("Please enter a command to discover in the following format:")
    print("python fuzz.py test url --vectors=file --sensitive=file OPTIONS") 


def loadFile(arg):
    filepath = arg.split("=", 1)[1]

    try:
        textfile = open(filepath, 'r')
        valueslist = textfile.read().split('\n')
        return valueslist
    except FileNotFoundError:
        print(filepath + " was not found.")
        return None

def main():
    args = sys.argv

    if len(args) < 4:
        printErrorMessage()
        return

    parsed = urlparse(args[2])
    url = parsed.scheme + '://' + parsed.netloc + parsed.path
    netloc = parsed.scheme + '://' + parsed.netloc

    try:
        response = requests.get(url)
    except:
        print("Please enter a valid URL starting with 'http://'")
        return

    if "--custom-auth=bodgeit" in args:
        temp = authenticate(url, netloc, "bodgeit")
        if temp.status_code == 200:
            response = temp
    elif "--custom-auth=dvwa" in args:
        temp = authenticate(url, netloc, "dvwa")
        if temp.status_code == 200:
            response = temp

    slow = 500
    random = False
    words = []
    vectors = []
    sensitive = []

    for i in range(3, len(args)):
        if args[i].find("--common-words") > -1:
            words = loadFile(args[i])

        if args[i].find("--common-words") > -1:
            slow = args[i].split("=", 1)[1]

        if args[i].find("--vectors") > -1:
             vectors = loadFile(args[i])

        if args[i].find("--sensitive") > -1:
            sensitive = loadFile(args[i])

        if args[i].find("--random") > -1:
            randomstr = args[i].split("=", 1)[1]
            if randomstr == "true":
                random = True
            elif randomstr == "false":
                random = False

    if args[1] == "discover":
        if len(args) < 4 or words == None:
            printDiscoverErrorMessage()
            return
        discover(url, netloc, words, parsed.query, response)
    elif args[1] == "test":
        if len(args) < 5 or vectors == None or sensitive == None:
            printTestErrorMessage()
            return
        discover(url, netloc, words, parsed.query, response)            
        test(url, response, vectors, sensitive, slow, random)
    else:
        printErrorMessage()

main()
