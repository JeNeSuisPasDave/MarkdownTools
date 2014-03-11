# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
"""
Unit tests for the Node class of of the mdmerge module.

"""

import unittest
import os

from mdmerge.node import Node

class NodeTests(unittest.TestCase):

    def __init__(self, *args):
        self.devnull = open(os.devnull, "w")
        super().__init__(*args)
        self.__root = os.path.dirname(__file__)
        self.__dataDir = os.path.join(self.__root, "data")

    # -------------------------------------------------------------------------+
    # setup, teardown, noop
    # -------------------------------------------------------------------------+

    def setUp(self):
        """Create data used by the test cases.

        """

        import tempfile

        self.tempDirPath = tempfile.TemporaryDirectory()
        return

    def tearDown(self):
        """Cleanup data used by the test cases.

        """

        import tempfile

        self.tempDirPath.cleanup()
        self.tempDirPath = None

    def testNoOp(self):
        """Excercise tearDown and setUp methods.

        This test does nothing itself. It is useful to test the tearDown()
        and setUp() methods in isolation (without side effects).

        """

        return

    # -------------------------------------------------------------------------+
    # tests for Node
    # -------------------------------------------------------------------------+

    def testNodeEmptyRoot(self):
        """Test Node.__init__().

        Create a root node with default initialization.

        """

        cut = Node("")
        self.assertTrue(cut.isAncestor(None))

    def testNodeRoot(self):
        """Test Node.__init__().

        Create a root node with a filepath.

        """

        cut = Node("", "book.txt")
        self.assertFalse(cut.isAncestor(None))
        self.assertTrue(cut.isAncestor("book.txt"))
        self.assertFalse(cut.isAncestor("wat.md"))

    def testNodeOneChild(self):
        """Test Node.__init__().

        R
        |
        A

        """

        cut = Node("", "root.md")
        aNode = cut.addChild("a.md")
        self.assertFalse(aNode.isAncestor(None))
        self.assertTrue(aNode.isAncestor("root.md"))
        self.assertTrue(aNode.isAncestor("a.md"))
        self.assertFalse(aNode.isAncestor("wat.md"))

    def testNodeBranches(self):
        """Test Node.__init__().

          R
          |
          A
         / \
        B   C
             \
              D

        """

        cut = Node("", "root.md")
        aNode = cut.addChild("a.md")
        bNode = aNode.addChild("b.md")
        cNode = aNode.addChild("c.md")
        dNode = cNode.addChild("d.md")
        self.assertFalse(bNode.isAncestor(None))
        self.assertTrue(dNode.isAncestor("root.md"))
        self.assertTrue(dNode.isAncestor("a.md"))
        self.assertFalse(dNode.isAncestor("b.md"))
        self.assertTrue(dNode.isAncestor("c.md"))
        self.assertTrue(dNode.isAncestor("d.md"))

    def testNodeCircularReference(self):
        """Test Node.__init__().

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
        aNode = cut.addChild("a.md")
        bNode = aNode.addChild("b.md")
        cNode = aNode.addChild("c.md")
        acbNode = cNode.addChild("b.md")
        with self.assertRaises(AssertionError):
            acbaNode = acbNode.addChild("a.md")

    def testNodeRootPath(self):
        """Test Node.__init__().

        Create a root node with a filepath and validate the rootPath.

        """

        cut = Node(filePath="/aone/btwo/cthree/book.txt")
        self.assertFalse(cut.isAncestor(None))
        self.assertTrue(cut.isAncestor("/aone/btwo/cthree/book.txt"))
        self.assertFalse(cut.isAncestor("/aone/btwo/cthree/wat.md"))
        self.assertEqual("/aone/btwo/cthree", cut.rootPath())

    def testEmptyNodeRootPath(self):
        """Test Node.__init__().

        Create a root node with a filepath and validate the rootPath.

        """

        cut = Node("/aone/btwo/cthree")
        self.assertTrue(cut.isAncestor(None))
        self.assertFalse(cut.isAncestor("/aone/btwo/cthree/book.txt"))
        self.assertFalse(cut.isAncestor("/aone/btwo/cthree/wat.md"))
        self.assertEqual("/aone/btwo/cthree", cut.rootPath())

    def testNodeOneChildRootPath(self):
        """Test Node.__init__().

        R
        |
        A

        """

        cut = Node(filePath="/aone/btwo/cthree/root.md")
        aNode = cut.addChild("/aone/btwo/cthree/a.md")
        self.assertFalse(aNode.isAncestor(None))
        self.assertTrue(aNode.isAncestor("/aone/btwo/cthree/root.md"))
        self.assertTrue(aNode.isAncestor("/aone/btwo/cthree/a.md"))
        self.assertFalse(aNode.isAncestor("/aone/btwo/cthree/wat.md"))
        self.assertEqual(cut.rootPath(), aNode.rootPath())

# eof