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

ows_server service
==================
install
-------
the file **ows_server.service** is a systemd startup file, it can be installed with the Makefile command ::

    	 #sudo su
	 -> type password
	 #make install

This can only be done as root!

startup
-------
To start the service, you just need to use the classical **service** commands, e.g ::

      #service ows-server start
      or
      #service ows-server stop
      or
      #service ows-server restart
      or, to check if eveything is running and ok
      service ows-server status
      ● ows-server.service - OWS Web Application Server
      	Loaded: loaded (/etc/systemd/system/ows-server.service; disabled; vendor preset: enabled)
     	Active: active (running) since Thu 2025-08-07 16:54:32 CEST; 3 days ago
   	Main PID: 13226 (python3)
      	Tasks: 8 (limit: 152995)
     	Memory: 79.1M
     	CGroup: /system.slice/ows-server.service
                └─13226 /usr/bin/python3 ows_serverv2.py

The generated output can also show up when you ask the **status** of the service ::

    Aug 07 16:55:10 ows-server python3[13226]: 2025-08-07 14:55:10,250 - ows-server - DEBUG - Standard Output: csvA -> /home/ubuntu/ows-server//uploads/simple.csv
    Aug 07 16:55:10 ows-server python3[13226]: csvB -> /home/ubuntu/ows-server//uploads/simple2.csv
    Aug 07 16:55:10 ows-server python3[13226]: csvM -> /home/ubuntu/ows-server//out/Brecht_20250807145505.csv
    Aug 07 16:55:10 ows-server python3[13226]: merging 2 csv files
    Aug 07 16:55:10 ows-server python3[13226]: ['1', 'simpel test', '145']
    Aug 07 16:55:10 ows-server python3[13226]: ['2', 'simple hallo', '909']
    Aug 07 16:55:10 ows-server python3[13226]: ['11', 'simpel 2 test', '1450']
    Aug 07 16:55:10 ows-server python3[13226]: ['12', 'simple 2 hallo', '7895']
    Aug 07 16:55:10 ows-server python3[13226]: 2025-08-07 14:55:10,251 - ows-server - DEBUG - Standard Error:
    Aug 07 16:55:10 ows-server python3[13226]: 2025-08-07 14:55:10,257 - ows-server - DEBUG - nothing to remove	
	

requirements of python script to be executed
============================================
The name of the script is specified in the section **[scripts]** in the ows.ini file. The script should provide 3 positional parameters, where the first two are the files to be compared , and the last is the name of the output file. Have a look at the test-scripts provided in de **tests** subdirectory, like **merge_csvs_pandas.py** ::

    >python merge_csvs_pandas_args.py
    usage: merge_csvs_pandas_args.py [-h] csvA csvB csvM
    merge_csvs_pandas_args.py: error: the following arguments are required: csvA, csvB, csvM

So csvA and csvB are the 2 files to be compared, csvM can is the merged csv file (output file). You can also provide an extra parameter **--verbose**, which can log extra debugging information.