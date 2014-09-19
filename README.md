fuzzer
======

A testing tool for discovering vulnerabilities in web-based systems.

Dependencies
---------

[Python 3.X](https://www.python.org/downloads/release/python-341/)  
[Requests](https://github.com/kennethreitz/requests)  
[BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/bs4/download/4.3/)  

Setup for Windows
-----------------
* Make sure you have a version Python3 installed on your machine. If not, visit the
Python 3.X link under Dependencies to download the msi for installation.  

* Download the Requests library from their Github page by visiting the Requests
link under Dependencies. On your machine, navigate to the requests folder in
the command line and run this command:  
`python setup.py install`  

* Download the BeautifulSoup library from their website by visiting the
BeautifulSoup link under Dependencies. On your machine, navigate to the bs4
folder in the command line and run this command:  
`python setup.py install`  

Usage
-----
To run the fuzzer from the command line, enter the following command:  
`python fuzz.py [discover | test] url OPTIONS`