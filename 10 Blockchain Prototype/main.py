import hashlib
import time
from ecdsa import SigningKey, VerifyingKey, SECP256k1
import socket
import threading

class Block:
    def __init__(self, index, timestamp, transaction, previous_hash,nonce):
        self.index = index  
        self.timestamp = timestamp  
        self.transactions = transaction    
        self.previous_hash = previous_hash  
        self.nonce = nonce
        self.hash = self.calculate_hash()
        
    @staticmethod
    def from_dict(data):
        transactions = [Transaction.from_dict(tx) for tx in data["transactions"]]

        block = Block(
            data["index"],
            data["timestamp"],
            transactions,
            data["previous_hash"],
            data["nonce"]
        )

        block.hash = data["hash"]
        return block
    
    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash
        }
    
    def calculate_hash(self):
        block_string = (
        str(self.index)
        + str(self.timestamp)
        + str([str(tx.__dict__) for tx in self.transactions])
        + str(self.previous_hash)
        + str(self.nonce)
        )
        return hashlib.sha256(block_string.encode()).hexdigest()

    def ProofofWork(self, difficulty_bits):
        while True:
            self.nonce += 1
            self.hash = self.calculate_hash()
            if self.hash.startswith("0" * difficulty_bits):
                break

    

class BlockChain:
    def __init__(self):
        self.difficulty = 4
        self.mempool = []
        self.mining_reward = 10
        self.chain = [self.create_genesis_block()]

    def mine_block(self, miner_address):
       
        reward_tx = Transaction("0", miner_address, self.mining_reward)  
        self.mempool.append(reward_tx)

        new_block = Block(
            len(self.chain),
            time.time(),
            self.mempool.copy(),
            self.get_latest_block().hash,
            0
        )

        new_block.ProofofWork(self.difficulty)

    
        if new_block.previous_hash != self.get_latest_block().hash:
            print("Invalid previous hash")
            return

        if not new_block.hash.startswith("0" * self.difficulty):
            print("Invalid proof of work")
            return
        if new_block.hash != new_block.calculate_hash():
            print("Invalid Hash")
            return

        self.chain.append(new_block)

        print("Mine reward added, current balance: ",reward_tx.balance(miner_address,self))
        print(f"[INFO] Block mined. Chain length: {len(self.chain)}")
        self.mempool = []

    def create_genesis_block(self):
        genesis = Block(
            0,
            1234567890,  
            [],
            "0",
            0
        )
        genesis.ProofofWork(self.difficulty)
        return genesis
        
    def get_latest_block(self):
        return self.chain[-1]

    def add_transaction(self, transaction,blockchain):
        if not transaction.validTransaction(blockchain):
            print("Invalid transaction")
            return False

        self.mempool.append(transaction)
        return True

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if not current_block.hash.startswith("0" * self.difficulty):
                return False
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

    def print_chain(self):
        for block in self.chain:
            print("------------------>")
            print("Index:", block.index)
            print("Timestamp:", block.timestamp)
            print("Transactions:", [tx.__dict__ for tx in block.transactions])
            print("Previous Hash:", block.previous_hash)
            print("Hash:", block.hash)
            
class Transaction:
    def __init__(self, from_address, to_address, amount,signature="",public_key=None):
        self.from_address = from_address
        self.to_address = to_address
        self.amount = amount
        self.signature = signature 
        self.public_key = public_key

    def sign(self, private_key):
        data = str(self.from_address) + str(self.to_address) + str(self.amount)
        self.signature = private_key.sign(data.encode())

    @staticmethod
    def from_dict(data):
        tx = Transaction(
            data["from_address"],
            data["to_address"],
            data["amount"]
        )

        tx.signature = bytes.fromhex(data["signature"]) if data["signature"] else None

        if data["public_key"]:
            tx.public_key = VerifyingKey.from_string(
                bytes.fromhex(data["public_key"]),
                curve=SECP256k1
            )

        return tx
    
    def to_dict(self):
        return {
            "from_address": self.from_address,
            "to_address": self.to_address,
            "amount": self.amount,
            "signature": self.signature.hex() if self.signature else "",
            "public_key": self.public_key.to_string().hex() if self.public_key else None
        }

    def balance(self, address,blockchain):
        balance = 0

        for block in blockchain.chain:
            for tx in block.transactions:
                if tx.from_address == address:
                    balance -= tx.amount
                if tx.to_address == address:
                    balance += tx.amount
        
        for(tx) in blockchain.mempool:
            if tx.from_address == address:
                balance -= tx.amount

        return balance
    
    def validTransaction(self,blockchain):
        if self.from_address == "0":  
            return True
        if self.balance(self.from_address,blockchain) < self.amount:
            return False
        if not self.signature:
            return False
        data = str(self.from_address) + str(self.to_address) + str(self.amount)
        if not self.public_key:
            return False  

        # derived_address = hashlib.sha256(self.public_key.to_string()).hexdigest()
        derived_address = hashlib.sha256(self.public_key.to_string()).hexdigest()
        if derived_address != self.from_address:
            return False
        try:
            return self.public_key.verify(self.signature, data.encode())
        except:
            return False

class Wallet:
    def __init__(self, username):
        self.name = username
        self.private_key = SigningKey.generate(curve=SECP256k1)
        self.public_key = self.private_key.get_verifying_key()
        self.address = hashlib.sha256(self.public_key.to_string()).hexdigest()


class Node:
    def __init__(self, blockchain, wallet, id, host, port):
        self.blockchain = blockchain
        self.wallet = wallet
        self.peersList = []  
        self.nodeid = id
        self.host = host
        self.port = port
        self.server_socket = None

    
    def startServer(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Node {self.nodeid} listening on {self.host}:{self.port}")

       
        threading.Thread(target=self.listenClients, daemon=True).start()

    
    def listenClients(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Node {self.nodeid} connected by {addr}")
            threading.Thread(target=self.handleClient, args=(client_socket,), daemon=True).start()

  
    def handleClient(self, client_socket):
        try:
            while True:
                message = client_socket.recv(4096).decode()
                if not message:
                    break

                data = deSerialization(message)

                msg_type = data["type"]
                msg_data = data["data"]

                self.handleMessage(msg_type, msg_data)

        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_socket.close()
       

    def handleMessage(self, msg_type, data):
   
        if msg_type == "NEW_TRANSACTION":
            tx = Transaction.from_dict(data)

         
            for existing_tx in self.blockchain.mempool:
                if existing_tx.signature == tx.signature:
                    return

            if self.blockchain.add_transaction(tx, self.blockchain):
                print(f"[NODE-{self.nodeid}] Transaction added to mempool")

               
                self.broadcast({
                    "type": "NEW_TRANSACTION",
                    "data": data
                })
     
        elif msg_type == "NEW_BLOCK":
            print(f"[Node {self.nodeid}] Received block, validating...")

            block = Block.from_dict(data)

          
            if block.hash == self.blockchain.get_latest_block().hash:
                return

            if (
                block.previous_hash == self.blockchain.get_latest_block().hash and
                block.hash.startswith("0" * self.blockchain.difficulty) and
                block.hash == block.calculate_hash()
            ):
                self.blockchain.chain.append(block)
                print(f"[Node {self.nodeid}] Block accepted")
            else:
                print(f"[Node {self.nodeid}] Invalid block rejected")

       
        elif msg_type == "REQUEST_CHAIN":
            print(f"[Node {self.nodeid}] Sending chain")

            response = {
                "type": "RESPONSE_CHAIN",
                "data": [block.to_dict() for block in self.blockchain.chain] 
            }

            self.broadcast(response)

    
        elif msg_type == "RESPONSE_CHAIN":
            print(f"[Node {self.nodeid}] Comparing chains")

            incoming_chain = [Block.from_dict(b) for b in data]
            if len(incoming_chain) > len(self.blockchain.chain):
                self.blockchain.chain = incoming_chain
                print(f"[Node {self.nodeid}] Chain replaced")


    def addPeer(self, host, port):
        self.peersList.append((host, port))

    def broadcast(self, message_dict):
        message = Serialization(message_dict)

        for peer_host, peer_port in self.peersList:
            self.sendMessage(peer_host, peer_port, message)

    def broadcastTransaction(self, tx):
        message = {
            "type": "NEW_TRANSACTION",
            "data": tx.to_dict() 
        }

        self.broadcast(message)

    def broadcastBlock(self, block):
        message = {
            "type": "NEW_BLOCK",
            "data": block.to_dict() 
        }

        self.broadcast(message)

    def requestChain(self):
        message = {
            "type": "REQUEST_CHAIN",
            "data": {}
        }

        self.broadcast(message)

    def sendMessage(self, peer_host, peer_port, message):

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((peer_host, peer_port))
                s.sendall(message.encode())
        except:
            print(f"Connection failed")


messageFormat = [{
    "type": "RESPONSE_CHAIN", "data": {} },{  "type": "REQUEST_CHAIN","data": {} },
    {  "type": "NEW_TRANSACTION","data": {} },{  "type": "NEW_BLOCK","data": {} }
]

import json

def Serialization(message_dict):
    return json.dumps(message_dict)

def deSerialization(message_str):
    return json.loads(message_str)


if __name__ == "__main__":
    import time

    def short(addr):
        return addr[:6] + "..." + addr[-6:]


    blockchain1 = BlockChain()
    blockchain2 = BlockChain()


    wallet1 = Wallet("Alice")
    wallet2 = Wallet("Bob")

   
    node1 = Node(blockchain1, wallet1, 1, "127.0.0.1", 5001)
    node2 = Node(blockchain2, wallet2, 2, "127.0.0.1", 5002)

    node1.addPeer("127.0.0.1", 5002)
    node2.addPeer("127.0.0.1", 5001)

    print("\n=== Node Startup ===")
    print(f"[NODE-1] Listening on port 5001 | Wallet: {short(wallet1.address)}")
    print(f"[NODE-2] Listening on port 5002 | Wallet: {short(wallet2.address)}")

    node1.startServer()
    node2.startServer()

    time.sleep(2)

  
    print("\n=== INITIAL MINING ===")

    node1.blockchain.mine_block(node1.wallet.address)

    time.sleep(1)
    node2.requestChain()
    time.sleep(2)

  
    print("\n=== TRANSACTION ===")

    tx = Transaction(wallet1.address, wallet2.address, 5, public_key=wallet1.public_key)
    tx.sign(wallet1.private_key)

    print(f"[NODE-1] Creating transaction:")
    print(f"From:   {short(wallet1.address)}")
    print(f"To:     {short(wallet2.address)}")
    print(f"Amount: {tx.amount} coins")
    print(f"Signature: {tx.signature.hex()[:20]}...  Valid")

    node1.blockchain.add_transaction(tx, node1.blockchain)
    node1.broadcastTransaction(tx)

    time.sleep(2)

    print("\n=== MINING ===")

    start = time.time()

    print(f"[NODE-2] Mining block #{len(node2.blockchain.chain)}...")
    print(f"Difficulty: {node2.blockchain.difficulty} (hash must start with {'0'*node2.blockchain.difficulty})")

    node2.blockchain.mine_block(node2.wallet.address)

    end = time.time()

    latest_block = node2.blockchain.get_latest_block()

    print(f"[NODE-2] Block mined in {round(end-start,2)}s")
    print(f"Hash:        {latest_block.hash[:20]}...")
    print(f"Prev Hash:   {latest_block.previous_hash[:20]}...")
    print(f"Transactions: {len(latest_block.transactions)}")
    print(f"Miner Reward: {node2.blockchain.mining_reward} coin → {short(node2.wallet.address)}")

    print("\n=== PROPAGATION ===")

    node2.broadcastBlock(latest_block)

    time.sleep(2)

 
    print("\n=== SYNC ===")
    node1.requestChain()
    time.sleep(2)

  
    print("\n=== WALLET BALANCES ===")

    b1 = Transaction("", "", 0).balance(wallet1.address, node1.blockchain)
    b2 = Transaction("", "", 0).balance(wallet2.address, node1.blockchain)

    print(f"{short(wallet1.address)}: {b1} coins")
    print(f"{short(wallet2.address)}: {b2} coins")

    print("\n=== FINAL CHAINS ===")

    print("\n--- Node 1 Chain ---")
    node1.blockchain.print_chain()

    print("\n--- Node 2 Chain ---")
    node2.blockchain.print_chain()