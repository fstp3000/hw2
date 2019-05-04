# coding:utf-8
from xmlrpc.server import SimpleXMLRPCServer  
from xmlrpc.client import ServerProxy
from node import get_nodes, add_node
from database import BlockChainDB, UnTransactionDB, TransactionDB
from lib.common import cprint
#from block import Block
server = None

PORT = 8301

class RpcServer():

    def __init__(self,server):
        self.server = server

    def ping(self):
        return True
    
    def get_blockchain(self):
        bcdb = BlockChainDB()
        return bcdb.find_all()

    def new_block(self,block):
        cprint('RPC', block)
        BlockChainDB().insert(block)
        UnTransactionDB().clear()
        cprint('INFO',"Receive new block.")
        return True

    def get_transactions(self):
        tdb = TransactionDB()
        return tdb.find_all()

    def new_untransaction(self,untx):
        cprint(__name__,untx)
        UnTransactionDB().insert(untx)
        cprint('INFO',"Receive new unchecked transaction.")
        return True

    def blocked_transactions(self,txs):
        TransactionDB().write(txs)
        cprint('INFO',"Receive new blocked transactions.")
        return True

    def add_node(self, address):
        add_node(address)
        return True
    
    def router(self, request):
        mode = request["method"] 
        if mode == "sendHeader":
            return self.send_Header(request)
        elif mode == "getBlocks":
            return self.get_Blocks(request)
        elif mode == "getBlockCount":
            return self.get_BlockCount(request)
        elif mode == "getBlockHash":
            return self.get_BlockHash(request)
        elif mode == "getBlockHeader":
            return self.get_BlockHeader(request)

    def send_Header(self, request):
        print('request:',request)
        #cprint('RPC', block)
        #transfer header to block format
        blockhash = request["data"]["block_hash"]
        
        version = request["data"]["block_header"][0:8]
        prev_block = request["data"]["block_header"][8:72]
        merkle_root = request["data"]["block_header"][72:136]
        target = request["data"]["block_header"][136:200]
        nouce = int(request["data"]["block_header"][200:208])
        
        block = {"version":version, "prev_block":prev_block, "merkle":merkle_root, "target":target, "nouce":nouce, "hash":blockhash}
        #print(block)
        BlockChainDB().insert(block)
        UnTransactionDB().clear()
        cprint('INFO',"Receive new block.")
        response = {"error":0}
        print('response:',response)
        return response

    def get_Blocks(self, request):
        print('request:',request)
        bcdb = BlockChainDB()
        alldata = bcdb.find_all()
        serias = []
        flag = False
        count_max = request['data']['hash_count']
        count = 0
        response = {"error":1, "result":[]}
        for block in alldata:
            if block['hash']==request['data']['hash_begin']:
                flag = True
                next
            if flag == True:
                if count < count_max:
                    count += 1
                    header = block["version"]+block["prev_block"]+block["merkle_root"]+block["target"]+str(block["nouce"])
                    serias.append(header)
                else:
                    response = {"error":0, "result":serias}
                    break 
        print('response:',response)
        return response
                
#node stat rpc
    def get_BlockCount(self, request):
        print('request:',request)
        bcdb = BlockChainDB()
        alldata = bcdb.find_all()
        response = {"error":0,"result":len(alldata)}
        print('response:',response)
        return response

    def get_BlockHash(self, request):
        print('request:',request)
        bcdb = BlockChainDB()
        alldata = bcdb.find_all()
        response = {"error":1,"result":""}
        height = request["data"]["block_height"]
        if alldata[height] is not None:
            response = {"error":0,"result":alldata[height]["hash"]}
        print('response:',response)
        return response
    
    def get_BlockHeader(self, request):
        print('request:',request)
        bcdb = BlockChainDB()
        alldata = bcdb.find_all()
        response = {"error":1,"result":""}
        for block in alldata:
            if block["hash"]==request["data"]["block_hash"]:
                response = {"error":0,"result":block}
        print('response:',response)
        return response
    

class RpcClient():

    ALLOW_METHOD = ['router', 'get_BlockHash', 'get_BlockHeader', 'get_BlockCount', 'get_Blocks', 'send_Header','get_transactions', 'get_blockchain', 'new_block', 'new_untransaction', 'blocked_transactions', 'ping', 'add_node']

    def __init__(self, node):
        self.node = node
        self.client = ServerProxy(node)
    
    def __getattr__(self, name):
        def noname(*args, **kw):
            if name in self.ALLOW_METHOD:
                return getattr(self.client, name)(*args, **kw)
        return noname

class BroadCast():

    def __getattr__(self, name):
        def noname(*args, **kw):
            cs = get_clients()
            rs = []
            for c in cs:
                try:
                    rs.append(getattr(c,name)(*args, **kw))
                except ConnectionRefusedError:
                    cprint('WARN', 'Contact with node %s failed when calling method %s , please check the node.' % (c.node,name))
                else:
                    cprint('INFO', 'Contact with node %s successful calling method %s .' % (c.node,name))
            return rs
        return noname

def start_server(ip, port=8301):
    server = SimpleXMLRPCServer((ip, port))
    rpc = RpcServer(server)
    server.register_instance(rpc)
    server.serve_forever()

def get_clients():
    clients = []
    nodes = get_nodes()

    for node in nodes:
        clients.append(RpcClient(node))
    return clients
