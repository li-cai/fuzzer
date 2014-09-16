import sys
import requests
import bs4

def printErrorMessage():
    print("Please enter a command in the following format:")
    print("python fuzz.py [discover | test] url OPTIONS")    

def discover(args):
    print("fuzz round 1 - discover!")

    url = args[2];
    response = requests.get(url);

    scrapeLinks(response);

def scrapeLinks(response):
    soup = bs4.BeautifulSoup(response.text);
    anchors = soup.find_all('a');

    for anchor in anchors:
        if anchor['href']:
            print(anchor['href']);

def test(args):
    print("fuzz round 2 - test!")

def main():
    args = sys.argv

    if (len(args) < 3):
        printErrorMessage();

    if args[1] == "discover":
        discover(args);
    elif args[1] == "test":
        test(args);

main();