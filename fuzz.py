import sys
import requests
import bs4


def discover(url, words):
    print("fuzz round 1 - discover!")

    response = requests.get(url);

    scrapeLinks(response);

# Rafa
def authenticate(response):
    pass

#Cailin
def scrapeLinks(response):
    soup = bs4.BeautifulSoup(response.text);
    anchors = soup.find_all('a');

    for anchor in anchors:
        if anchor['href']:
            print(anchor['href']);

# Cailin
def guessLinks(response):
    pass

# Karen
def scrapeInput(response):
    pass

# Cailin
def guessInput(response):
    pass

# Karen 
def scrapeCookies(response):
    # Get cookies
    cookies = response.cookies

# TBD - Round 2
def test(args):
    print("fuzz round 2 - test!")


def printErrorMessage():
    print("Please enter a command in the following format:")
    print("python fuzz.py [discover | test] url OPTIONS")   


def main():
    args = sys.argv

    if len(args) < 4:
        printErrorMessage();
    elif args[3].find("--common-words") < 0:
        printErrorMessage();
    else:
        filepath = args[3].split("=", 1)[1]

        try:
            textfile = open(filepath, 'r')

            words = textfile.read().split('\n')

            if args[1] == "discover":
                discover(args[2], words);
            elif args[1] == "test":
                test(args);

            print(words)
        except FileNotFoundError:
            print(filepath + " was not found.")

main();