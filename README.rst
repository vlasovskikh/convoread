===========
 convoread
===========

Simple console reader for `Convore`_.

.. _Convore: https://convore.com/


Description
-----------

``convoread`` streams live Convore messages to the standard output or shows
desktop notifications (only for Ubuntu and similar systems at this moment).

Future versions will include posting messages, creating topics, and managing
groups.

See `discussion`_ on Convore for ``convoread`` announcements, support, etc.

.. _discussion: https://convore.com/feedback/convoread-simple-console-client-for-convore/


Usage
-----

You can watch your live stream indefinitely::

    $ convoread
    13:06 !mygroup @user1: hello
    13:21 !mygroup @user2: convoread works
    13:22 !mygroup @user1: @user2 indeed!
    ^Cinterrupted

Press ``Ctrl+C`` to exit.

You can also enable desktop notifications for Ubuntu and similar systems that
support ``libnotify``::

    $ convoread --notify

For more info on usage type::

    $ convoread --help


Installation
------------

You can install it from PyPI::

    $ pip install convoread

Use ``-U`` option to upgrade to the latest version.

Or you can clone it from GitHub and then use ``develop`` command to get it
symlinked to your system-wide ``$PATH``::

    $ git clone https://github.com/foobarbuzz/convoread.git
    $ cd convoread
    $ python setup.py develop

Or symlink it to your home directory only::

    $ python setup.py develop --user

Check that ``~/.local/bin`` is in your ``$PATH``.


Requirements
~~~~~~~~~~~~

* Python ≥ 2.6 (Python 3 has some issues yet)

Optional requirements:

* pynotify (on some systems: python-notify) for desktop notifications


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
