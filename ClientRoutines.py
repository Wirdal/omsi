import datetime
import select
import socket
import time
import os

import Checksum
import ClientGlobals
import NetworkMonitor
import ProcessMonitor


# module that provides an interface for all server related requests
# sets up connection with the running server on localhost and port 20500
# all methods are static and should be called statically


# executes a function on the server
# input function name to be executed
# return value True or False depending on success on server
def callFunctionOnServer(functionName):

    #create and configure the socket
    lSocket = configureSocket()

    # execute the function
    lSocket.send(functionName)

    # see what the server has to say and return it
    lServerResponse = getResponseFromServer(lSocket)

    if lServerResponse == "s" or lServerResponse == "f":
        return lServerResponse
    else:
        # the server is trying to send a file
        if lServerResponse == "file":
            receiveExamQuestionsFile(lSocket)
        else:
            return "f"


def computeChecksum(filename):

    # values students need to copy down for reference
    h = Checksum.checksum(filename)

    print 'Please hand copy the following value and turn it into the professor: ' + h


# initialization of socket, no connection is established yet
def configureSocket():
    # connection on localhost for now

    try:
        # create local Internet TCP socket (domain, type)
        pSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # initiate server connection to global
        pSocket.connect((ClientGlobals.gHost, ClientGlobals.gPort))
        return pSocket

    #connection problem
    except socket.error, (value, message):
        if pSocket:
            # close socket
            pSocket.close()
        raise RuntimeError("Could not open socket on Client: " + message)
        return False


def createExamQuestionsFile():
    # create new or truncate old file - hence the w flag

    # first try creating the file in the desired directory
    try:
        lFilePath = os.path.join(ClientGlobals.gStudentHomeDirectory, "ExamQuestions.txt")
        lNewFile = open(lFilePath, 'w')
        return lNewFile
    except IOError:
        try:
            lFilePath = "ExamQuestions.txt"
            lNewFile = open(lFilePath, 'w')
            print "Your home directory: %s was not accessible! Please make sure the directory exists" \
                  "The questions file was successfully created in the directory where this code is located."
            return lNewFile
        except IOError:
            print "Error: Exam questions file could not be created on Client's machine\n"
            return False


# close the connection
# returning success/failure message or initiating a file transfer from server to student
def getResponseFromServer(pSocket):
    # block until server response received
    lServerResponse = pSocket.recv(1024)
    if lServerResponse != "file":
        pSocket.close()
        if lServerResponse == "s":
            return True
        else:
            print lServerResponse
            return False
    else:
        return "file"


def monitorProcesses(pSamplingFrequency, pExamDuration):

    # calculate end time
    lEndTime = datetime.datetime.now() + datetime.timedelta(minutes=pExamDuration)

    # collect process information from student's machine
    while datetime.datetime.now() < lEndTime:

        # open file to store process information
        lOutputFile = open('processes-' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.txt', 'w')

        # write process information to file
        ProcessMonitor.collectProcessesInformation(lOutputFile)

        # close file
        lOutputFile.close()

        # submit file to server

        time.sleep(pSamplingFrequency)

def monitorNetworkTraffic(pExamDuration):

    # calculate end time
    lEndTime = datetime.datetime.now() + datetime.timedelta(minutes=pExamDuration)

    # capture packets, save to file
    lOutputFile = NetworkMonitor.collectPackets(lEndTime)

    # submit file to server


# this opens a file with read permissions on the file
# ATTENTION: an open file is returned! Call file.close() on the returned object
def openFileOnClient(pFileName):
    try:
      lOpenFile = open(pFileName, "r")
      return lOpenFile
    except IOError:
      print "Error: File %s could not be opened. Make sure you entered the correct filename " % pFileName
      return 0


# download exam questions from professor's machine
def receiveExamQuestionsFile(pClientSocket):

    # create local file to write exam questions to
    lExamQuestionsFile = createExamQuestionsFile()

    # if file was not created, notify the server
    if not lExamQuestionsFile:
        print "We could not create a local file for the questions. /n " \
              "Please try again. Make sure your directory exists and is set properly"

    # create boolean to track
    lSuccess = False
    try:
        # if file was successfully created, notify server to begin sending exam questions
        pClientSocket.send("ClientWantsQuestions")

        print "Reading Questions file from server\n"

        # write data from server to file
        while True:
            ready = select.select([pClientSocket], [], [], 2)
            lChunkOfFile = pClientSocket.recv(1024)
            if ready[0] and lChunkOfFile != '':
                lExamQuestionsFile.write(lChunkOfFile)
            else:
                print "Finished reading Questions file from server"
                lSuccess = True
                break

    finally:
        # if exam questions were not successfully downloaded, print error
        if not lSuccess:
            print "Error: File transfer was not successful"

        # close file, regardless of success
        lExamQuestionsFile.close()

        # return File
        return lExamQuestionsFile


# sends a file from the student to the professor
# submission of file
def sendFileToServer(pFileName):

    # create and configure the socket
    lSocket = configureSocket()

    # open the file

    lOpenFile = openFileOnClient(pFileName)

    lFileChunk = lOpenFile.read(1024)

    if (lFileChunk != ""):

        lOpenFile.close()

        # first tell the server that we are sending a file
        lSocket.send("ClientIsSendingAFile")

        # block this before sending the filename, otherwise both the command and the file name will be appended on the server
        lDebugging = lSocket.recv(1024);

        # send the name of the file
        lSocket.send(pFileName)

        # block client until server is ready to accept the email of the student
        lDebugging = lSocket.recv(1024)

        #send the student email
        lSocket.send(ClientGlobals.gStudentEmail)

        # all information has been sent, get the go sign from the server
        lResponse = lSocket.recv(1024)

        # check if something went wrong server side
        if lResponse != "ReadyToAcceptClientFile":
            print "The server aborted prior to transmission of file, check server logs for more details"
            return

        # send the file
        lOpenFile = open(pFileName, "r")
        lFileChunk = lOpenFile.read(1024)
        while (lFileChunk):
            print "Sending File %s" % pFileName
            lSocket.send(lFileChunk)
            lFileChunk = lOpenFile.read(1024)

        # any chance that the file cant be sent?
        lOpenFile.close()

    # print msg if file cannot be opened
    else:
        # Error message for a bad student submission file
        print "Unable to read file: " + pFileName + "." \
                                                    "Make sure your submission file is in the " \
                                                    "right directory and is of type .txt."
    # closing the file
    lOpenFile.close()
    return getResponseFromServer(lSocket)

# simple setter
# pHost = IP address provided by prof
# pPort = Port provided by prof
def setUpServer(pHost, pPort):
    global gPORT, gHOST
    # deactivated during testing phase! The connection is set up on localhost
    # gPORT = pPort
    # gHOST = pHost