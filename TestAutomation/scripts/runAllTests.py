#!/usr/bin/python
 
import subprocess   
import os.path
import sys
from importlib import import_module

def getTestCases():
    os.chdir("..")
    folder = "testCases/"
    allFiles = os.listdir(folder)
    return [fileName for fileName in allFiles if ".txt" in fileName]
     
def executeTest(testCase):
    importStatement = convertPathToImport(testCase.modulePath)
    sys.path.append(testCase.modulePath)
    module = __import__(importStatement, fromlist=[testCase.methodName])
    methodToTest = getattr(module, testCase.methodName.replace("()",""))
    result = methodToTest(testCase.inputValue)
    
    #actual test
    if result == testCase.expectedResult:
        return True
    return False

def convertPathToImport(path):
    path = path.replace("/", ".")
    path = path.replace(".py","")
    return path.split(".")[-1]

class TestCase:
    def __init__(self, fileName):
        os.chdir("testCases")
        file = open(fileName, 'r')
        fileContents = file.read().split("\n")
        self.id = fileContents[0].strip()
        self.description = fileContents[1].strip()
        self.modulePath = fileContents[2].strip()
        self.methodName = fileContents[3].strip()
        self.inputValue = fileContents[4].strip()
        self.expectedResult = fileContents[5].strip()

        file.close()
        
        
def clearTempFolder():
    #go back a directory, remove everyting from temp,
    #if nothing is in temp, the warning is suppressed by sending it to null
    subprocess.call("rm ../temp/* 2>/dev/null", shell=True)

def main():
    clearTempFolder()
    testCaseNames = getTestCases()
    for testCaseName in testCaseNames:
        testCase = TestCase(testCaseName)
        if executeTest(testCase):
            print "Test case "+testCase.id+" passed!"
        else:
            print "Test case "+testCase.id+" FAILED!"
            
main()
