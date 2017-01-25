#SupportStreamliner


This is a nifty little tool build in order to help the team avoid performing repetitive tasks (i.e. executing the same command in 10+ servers), it is built using python and fabric,

This makes use of an xml file that contains the connection information for the servers, due to security reasons i am not uploading it,

##Build instructions

A build to an exe file is possible, and advised, so the destination machine won't need to install fabric among other dependencies, the build script is uploaded on this repo under the name setup.py, it uses py2exe.
