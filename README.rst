===========
 convoread
===========

Command-line tool for `Convore`_.

Latest version: 0.5, 2011-02-18.

.. _Convore: https://convore.com/


Description
-----------

``convoread`` is a tool for sending and receiving Convore messages from the
command line.

Some of it's features include:

- Interactive console chat interface
- Desktop notifications [*]_
- Convenient topic switching
- Unread topics by group
- Recent topics and messages

.. [*] At this moment desktop notifications work only for Ubuntu and similar
       systems with ``libnotify`` installed.

Future versions of ``convoread`` will allow creating topics, managing
notifications, etc.

See a `discussion`_ on Convore for ``convoread`` announcements and support.

.. _discussion: https://convore.com/feedback/convoread-simple-console-client-for-convore/


What's New in 0.5
-----------------

- More readable chat logs with topic change messages
- Command ``/ts`` displays topics by group, including unread messages count
- Command ``/t`` selects a topic *and* lists recent messages
- Removed command ``/ls``
- Recent topics are updated dynamically based on incoming messages
- Input and output characters don't interfere anymore
- Timestamps in the local timezone
- Various bug fixes

See also the `changelog`_.

.. _changelog: https://github.com/foobarbuzz/convoread/blob/master/CHANGES.rst


Usage
-----

Run the program::

    $ convoread
    welcome to convoread! type /help for more info
    >

You are now in ``convoread`` shell. You can just watch your live stream
indefinitely::

    *** topic mygroup/1234: Some tests
    13:06 <user1> hello
    13:21 <user2> convoread works
    13:22 <user1> @user2 indeed!

    *** topic othergroup/5678: Another topic
    14:07 <user3> convoread is nice
    >

You can also list recent topics and send messages::

    > /ts
    python:
        4393    3 pyquery - a jquery-like library for python
        4383    1 Fate of PySide
    vim:
        3012    1 Configuring Vim for Python
    mercurial:
        2412    1 Extensions I just can live without
    emacs:
    feedback:
    > /t 3012

    *** topic vim/3012: Configuring Vim for Python
    12:46 <user3> i configured it in .vimrc
    12:47 <user3> and i use this feature every day
    > hello vim community!
    13:25 <user3> welcome
    > so, vim or emacs? :)
    13:26 <user3> vim!
    >

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

* libnotify for desktop notifications
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
