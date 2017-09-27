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

__authors__ = ["Olof Svensson"]
__license__ = "MIT"
__date__ = "27/09/2017"

import os
import time

from workflow_lib import mxnice


def run(workingDirectory=None, oarJobId=None, **kwargs):

    started = "false"
    dictOARStat = {}

    if workingDirectory is not None:
        startedFile = os.path.join(workingDirectory, "STARTED")

        while not os.path.exists(startedFile):
            time.sleep(1)
            os.system("ls {0}".format(workingDirectory))

        if os.path.exists(startedFile) and oarJobId is not None:
            started = "true"
            oarJobId = int(oarJobId)
            dictOARStat = mxnice.getOarStat(oarJobId)


    return {"dictOARStat": dictOARStat,
            "started": started}


