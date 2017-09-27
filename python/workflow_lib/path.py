# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/

"""
Workflow library module defining path help methods for workflows.
"""

__authors__ = ["Olof Svensson"]
__license__ = "MIT"
__date__ = "27/09/2017"


import os
import math

def extractBeamlineFromDirectory(directory):
    """Returns the name of a beamline given a directory path"""
    this_beamline = None
    list_directory = directory.split(os.sep)
    # First check: directory must start with "data":
    if list_directory[1] == "data":
        # Then check if second level is "visitor":
        if list_directory[2] == "visitor":
            this_beamline = list_directory[4]
        elif list_directory[3] == "inhouse":
            this_beamline = list_directory[2]
    if this_beamline is None:
        raise Exception("Could not extract beamline from path %s" %
                        directory)
    return this_beamline

def eigerTemplateToImage(fileTemplate, imageNumber, overlap=0):
    if math.fabs(overlap) < 1:
        fileNumber = int(imageNumber / 100)
        if fileNumber == 0:
            fileNumber = 1
        eigerFileTemplate = fileTemplate.replace("%04d", "1_data_%06d" % fileNumber)
    else:
        eigerFileTemplate = fileTemplate.replace("%04d", "%d_data_000001" % imageNumber)
    return eigerFileTemplate
