===========
 convoread
===========

Simple console reader for `Convore`_.


Description
-----------

``convoread`` supports streaming live messages to the standard output.

Future versions will include posting messages, creating topics, and managing
groups.

.. _Convore: https://convore.com/


Usage
-----

You can watch your live stream indefinitely::

    $ python convoread.py
    13:06 @user1: hello
    13:21 @user2: convoread works
    13:22 @user1: @user2 indeed!
    ^Cinterrupted

Press ``Ctrl+C`` to exit.

For more info on usage type::

    $ python convoread.py --help


Requirements
------------

* Python ≥ 2.6 (Python 3 has some issues yet)


Configuration
-------------

``convoread`` uses login and password, supplied in ``~/.netrc`` file in a standard
format. If you're wondering, what is the format of ``.netrc``::

    machine convore.com
        login <your-username>
        password <your-password>


Authors
-------

* `Andrey Vlasovskikh`_
* `Alexander Solovyov`_
* Mikhail Krivushin
* Timofei Perevezentsev

.. _Andrey Vlasovskikh: http://pirx.ru/
.. _Alexander Solovyov: http://piranha.org.ua/


License
-------

MIT License.
