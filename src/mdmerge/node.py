# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
from __future__ import print_function, with_statement, generators, \
    unicode_literals
import os.path

class Node:
    """A tree node used to build a tree of filepaths that contain
    no cycles.

    """

    def __init__(self, rootPath=None, filePath=None, parentNode=None):
        self.__rootPath = rootPath
        self.__filePath = filePath
        self.__parent = parentNode
        self.__children = []
        if (None == rootPath
        and None != filePath):
            self.__rootPath = os.path.dirname(os.path.abspath(filePath))

    def addChild(self, filePath):
        if self.isAncestor(filePath):
            fmts = ("Circular reference."
                " File '{0}' is an ancestor of itself.")
            raise AssertionError(fmts.format(filePath))
        node = Node(self.__rootPath, filePath, self)
        self.__children.append(node)
        return node

    def filePath(self):
        return self.__filePath

    def isAncestor(self, filePath):
        if self.__filePath == filePath:
            return True
        if self.__parent == None:
            return False
        if self.__parent.__filePath == None:
            return False
        return self.__parent.isAncestor(filePath)

    def rootPath(self):
        return self.__rootPath
