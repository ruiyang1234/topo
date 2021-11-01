from ncclient import manager

MGR=manager.connect(host='sandbox-iosxr-1.cisco.com',
		port=830,
		username='admin',
		password='C1sco12345',
		hostkey_verify=False,
		device_params={'name':'iosxr'})

output=MGR.get_config('running')
print(output)
save=open('xmlconfig.xml','w')
save.write(str(output))
save.close
MGR.close_session()
