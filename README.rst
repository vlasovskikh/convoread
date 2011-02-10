===========
 convoread
===========

Simple console reader for `Convore`_.

.. _Convore: https://convore.com/


Description
-----------

``convoread`` supports streaming live messages to the standard output.

Future versions will include posting messages, creating topics, and managing
groups.

See `discussion`_ on Convore for ``convoread`` announcements, support, etc.

.. _discussion: https://convore.com/feedback/convoread-simple-console-client-for-convore/


Usage
-----

You can watch your live stream indefinitely::

    $ convoread
    13:06 @user1: hello
    13:21 @user2: convoread works
    13:22 @user1: @user2 indeed!
    ^Cinterrupted

Press ``Ctrl+C`` to exit.

You can also enable desktop notifications for Ubuntu and similar OSes that
support ``libnotify``::

    $ convoread --notify

For more info on usage type::

    $ convoread --help


Installation
------------

You can install it from PyPI::

    $ pip install convoread # add -U if you're updating it

Or you can clone it from GitHub and then use ``develop`` command to get it
symlinked to your $PATH::

    $ git clone https://github.com/foobarbuzz/convoread.git
    $ cd convoread
    $ ./setup.py develop

Or just run it directly from repository::

    $ python convoread/__init__.py


Requirements
~~~~~~~~~~~~

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
