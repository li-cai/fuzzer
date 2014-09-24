import sys
import requests
import bs4
from urllib.parse import urlparse

extensions = ['.html', '.jsp', '.php', '.asp', '.htm', '.css', '.js', \
              '.xhtml', '.dll']

def discover(url, words, query):
    print("======================= fuzz round 1 - discover! =======================")

    response = requests.get(url)

    scrapeLinks(response)
    guessLinks(url, words)
    scrapeInput(response)
    parseInput(query)
    scrapeCookies(response)


def authenticate(url):
    print(requests.get(url, auth=requests.auth.HTTPBasicAuth('admin', 'password')));


def scrapeLinks(response):
    soup = bs4.BeautifulSoup(response.text)
    anchors = soup.find_all('a')

    print("")
    print("=================== Links Discovered ===================")

    for anchor in anchors:
        if anchor.has_attr('href') and anchor['href']:
            print(anchor['href'])


def guessLinks(url, words):
    print("")
    print("=================== Guessing Links... ===================")

    count = 0

    for word in words:
        newURL = url + '/' + word
        response = requests.get(newURL)
        if (response.status_code == 200):
            print(newURL)
            count += 1

        for ext in extensions:
            newURL = url + '/' + word + ext
            response = requests.get(newURL)
            if (response.status_code == 200):
                print(newURL)
                count += 1

    print("========== Link Guessing Complete: " + str(count) + " Links Guessed ==========")


def scrapeInput(response):
    soup = bs4.BeautifulSoup(response.text)
    anchors = soup.find_all('input')

    print("")
    print("=================== Inputs Discovered ===================")

    for anchor in anchors:
        if anchor.has_attr('name'):
            print(anchor['name'])


def parseInput(query):
    print("")
    print("============== Parsing Input from URL... ==============")

    query = query.split('&')

    for elem in query:
        qvalues = elem.split('=')
        if len(qvalues) > 1:
            print("Input: " + qvalues[0] + ", Value: " + qvalues[1])


def scrapeCookies(response):
    # Get cookies
    cookies = response.cookies

    # Make a session
    session = requests.session()

    print("")
    print("================== Cookies Discovered =====================")
    for cookie in requests.utils.dict_from_cookiejar(cookies):
        print(cookie + " : " + requests.utils.dict_from_cookiejar(cookies)[cookie])


# TBD - Round 2
def test(args):
    print("============ fuzz round 2 - test! ============")


def printErrorMessage():
    print("Please enter a command in the following format:")
    print("python fuzz.py [discover | test] url OPTIONS")   


def main():
    args = sys.argv

    if len(args) < 4:
        printErrorMessage()
        return

    parsed = urlparse(args[2])
    url = parsed.scheme + '://' + parsed.netloc + parsed.path

    for i in range(3, len(args)):
        if (args[i].find("--common-words") > -1):
            filepath = args[i].split("=", 1)[1]

            try:
                textfile = open(filepath, 'r')

                words = textfile.read().split('\n')

                if args[1] == "discover":
                    discover(url, words, parsed.query)
                elif args[1] == "test":
                    test(args)

            except FileNotFoundError:
                print(filepath + " was not found.")

        elif (args[i].find("--custom-auth") > -1):
            authenticate(url)

main()
