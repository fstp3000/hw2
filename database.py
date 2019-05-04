#coding:utf-8
import json
import os
import hashlib
BASEDBPATH = 'data'
BLOCKFILE = 'blockchain'
TXFILE = 'tx'
UNTXFILE = 'untx'
ACCOUNTFILE = 'account'
NODEFILE = 'node'

class BaseDB():

    filepath = ''

    def __init__(self):
        self.set_path()
        self.filepath = '/'.join((BASEDBPATH, self.filepath))

    def set_path(self):
        pass

    def find_all(self):
        return self.read()

    def insert(self, item):
        self.write(item)  

    def read(self):
        raw = ''
        if not os.path.exists(self.filepath):
            return []
        with open(self.filepath,'r+') as f:
            raw = f.readline()
        if len(raw) > 0:
            data = json.loads(raw)
        else:
            data = []
        return data

    def write(self, item):
        data = self.read()
        if isinstance(item,list):
            data = data + item
        else:
            data.append(item)
        with open(self.filepath,'w+') as f:
            f.write(json.dumps(data))
        return True

    def clear(self):
        with open(self.filepath,'w+') as f:
            f.write('')

    def tx_hash_insert(self, item):
        exists = False
        for i in self.find_all():
            if item['hash'] == i['hash']:
                exists = True
                break
        if not exists:
            self.write(item)  
    
    def block_hash_insert(self, item):
        exists = False
        alldata = self.find_all()
        print('item:',item)
        if len(alldata)==0:
            print('nodata')
            return "error"
        else:
            if item["prev_block"]!=alldata[-1]["hash"]:
                return "fakeblock"
            hash_check =  hashlib.sha256(( str(item["version"]) + str(item["prev_block"]) + str(item["merkle_root"]) + str(item["target"]) + str(item["nouce"]).zfill(8)).encode('utf-8')).hexdigest()
            if hash_check != item["hash"]:
                return "fakeblock"
         
            self.write(item)  

class NodeDB(BaseDB):

    def set_path(self):
        self.filepath = NODEFILE
    def find_all(self):
        with open('config.json') as f:
            config = json.load(f)
        nodes = []
        for node in config["neighbor_list"]:
            nodes.append("http://"+str(node["ip"])+":"+str(node["p2p_port"]))
        #raw = ''
        #if not os.path.exists(self.filepath):
        #    return []
        #with open(self.filepath,'r+') as f:
        #    raw = f.readline()
        #if len(raw) > 0:
        #    data = json.loads(raw)
        #else:
        #    data = []
        return nodes


class AccountDB(BaseDB):
    def set_path(self):
        self.filepath = ACCOUNTFILE  

    def find_one(self):
        ac = self.read()
        return ac[0]


class BlockChainDB(BaseDB):

    def set_path(self):
        self.filepath = BLOCKFILE

    def last(self):
        bc = self.read()
        if len(bc) > 0:
            return bc[-1]
        else:
            return []

    def find(self, hash):
        one = {}
        for item in self.find_all():
            if item['hash'] == hash:
                one = item
                break
        return one

    def insert(self, item):
        self.block_hash_insert(item)

class TransactionDB(BaseDB):
    """
    Transactions that save with blockchain.
    """
    def set_path(self):
        self.filepath = TXFILE

    def find(self, hash):
        one = {}
        for item in self.find_all():
            if item['hash'] == hash:
                one = item
                break
        return one

    def insert(self, txs):
        if not isinstance(txs,list):
            txs = [txs]
        for tx in txs:
            self.tx_hash_insert(tx)

class UnTransactionDB(TransactionDB):
    """
    Transactions that doesn't store in blockchain.
    """
    def set_path(self):
        self.filepath = UNTXFILE

    def all_hashes(self):
        hashes = []
        for item in self.find_all():
            hashes.append(item['hash'])
        return hashes


