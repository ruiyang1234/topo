import json
import xmltodict
import xml.etree.ElementTree as ET

with open('xmlconfig.xml',encoding='utf-8') as f:
	xml=f.read()
	root=ET.fromstring(xml)
	interface_config=root[0].find('doc:interface-configurations',namespaces={'doc':'http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg'})
	#a=ET.tostring(interface_config,encoding='utf8',method='xml')
	#interface_config=root.find('interface-configurations')
	a=ET.tostring(interface_config,encoding='utf8')
	namespaces={'http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg':None,
	'http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-io-cfg':None,
	'http://cisco.com/ns/yang/Cisco-IOS-XR-infra-statsd-cfg':None,
	'http://cisco.com/ns/yang/Cisco-IOS-XR-tunnel-gre-cfg':None,
	'http://cisco.com/ns/yang/Cisco-IOS-XR-ipv6-ma-cfg':None}
	convertjson=xmltodict.parse(a,encoding='utf-8',process_namespaces=True,namespaces=namespaces)
	#convertjson=xmltodict.parse(xml,encoding='utf-8')
	jsonstr=json.dumps(convertjson,indent=1)
with open('json1.json','w',encoding='utf-8') as f:
	f.write(jsonstr)
