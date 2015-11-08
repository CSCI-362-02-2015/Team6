#!/usr/bin/python
 
from sys import platform as _platform
import subprocess   
import os.path
import sys
from importlib import import_module

def getTestCases():
    os.chdir("../testCases/")
    allFiles = os.listdir(".")
    return [TestCase(fileName) for fileName in allFiles if ".txt" in fileName and fileName[-1] != '~']
     
def executeTest(testCase):
    importStatement = convertPathToImport(testCase.modulePath)
    sys.path.append(testCase.modulePath)
    module = __import__(importStatement, fromlist=[testCase.methodName])
    #Just gets method name itself, not parameters or other signature
    methodNameTrimmed =  testCase.methodName[0:testCase.methodName.find('(')]
    methodToTest = getattr(module, methodNameTrimmed)
    result = methodToTest(*testCase.inputValue)
    testCase.actualResult = result
    
    #actual test
    if str(result) == testCase.expectedResult:
        testCase.testPassed = True
    return testCase

def convertPathToImport(path):
    path = path.replace("/", ".")
    path = path.replace(".py","")
    return path.split(".")[-1]

class TestCase:
    def __init__(self, fileName):
        file = open(fileName, 'r')
        fileContents = file.read().split("\n")
        self.id = fileContents[0]
        self.description = fileContents[1]
        self.modulePath = fileContents[2].strip()
        self.methodName = fileContents[3].strip()
        self.inputValue = fileContents[4].split('$,')
        self.expectedResult = fileContents[5]

        self.actualResult = ""
        self.testPassed = False

        file.close()
        
    
def clearTempFolder():
    #go back a directory, remove everyting from temp,
    #if nothing is in temp, the warning is suppressed by sending it to null
    subprocess.call("rm ../temp/* 2>/dev/null", shell=True)

def generateHtml(testResults):
    html = "<html>"
    html += "<body>"
    html += "<h1>Test Results</h1>"
    html += testResults
    html += "</body>"
    return html + "</html>"

def writeHtmlFile(html):
    os.chdir("..")
    os.chdir("./reports/")
    filename = "test_results.html"
    output = open(filename,'w')
    output.write(html)
    if _platform == "linux" or _platform == "linux2":
        # linux:
        subprocess.call("xdg-open " + filename, shell=True)
    elif _platform == "darwin":
        # OS X:
        subprocess.call("open " + filename, shell=True)


def main():
    clearTempFolder()
    testCases = getTestCases()
    outputString = ""
    for testCase in testCases:
        executeTest(testCase)
        if testCase.testPassed:
            outputString += '<p style = "color:green">'
            outputString += "Test case "+testCase.id+" passed!"
            outputString += '</p>'
        else:
            outputString += '<p style = "color:red">'
            outputString += "Test case "+testCase.id+" FAILED!"
            outputString += '</p>'
        outputString += "<ul>"
        outputString += "<li>\tInputs: " + str(testCase.inputValue) + "</li>"
        outputString += "<li>\tExpected Result: " + testCase.expectedResult + "</li>"
        outputString += "<li>\tActual Output: " + str(testCase.actualResult) + "</li>"
        outputString += "</ul>"
    htmlBody = generateHtml(outputString)
    writeHtmlFile(htmlBody)

            
main()
