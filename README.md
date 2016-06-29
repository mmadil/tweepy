# tweepy

tweepy is a simple twitter clone made on [flask - a python micro framework](flask.pocoo.org).

### Stack

- Python
- Flask
- postgres

## Installation

Process of installation is easy. This project uses pip-tools to effectively keep track of requirements.

- make a virtual environment

        virtualenv venv

- activate the virtual environment

        source venv/bin/activate

- install pip-tools

        pip install pip-tools

- be in sync with the requirements using pip-sync

        pip-sync requrements.txt


## Features and Requirements
- [x] User can register/signin/signout
- [x] User can post tweets
- [ ] Add simple user profile page
- [ ] Implement follow user and filter query
- [ ] Add more tests and refactor

## License

MIT License

Copyright (c) 2016 Mohammad Adil

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
