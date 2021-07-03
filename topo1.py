

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
#from mininet.util import irange.dumpNodeConnections
from mininet.log import setLogLevel

class MyTopo(Topo):
	def __init__(self):
		#initialise topology
		Topo.__init__(self)
		crSw=[]
		agSw=[]
		edSw=[]
		ho=[]
		self.num=0
		self.k=int(input('please input the even k value:'))
		k=self.k
		if k>=4 and k%2==0:
			#add (k/2)^2 number of core switches
			for i in range(int(self.k/2)):
				for j in range(int(self.k/2)):
					sw=self.addSwitch('crSw{}'.format(i*k/2+j),dpid='0000000000{}{}{}'.format(str(k).zfill(2),str(i).zfill(2),str(j).zfill(2)))
					crSw.append(sw)
			#add aggregation,edge switches and hosts
			self.num=1
			for i in range(self.k):
				for j in range(int(self.k/2)):
					
					#add aggregation switches
					sw=self.addSwitch('agSw{}{}'.format(i,j),dpid='0000000000{}{}01'.format(str(i).zfill(2),str(self.k+j).zfill(2)))
					agSw.append(sw)
					#add edge switches
					sw1=self.addSwitch('edSw{}{}'.format(i,j),dpid='0000000000{}{}01'.format(str(i).zfill(2),str(j).zfill(2)))
					edSw.append(sw1)
					#add hosts
					for l in range(int(self.k/2)):
						self.num+=1
						b=int(i*j*k/2+l)
						host=self.addHost('h{}'.format(int((i*k/2)*k/2+j*k/2+l)),ip='10.{}.{}.{}'.format(str(i).zfill(2),str(j).zfill(2),str(self.num).zfill(2)))
						#host=Host('h{}'.format(i+j+1))
						#host.setIP('10.{}.{}.{}'.format(str(i).zfill(2),str(j).zfill(2),str(self.num).zfill(2)))
						ho.append(host)
						#self.get(ho[-1]).setIP('10.{}.{}.{}'.format(str(i).zfill(2),str(j).zfill(2),str(self.num).zfill(2)))
			#then we add links to the system
			#first link the core and aggregation sw
			a=int(pow(k/2,2))
			for i in range(a):
				for j in range(k):
					self.addLink(crSw[i],agSw[int(k*j/2+i//(k/2))])
			#link the aggre and edge sw
			for i in range(k):
				for j in range(int(k/2)):
					for l in range(int(k/2)):
						self.addLink(agSw[int(i*k/2+j)],edSw[int(i*k/2+l)])
			#link the edge sw and the hosts
			for i in range(int(k*k/2)):
				for j in range(int(k/2)):
					self.addLink(edSw[i],ho[int(i*k/2+j)])
		else:
			print('please input an vaild number!')

topos = {'mytopo':(lambda:MyTopo())}










		
