PSClient
========

Unofficial Cisco Parstream Client with improved cli.

Still in Beta, tested with Parstream 4.4.x on ubuntu and windows 10.

Install it using ``pip``:

::

   $ pip install pscli

NOTE: python 3.5 or above required

You can use it from cli or use its client class (``PSClient``) in your python code.
There is also a class (``AIOPSClient``) that supports async paradigm. Use ``batch`` function to execute parallel statements.

The execution of a statement returns 2 value:

1. raw output string from parstream server
2. a dict that contains timing info: start time, first packet time and final time (useful for performance test)


Features
~~~~~~~~

1. commands history (file: ``$HOME/.psclient_history``)
2. autocomplete from history, sql syntax and cli commands
3. sql syntax highlight
4. cli commands
5. query output as table instead of csv
