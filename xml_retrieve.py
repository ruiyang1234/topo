from ncclient import manager
import xml.etree.ElementTree as ET
#Using the ncclient manager method to connect to the Cisco router by the information it provided
MGR=manager.connect(host='sandbox-iosxr-1.cisco.com',
		port=830,
		username='admin',
		password='C1sco12345',
		hostkey_verify=False,
		device_params={'name':'iosxr'})
#manager get_config method to get the running configuration of the yang model 
output=MGR.get_config('running')
#save the configuration into the xml file
save=open('xmlconfig.xml','w')
save.write(str(output))
save.close
MGR.close_session()
