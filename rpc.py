# coding:utf-8
from xmlrpc.server import SimpleXMLRPCServer  
from xmlrpc.client import ServerProxy
from node import get_nodes, add_node
from database import BlockChainDB, UnTransactionDB, TransactionDB
from lib.common import cprint
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
#data format between p2p network
    
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
        bcdb = BlockChainDB()
        alldata = bcdb.find_all()
        alldata = alldata[0]
        block = alldata["version"]+alldata["prev_block"]+alldata["merkle_root"]+alldata["target"]+alldata["nonce"]
        print(block)
        dict1 = {"error":0}
        return True

    def get_Blocks(self, request):
        bcdb = BlockChainDB()
        alldata = bcdb.find_all()
        result = []
        flag = False
        print('request:',request)
        count_max = request['data']['hash_count']
        count = 0
        for index,block in enumerate(alldata):
            if block['hash']==request['data']['hash_begin']:
                flag = True
            if flag == True:
                if count < count_max:
                    result.append(block['hash'])
                else:
                    break
        return result
                
#node stat rpc
    def get_BlockCount(self, request):
        bcdb = BlockChainDB()
        alldata = bcdb.find_all()
        result = alldata[0]
        #print('request:',request)
        return result

    def get_BlockHash(self, request):
        bcdb = BlockChainDB()
        alldata = bcdb.find_all()
        result = alldata[0]
        #print('request:',request)
        return result

    def get_BlockHeader(self, request):
        bcdb = BlockChainDB()
        alldata = bcdb.find_all()
        alldata = alldata[0]
        dict1 = {"error":0,"result":alldata}
        print(dict1)
        return dict1
    

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
