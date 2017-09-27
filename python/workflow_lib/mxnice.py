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
Workflow library module for launching jobs on OAR
"""

__authors__ = ["Olof Svensson"]
__license__ = "MIT"
__date__ = "27/09/2017"



import shlex
import pprint
import threading
import subprocess


# From http://stackoverflow.com/questions/1191374/using-module-subprocess-with-timeout
def runCommand(command, timeout_sec=5, cwd=None):
    proc = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
    kill_proc = lambda p: p.kill()
    timer = threading.Timer(timeout_sec, kill_proc, [proc])
    try:
        timer.start()
        stdout, stderr = proc.communicate()
    finally:
        timer.cancel()
    return stdout, stderr

def checkLoadOnMxNICE(timeOut=5):
    listHosts = []
    listExcludedHosts = []
    loadDict = {}

#    # mxhpc2-16??
#    for hostNumber in range(1601, 1609):
#        hostName = "mxhpc2-{0:4d}".format(hostNumber)
#        if not hostName in listExcludedHosts:
#            listHosts.append(hostName)
#
#    # mxhpc2-17??
#    for hostNumber in range(1701, 1705):
#        hostName = "mxhpc2-{0:4d}".format(hostNumber)
#        if not hostName in listExcludedHosts:
#            listHosts.append(hostName)

    # mxhpc3-220[1-4]
    for hostNumber in range(2201, 2205):
        hostName = "mxhpc3-{0:4d}".format(hostNumber)
        if not hostName in listExcludedHosts:
            listHosts.append(hostName)

    # mxhpc3-230[1-4]
    for hostNumber in range(2301, 2305):
        hostName = "mxhpc3-{0:4d}".format(hostNumber)
        if not hostName in listExcludedHosts:
            listHosts.append(hostName)

    # Check load
    for hostName in listHosts:
        response = ""
        load = "unknown"
        stdout, stderr = runCommand("ssh %s uptime" % hostName, timeOut)
        response = stdout
        listLines = response.split("\n")
        for line in listLines:
            listItems = line.split()
            noItems = len(listItems)
            for position in range(noItems):
                if listItems[position] == "load":
                    load = float(listItems[position + 2].split(",")[0])
                    loadDict[hostName] = load

    listSorted = sorted(loadDict.items(), key=lambda x: x[1])
    return listSorted


def submitJobToOar(commandLine, workingDirectory, nodes=1, core=4, walltime="2:00:00", queue=None, name=None):
    oarJobId = None
    oarCommand = "oarsub"
    # Queue
    if queue is not None:
        oarCommand += " -q {0}".format(queue)
    # Resources
    oarCommand += " -l nodes={nodes}/core={core},walltime={walltime}".format(nodes=nodes,
                                                                             walltime=walltime,
                                                                             core=core)
    # Working directory
    oarCommand += " -d {0}".format(workingDirectory)
    # Name
    if name is not None:
        oarCommand += " -n '{0}'".format(name)
    # Execute the command
    oarCommand += " '{0}'".format(commandLine)
    print(oarCommand)
    stdout, stderr = runCommand(oarCommand)
    # Extract the oar job number
    listLines = stdout.split("\n")
    for line in listLines:
        if 'OAR_JOB_ID' in line:
            oarJobId = int(line.split("=")[1])
    return oarCommand, oarJobId


def parseOarStat(oarStat):
    listLines = oarStat.split("\n")
    dictOarStat = {}
    for line in listLines:
        if line != "":
            if " = " in line:
                key, value = line.split(" = ", 1)
            elif ": " in line:
                key, value = line.split(": ", 1)
            else:
                key = line.split(" =", 1)
                value = None
            if key is not None and value is not None:
                dictOarStat[key.strip()] = value.strip()
    return dictOarStat

def getOarStat(oarJobId):
    stdout, stderr = runCommand("oarstat -f -j {0}".format(oarJobId))
    return parseOarStat(stdout)


