# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

class Node:
    """A tree node used to build a tree of filepaths that contain
    no cycles.

    """

    def __init__(self, filePath=None, parentNode=None):
        self.__filePath = filePath
        self.__parent = parentNode
        self.__children = []

    def addChild(self, filePath):
        if self.isAncestor(filePath):
            fmts = ("Circular reference."
                " File '{0}' and an ancestor of itself.")
            raise AssertionError(fmts.format(filePath))
        node = Node(filePath, self)
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
