# -*- coding: utf-8 -*-

import vim

import os
import datetime

from orgmode._vim import echo, ORGMODE, apply_count, repeat, realign_tags
from orgmode.menu import Submenu, ActionEntry
from orgmode.keybinding import Keybinding, Plug
from orgmode.py3compat.py_py3_string import VIM_PY_CALL


class Archive(object):

    def __init__(self):
        u""" Initialize plugin """
        object.__init__(self)
        # menu entries this plugin should create
        self.menu = ORGMODE.orgmenu + Submenu(u'&Archive')

        # key bindings for this plugin
        # key bindings are also registered through the menu so only additional
        # bindings should be put in this variable
        self.keybindings = []

    @classmethod
    @realign_tags
    @repeat
    @apply_count
    def archive_tree(cls):
        d = ORGMODE.get_document(allow_dirty=True)

        heading = d.current_heading()
        if not heading:
            return

        fn = os.path.splitext(vim.current.buffer.name)
        filename = fn[0] + '_archive' + fn[1]
        f = open(filename, "a")
        if heading.body:
            f.write("%s\n%s\n" % (heading, "\n".join(heading.body)))
        else:
            f.write("%s\n" % (heading))
        f.close()

        l = heading.get_parent_list()
        l.remove(heading)
        d.write()

        echo(u'moved subtree to: %s' % filename)
        return True

    @classmethod
    @realign_tags
    @repeat
    @apply_count
    def refile_tree(cls):
        d = ORGMODE.get_document(allow_dirty=True)

        heading = d.current_heading()
        if not heading:
            return

        # fn = os.path.splitext(vim.current.buffer.name)
        # filename = fn[0] + '_archive' + fn[1]
        today = datetime.datetime.today()
        name = datetime.datetime.strftime(today, "%Y-%m-%d")
        filename = os.path.join("/home/acid/notes/diary", name + ".org")
        f = open(filename, "a")
        if heading.body:
            f.write("%s\n%s\n" % (heading, "\n".join(heading.body)))
        else:
            f.write("%s\n" % (heading))
        f.close()

        l = heading.get_parent_list()
        l.remove(heading)
        d.write()

        echo(u'moved subtree to: %s' % filename)
        return True


    def register(self):
        self.keybindings.append(Keybinding(u'<localleader>at', Plug(
            u'OrgArchiveTreeNonInteractive',
            u'%s ORGMODE.plugins[u"Archive"].archive_tree()<CR>' % VIM_PY_CALL)))
        self.menu + ActionEntry(u'&Archive Subtree', self.keybindings[-1])

        self.keybindings.append(Keybinding(u'<localleader>rd', Plug(
            u'OrgRefileTreeNonInteractive',
            u'%s ORGMODE.plugins[u"Archive"].refile_tree()<CR>' % VIM_PY_CALL)))
        self.menu + ActionEntry(u'&Refile Subtree', self.keybindings[-1])
