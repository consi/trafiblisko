trafiblisko.py - a Traficar reservation bot
===========================================

This script is doing permanent reservation of Traficar Car nearest to given coords
Do not use this on your traficar account as it *may be locked because of abuse*

Why I'm doing this?
-------------------
Because someone did this too (and agreement doesn't forbid it)! In effect: I'm standing in the rain 
in face of permanently reserved Traficar - traficar guys, please investigate options to stop this problem!

Installation
------------
```virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt```

Usage
-----
```$ ./trafiblisko.py --help
Usage: trafiblisko.py [OPTIONS]

  Simple script that locks traficar nearest to you ;)

Options:
  --login TEXT                 Your traficar login (email)
  --password TEXT              Your traficar password
  --lat FLOAT                  Your latitude
  --lon FLOAT                  Your longitude
  --recheck FLOAT              How often check (in seconds) if there's a car
                               in neighboorhod or better one than reserved
                               (default is 20 sec)
  --reservation-recheck FLOAT  How often check for reservation (default is
                               15min 03s)
  --help                       Show this message and exit.```

License
-------
The MIT License (MIT)

Copyright (c) 2013 Thomas Park

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Contact
-------
Marek Wajdzik <wajdzik.m@gmail.com>