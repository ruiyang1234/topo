from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3

class Flowprotocol(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Flowprotocol, self).__init__(*args, **kwargs)
        #Add a new data structure to store the host Mac. The category is dict (Dictionary)
        self.k = int(input('please input k: '))
        self.mac_to_port = {}

    def Datapath_id_Formalise(self, x):
        x = hex(x)
        x = x[2:]
        while len(x) != 6:
            x = '0' + x
        return x

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        # Get the of protocol and parser corresponding to the if version used by switch
        # Construct and send flow message 
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        # Defines the action to be performed when the packet satisfies match
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instructions=inst)
        # Defines the flow entry in switch
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPSwitchProtocol, CONFIG_DISPATCHER)
    def switch_Protocol_handler(self, ev):
        msg = ev.msg # Received a packet from switch that didn't know how to handle it
        datapath = msg.datapath   # Receive openflow switch instance
        ofproto = datapath.ofproto   # OF protocol version used by openflow switch
        parser = datapath.ofproto_parser   # Parser for processing of protocol
        dpid = self.Datapath_id_Formalise(datapath.id) # Datapath ID of switch (unique ID)
        match = parser.OFPMatch()   # Add an empty match which is a match rule that can match any packet
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        # Send all packets that you don't know how to handle to controller
        self.add_flow(datapath, 0, match, actions)
        # Set the table miss flowentry to switch and specify the priority as 0 (lowest)

        # core switch routing protocol
        # dpid = "00:%02d:%02d:%02d" % (self.k, j, i)?
        if int(dpid[0]+dpid[1]) == self.k:
            for c in range(self.k):
                ip = '10.%d.0.0' % c
                mask = '255.255.0.0'
                out_port = c+1
                match = parser.OFPMatch(ipv4_dst=(ip, mask), eth_type=0x0800)
                actions = [parser.OFPActionOutput(out_port, 0)]
                self.add_flow(datapath, 10, match, actions)

        # aggregation switch routing protocol
        # s in range(int(self.k / 2), self.k)
        # dpid = "00:%02d:%02d:01" % (p, s)?
        elif int(dpid[2]+dpid[3]) >= self.k/2:
            for p in range(self.k):
                # prefix
                for s in range(int(self.k/2)):
                    # prefix
                    if int(dpid[0]+dpid[1]) == p:
                        ip = '10.%d.%d.0' % (p, s)
                        mask = '255.255.255.0'
                        out_port = int(s+self.k/2+1)
                        match = parser.OFPMatch(ipv4_dst=(ip, mask), eth_type=0x0800)
                        actions = [parser.OFPActionOutput(out_port, 0)]
                        self.add_flow(datapath, 10, match, actions)

                    # suffix
                    else:
                        ip = '0.0.0.%d' % (2+s) #(2/k+s)?
                        mask = '0.0.0.255'
                        out_port = s+1
                        match = parser.OFPMatch(ipv4_dst=(ip, mask), eth_type=0x0800)
                        actions = [parser.OFPActionOutput(out_port, 0)]
                        self.add_flow(datapath, 1, match, actions)

        # edge switch routing protocol
        # s in range(int(self.k / 2)):
        # dpid = "00:%02d:%02d:01" % (p, s)?
        else:
            for p in range(self.k):
                for s in range(int(self.k / 2)):
                    for h in range(2, 2+int(self.k / 2)):
                        # prefix
                        if int(dpid[0]+dpid[1]) == p and int(dpid[2]+dpid[3]) == s:
                            ip = '10.%d.%d.%d' % (p, s, h)
                            out_port = int(h+self.k/2-1)
                            match = parser.OFPMatch(ipv4_dst=ip, eth_type=0x0800)
                            actions = [parser.OFPActionOutput(out_port, 0)]
                            self.add_flow(datapath, 10, match, actions)

                        # suffix
                        else:
                            ip = '0.0.0.%d' % h
                            mask = '0.0.0.255'
                            out_port = h-1
                            match = parser.OFPMatch(ipv4_dst=(ip, mask), eth_type=0x0800)
                            actions = [parser.OFPActionOutput(out_port, 0)]
                            self.add_flow(datapath, 1, match, actions)
