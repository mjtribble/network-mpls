from network_3 import Router, Host
from link_3 import Link, LinkLayer
import threading
import time
import sys
from copy import deepcopy

# configuration parameters
router_queue_size = 0  # 0 means unlimited
simulation_time = 30  # give the network sufficient time to execute transfers

if __name__ == '__main__':
    object_L = []  # keeps track of objects, so we can kill their threads at the end

    # create network hosts
    host_1 = Host('H1')
    object_L.append(host_1)
    host_2 = Host('H2')
    object_L.append(host_2)
    host_3 = Host('H3')
    object_L.append(host_3)

    # create routers and routing tables for connected clients (subnets)

    # table used to encapsulate network packets into MPLS frames
    # checks the network packet destination (key)
    # determines which router need sot encapsulate the packet as MPLS
    # {destination: first hop router}
    encap_tbl_D = {'H3': 'RA',
                   'H2': 'RD',
                   'H1': 'RD'}

    # tables used to forward MPLS frames
    # { in-label: [ out-label, destination, out-interface, in-interface ]
    frwd_tbl_DA = {'01': ['01', 'H1', 0, 1],
                   '03': ['03', 'H3', 1, 1],
                   '11': ['11', 'H1', 0, 1],
                   '33': ['33', 'H3', 1, 1]}

    frwd_tbl_DB = {'01': ['01', 'RA', 0, 1],
                   '03': ['03', 'RD', 1, 0],
                   '11': ['11', 'RA', 0, 1],
                   '33': ['33', 'RD', 1, 0]
                   }

    frwd_tbl_DC = {'01': ['01', 'RA', 0, 1],
                   '03': ['03', 'RD', 1, 0],
                   '11': ['11', 'RA', 0, 1],
                   '33': ['33', 'RD', 1, 0]
                   }

    frwd_tbl_DD = {'01': ['01', 'H1', 0, 1],
                   '03': ['03', 'H3', 1, 1],
                   '11': ['11', 'H1', 0, 1],
                   '33': ['33', 'H3', 1, 1]
                   }

    # table used to decapsulate network packets from MPLS frames
    # {destination: last hop router}
    decap_tbl_D = {'H1': 'RA',
                   'H2': 'RA',
                   'H3': 'RD'}

    router_a = Router(name='RA',
                      intf_capacity_L=[500, 500],
                      encap_tbl_D=encap_tbl_D,
                      frwd_tbl_D=frwd_tbl_DA,
                      decap_tbl_D=decap_tbl_D,
                      max_queue_size=router_queue_size)
    object_L.append(router_a)

    router_b = Router(name='RB',
                      intf_capacity_L=[500, 500],
                      encap_tbl_D=encap_tbl_D,
                      frwd_tbl_D=frwd_tbl_DB,
                      decap_tbl_D=decap_tbl_D,
                      max_queue_size=router_queue_size)
    object_L.append(router_b)

    router_c = Router(name='RC',
                      intf_capacity_L=[500, 500],
                      encap_tbl_D=encap_tbl_D,
                      frwd_tbl_D=frwd_tbl_DC,
                      decap_tbl_D=decap_tbl_D,
                      max_queue_size=router_queue_size)
    object_L.append(router_c)

    router_d = Router(name='RD',
                      intf_capacity_L=[500, 100],
                      encap_tbl_D=encap_tbl_D,
                      frwd_tbl_D=frwd_tbl_DD,
                      decap_tbl_D=decap_tbl_D,
                      max_queue_size=router_queue_size)
    object_L.append(router_d)

    # create a Link Layer to keep track of links between network nodes
    link_layer = LinkLayer()
    object_L.append(link_layer)

    # add all the links - need to reflect the connectivity in cost_D tables above
    link_layer.add_link(Link(host_1, 0, router_a, 0))
    link_layer.add_link(Link(router_a, 1, router_b, 0))
    link_layer.add_link(Link(router_b, 1, router_d, 0))
    link_layer.add_link(Link(router_d, 1, host_3, 0))

    link_layer.add_link(Link(host_2, 0, router_a, 0))
    link_layer.add_link(Link(router_a, 1, router_c, 0))
    link_layer.add_link(Link(router_c, 1, router_d, 0))
    link_layer.add_link(Link(router_d, 1, host_3, 0))

    # start all the objects
    thread_L = []
    for obj in object_L:
        thread_L.append(threading.Thread(name=obj.__str__(), target=obj.run))

    for t in thread_L:
        t.start()

    # create some send events
    for i in range(5):
        priority = i % 2
        host_1.udt_send('H3', 'MESSAGE_%d_FROM_H1' % i, priority)
    for i in range(2):
        priority = i % 2
        host_2.udt_send('H3', 'MESSAGE_%d_FROM_H2' % i, priority)

    # host_1.udt_send('H3', 'MESSAGE_%d_FROM_H1' % 0, 0)
    # host_1.udt_send('H3', 'MESSAGE_%d_FROM_H1' % 1, 1)

    # give the network sufficient time to transfer all packets before quitting
    time.sleep(simulation_time)

    # join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()

    print("All simulation threads joined")
