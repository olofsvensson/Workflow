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
import sys
import time
import tempfile
import traceback

from workflow_lib import path
from workflow_lib import edna_mxv1

def run(image_path, jpeg_path, jpeg_thumbnail_path, **kwargs):

    try:
        errorMessage = ""
        thumbnailsCreated = "false"
        pathToTempDir = None

        user = None
        try:
            user = path.extractBeamlineFromDirectory(image_path)
        except:
            pass
        if user is None:
            user = os.environ["USER"]

        strDate = time.strftime("%Y%m%d", time.localtime(time.time()))
        strTime = time.strftime("%H%M%S", time.localtime(time.time()))
        strTmpUser = os.path.join("/tmp", user, strDate)

        if not os.path.exists(strTmpUser):
            os.makedirs(strTmpUser, 0755)
        pathToTempDir = tempfile.mkdtemp(prefix="{0}_thumbnail_".format(strTime), dir=strTmpUser)

        list_image_creation = [{"imagePath": image_path}]

        edna_mxv1.create_thumbnails_for_pyarch(list_image_creation, pathToTempDir)

        if os.path.exists(jpeg_path) and os.path.exists(jpeg_thumbnail_path):
            thumbnailsCreated = "true"

    except:

        (exc_type, exc_value, exc_traceback) = sys.exc_info()
        errorMessage = "{0} {1}".format(exc_type, exc_value)
        listTrace = traceback.extract_tb(exc_traceback)
        for listLine in listTrace:
            errorMessage += "  File \"%s\", line %d, in %s%s" % (listLine[0], listLine[1], listLine[2], os.linesep)

    return {"errorMessage": errorMessage,
            "thumbnailsCreated": thumbnailsCreated,
            "pathToTempDir": pathToTempDir}
