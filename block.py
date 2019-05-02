# coding:utf-8
import hashlib
import time
from model import Model
from rpc import BroadCast

class Block(Model):

    def __init__(self, previous_hash):
        self.version = '00000001'
        self.prev_block = previous_hash
        self.merkle_root = '0000000000000000000000000000000000000000000000000000000000000000'
        self.target = '0001000000000000000000000000000000000000000000000000000000000000'


    def pow(self):
        """
        Proof of work. Add nouce to block.
        """        
        nouce = 0
        while self.valid(nouce) is False:
            nouce += 1
        self.nouce = nouce
        return nouce

    def make(self, nouce):
        """
        Block hash generate. Add hash to block.
        """
        self.hash = self.ghash(nouce)
    
    def ghash(self, nouce):
        self.nouce = nouce
        return hashlib.sha256(( str(self.version) + str(self.prev_block) + str(self.merkle_root) + str(self.target) + str(self.nouce).zfill(8)).encode('utf-8')).hexdigest()

    def valid(self, nouce):
        """
        Validates the Proof
        """
        return self.ghash(nouce)[:4] == "0000"

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, bdict):
        b = cls(bdict['version'], bdict['prev_block'], bdict['merkle_root'], bdict['target'])
        b.hash = bdict['hash']
        b.nouce = bdict['nouce']
        return b

    @staticmethod
    def spread(block):
        BroadCast().new_block(block)
if __name__=="__main__":
    bc = Block('0000000008e647742775a230787d66fdf92c46a48c896bfbc85cdc8acc67e87d')
    print(bc.ghash(bc.pow()))
