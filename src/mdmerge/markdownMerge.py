# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
import os
import os.path
import sys
import argparse
import re
import io
from collections import deque

class MarkdownMerge:

    def __init__(self,
        wildcardExtensionIs=".html",
        bookTxtIsSpecial=False):
        self.__wildcardExtensionIs = wildcardExtensionIs
        self.__bookTxtIsSpecial = bookTxtIsSpecial

        self.__reoIndexComment = re.compile("^#")
        self.__reoLeanpubIndexMarker = re.compile("^frontmatter\:$")
        self.__reoLeanpubIndexMeta = re.compile(
            "^(frontmatter\:|mainmatter:|backmatter:)$")
        self.__reoMultiMarkdownIndexMarker = re.compile("^#merge$")
        self.__reoMmdTransclusion = re.compile("^\{\{(.+)\}\}$")
        self.__reoPathAndWildcardExtension = re.compile("^(.+)\.\*$")
        self.__reoMarkedInclude = re.compile("^<<\[(.+)\]$")
        self.__reoLeanpubInclude = re.compile("^<<\((.+)\)$")
        self.__reoLeanpubCodeInclude = re.compile("^<<\[.*\]\((.+)\)$")
        self.__reoCodeFence = re.compile("^\~\~\~[a-zA-Z0-9]+$")
        self.__reoFence = re.compile("^\~\~\~$")
        self.buf = deque()

    def _findIncludePath(self, lines):
        """Detect wheter line is an include specification.

        Args:
            lines: up to 5 lines of input to be examined for file
                include specifications
        Returns:
            A tuple containing, in order:
                includePath: None if the line is not an include
                    specification. Otherwise, returns the file
                    specification as a string value.
                isCode: True if the include specification is for code;
                    otherwise, False.
                needsFencing: True if the code include needs to be wrapped
                    in a fence; False if not a code include or if fence already
                    exists.

        """

        if None == lines:
            return None, False, False

        # look for code file transclusion specification, which is:
        #
        #   1. A blank line, followed by
        #   2. A code fence start (e.g. `~~~` or `~~~python` or similar, followed by
        #   3. A line containing only `{{filepath}}`, followed by
        #   4. A code fence termination (e.g. `~~~`), followed by
        #   5. Another blank line.
        #
        # Of course, the first line could be None, indicating top of file.
        # And the last line could be None, indicating end of file
        #
        if (5 == len(lines)):
            if (self._stringIsNullOrWhitespace(lines[0])
            and self._stringIsNullOrWhitespace(lines[4])
            and not self._stringIsNullOrWhitespace(lines[1])
            and not self._stringIsNullOrWhitespace(lines[2])
            and not self._stringIsNullOrWhitespace(lines[3])
            and self._lineIsCodeFence(lines[1])
            and self._lineIsEndingFence(lines[3])):
                spec = self._findTransclusion(lines[2])
                if (None != spec):
                    return spec, True, False

        # look for normal file transclusion specification, which is:
        #
        #   1. A blank line, followed by
        #   2. A line containing only `{{filepath}}`, followed by
        #   3. Another blank line.
        #
        if (3 == len(lines)):
            if (self._stringIsNullOrWhitespace(lines[0])
            and self._stringIsNullOrWhitespace(lines[2])):
                spec = self._findTransclusion(lines[1])
                if (None != spec):
                    return spec, False, False

        # look for Marked file include specification, which is:
        #
        #   1. A blank line, followed by
        #   2. A line containing only `<<[filepath]`, followed by
        #   3. Another blank line.
        #
        if (3 == len(lines)):
            if (self._stringIsNullOrWhitespace(lines[0])
            and self._stringIsNullOrWhitespace(lines[2])):
                spec = self._findMarkedInclude(lines[1])
                if (None != spec):
                    return spec, False, False

        # look for Leanpub file include specification, which is:
        #
        #   1. A blank line, followed by
        #   2. A line containing only `<<(filepath)`, or
        #      `<<[code caption](filepath) followed by
        #   3. Another blank line.
        #
        if (3 == len(lines)):
            if (self._stringIsNullOrWhitespace(lines[0])
            and self._stringIsNullOrWhitespace(lines[2])):
                spec = self._findLeanpubInclude(lines[1])
                if (None != spec):
                    return spec, True, True

        # Get out
        #
        return None, False, False

    def _findLeanpubInclude(self, line):
        """Parse the line looking for a Leanpub file include
        specification.

        Args:
            line: The line of the input file to examine.

        Returns:
            `None` if no file include specification is found in the line.
            If a file include specification is found in the line, then
            the specified file path is returned. If the specified path used
            a wildcard extension, the the wildcard is replaced with the
            export extension.

        """

        m = self.__reoLeanpubInclude.match(line)
        if not m:
            m = self.__reoLeanpubCodeInclude.match(line)
            if not m:
                return None
        filepath = m.group(1)
        return filepath

    def _findMarkedInclude(self, line):
        """Parse the line looking for a Marked file include
        specification.

        Args:
            line: The line of the input file to examine.

        Returns:
            `None` if no file include specification is found in the line.
            If a file include specification is found in the line, then
            the specified file path is returned. If the specified path used
            a wildcard extension, the the wildcard is replaced with the
            export extension.

        """

        m = self.__reoMarkedInclude.match(line)
        if not m:
            return None
        filepath = m.group(1)
        return filepath

    def _findTransclusion(self, line):
        """Parse the line looking for a Multimarkdown file transclusion
        specification.

        Args:
            line: The line of the input file to examine.

        Returns:
            `None` if no file transclusion specification is found in the line.
            If a file transclusion specification is found in the line, then
            the specified file path is returned. If the specified path used
            a wildcard extension, the the wildcard is replaced with the
            export extension.

        """

        m = self.__reoMmdTransclusion.match(line)
        if not m:
            return None
        filepath = m.group(1)
        if filepath.endswith(".*"):
            m = self.__reoPathAndWildcardExtension.match(filepath)
            if m:
                filepath = "{0}{1}".format(
                    m.group(1), self.__wildcardExtensionIs)
        return filepath

    def _getAbsolutePath(self, mainDocumentPath, filePath):
        """A method to determine the absolute path of a file path
        that might be relative or in the users home directory.

        """
        absPath = os.path.expandvars(filePath)
        absPath = os.path.expanduser(absPath)
        if os.path.isabs(absPath):
            return absPath
        absPath = os.path.join(os.path.dirname(mainDocumentPath), absPath)
        return absPath

    def _isFileAnIndex(self, absFilePath):
        """Examines the initial lines of a file to determine whether it
        is an index file.

        Args:
            absFilePath: the full file path of the file to be examined.

        Returns:
            True if the file is a mmd_merge or a LeanPub index file.

        """

        if (None == absFilePath
        or not os.path.exists(absFilePath)):
            return False
        with io.open(absFilePath, "r") as idxfile:
            for line in idxfile:
                line = line.strip()
                if (0 == len(line)
                or self._isIndexComment(line)):
                    continue # skip blanks and comments
                if self._isLeanpubIndexMarker(line):
                    return True
                break
        return False

    def _isIndexComment(self, line):
        """Detect whether line begins with '#'. Such lines are comments
        when in an index file.

        Returns:
            True if the line begins with '#'; otherwise, False.

        """

        m = self.__reoIndexComment.match(line)
        if not m:
            return False
        return True

    def _isLeanpubIndexMarker(self, line):
        """Detect whether line is 'frontmatter:', indicating the line
        is a marker for leanpub index files.

        Returns:
            True if the line is 'frontmatter:'; otherwise, False.

        """

        m = self.__reoLeanpubIndexMarker.match(line)
        if not m:
            return False
        return True

    def _isLeanpubIndexMeta(self, line):
        """Detect whether line is some LeanPub meta tag. Specifically:
        'frontmatter:', 'mainmatter:', 'backmatter:'.

        Returns:
            True if the line is a LeanPub meta tag; otherwise, False.

        """

        m = self.__reoLeanpubIndexMeta.match(line)
        if not m:
            return False
        return True

    def _isMultiMarkdownIndexMarker(self, line):
        """Detect whether line is '#merge', indicating the line
        is a marker for mmd_merge index files.

        Returns:
            True if the line is '#merge'; otherwise, False.

        """

        m = self.__reoMultiMarkdownIndexMarker.match(line)
        if not m:
            return False
        return True

    def _lineIsCodeFence(self, line):
        """Detect whether the line contains a code fence directive.

        Args:
            line: the text line to examine

        Returns:
            True if the line is a code fence directive.
            Otherwise returns False.

        """

        m = self.__reoCodeFence.match(line)
        if not m:
            m = self.__reoFence.match(line)
            if not m:
                return False
        return True

    def _lineIsEndingFence(self, line):
        """Detect whether the line contains a terminating fence directive.

        Args:
            line: the text line to examine

        Returns:
            True if the line is a terminating fence directive.
            Otherwise returns False.

        """

        m = self.__reoFence.match(line)
        if not m:
            return False
        return True

    def _mergedLines(self,
        mainDocumentPath, infileNode, infile, isCode, needsFence):
        """A generator function that examines each line of the
        input file and recursively calls itself for each included
        file. If the file is code, then include specifications are not
        followed but are reproduced as is.

        Args:
            mainDocumentPath: the absolute file path of the main document;
                used to determine the location of relative file paths found
                in include specifications.
            infileNode: the Node object representing the input file
            infile: the file object of the opened input file
            isCode: True if the include specification is for code;
                otherwise, False.
            needsFence: True if the code include needs to be wrapped
                in a fence; False if not a code include or if fence already
                exists.

        Returns:
            The next line to be written to the output file, or None
            if there are no more input lines.

        """

        buf5 = deque(maxlen=5)
        buf3 = deque(maxlen=3)
        buf5.append(None) # indicate top of file
        buf3.append(None) # indicate top of file
        buf5.append(None) # align with buf3 so that buf3 always
        buf5.append(None) #   corresponds to buf5[2:4]

        startFenceProduced = False
        endFenceProduced = False

        while True:
            if (needsFence
            and not startFenceProduced):
                self.buf.append("~~~")
                startFenceProduced = True
            line = infile.readline()
            if not line:
                # at end of file, so just move buf5 into buf
                if 0 != len(buf5):
                    bline = buf5.popleft()
                    if None != bline:
                        self.buf.append(bline)
                    else:
                        continue # skip leading None objects
                if 0 == len(self.buf):
                    if (needsFence
                    and not endFenceProduced):
                        self.buf.append("~~~")
                        endFenceProduced = True
                    else:
                        break;
            elif isCode:
                self.buf.append(line);
            else:
                if 5 == len(buf5):
                    # roll line out of buf5 into buf, so we don't lose it
                    bline = buf5.popleft()
                    if None != bline:
                        self.buf.append(bline)
                # add the new line to the deques
                buf5.append(line)
                buf3.append(line)
                # check whether this is a 5-line include pattern, ...
                includePath, lclIsCode, lclNeedsFence = (
                    self._findIncludePath(buf5))
                if includePath:
                    # consuming blank line, the start of the fence, and the
                    # include.
                    for x in range(2):
                        if None != x:
                            self.buf.append(buf5.popleft())
                    buf5.popleft()
                    buf3.clear()
                else:
                    # ... or a 3-line include pattern.
                    includePath, lclIsCode, lclNeedsFence = (
                        self._findIncludePath(buf3))
                    if includePath:
                        # consuming the preceding two buffered lines,
                        # then the blank line and the include
                        for x in range(2):
                            if None != x:
                                self.buf.append(buf5.popleft())
                        bline = buf5.popleft()
                        if None != bline:
                            self.buf.append(bline)
                        buf5.popleft()
                        for x in range(2):
                            buf3.popleft()
                if includePath:
                    # merge in the include file
                    #
                    absIncludePath = self._getAbsolutePath(
                        mainDocumentPath, includePath)
                    includedfileNode = infileNode.addChild(absIncludePath)
                    with io.open(absIncludePath, "r") as includedfile:
                        for deeperLine in self._mergedLines(
                            mainDocumentPath, includedfileNode, includedfile,
                            lclIsCode, lclNeedsFence):
                            yield deeperLine
            if 0 != len(self.buf):
                yield self.buf.popleft()

    def _mergeSingleFile(self,
        mainDocumentPath, absInfilePath, infileNode, outfile):
        """Add the merged lines of a single top-level file to the output.

        Args:
            mainDocumentPath: the absolute file path of the main document;
                used to determine the location of relative file paths found
                in include specifications.
            absInfilePath: the full filename of the input file to process.
            infileNode: the node representing the input file to process.
            outfile: the open output file in which to write the merged lines.

        """

        with io.open(absInfilePath, "r") as infile:
            for line in self._mergedLines(
                    mainDocumentPath, infileNode, infile, False, False):
                if None == line:
                    continue
                outline = line.rstrip("\r\n")
                outfile.write(outline + '\n')

    def _mergeIndexFile(self, absIdxfilePath, idxfileNode, outfile):
        """Treat each line of the index file as an input file. Process
        each input file to add the merged result to the output file.

        Args:
            absIdxfilePath: the full filename of the index file to process.
            idxfileNode: the node representing the index file to process.
            outfile: the open output file in which to write the merged lines.

        """

        with io.open(absIdxfilePath, "r") as idxfile:
            for line in idxfile:
                infilePath = line.strip();
                if (0 == len(infilePath)
                or self._isIndexComment(line)
                or self._isLeanpubIndexMeta(line)):
                    continue
                absInfilePath = self._getAbsolutePath(
                    absIdxfilePath, infilePath)
                infileNode = idxfileNode.addChild(absInfilePath)
                self._mergeSingleFile(
                    absIdxfilePath, absInfilePath, infileNode, outfile)

    def _stringIsNullOrWhitespace(self, s):
        """Detect whether the string is null, empty, or contains only
        whitespace.

        Args:
            s: the string object to test

        Returns:
            True if the string is None, zero-length, or contains only
            whitespace characters. Otherwise returns False.

        """

        if None == s:
            return True
        if 0 == len(s):
            return True
        if s.isspace():
            return True
        return False

    def merge(self, infileNode, outfile):
        """Give the input file (via a Node object) and the output file
        stream object, process the input file, including other files as
        specified by the include specification encountered, writing the
        resulting output lines to the output file stream.

        Args:
            infileNode: a Node object that represents the input
                file to be processed.
            outfile: the output file stream to which the resulting
                lines will be written.

        """

        infilePath = infileNode.filePath()
        absInfilePath = os.path.abspath(infilePath)
        infileName = os.path.basename(absInfilePath)
        if (self.__bookTxtIsSpecial
        and "book.txt".casefold() == infileName.casefold()):
            self._mergeIndexFile(absInfilePath, infileNode, outfile)
        elif self._isFileAnIndex(absInfilePath):
            self._mergeIndexFile(absInfilePath, infileNode, outfile)
        else:
            self._mergeSingleFile(
                absInfilePath, absInfilePath, infileNode, outfile)
