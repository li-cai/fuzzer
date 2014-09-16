import requests;
import sys;

def printErrorMessage():
    print("Please enter a command in the following format:")
    print("python fuzz.py [discover | test] url OPTIONS")    

def discover(url):
    print("fuzz round 1 - discover!")
    print(url);

def test():
    print("fuzz round 2 - test!")

def main():
    args = sys.argv

    if (len(args) < 3):
        printErrorMessage();

    if args[1] == "discover":
        discover(args[2]);

main();