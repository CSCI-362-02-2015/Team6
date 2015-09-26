#!/usr/bin/python
 
import subprocess   
 
def main():
    #clear out temp folder
    subprocess.call("rm ../temp/*", shell=True)

main()
