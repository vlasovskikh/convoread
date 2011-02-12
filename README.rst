===========
 convoread
===========

Simple console reader for `Convore`_.

Latest version: 0.4, 2011-02-12.

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

Run the program::

    $ convoread
    welcome to convoread! type /help for more info
    >

You are now in ``convoread`` shell. You can just watch your live stream
indefinitely::

    [13:06] mygroup/1234 <user1>
        hello
    [13:21] mygroup/1234 <user2>
        convoread works
    [13:22] mygroup/1234 <user1>
        @user2 indeed!

You can also list recent topics and send messages::

    > /t
       4393   pyquery - a jquery-like library for python
       4383   Fate of PySide
       3012   Configuring Vim for Python
       3716   Multiprocessing & Socket Duplication
       2412   Extensions I just can live without
    > /t 3012
    > hello vim community!
    [13:24] vim/3012 <user1>
        hello vim community!
    [13:25] vim/3012 <user3>
        welcome

Press ``/q`` to exit::

    > /q
    quit

You can also enable desktop notifications for Ubuntu and similar systems that
support ``libnotify``::

    $ convoread --notify

For more info on usage type::

    $ convoread --help


Installation
------------

You can install (or update) it from PyPI::

    $ pip install -U convoread

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

* Python >= 2.6 (Python 3 has some issues yet)

Optional:

* pynotify (on some systems: python-notify) for desktop notifications
* PIL (Python Imaging Library) for avatars in notifications


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
* `Mikhail Krivushin`_
* Timofei Perevezentsev

.. _Andrey Vlasovskikh: http://pirx.ru/
.. _Alexander Solovyov: http://piranha.org.ua/
.. _Mikhail Krivushin: http://deepwalker.blogspot.com/


License
-------

MIT License.
