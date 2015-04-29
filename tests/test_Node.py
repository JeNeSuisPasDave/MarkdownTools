# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
"""Unit tests for the Node class of of the mdmerge module."""

import unittest
import os

from mdmerge.node import Node


class NodeTests(unittest.TestCase):

    """Unit tests for the node.py module."""

    def __init__(self, *args):
        """Constructor."""
        self.devnull = open(os.devnull, "w")
        super().__init__(*args)
        self.__root = os.path.dirname(__file__)
        self.__data_dir = os.path.join(self.__root, "data")

    def __del__(self):
        """Destructor."""
        self.devnull.close()
        self.devnull = None

    # -------------------------------------------------------------------------+
    # setup, teardown, noop
    # -------------------------------------------------------------------------+

    def setUp(self):
        """Create data used by the test cases."""
        import tempfile

        self.temp_dir_path = tempfile.TemporaryDirectory()
        return

    def tearDown(self):
        """Cleanup data used by the test cases."""
        self.temp_dir_path.cleanup()
        self.temp_dir_path = None

    def test_no_op(self):
        """Excercise tearDown and setUp methods.

        This test does nothing itself. It is useful to test the tearDown()
        and setUp() methods in isolation (without side effects).

        """
        return

    # -------------------------------------------------------------------------+
    # tests for Node
    # -------------------------------------------------------------------------+

    def test_node_empty_root(self):
        """Test Node.__init__().

        Create a root node with default initialization.

        """
        cut = Node("")
        self.assertTrue(cut.is_ancestor(None))

    def test_node_root(self):
        """Test Node.__init__().

        Create a root node with a file_path.

        """
        cut = Node("", "book.txt")
        self.assertFalse(cut.is_ancestor(None))
        self.assertTrue(cut.is_ancestor("book.txt"))
        self.assertFalse(cut.is_ancestor("wat.md"))

    def test_node_one_child(self):
        r"""Test Node.__init__().

        R
        |
        A

        """
        cut = Node("", "root.md")
        a_node = cut.add_child("a.md")
        self.assertFalse(a_node.is_ancestor(None))
        self.assertTrue(a_node.is_ancestor("root.md"))
        self.assertTrue(a_node.is_ancestor("a.md"))
        self.assertFalse(a_node.is_ancestor("wat.md"))

    def test_node_branches(self):
        r"""Test Node.__init__().

          R
          |
          A
         / \
        B   C
             \
              D

        """
        cut = Node("", "root.md")
        a_node = cut.add_child("a.md")
        b_node = a_node.add_child("b.md")
        c_node = a_node.add_child("c.md")
        d_node = c_node.add_child("d.md")
        self.assertFalse(b_node.is_ancestor(None))
        self.assertTrue(d_node.is_ancestor("root.md"))
        self.assertTrue(d_node.is_ancestor("a.md"))
        self.assertFalse(d_node.is_ancestor("b.md"))
        self.assertTrue(d_node.is_ancestor("c.md"))
        self.assertTrue(d_node.is_ancestor("d.md"))

    def test_node_circular_reference(self):
        r"""Test Node.__init__().

          R
          |
          A
         / \
        B   C
             \
              B
               \
                A (should fail)

        """
        cut = Node("", "root.md")
        a_node = cut.add_child("a.md")
        a_node.add_child("b.md")
        c_node = a_node.add_child("c.md")
        acb_node = c_node.add_child("b.md")
        with self.assertRaises(AssertionError):
            acb_node = acb_node.add_child("a.md")

    def test_node_root_path(self):
        """Test Node.__init__().

        Create a root node with a file_path and validate the rootPath.

        """
        cut = Node(file_path="/aone/btwo/cthree/book.txt")
        self.assertFalse(cut.is_ancestor(None))
        self.assertTrue(cut.is_ancestor("/aone/btwo/cthree/book.txt"))
        self.assertFalse(cut.is_ancestor("/aone/btwo/cthree/wat.md"))
        self.assertEqual("/aone/btwo/cthree", cut.root_path())

    def test_empty_node_root_path(self):
        """Test Node.__init__().

        Create a root node with a file_path and validate the rootPath.

        """
        cut = Node("/aone/btwo/cthree")
        self.assertTrue(cut.is_ancestor(None))
        self.assertFalse(cut.is_ancestor("/aone/btwo/cthree/book.txt"))
        self.assertFalse(cut.is_ancestor("/aone/btwo/cthree/wat.md"))
        self.assertEqual("/aone/btwo/cthree", cut.root_path())

    def test_node_one_child_root_path(self):
        r"""Test Node.__init__().

        R
        |
        A

        """
        cut = Node(file_path="/aone/btwo/cthree/root.md")
        a_node = cut.add_child("/aone/btwo/cthree/a.md")
        self.assertFalse(a_node.is_ancestor(None))
        self.assertTrue(a_node.is_ancestor("/aone/btwo/cthree/root.md"))
        self.assertTrue(a_node.is_ancestor("/aone/btwo/cthree/a.md"))
        self.assertFalse(a_node.is_ancestor("/aone/btwo/cthree/wat.md"))
        self.assertEqual(cut.root_path(), a_node.root_path())

# eof
