# coding:utf-8
import multiprocessing
import rpc
from database import NodeDB, TransactionDB, BlockChainDB
from lib.common import cprint
import json
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
    
if __name__=='__main__':

    msg_send_Header = {"method": "sendHeader","data": {"block_hash": "0000be5b53f2dc1a836d75e7a868bf9ee576d57891855b521eaabfa876f8a606","block_header": "000000010000000008e647742775a230787d66fdf92c46a48c896bfbc85cdc8acc67e87d0000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000002321","block_height": 10 }}
    msg_get_Blocks = {"method":"get_Blocks","data":{"hash_count":1,"hash_begin":"0000a1aff3716cb8925b18d2f6bb38d3f168d682c1218a70b503b5c600474e28","hash_stop":"00000d08eafd831c138e4eb4c06ee5c3dc63aa40564c5a4322dcb824622754cf"}}
    msg_get_BlockCount = {"method":"getBlockCount"}
    msg_get_BlockHash = {"method": "getBlockHash","data": {"block_height": 10}}
    msg_get_BlockHeader = {"method": "getBlockHeader","data": {"block_hash": "0000be5b53f2dc1a836d75e7a868bf9ee576d57891855b521eaabfa876f8a606"}}
    #send_Header test
    #response = rpc.BroadCast().router(msg_send_Header)
    #print(json.dumps(response, indent = 4, sort_keys=True))
    
    #get_Blocks test
    response = rpc.BroadCast().router(msg_get_Blocks)
    print(json.dumps(response, indent = 4, sort_keys=True))
    
    #get_BlockCount test
    #response = rpc.BroadCast().router(msg_get_BlockCount)
    #print(json.dumps(response, indent = 4, sort_keys=True))
    
    #get_BlockHash test
    #response = rpc.BroadCast().router(msg_get_BlockHash)
    #print(json.dumps(response, indent = 4, sort_keys=True))
    
    #getBlockHeader test
    #response = rpc.BroadCast().router(msg_get_BlockHeader)
    #print(json.dumps(response, indent = 4, sort_keys=True))
