# coding:utf-8
import multiprocessing
import rpc
from database import NodeDB, TransactionDB, BlockChainDB
from lib.common import cprint

def start_node(hostport='0.0.0.0:3009'):
    init_node()
    cprint('INFO', 'Node initialize success.')
    try:
        if hostport.find('.') != -1:
            host,port = hostport.split(':')
        else:
            host = '0.0.0.0'
            port = hostport
    except Exception:
        cprint('ERROR','params must be {port} or {host}:{port} , ps: 3009 or 0.0.0.0:3009')
    p = multiprocessing.Process(target=rpc.start_server,args=(host,int(port)))
    p.start()
    cprint('INFO','Node start success. Listen at %s.' % (hostport,))

def init_node():
    """
    Download blockchain from node compare with local database and select the longest blockchain.
    """
    all_node_blockchains = rpc.BroadCast().get_blockchain()
    all_node_txs = rpc.BroadCast().get_transactions()
    bcdb = BlockChainDB()
    txdb = TransactionDB()
    blockchain = bcdb.find_all()
    transactions = txdb.find_all()
    # If there is a blochain downloaded longer than local database then relace local's.
    for bc in all_node_blockchains:
        if len(bc) > len(blockchain):
            bcdb.clear()
            bcdb.write(bc)
    for txs in all_node_txs:
        if len(txs) > len(transactions):
            txdb.clear()
            txdb.write(txs)
    
def get_nodes():
    return NodeDB().find_all()

def add_node(address):
    ndb = NodeDB()
    all_nodes = ndb.find_all()
    if address.find('http') != 0:
        address = 'http://127.0.0.1:' + address
    all_nodes.append(address)
    ndb.clear()
    ndb.write(rm_dup(all_nodes))
    return address

def check_node(address):
    pass

def rm_dup(nodes):
    return sorted(set(nodes)) 
    
#if __name__=='__main__':
#    start_node()
if __name__=='__main__':
    #start_node()
    dic = {"method":"getBlocks",
           "data":{
             "hash_count":1,
             "hash_begin":"0000a1aff3716cb8925b18d2f6bb38d3f168d682c1218a70b503b5c600474e28",
             "hash_stop":"00000d08eafd831c138e4eb4c06ee5c3dc63aa40564c5a4322dcb824622754cf"
           }
          }
    
    response = rpc.BroadCast().get_blockchain()
    print(response)
    response = rpc.BroadCast().getBlocks(dic)
    print(response)
    #print(len(all_node_blockchains[0]))
    #for idx,block in enumerate(all_node_blockchains[0]):
    #    print(idx,':',block)
#if __name__=="__main__":
#    arpc = RpcServer()
#    print(arpc)
