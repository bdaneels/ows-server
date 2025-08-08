OWS server
==========
The purpose is to execute a python script, which compares 2 xlsx files, and generates an output. A web interface is provided, based on **NiceGUI**. The [OWS-server] (URL is http://ows.flw.uantwerpen.be) is only available inside the UA network, or via a VPN. This application runs on srv1 (srv1.flw.uantwerpen.be).

Requirements
------------
Python 3.10
NiceGUI 2.21.1
pandas 2.3.1

Configuration
-------------
**ows.ini.j2** is an ini configuration file, which will be converted to **ows.ini** via the Makefile. Path specific parameters and some others will be different based on where the service is running (**server** or **home**).