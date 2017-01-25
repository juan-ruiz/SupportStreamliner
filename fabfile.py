'''
Created on aug 10, 2015

@author: theNumberJuan
'''
from __future__ import with_statement
import os,sys,time
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.tasks import execute
import xml.etree.ElementTree as etree
from sre_parse import isname
 


 

def systemStatus():
    return 'SYSTEMSTAT'

def retrieveLogRightv(addr, user, password,name):
    env.host_string = user+'@'+addr
    env.user = user
    env.password= password
    localPath="logfolder_RTV_"+name
    os.mkdir(localPath)
    run("tar -zcvf /export/home/rightv/logtool_rightvadmin_"+name+".tar.gz /export/home/rightv/jboss/server/admin-RIGHTV/log")
    remotePath= "/export/home/rightv/logtool_rightvadmin_"+name+".tar.gz"
    get(remotePath, localPath)
    run("tar -zcvf /export/home/rightv/logtool_rightvrte_"+name+".tar.gz /export/home/rightv/jboss/server/rte-RIGHTV/log")
    remotePath= "/export/home/rightv/logtool_rightvrte_"+name+".tar.gz"
    get(remotePath, localPath)
    run("rm -rf /export/home/rightv/logtool_rightvrte_"+name+".tar.gz")
    run("rm -rf /export/home/rightv/logtool_rightvadmin_"+name+".tar.gz")
    
    
def retrieveLogCAS(addr, user, password, name):
    env.host_string = user+'@'+addr
    env.user = user
    env.password= password
    localPath="logfolder_CAS_"+name
    os.mkdir(localPath)
    casComponents=['bdd','cmsi', 'ecmg','emmi','gta']
    
    for component in casComponents:
        run("tar -zcvf /u/"+component+"/trace/TRACE_"+component+"_"+name+".trx.tar.gz /u/"+component+"/trace/TRACE.TRX")
        remotePath="/u/"+component+"/trace/TRACE_"+component+"_"+name+".trx.tar.gz"
        get(remotePath,localPath)
        run("rm -rf  /u/"+component+"/trace/TRACE_"+component+"_"+name+".trx.tar.gz")
        


def executeCommand(addr, user, password, name, command):
    env.host_string = user+'@'+addr
    env.user = user
    env.password= password
    run(command)
    
def loadHostList():
    hostsTree=etree.parse('HostData.xml')
    root = hostsTree.getroot()
    return root
    
def getCustomersList(hostsData):
    customersList = ''
    i = 0
    for child in hostsTreeRoot:
        i+=1
        customersList += str(i) + '-- ' + child.find("CustName").text + '\n'
        
    return customersList


def getCustomerEnvs(customer): 
    envList = ''
    i = 0
    for child in customer.findall('Environment'):
        i+=1
        envList += str(i) + '-- ' + child.find("EnvName").text + '\n'
        
    return envList


def getEnvApps(environment):
    appList = ''
    i=0
    for child in environment.findall('Application'):
        i+=1
        appList += str(i) + '-- ' + child.find("AppName").text + '\n'
        
    return appList
    

def getAppServers(app):
    serverList = ''
    i=0
    for child in app.findall('Server'):
        i+=1
        serverList += str(i) + '-- ' + child.find("Hostname").text + '\n'
        
    return serverList
    

def systemDiag(addr, user, password,name ,resultFile):
    env.host_string = user+'@'+addr
    env.user = user
    env.password= password
    print "Execution of the SysDiag Utility on host = "+env.host_string
    resultFile.write('System status for server  '+name+'  Executed with user/password =  '+user+'/'+password+'\n \n \n')
    run("echo '--------List of top 10 processes in regards to CPU consummation-------- \n' ")
    resultFile.write('--------List of top 10 processes in regards to CPU consummation-------- \n \n')
    diskSpace=run("ps aux --sort -%cpu | head -n  11")
    resultFile.write(diskSpace+'\n \n')
    run("echo '--------List top 10 Memory consummation processes--------' ")
    resultFile.write('--------List top 10 Memory consummation processes-------- \n \n')
    diskSpace=run("ps aux --sort -rss | head -n  11")
    resultFile.write(diskSpace+'\n \n')
    run("echo '--------Disk space--------' ")
    resultFile.write('--------Disk space-------- \n \n')
    diskSpace= run("df -h")
    resultFile.write(diskSpace)
    run("echo '----------END OF SYSTEM STATUS-----------'")
    resultFile.write('\n ----------END OF SYSTEM STATUS----------- \n \n \n \n \n')
    
         
         
         





hostsTreeRoot=loadHostList()
operationType = raw_input('Please select the kind of operation you would like to perform\n1-- get the system status\n2-- retrieve logs\n3-- Execute a linux command in several servers\n')
isNumber = None
try:
    operationType = int(operationType) 
    isNumber = True
except ValueError:
    isNumber = False


while(not (isNumber and (0<operationType<4))):
    operationType = raw_input('Please select the kind of operation you would like to perform\n1-- get the system status\n2-- retrieve logs\n3-- Execute a linux command in several servers\n')
    try:
        operationType = int(operationType) 
        isNumber = True
    except ValueError:
        isNumber = False


    
        
customerList = getCustomersList(hostsTreeRoot)
customer = raw_input('Please select the customer\n' + customerList)
isNumber = None
try:
    customer = int(customer) 
    isNumber = True
except ValueError:
    isNumber = False
    

while(not(isNumber and (0<customer<(len(hostsTreeRoot.findall('Customer'))+1)))):
    customer = raw_input('Please select the customer\n' + customerList)
    try:
        customer = int(customer)
        isNumber=True
    except ValueError:
        isNumber = False


customer -=1
environmentList = getCustomerEnvs(hostsTreeRoot[customer])
environment = raw_input('Please select the environment\n' + environmentList)
isNumber = None
try:
    environment = int(environment) 
    isNumber = True
except ValueError:
    isNumber = False
    

while(not(isNumber and (0<environment<(len(hostsTreeRoot[customer].findall('Environment'))+1)))):
    environment = raw_input('Please select the environment\n' + environmentList)
    try:
        environment = int(environment)
        isNumber=True
    except ValueError:
        isNumber = False

        
environment-=1


if operationType == 1:
    serverList = ''
    resultFile = open ('ResultFile.txt','w')
    for child in hostsTreeRoot[customer].findall('Environment')[environment].findall('Application'):
        serverList+=getAppServers(child)
    
    print 'You are executing SysDiag Utility for the following servers \n'+serverList
    
    for app in hostsTreeRoot[customer].findall('Environment')[environment].findall('Application'):
        for server in app.findall('Server'):
            execute(systemDiag,server.find('Hostname').text, server.find('UserName').text, server.find('Password').text, server.find('Name').text,resultFile)
            
    print '\n \n SysDiag Utility complete'
    
    
    
    
    
elif operationType == 2:
    print' \n \n LOG RETRIEVAL UTIL'
    
    applist=getEnvApps(hostsTreeRoot[customer].findall('Environment')[environment])
    application=raw_input('\n \n Please select the Application\n' + applist)
    isNumber = None
    try:
        application = int(application) 
        isNumber = True
    except ValueError:
        isNumber = False
    while(not(isNumber and (0<application<(len(hostsTreeRoot[customer].findall('Environment')[environment].findall('Application'))+1)))):
        application=raw_input('\n \n Please select the Application\n' + applist)
        try:
            application = int(application) 
            isNumber = True
        except ValueError:
            isNumber = False
    
    application-=1
    applicationName=hostsTreeRoot[customer].findall('Environment')[environment].findall('Application')[application].find('AppName')
    serverList=getAppServers(hostsTreeRoot[customer].findall('Environment')[environment].findall('Application')[application])
    print '\n \n The log retrieving utility is going to be executed for the following servers \n' +serverList
    if(applicationName.text=='RIGHTV'):
        for server in hostsTreeRoot[customer].findall('Environment')[environment].findall('Application')[application].findall('Server') :
            execute(retrieveLogRightv,server.find('Hostname').text, server.find('UserName').text, server.find('Password').text, server.find('Name').text)
    
    
    if(applicationName.text=='CAS'):
        for server in hostsTreeRoot[customer].findall('Environment')[environment].findall('Application')[application].findall('Server') :
            execute(retrieveLogCAS,server.find('Hostname').text, server.find('UserName').text, server.find('Password').text, server.find('Name').text)
   
    print '\n \n Log retrieve Utility complete'

    
    
elif operationType == 3:
    applist=getEnvApps(hostsTreeRoot[customer].findall('Environment')[environment])
    application=raw_input('Please select the Application\n' + applist)
    isNumber = None
    try:
        application = int(application) 
        isNumber = True
    except ValueError:
        isNumber = False
    while(not(isNumber and (0<application<(len(hostsTreeRoot[customer].findall('Environment')[environment].findall('Application'))+1)))):
        application=raw_input('Please select the Application\n' + applist)
        try:
            application = int(application) 
            isNumber = True
        except ValueError:
            isNumber = False
    
    application-=1
    applicationName=hostsTreeRoot[customer].findall('Environment')[environment].findall('Application')[application].find('AppName')
    serverList=getAppServers(hostsTreeRoot[customer].findall('Environment')[environment].findall('Application')[application])
    command = raw_input("Please enter the command you would like to run on all servers \n"+"Please note that the command will be executed using the User on the HostData.xml file, even if its the root User\n"+"May the force be with you.")
    print '\n \n'+'The following command \n \n'+command+'\n \n is going to be executed on the following servers \n' +serverList+'\n\n'
    for remaining in range(5, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("{:2d}".format(remaining)) 
        sys.stdout.flush()
        time.sleep(1)
    print '\n\n'
    for server in hostsTreeRoot[customer].findall('Environment')[environment].findall('Application')[application].findall('Server') :
        execute(executeCommand,server.find('Hostname').text, server.find('UserName').text, server.find('Password').text, server.find('Name').text,command)
    print 'Command execution utility complete'
    
    
#execute(SystemDiag)
