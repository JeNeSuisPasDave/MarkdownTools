# Copyright 2015 Dave Hein
#
# This file is part of MarkdownTools
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

"""Module of classes to model the hierarchy of input files."""

import os.path


class Node:

    """A filepath tree node.

    A tree node used to build a tree of filepaths that contain
    no cycles.

    """

    def __init__(self, root_path=None, file_path=None, parent_node=None):
        """Constructor."""
        self.__root_path = root_path
        self.__file_path = file_path
        self.__parent = parent_node
        self.__children = []
        if ((None == self.__root_path)
                and (None != self.__file_path)):
            self.__root_path = os.path.dirname(os.path.abspath(
                self.__file_path))

    def add_child(self, file_path):
        """Add a child node.

        Args:
            file_path: The file_path to store in the new child node.
        """
        if self.is_ancestor(file_path):
            fmts = (
                "Circular reference."
                " File '{0}' is an ancestor of itself.")
            raise AssertionError(fmts.format(file_path))
        node = Node(self.__root_path, file_path, self)
        self.__children.append(node)
        return node

    def file_path(self):
        """Get the file path held by this node."""
        return self.__file_path

    def is_ancestor(self, file_path):
        """Whether a file path is held by an ancestor node."""
        if self.__file_path == file_path:
            return True
        if self.__parent is None:
            return False
        if self.__parent.__file_path is None:
            return False
        return self.__parent.is_ancestor(file_path)

    def root_path(self):
        """Get the root path of the root node of the hierarchy."""
        return self.__root_path
