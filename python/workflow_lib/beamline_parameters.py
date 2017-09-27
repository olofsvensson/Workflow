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
Dictionary with all beamline specific parameters
"""

__authors__ = ["Olof Svensson"]
__license__ = "MIT"
__date__ = "27/09/2017"



DICT_PARAMETER = {


    "simulator_mxcube": {
        "besPort": 8090,
        "workflowExecutorDevice": "simulator_mxcube/bes/1",
        "detectorMode": "Hardware binned",
        "detectorDark" : "0",
        "stacDevice": None,
        "dehydrationDevice": None,
        "suffix": "cbf",
        "mxCuBEv1URI": None,
        "mxCuBEv2URI": "http://ub1004.esrf.fr:7171",
        "defaultUser": "simulator",
        "minExposureTime": 0.1,
        "maxOscillationSpeed": 360.0,
        "minOscillationWidth": 0.05,
        "numberPasses": 1,
        "phiyMaxSpeed": 0.05,
        "phizMaxSpeed": 0.05,
        "sampxMaxSpeed": 0.01,
        "sampyMaxSpeed": 0.01,
        "minTransmission": 1.0,
        "omegaRot": [0.00098, -0.00189, 1.00000],
        "kappaRot": [-0.2822, -0.29432, 0.91309],
#                "kappaRot": [-0.29173, -0.28925, 0.91172],
        "phiRot": [0.00939, -0.01221 , 0.99988],
        "defaultOscillationRange": 1.0,
        "defaultCharacterisationExposureTime": 1.0,
        "defaultCharacterisationTransmission": 100.0,
        "defaultGridExposureTime": 1.0,
        "defaultGridTransmission": 100.0,
        "defaultCollectExposureTime": 1.0,
        "defaultCollectTransmission": 100.0,
        "defaultDehydrationTransmission": 50.0,
        "detectorRadius": None,
        "maxResolution": 1.3,
    },

}

