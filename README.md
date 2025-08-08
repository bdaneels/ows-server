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
the keys are short (without any spaces,special characters in it). The values refer to the path of the script. You can specify the script path as a variable ( ${paths:script} ), with is under the secion paths. If the script is in a subdirectory of the scripts path, just add this subdirectory to the path.

comment
-------
this comment applies to the scripts in the above paragraph. It will appear in space above the button, associated with the script. It is meant as an small explanation for the script.The text can have markdown markup.

installation
============
Depending on where you are running the application (server or home), run the Makefile like this::

	 > make home
	 or
	 > make server

This will create the directories needed (uploads, script andout), create a correct **ows.ini** file. and generate a startup script, which is handy for debugging.
The file **ows-server.service** should be placed under **/etc/systemd/system**, so that the **ows-server** can be started, stopped and restarted if needed (root user)::

    	 #service ows_server start
	 or
	 #service ows_server stop
	 or
	 #service ows_server restart
	 or
	 #service ows_server status
