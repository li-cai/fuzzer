Fuzzer
======

A testing tool for discovering vulnerabilities in web-based systems.

Dependencies
------------

[Python 3.X](https://www.python.org/downloads/release/python-341/)  
[Requests](https://github.com/kennethreitz/requests)  
[BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/bs4/download/4.3/)  

Setup for Windows
-----------------
* Make sure you have a version Python3 installed on your machine. If not,
visit the Python 3.X link under Dependencies to download the msi for
installation.  

* Download the Requests library by visiting the Requests from the link under
Dependencies. On your machine, navigate to the requests folder in the command
line and run this command:  
`python setup.py install`  

* Download the BeautifulSoup library from BeautifulSoup link under Dependencies.
On your machine, navigate to the bs4 folder in the command line and run this
command:  
`python setup.py install`  

Usage
-----
To run the fuzzer from the command line, enter the following command:  
`python fuzz.py [discover | test] url OPTIONS`    

### Commands
* `discover` - Output a list of all discovered input to the system.
* `test` - Discover all inputs, then attempt a list of exploit vectors
on those inputs to report potential vulnerabilities.

### Discover Options
* `--common-words=file` - Newline delimited file of common words to be used in
page and input guessing. (Required)
* `--custom-auth=string` - Signals that the fuzzer should use hard-coded
authentication for a specific application. *dvwa* and *bodgeit* are
currently supported. (Optional)

### Test Options
* `--vectors=file` - Newline delimited file of common exploits to
vulnerabilities. (Required)
* `--sensitive=file` - Newline delimited file of data that should
never be leaked. (Required)
* `--slow=500` - Number of milliseconds for a response to be
considered "slow". Default is 500 milliseconds. (Optional)
* `--random=[true|false]` - When false, input to each page is tried
systematically. When true, a random page and random input field
are chosen to test all vectors. Default is false. (Optional)