import argparse
import bz2
import socket
import struct

parser = argparse.ArgumentParser()
parser.add_argument('-n', dest = 'node_file', default = '', help = 'Please enter the file name of Nodes File')
parser.add_argument('-l', dest = 'link_file', default = '', help = 'Please enter the file name of Links File')
parser.add_argument('-a', dest = 'nodeas_file', default = '', help = 'Please enter the file name of Node-AS File')
parser.add_argument('-g', dest = 'geo_file', default = '', help = 'Please enter the file name of Node_Geolocation File')
args = parser.parse_args()


# ====================================================
# These variables are for testing the script, 
# should not be included in the actual solution
key_freq = {}
placeholder_set = set()
# ====================================================

# create dictionary
nodes = {}
MASK_3 = struct.unpack("!I", socket.inet_aton("224.0.0.0"))[0]
PREFIX_224 = MASK_3
PREFIX_0 = struct.unpack("!I", socket.inet_aton("0.0.0.0"))[0]


# ====================================================
# These functions are for testing the coreection of the script,
# this part should not be included in the actual solution
def count(key):
    """

    """
    if key not in key_freq:
        key_freq[key] = 1
    else:
        key_freq[key] += 1

# ====================================================

def node_lookup(nid):
    """
    To check whether nid is in the ndoes.
    If not, then create one in nodes.

    param: string, input node id
    """
    if nid not in nodes:
        node_id = nid.replace("N", "")
        nodes[nid] = {
            "id": node_id,
            "asn": "",
            "isp": [],
            "neighbor": set(),
            "location": {
                "continent": "",
                "country": "",
                "region": "",
                "city": ""
                }
        }
    return nodes[nid]

def placeholder_lookup(addr):
    """
    The function is to check whether the node is a placeholder or not

    param:
    addr: string, input IPv4 addresss

    """
    binary_addr = struct.unpack("!I", socket.inet_aton(addr))[0]

    if (binary_addr & MASK_3) != PREFIX_224 and (binary_addr & MASK_3) != PREFIX_0:    
        return False
    else:
        return True

# load nodes.bz2
with bz2.open(args.node_file, mode='r') as f:

    for line in f:
    
        # convert byte string to string
        line = line.decode() 

        # skip the comments or the length of line is zero
        if len(line) == 0 or line[0] == "#":
            continue

        value = line.strip(" \n") # remove tailing newline
        value = value.split(" ")
        value[1] = value[1].replace(":", "") # value[1] == nid
             
        # get isp and check whether the node is placeholder
        isp_list = []
        placeholder = False
        for isp in value[2:]:
            if len(isp) == 0:
                continue
            if placeholder_lookup(isp):
                placeholder = True
                # ====================================================
                # for testing
                placeholder_set.add(value[1])
                count("placeholder") 
                # ====================================================
                break
            isp_list.append(isp)

        # if the node the not placeholder, then process the node
        if not placeholder:
            node = node_lookup(value[1])
            node['isp'] = isp_list
            # ====================================================
            count("non-placeholder") # for testing
            # ====================================================

# load nodes.as.bz2
with bz2.open(args.nodeas_file, mode = 'r') as f:
    for line in f:
        line = line.decode()
        value = line.split(" ")

        # if the node is in nodes, assign AS number to each node
        if value[1] in nodes:
            nodes[value[1]]["asn"] = value[2]
        # ====================================================
        # testing
        elif value[1] in placeholder_set:
            count("placeholder_in_AS")
            print("Placeholder node:{} is in the AS file.".format(value[1]))

        # ====================================================
        
# load nodes.geo.bz2 file
with bz2.open(args.geo_file, 'r') as f:
    for line in f:
        line = line.decode()

        # skip over comments
        if len(line) == 0 or line[0] == "#":
            continue

        value = line.split(" ")
        value[1] = value[1].split("\t")
        value[1][0] = value[1][0].replace(":", "")

        # if the node is in nodes, assign geo info to each node
        if value[1][0] in nodes:
            node = nodes[value[1][0]]
            node["location"]["continent"] = value[1][1]
            node["location"]["country"] = value[1][2]
            node["location"]["region"] = value[1][3]
            node["location"]["city"] = value[1][4]
        # ====================================================
        # testing
        elif value[1][0] in placeholder_set:
            count("placeholder_in_geo")
            print("Placeholder node:{} is in the GEO file.".format(value[1][0]))
        # ====================================================  

# load links.bz2 file
with bz2.open(args.link_file, 'r') as f:
    for line in f:
        line = line.decode()

        # skip over comments of the length of line is zero
        if len(line) == 0 or line[0] == "#":
            continue

        value = line.strip(" \n")
        value = value.split(" ")
    
        neighbors = []
        for nid in value[3:]:
            neighbors.append(nid.split(":")[0])

        for nid in neighbors:
            if nid in nodes:
                for n in neighbors:
                
                    #skip its neighbors are the node itself 
                    if nid == n and n not in nodes:
                        continue

                    nodes[nid]["neighbor"].add(n)
                    nodes[n]["neighbor"].add(nid)
        # ====================================================
        # testing
        count("link")

        # ====================================================

# ====================================================
# testing
print("Checking whether every node has at least one neighbor...")

for node in nodes:
    if len(node["neighbor"]) == 0:
        print("Node {} has no any neighbor node.".format(node))
        count("no_neighbor")

# ====================================================

#print(nodes)