===========
 convoread
===========

Command-line tool for `Convore`_.

Latest version: 0.4, 2011-02-14.

.. _Convore: https://convore.com/


Description
-----------

``convoread`` streams live Convore messages to the standard output or shows
desktop notifications (only for Ubuntu and similar systems at this moment). It
also allows posting new messages and listing recent messages in topics.

Future versions will allow creating topics, managing notifications, etc.

See `discussion`_ on Convore for ``convoread`` announcements, support.

.. _discussion: https://convore.com/feedback/convoread-simple-console-client-for-convore/


Usage
-----

*This section describes the next version 0.5. Stay tuned!*

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
       4393    3 pyquery - a jquery-like library for python
       4383    1 Fate of PySide
       3012      Configuring Vim for Python
     * 3716      Multiprocessing & Socket Duplication
       2412      Extensions I just can live without
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
support libnotify::

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
