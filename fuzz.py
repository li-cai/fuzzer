import sys
import requests
import bs4
import random
from urllib.parse import urlparse

extensions = ['.html', '.jsp', '.php', '.asp', '.htm', '.css', '.js', '.dll']

pageurlparam = {}
pageforminput = {}

pages = []

def discover(url, netloc, words, query, response):
    """
    Starts the discover process of fuzzing.
    """
    print("")
    print("================ FUZZ ROUND 1 - DISCOVER! ================")

    pageurlparam[url] = []
    pageforminput[url] = []
    pages.append(url)

    print("\n================== Discovering Links... ==================")
    count = scrapeLinks(response, url, True)
    print("================== " + str(count) + " Links Discovered ==================")

    print("\n=================== Guessing Links... ===================")
    count = guessLinks(url, words, True)
    print("==================== " + str(count) + " Links Guessed ====================")

    print("\n================= Discovering Input... ==================") 
    count = scrapeInput(response, url, True)
    print("================== " + str(count) + " Inputs Discovered ==================")

    print("\n=============== Parsing Input from URL... ===============")
    count = parseInput(query, url, True)
    print("==================== " + str(count) + " Inputs Parsed ====================")

    print("\n=============== Discovering Cookies... ==================")
    count = scrapeCookies(response)
    print("================= " + str(count) + " Cookies Discovered ==================")


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

        with requests.Session() as session:
            session.post(netloc +'/dvwa/login.php', data = payload)
            # r = s.get(url, allow_redirects=False)
            return session

    elif appname == 'bodgeit':
        payload = {
            'username': 'dankrutz@rit.edu',
            'password1': 'password',
            'password2': 'password',
            'submit': 'submit'
        }

        with requests.Session() as session:
            session.post(netloc + '/register.jsp', data=payload)
            # r = s.get(url, allow_redirects=False)
            return session


def scrapeLinks(response, url, toprint):
    """
    Parses the HTML to find all links.
    """
    soup = bs4.BeautifulSoup(response.text)
    anchors = soup.find_all('a')

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
                pages.append(link)
                addLinkToDict(link, pageurlparam, pageforminput)

            if toprint:
                print(link)

            count += 1
    return count

def guessLinks(url, words, toprint):
    """
    Attempts to guess valid links using the given list of common words.
    """
    count = 0

    newURL = url
    if not url.endswith('/'):
        newURL = url + '/'

    for word in words:
        currURL = newURL + word

        response = requests.get(currURL)
        if (response.status_code == 200):
            count += 1
            pages.append(currURL)
            addLinkToDict(currURL, pageurlparam, pageforminput)
            if toprint:
                print(currURL)

        for ext in extensions:
            currURL = newURL + word + ext
            response = requests.get(currURL)
            if (response.status_code == 200):
                count += 1
                pages.append(currURL)
                addLinkToDict(currURL, pageurlparam, pageforminput)
                if toprint:
                    print(currURL)
    return count


def addLinkToDict(link, dict1, dict2):
    if link not in dict1:
        pageforminput[link] = []
    if link not in dict2:
        pageurlparam[link] = []


def scrapeInput(response, url, toprint):
    """
    Parses the HTML to find all input values and types.
    """
    soup = bs4.BeautifulSoup(response.text)
    
    count = 0

    inputs = soup.find_all('input')

    for inpt in inputs:
        value = inpt.get('name')
        input_type = inpt.get('type')

        if toprint:
            if value:
                print(value + " : " + str(input_type))
            else:
                print("input has no name : " + input_type)

        if url in pageforminput:
            pageforminput[url].append(value)

        count += 1
    return count


def parseInput(query, url, toprint):
    """
    Parses input from the given URL.
    """
    query = query.split('&')

    count = 0
    for elem in query:
        qvalues = elem.split('=')
        if len(qvalues) > 1:
            count += 1
            if url in pageurlparam:
                pageurlparam[url].append(qvalues[0])

            if toprint:
                print("Input: " + qvalues[0] + ", Value: " + qvalues[1])
        else:
            pageurlparam[url] = []

    return count


def scrapeCookies(response):
    """
    Discovers cookies for the given url
    """
    # Get cookies
    cookies = response.cookies

    # Make a session
    session = requests.session()

    count = 0
    for cookie in requests.utils.dict_from_cookiejar(cookies):
        count += 1
        print(cookie + " : " + requests.utils.dict_from_cookiejar(cookies)[cookie])
    return count


def test(session, url, words, vectors, sensitive, slow, isRandom):
    print("\n\n======================== FUZZ ROUND 2 - TEST! ========================")

    count = 0
    if not isRandom:
        for urlkey in pages:

            parsed = urlparse(urlkey)
            response = session.get(urlkey, allow_redirects=False)

            scrapeInput(response, urlkey, False)
            parseInput(parsed.query, urlkey, False)

            vulnerabilities = sendVectors(session, urlkey, vectors, sensitive, slow)

            if len(vulnerabilities) > 0:
                count += len(vulnerabilities)

                print("\n\n----------------------------------------------------------------------")
                print(urlkey)
                print("form inputs = " + str(pageforminput[urlkey]))
                print("----------------------------------------------------------------------")
                for vulnerability in vulnerabilities:
                    print(vulnerability)
    else:
        randompage = random.choice(list(pageforminput.keys()))
        vulnerabilities = sendVectors(session, randompage, vectors, sensitive, slow)
        count += len(vulnerabilities)

        print("\n\n----------------------------------------------------------------------")
        print(randompage)
        print("----------------------------------------------------------------------")
        for vulnerability in vulnerabilities:
            print(vulnerability)

    print("\n\n============ " + str(count) + " Potential Vulnerabilities Discovered ============")


def sendVectors(session, url, vectors, sensitive, slow):
    inputs = []
    params = []

    if url in pageforminput:
        inputs = pageforminput[url]
    if url in pageurlparam:
        params = pageurlparam[url]

    vulnerabilities = []

    payload = {}
    for ipt in inputs:
        if ipt not in payload:
            payload[ipt] = ''

    getpayload = {}
    for param in params:
        if param not in getpayload:
            getpayload[param] = ''

    for vector in vectors:
        for key in payload:
            payload[key] = vector

        postresponse = session.post(url, data=payload)

        if vector in postresponse.text:
            vulnerabilities.append("Unsanitized vector discovered: " + vector)

        sensitiveFound = checkSensitiveData(postresponse, sensitive, vector)

        vulnerabilities.extend(sensitiveFound)

        if slowResponse(postresponse, slow):
            vulnerabilities.append("Delayed Reponse time detected: over " + str(slow) + \
                                   " milliseconds with vector " + vector)

        if badHTTPCode(postresponse):
            vulnerabilities.append("Bad HTTP Response Code : " + str(postresponse.status_code) + \
                                   " with vector " + vector)

        for key in getpayload:
            getpayload[key] = vector

        if len(getpayload) > 0:
            getresponse = requests.get(url, params=getpayload)
            if vector in getresponse.text:
                vulnerabilities.append(vector + " : unsanitized")

        if len(payload) == 0:
            break;

    return vulnerabilities


def checkSensitiveData(response, sensitive, vector):
    sensitiveData = []
    sensitiveTrack = []
    for word in sensitive:
        if word in response.text and word not in sensitiveTrack:
            sensitiveData.append("Sensitive data discovered: " + word + \
                                 " with vector " + vector)

    return sensitiveData
          

def slowResponse(response, slow):
    """
    Discovers if the response message is being recieved to slow signaling
    a possible DOS attack.
    Returns true if the response was slower than our slow limit, and false
    if the response was fast enough.
    """
    respTime = response.elapsed.total_seconds()
    if (slow/1000 < respTime):
        return True
    return False


def badHTTPCode(response):
    """
    Checks the response status code to ensure everything is okay
    Returns true if there is a problem and false if the response was okay
    """
    if (response.status_code != requests.codes.ok):
        return True
    return False


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

    authSession = requests.Session()
    print(authSession)

    if "--custom-auth=bodgeit" in args:
        authSession = authenticate(url, netloc, "bodgeit")
        temp = authSession.get(url, allow_redirects=False)
        if temp.status_code == 200:
            response = temp
    elif "--custom-auth=dvwa" in args:
        authSession = authenticate(url, netloc, "dvwa")
        temp = authSession.get(url, allow_redirects=False)
        if temp.status_code == 200:
            response = temp

    print(authSession)

    slow = 500
    random = False
    words = []
    vectors = []
    sensitive = []

    for i in range(3, len(args)):
        if args[i].find("--common-words") > -1:
            words = loadFile(args[i])

        if args[i].find("--slow") > -1:
            slow = int(args[i].split("=", 1)[1])

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
        test(authSession, url, words, vectors, sensitive, slow, random)
    else:
        printErrorMessage()

main()
