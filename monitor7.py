from operator import attrgetter
from ryu.base import app_manager
from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.lib.packet import ethernet, arp, ipv4
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
from ryu.ofproto import ofproto_v1_3

from ryu.lib.packet import packet
from ryu.lib.packet import ether_types
from ryu.topology import event
from ryu.topology.api import get_switch, get_link
from ryu.ofproto import ether

import sys
import copy
import binascii
import difflib
import requests


class SimpleMonitor13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    #initial stage
    def __init__(self, *args, **kwargs):
        super(SimpleMonitor13, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.ac=0
        self.bc=0
        self.a_delete=0
        self.b_delete=0
        self.x=0
        self.y=0
        self.m=0
        self.n=0
        self.t=0
        #self.v=0
        self.finish=1
        self.sleep=2
        self.limitA=input('(clientA)Thanks for your register,please input how many data do you want to buy?')
        self.limitB=input('(clientB)Thanks for your register,please input how many data do you want to buy?')
        self.i=self.limitA
        self.j=self.limitB
        self.monitor_thread = hub.spawn(self._monitor)
        self.mac_to_port={}
        #self.u=1
        self.buy_messageA=''
        self.buy_messageB=''
        

    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    #Monitor whether there is client out of quota
    def _monitor(self):
        while self.finish==1:
            self.finish=0
            for dp in self.datapaths.values():
                self._request_stats(dp)
            
            #if self.v==1:
             #   print('abc')
              #  hub.sleep(10)
                
               # self.v=0
            #print('A')
            #hub.sleep(5)
            #print('B')
            
            #out of quota
            if self.limitA== '0':
                #self.v=1
                #self.sleep=60
                self.buy_messageA=input('Client A have gone over data limit, do you want to buy more data?(yes/no)')
                #self.sleep=5
                print('we now have ',self.finish)
                #choose to not buy
                if self.buy_messageA=='no':
                    self.logger.info('Thanks for A using our service, your account has closed')
                    self.limitA='a'
                    self.a_delete=1
                
                #choose to buy
                elif self.buy_messageA=='yes':
                    self.x=1
                    buy_amountA=input('How much quota do you want to buy?')
                    print('Thank you, we have added the limit for your account and below is your data info')
                    
                    
                    self.limitA=buy_amountA
                    self.i=int(self.i)+int(self.limitA)
                    #print(self.i)
                    print('Client A limit now is %d', self.limitA)
                    print("Client A total quota is %d",self.i)
                    #out_port1=2
                    #out_port2=1
                    out_port1=3
                    match = self.parser.OFPMatch(in_port=1)
                    actions = [self.parser.OFPActionOutput(out_port1, 0)]
                    self.add_flow(self.datapath, 1, match, actions)
                    print('success')
                    
            if self.limitB== '0':
                #self.v=1
                self.buy_messageB=input('Client B have gone over your data limit, do you want to buy some more data?(yes/no)')
                if self.buy_messageB=='no':
                    
                    self.logger.info('Thanks for B using our service, your account has closed')
                    self.limitB='b'
                    self.b_delete=1
                
                elif self.buy_messageB=='yes':
                    self.y=1
                    buy_amountB=input('How many data bits do you want to buy?')
                    print('thank you, we have add the limit for your account and below is your data info')
                    
                    
                    self.limitB=buy_amountB
                    self.j=int(self.j)+int(self.limitB)
                    print('Client B limit now is %d', self.limitB)
                    print("Client B total quota is %d",self.j)
                    #print(self.j)
                    #out_port1=2
                    #out_port2=1
                    out_port1=3
                    match = self.parser.OFPMatch(in_port=2)
                    actions = [self.parser.OFPActionOutput(out_port1, 0)]
                    self.add_flow(self.datapath, 1, match, actions)
                    print('success')
                    
            if self.limitA=='a'and self.limitB=="b":
                print('All services are done')
                break
            
            self.finish=1
            hub.sleep(self.sleep)
    #This decorator can monitor each time the new switch connect to the openflow controller and 
    #implement the following function
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        #in this function we are going to initialise the flow table for each switch based on its
        #type
        if self.t==0:
            msg = ev.msg
            datapath = msg.datapath
            self.datapath=datapath
            ofproto = datapath.ofproto
            self.ofproto = datapath.ofproto
            parser = datapath.ofproto_parser
            self.parser = datapath.ofproto_parser
        #self.logger.info('we are now in')
        #dpid = self.Dpid_Formalise(datapath.id)
	#add default flow entry that forward to controller with lowest priority and match everything
            #match = parser.OFPMatch()
            #actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
            #self.add_flow(datapath, 0, match, actions)
	#Then we add two example flow rules
        #ip1='10.0.0.1'
        #ip2='10.0.0.2'
        #mask='255.255.255.255'
        #out_port1=2
        #out_port2=1
        #if self.t==0:
        
            #Add flow for ClientA and ClientB
            out_port1=3
            out_port2=3
            match = parser.OFPMatch(in_port=1)
            actions = [parser.OFPActionOutput(out_port1, 0)]
            self.add_flow(datapath, 1, match, actions)
            match = parser.OFPMatch(in_port=2)
            actions = [parser.OFPActionOutput(out_port2, 0)]
            self.add_flow(datapath, 1, match, actions)
            #Add flow from h3 to h2 and h1
            ip="10.0.0.4"
            ip1="10.0.0.2"
            ip2="10.0.0.3"
            mask="255.255.255.255"
            out_port1=1
            out_port2=2
            match = parser.OFPMatch(eth_type=0x800,ipv4_dst=(ip1, mask))
            #match = parser.OFPMatch(ipv4_dst=(ip1, mask),eth_type=0x0800)
            #match = parser.OFPMatch(in_port=1)
            actions = [parser.OFPActionOutput(out_port1,1)]
            self.add_flow(datapath, 2, match, actions)
            match = parser.OFPMatch(eth_type=0x800,ipv4_dst=(ip2, mask))
            #match = parser.OFPMatch(ipv4_dst=(ip2, mask),eth_type=0x0800)
            #match = parser.OFPMatch(in_port=2)
            actions = [parser.OFPActionOutput(out_port2,1)]
            self.add_flow(datapath, 2, match, actions)
            print('Added successfully')
            self.t=1
	
        if self.buy_messageA=='yes':
            msg = ev.msg
            datapath = msg.datapath
            self.datapath=datapath
            ofproto = datapath.ofproto
            self.ofproto = datapath.ofproto
            parser = datapath.ofproto_parser
            self.parser = datapath.ofproto_parser
            out_port1=3
            out_port2=3
            match = parser.OFPMatch(in_port=1)
            actions = [parser.OFPActionOutput(out_port1, 0)]
            self.add_flow(datapath, 1, match, actions)
        elif self.buy_messageB=='yes':
            msg = ev.msg
            datapath = msg.datapath
            self.datapath=datapath
            ofproto = datapath.ofproto
            self.ofproto = datapath.ofproto
            parser = datapath.ofproto_parser
            self.parser = datapath.ofproto_parser
            out_port1=3
            out_port2=3
            match = parser.OFPMatch(in_port=2)
            actions = [parser.OFPActionOutput(out_port2, 0)]
            self.add_flow(datapath, 1, match, actions)

    #add the flow chart to the switch
    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        # construct flow_mod message and send it.
	#instruction is the action that are going to implement when match
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
	#modification of switch, define the flow entry that going to be added into switch
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instructions=inst)
	#send the flow entry to the switch datapath
        datapath.send_msg(mod)


    

    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        
        #if int(self.u)==1:
        #    print("success")
        #    self.send_flow_modC(ev.msg.datapath)
        #    self.send_flow_modD(ev.msg.datapath)
        #    self.u=0
            
        body = ev.msg.body
        #self.logger.info('datapath         '
        #                 'in-port  eth-dst           '
        #                 'out-port packets  bytes')
        #self.logger.info('---------------- '
        #                 '-------- ----------------- '
        #                 '-------- -------- --------')
        self.logger.info('datapath         '
                         'in-port '
                         'out-port packets  up bytes  down bytes')
        self.logger.info('--------------------------- '
                         '-------- --------- -------- '
                         '-------- -------- --------')
                         
                         
                         
        for stat in sorted([flow for flow in body if flow.priority == 1],
                           key=lambda flow: (flow.match['in_port'])):
            #Match the flow for h1               
            if stat.match['in_port']==1:
                
                
                print('Total available quota(bytes) %d',int(self.i))
                print('Upstream traffic(bytes) %d',int(stat.byte_count))
                #print(int(self.ac))
                #print(int(self.m))
                #if int(stat.byte_count+self.ac-self.i) < int(self.limitA):
                
                #Judge whether the downstram traffic out of quota
                if int(self.ac)<int(self.i):
                #if int(int(self.i)-int(stat.byte_count)-int(self.ac)) > 100:
                #if int(int(self.limitA)-int(stat.byte_count)-(int(self.ac)-int(self.m))) > 100:
                    self.logger.info('we have %016x %8x %8x %8d %8d %8d',
                                     ev.msg.datapath.id,
                                     stat.match['in_port'],
                                     stat.instructions[0].actions[0].port,
                                     stat.packet_count, stat.byte_count, self.ac)
                
                #If out of quota, delete corresponding flow
                else:
                    #if self.a_delete != 1:
                        
                        self.send_flow_modA(ev.msg.datapath)
                        print('Delete')
                        #self.call()
                        self.limitA='0'
            #Match the flow h2        
            if stat.match['in_port']==2:
                #if int(stat.byte_count+self.bc-self.j) < int(self.limitB):
                #if int(int(self.j)-int(stat.byte_count)-int(self.bc)) > 100:
                
                print('Total available quota(bytes) %d',int(self.j))
                print('Upstream traffic(bytes) %d',int(stat.byte_count))
                #Judge whether the downstram traffic out of quota
                if int(self.bc)<int(self.j):
                
                
                #print(int(self.limitB))
                #print(int(stat.byte_count))
                #print(int(self.bc))
                #print(int(self.n))
                #if int(int(self.limitB)-int(stat.byte_count)-(int(self.bc)-int(self.n))) > 100:
                    self.logger.info('we have %016x %8x %8x %8d %8d %8d',
                                     ev.msg.datapath.id,
                                     stat.match['in_port'],
                                     stat.instructions[0].actions[0].port,
                                     stat.packet_count, stat.byte_count, self.bc)
                                     
                #If out of quota, delete corresponding flow                     
                else:
                    #if self.b_delete != 1:
                        
                        self.send_flow_modB(ev.msg.datapath)
                        print('Delete')
                        #self.call()
                        self.limitB='0'
                        
        #Read the bytes of downstream for h1 and h2                    
        for stat in sorted([flow for flow in body if flow.priority == 2],
                          key=lambda flow: (flow.match['eth_type'])):
            if stat.match['ipv4_dst']=="10.0.0.2":
                
                self.ac=stat.byte_count
                if self.x==1:
                    self.m=self.ac
                    self.x=0
                
                
            else:
                self.bc=stat.byte_count
                if self.y ==1:
                    self.n=self.bc
                    self.y=0

    
    
    

    #delete the flow for h1 in the flow table whose priority is 1
    def send_flow_modA(self, datapath):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        #cookie = cookie_mask = 0
        #table_id = 0
        #idle_timeout = hard_timeout = 0
        priority = 1
        #buffer_id = ofp.OFP_NO_BUFFER
        match = ofp_parser.OFPMatch(in_port=1)
        #actions = [ofp_parser.OFPActionOutput(ofp.OFPP_NORMAL, 0)]
        #inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS,
        #                                         actions)]
        req = ofp_parser.OFPFlowMod(datapath, command=ofp.OFPFC_DELETE,
                                    out_port=ofp.OFPP_ANY, out_group=ofp.OFPG_ANY,
                                    priority=1,match=match)
        datapath.send_msg(req)
        
        
    #delete the flow for h2 in the flow table whose priority is 1    
    def send_flow_modB(self, datapath):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        #cookie = cookie_mask = 0
        #table_id = 0
        #idle_timeout = hard_timeout = 0
        priority = 1
        #buffer_id = ofp.OFP_NO_BUFFER
        match = ofp_parser.OFPMatch(in_port=2)
        #actions = [ofp_parser.OFPActionOutput(ofp.OFPP_NORMAL, 0)]
        #inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS,
        #                                         actions)]
        req = ofp_parser.OFPFlowMod(datapath, command=ofp.OFPFC_DELETE,
                                    out_port=ofp.OFPP_ANY, out_group=ofp.OFPG_ANY,
                                    priority=1,match=match)
        datapath.send_msg(req)
