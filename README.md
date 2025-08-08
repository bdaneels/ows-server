OWS server
==========
The purpose is to execute a python script, which compares 2 xlsx files, and generates an output. A web interface is provided, based on **NiceGUI**. The OWS-server URL is http://ows.flw.uantwerpen.be and is only available inside the UA network, or via a VPN. This application runs on srv1 (srv1.flw.uantwerpen.be).

Requirements
============
 * Python 3.10
 * NiceGUI 2.21.1
 * pandas 2.3.1

Configuration
=============
**ows.ini.j2** is an ini configuration file, which will be converted to **ows.ini** via a Makefile. Path specific parameters and some others will be different based on where the service is running (**server** or **home**). We will explain each section herafter.
paths
-----
specify different paths for the application, **home** is where the application resides (and will be executed). A Makefile will automatically fill this in. **upload** is where the uploaded files will end up, **script** is the directory where different scripts or script directories will remain. **out** is the map where the output of the script will be generated.

general
-------
**hostname** is the name of the server where the application will run. **index_page** contains text (markdown) that will appear on the home page of the application. The **header_label** appears in the left side of the header. **users** holds all first names of the users that will use the application, and these will appear in a dropdown button on the homepage. The **storage secret** is needed to be able to work with storage in NiceGUI. **download_lbl** and **delete_lbl* give the buttons on the download page a name (keep it short!).

uploader
--------
This is the file uploader used by **NiceGUI**. You can soecify the **max_file_size** allowed for uploads (e.g. 1 * MB or 10 * MB, or KB or  GB). The value will be safely evaluated at runtime. You can also specify a label that appears at the top of the file uploader , **label**

scripts
-------


comment
-------

