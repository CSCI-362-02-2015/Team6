#!/usr/bin/python
 
from sys import platform as _platform
import subprocess   
import os.path
import sys
from importlib import import_module

'''
 This python script runs a series of test cases specified in text documents located
 in then TestCases directory of this project.  

 The main method at the bottom of this file shows the basic operations being performed
'''

#goes to the codebase_path.txt file located in the docs folder to find where to 
#look for the root directory of the codebase being tested, stores path in global variable
def getPathToTestCodebase():
    os.chdir("./docs/")
    codebasePathFile = open('codebase_path.txt')
    fileContents = codebasePathFile.read().split("\n")
    pathToCodebase = fileContents[0]
    codebasePathFile.close()
    os.chdir('..')
    return pathToCodebase

def getTestCases():
    os.chdir("./testCases/")
    allFiles = os.listdir(".")
    # files ending in ~ are temporary files, don't execute those test cases!
    testCases = [TestCase(fileName) for fileName in allFiles if ".txt" in fileName and fileName[-1] != '~']
    os.chdir("..")
    return testCases

def executeTest(testCase):
    moduleName = convertPathToImport(testCase.modulePath)
    #take out module name from path
    pathToCodebase = getPathToTestCodebase()
    pathToModule = pathToCodebase + "/".join(testCase.modulePath.split("/")[0:-1])
    sys.path.insert(0,pathToModule)
    module = import_module(moduleName)

    #Just gets method name itself, not parameters or other signature
    methodNameTrimmed =  testCase.methodName[0:testCase.methodName.find('(')]
    methodToTest = getattr(module, methodNameTrimmed)
    result = methodToTest(*testCase.inputValue)
    testCase.actualResult = result
    sys.path.pop(0)
    #actual test
    if str(result) == testCase.expectedResult:
        testCase.testPassed = True
    return testCase

def convertPathToImport(path):
    path = path.replace("/", ".")
    path = path.replace(".py","")
    return path.split(".")[-1]

#this is the TestCase object, give it the filename of a test case txt file, and it 
#creates an object containing all of the test case's details 
class TestCase:
    def __init__(self, fileName):
        file = open(fileName, 'r')
        fileContents = file.read().split("\n")
        self.id = fileContents[0]
        self.description = fileContents[1]
        self.modulePath = fileContents[2].strip()
        self.methodName = fileContents[3].strip()
        self.inputValue = fileContents[4].split('$,')
        #go through parameters and pluck out strings vs numbers
        for i in range(len(self.inputValue)):
            if('"' in self.inputValue[i]):
                self.inputValue[i] = self.inputValue[i][1:-1]
            else: #else it's a number
                self.inputValue[i] = eval(self.inputValue[i])
        self.expectedResult = fileContents[5]

        self.actualResult = ""
        self.testPassed = False

        file.close()
        
    
def clearTempFolder():
    #go back a directory, remove everyting from temp,
    #if nothing is in temp, the warning is suppressed by sending it to null
    subprocess.call("rm ../temp/* 2>/dev/null", shell=True)

#Takes a list of test case objects (test cases should have been executed already)
#and constructs the html results page
def generateHtml(testCases):
    html = "<html>"
    html += "<body>"
    html += "<h1>Test Results</h1>"
    #generate body
    html += '<table border = "1">'
    html += '<tr>'
    html += '<td>Test case number</td>'
    html += '<td>Status</td>'
    html += '<td>Method Being Tested</td>'
    html += '<td>Inputs</td>'
    html += '<td>Expected Result</td>'
    html += '<td>Actual Result</td>'
    html += '</tr>'
    for testCase in testCases:
        html += '<tr>'
        html += '<td>' + testCase.id +'</td>'
        result = ''
        if testCase.testPassed:
            result = '<p style = "color:green">'
            result += 'Passed!'
            result += '</p>'
        else:
            result = '<p style = "color:red">'
            result += 'Failed!'
            result += '</p>'
        html += '<td>' + result +'</td>'  
        html += '<td>'+ testCase.methodName+'</td>'
        html += '<td>'+ str(testCase.inputValue)+'</td>'
        html += '<td>'+ testCase.expectedResult+'</td>'
        html += '<td>'+ str(testCase.actualResult)+'</td>'
        html += '</tr>'
    html += '</table>'
    html += "</body>"
    return html + "</html>"

def writeHtmlFile(html):
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
    getPathToTestCodebase() #find where the user put the codebase to test
    testCases = getTestCases()
    testCases.sort(key= lambda x: eval(x.id)) #sort the test cases by id
    for testCase in testCases:
        executeTest(testCase)
    htmlBody = generateHtml(testCases)
    writeHtmlFile(htmlBody)
            
main()
