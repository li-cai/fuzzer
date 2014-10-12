import sys
import requests
import bs4
from urllib.parse import urlparse

extensions = ['.html', '.jsp', '.php', '.asp', '.htm', '.css', '.js', \
              '.xhtml', '.dll']



def discover(url, words, query, response):
    """
    Starts the discover process of fuzzing.
    """
    print("")
    print("================ FUZZ ROUND 1 - DISCOVER! ================")

    scrapeLinks(response)
    guessLinks(url, words)
    scrapeInput(response)
    parseInput(query)
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


def scrapeLinks(response):
    """
    Parses the HTML to find all links.
    """
    soup = bs4.BeautifulSoup(response.text)
    anchors = soup.find_all('a')

    print("")
    print("================== Discovering Links... ==================")

    count = 0;
    for anchor in anchors:
        if anchor.has_attr('href') and anchor['href'] != '':
            print(anchor['href'])
            count += 1;

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
            print(currURL)

        for ext in extensions:
            currURL = newURL + word + ext

            response = requests.get(currURL)
            if (response.status_code == 200):
                count += 1
                print(currURL)

    print("==================== " + str(count) + " Links Guessed ====================")


def scrapeInput(response):
    """
    Parses the HTML to find all input values and types.
    """
    soup = bs4.BeautifulSoup(response.text)

    print();
    print("================= Discovering Input... ==================") 
    
    count = 0

    anchors = soup.find_all('input', {'type':'text'})
    for anchor in anchors:
        value = anchor.get('name')
        count += 1
        if value:
            print(value + " : Textbox")

    anchors = soup.find_all('input', {'type':'submit'})
    for anchor in anchors:
        value = anchor.get('name')
        count += 1
        if value:
            print(value + " : Button")
        else:
            print('Button input has no name')

    anchors = soup.find_all('input', {'type':'radio'})
    for anchor in anchors:
        value = anchor.get('name')
        count += 1
        if value:
            print(value + " : Radio Button")
        else:
            print('Radio Button input has no name')

    anchors = soup.find_all('input', {'type':'password'})
    for anchor in anchors:
        value = anchor.get('name')
        count += 1
        if value:
            print(value + " : Password")
        else:
            print('Password input has no name')

    anchors = soup.find_all('input', {'type':'checkbox'})
    for anchor in anchors:
        count += 1
        value = anchor.get('name')
        if value:
            print(value + " : Checkbox")
        else:
            print('Checkbox input has no name')

    anchors = soup.find_all('input', {'type':'hidden'})
    for anchor in anchors:
        count += 1
        value = anchor.get('name')
        if value:
            print(value + " : Hidden Input")
        else:
            print('Hidden input has no name')

    print("================== " + str(count) + " Inputs Discovered ==================")

def parseInput(query):
    """
    Parses input from the given URL.
    """
    print("")
    print("=============== Parsing Input from URL... ===============")

    query = query.split('&')

    count = 0
    for elem in query:
        qvalues = elem.split('=')
        if len(qvalues) > 1:
            count += 1
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

    print("")
    print("=============== Discovering Cookies... ==================")

    count = 0
    for cookie in requests.utils.dict_from_cookiejar(cookies):
        count += 1
        print(cookie + " : " + requests.utils.dict_from_cookiejar(cookies)[cookie])

    print("================= " + str(count) + " Cookies Discovered ==================")


# TBD - Round 2
def test(url, response, vectors, sensitive, slow, random):
    print("================ FUZZ ROUND 2 - TEST! ================")
    # for vector in vectors:
    #     print(vector)

def checkSanitizedInput(vectors):
    pass

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
        discover(url, words, parsed.query, response)
    elif args[1] == "test":
        if len(args) < 5 or vectors == None or sensitive == None:
            printTestErrorMessage()
            return
        test(url, response, vectors, sensitive, slow, random)
    else:
        printErrorMessage()

main()
