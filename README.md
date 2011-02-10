convoread
=========

Simple console reader for [Convore][].


Description
-----------

`convoread` supports streaming live messages to the standard output.

Future versions will include posting messages, creating topics, and managing
groups.


Usage
-----

You can watch your live stream indefinitely:

    $ python convoread.py
    @user1: hello
    @user2: convoread works
    @user1: @user2 indeed!
    ^Cinterrupted

Press `Ctrl+C` to exit.

For more info on usage type:

    $ python convoread.py --help


Requirements
------------

* Python ≥ 2.6 (Python 3 has some issues yet)


Configuration
-------------

`convoread` uses login and password, supplied in `~/.netrc` file in a standard
format. If you're wondering, what is the format of `.netrc`:

    machine convore.com
        login <your-username>
        password <your-password>


Authors
-------

* [Andrey Vlasovskikh][vlasovskikh]
* [Alexander Solovyov][asolovyov]
* Mikhail Krivushin
* Timofei Perevezentsev


License
-------

MIT License.


  [convore]: https://convore.com/
  [vlasovskikh]: http://pirx.ru/
  [asolovyov]: http://piranha.org.ua/

