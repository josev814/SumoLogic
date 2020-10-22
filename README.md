# SumoLogic
An application built with python to allow defining logs and Sumologic endpoints to transfer the logs to

#Installing
python3 setup.py install

#configuration
vim /etc/sumologic/config.d/config


#Running
/usr/local/bin/sumologic-daemon restart

or

This runs in foreground

/usr/local/bin/sumologic.py -f

#Stopping
/usr/local/bin/sumologic-daemon stop

#Status
/usr/local/bin/sumologic-daemon status