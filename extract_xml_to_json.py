import json
import xmltodict
import xml.etree.ElementTree as ET

#open the xml file encoded in utf-8 format
with open('xmlconfig.xml',encoding='utf-8') as f:
	xml=f.read()
	#using fromstring to format the xml to element tree form
	root=ET.fromstring(xml)
	#find the current routing table information from router-static element along with its namespace
	route_table=root[0].find('doc:router-static',namespaces={'doc':'http://cisco.com/ns/yang/Cisco-IOS-XR-ip-static-cfg'})
	#convert the routing table to xml format
	a1=ET.tostring(route_table,encoding='utf8')
	#set the ns to filter out the namespace in the xml file
	namespaces1={'http://cisco.com/ns/yang/Cisco-IOS-XR-ip-static-cfg':None}
	#parse the xml file and convert it to dictionary
	convertjson3=xmltodict.parse(a1,encoding='utf-8',process_namespaces=True,namespaces=namespaces1)
	#using dumps method to convert the python dictionary to json format
	routing_table_jsonstr=json.dumps(convertjson3,indent=1)

	#extraction of the interface configuration is same as the extracting routing table
	interface_config=root[0].find('doc:interface-configurations',namespaces={'doc':'http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg'})
	a2=ET.tostring(interface_config,encoding='utf8')
	#filter out all the namespaces show up in the xml
	namespaces2={'http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg':None,
	'http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-io-cfg':None,
	'http://cisco.com/ns/yang/Cisco-IOS-XR-infra-statsd-cfg':None,
	'http://cisco.com/ns/yang/Cisco-IOS-XR-tunnel-gre-cfg':None,
	'http://cisco.com/ns/yang/Cisco-IOS-XR-ipv6-ma-cfg':None}
	convertjson2=xmltodict.parse(a2,encoding='utf-8',process_namespaces=True,namespaces=namespaces2)
	interface_jsonstr=json.dumps(convertjson2,indent=1)

#write the configuration in json file
with open('jsonfile.json','w',encoding='utf-8') as f:
	#find out all the yang model in the xml and write them in json
	for yang in root[0]:
		#using tag to get the name as well as the namespaces
		yang_model=str(yang.tag)
		#using split to saperate the namespace and name 
		b=yang_model.replace('{',' ').replace('}',' ').split()
		#format the yang model
		true_yang_model='Yang model: '+b[0]
		jsonstr1=json.dumps(true_yang_model,indent=1)
		f.write(jsonstr1+"\n")
	#After the yang model write the interface configuration 
	f.write(interface_jsonstr+"\n")
	#finally write the json for routing table
	f.write(routing_table_jsonstr)
