from ryu.base import app_manager
from ryu.ofproto import ofproto_v1_3
from ryu.controller.handler import set_ev_cls
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller import ofp_event


class FlowRules(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(FlowRules, self).__init__(*args, **kwargs)
        self.k = int(input('please input k: '))
        self.mac_to_port = {}

    def Dpid_Formalise(self, x):
	#convert the 64-bit integer datapath id to hex decimal
        x = hex(x)
	#delete the first two bits '0x'
        x = x[2:]
        #make sure there is 6 bits so that we can use to identify switch tpye from dpid
        while len(x) != 6:
            x = '0' + x
        return x
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
        dpid = self.Dpid_Formalise(datapath.id)
	#add default flow entry that forward to controller with lowest priority and match everything
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

	#then we also going to initialise the route protocol to all types of switches
        # core sw
        if int(dpid[0])*16+int(dpid[1]) == self.k:
	    #for each core switch we are going to add k number of flow entry, each corresponding
	    #a port connection to each pod
            for c in range(self.k):
                ip = '10.%d.0.0' % c
                mask = '255.255.0.0'
		#output port number starts from 1
                out_port = c
		#when match the exact destination IP address we will forward to the corresponding
		#output
                match = parser.OFPMatch(ipv4_dst=(ip, mask), eth_type=0x0800)
                actions = [parser.OFPActionOutput(out_port, 0)]
                self.add_flow(datapath, 10, match, actions)

        # ag sw
	#if the switch number is greater or equal to k/2, then that switch is agg switch
        elif int(dpid[2])*16+int(dpid[3]) >= self.k/2: #
	    #go through each pod
            for p in range(self.k):
                # prefix
                for s in range(int(self.k/2)):
                    # prefix
                    if int(dpid[0])*16+int(dpid[1]) == p:
                        ip = '10.%d.%d.0' % (p, s)
                        mask = '255.255.255.0'
                        #out_port = int(s+self.k/2+1)
                        out_port=s
                        match = parser.OFPMatch(ipv4_dst=(ip, mask), eth_type=0x0800)
                        actions = [parser.OFPActionOutput(out_port, 0)]
                        self.add_flow(datapath, 10, match, actions)

                    # suffix
                    else:
                        ip = '0.0.0.%d' % (2+p)
                        mask = '0.0.0.255'
                        #out_port = s+1
                        out_port=(p-2+s)%int(self.k/2)+int(self.k/2)
                        match = parser.OFPMatch(ipv4_dst=(ip, mask), eth_type=0x0800)
                        actions = [parser.OFPActionOutput(out_port, 0)]
                        self.add_flow(datapath, 1, match, actions)

        # ed sw
        else:
            for p in range(self.k):
                for s in range(int(self.k / 2)):
                    for h in range(2, 2+int(self.k / 2)):
                        # prefix
                        if int(dpid[0])*16+int(dpid[1]) == p and int(dpid[2])*16+int(dpid[3]) == s:
                            ip = '10.%d.%d.%d' % (p, s, h)
                            out_port = h-2
                            match = parser.OFPMatch(ipv4_dst=ip, eth_type=0x0800)
                            actions = [parser.OFPActionOutput(out_port, 0)]
                            self.add_flow(datapath, 10, match, actions)

                        # suffix
                        else:
                            ip = '0.0.0.%d' % h
                            mask = '0.0.0.255'
                            out_port = (h-4+s)%int(self.k/2)+int(self.k/2)
                            match = parser.OFPMatch(ipv4_dst=(ip, mask), eth_type=0x0800)
                            actions = [parser.OFPActionOutput(out_port, 0)]
                            self.add_flow(datapath, 1, match, actions)
