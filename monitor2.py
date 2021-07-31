from operator import attrgetter
from ryu.base import app_manager
from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
from ryu.ofproto import ofproto_v1_3

class SimpleMonitor13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    def __init__(self, *args, **kwargs):
        super(SimpleMonitor13, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)
        self.mac_to_port={}

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

    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(5)

    #this decorator can monitor each time the new switch connect to the openflow controller and 
    #implement the following function
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        #in this function we are going to initialise the flow table for each switch based on its
        #type
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        #self.logger.info('we are now in')
        #dpid = self.Dpid_Formalise(datapath.id)
	#add default flow entry that forward to controller with lowest priority and match everything
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)
	#Then we add two example flow rules
        ip1='10.0.0.1'
        ip2='10.0.0.2'
        mask='255.255.255.255'
        out_port1=2
        out_port2=1
        match = parser.OFPMatch(in_port=1,ipv4_dst=(ip2, mask),ipv4_src=(ip1, mask), eth_type=0x0800)
        actions = [parser.OFPActionOutput(out_port2, 0)]
        self.add_flow(datapath, 1, match, actions)
        match = parser.OFPMatch(in_port=2,ipv4_dst=(ip1, mask),ipv4_src=(ip2, mask), eth_type=0x0800)
        actions = [parser.OFPActionOutput(out_port1, 0)]
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
        
        body = ev.msg.body
        #self.logger.info('datapath         '
        #                 'in-port  eth-dst           '
        #                 'out-port packets  bytes')
        #self.logger.info('---------------- '
        #                 '-------- ----------------- '
        #                 '-------- -------- --------')
        self.logger.info('datapath         '
                         'in-port  ipv4-src  ipv4-dst  '
                         'out-port packets  bytes')
        self.logger.info('---------------- '
                         '-------- --------- -------- '
                         '-------- -------- --------')
        for stat in sorted([flow for flow in body if flow.priority == 1],
                           key=lambda flow: (flow.match['in_port'],
                                             flow.match['ipv4_src'])):
            if stat.byte_count < 1000:
            
                self.logger.info('we have %016x %8x %s %s %8x %8d %8d',
                                 ev.msg.datapath.id,
                                 stat.match['in_port'], stat.match['ipv4_src'], stat.match['ipv4_dst'],
                                 stat.instructions[0].actions[0].port,
                                 stat.packet_count, stat.byte_count)
            else:
                self.send_flow_mod(ev.msg.datapath)
                
                #self.logger.info('we are in %016x %8x %17s %8x %8d %8d',
                #                 ev.msg.datapath.id,
                #                 stat.match['in_port'], stat.match['eth_dst'],
                #                 stat.instructions[0].actions[0].port,
                #                 stat.packet_count, stat.byte_count)
                
                self.logger.info('%016x %8x %s %s %8x %8d %8d',
                                 ev.msg.datapath.id,
                                 stat.match['in_port'], stat.match['ipv4_src'], stat.match['ipv4_dst'],
                                 stat.instructions[0].actions[0].port,
                                 stat.packet_count, stat.byte_count)
                
            
    

    def send_flow_mod(self, datapath):
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

    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.info('datapath         port     '
                         'rx-pkts  rx-bytes rx-error '
                         'tx-pkts  tx-bytes tx-error')
        self.logger.info('---------------- -------- '
                         '-------- -------- -------- '
                         '-------- -------- --------')
        for stat in sorted(body, key=attrgetter('port_no')):
            self.logger.info('%016x %8x %8d %8d %8d %8d %8d %8d',
                             ev.msg.datapath.id, stat.port_no,
                             stat.rx_packets, stat.rx_bytes, stat.rx_errors,
                             stat.tx_packets, stat.tx_bytes, stat.tx_errors)
