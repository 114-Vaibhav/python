# Blockchain Prototype

A simple Python blockchain prototype that demonstrates:

- block creation and hashing
- proof-of-work mining
- wallet generation with ECDSA keys
- signed transactions
- miner rewards
- basic peer-to-peer node communication over sockets
- longest-chain style synchronization between two local nodes

This project is designed as a learning prototype rather than a production blockchain.

## Features

- `Block` objects with index, timestamp, transactions, previous hash, nonce, and current hash
- Proof-of-work mining using a configurable difficulty
- `Transaction` validation using ECDSA signatures on the `SECP256k1` curve
- `Wallet` creation with derived addresses from public keys
- `BlockChain` support for mempool, mining rewards, and chain validation
- `Node` networking using Python sockets and threads
- JSON-based message serialization for transaction and chain exchange

## Tech Stack

- Python 3
- `hashlib`
- `socket`
- `threading`
- `json`
- `ecdsa`

## Project Structure

- `main.py` - main blockchain, wallet, transaction, and node implementation
- `output.txt` - sample output from running the demo
- `Learning.py` - extra project file in the repository

## How It Works

The demo in `main.py` starts two local blockchain nodes:

1. Node 1 and Node 2 each create their own blockchain and wallet.
2. Both nodes start socket servers on `127.0.0.1` using ports `5001` and `5002`.
3. Node 1 mines the first reward block.
4. Node 2 requests the longer chain and syncs with Node 1.
5. Node 1 creates a signed transaction sending coins to Node 2.
6. The transaction is broadcast to peers.
7. Node 2 mines a new block including the transaction and mining reward.
8. The new block is broadcast, and nodes sync again.
9. Final wallet balances and both chains are printed.

## Installation

Make sure Python 3 is installed, then install the required package:

```bash
pip install ecdsa
```

## Run

From the project folder, run:

```bash
python main.py
```

## Example Output

When you run the project, you will see output similar to:

- node startup messages
- mining progress
- transaction broadcast events
- chain synchronization logs
- final wallet balances
- full blockchain contents for both nodes

A saved example run is available in `output.txt`.

## Core Classes

### `Block`

Represents one block in the chain. It stores:

- block index
- timestamp
- list of transactions
- previous hash
- nonce
- current hash

It also handles hash calculation and proof-of-work.

### `BlockChain`

Manages:

- the chain
- mining difficulty
- mempool
- mining reward
- block mining
- chain validation

### `Transaction`

Represents a transfer of coins from one wallet address to another. It supports:

- signing with a private key
- signature verification with the sender's public key
- balance checking
- transaction validation

### `Wallet`

Creates:

- a private key
- a public key
- a wallet address derived from the public key hash

### `Node`

Handles:

- socket server startup
- peer connections
- transaction broadcast
- block broadcast
- chain requests
- basic chain replacement

## Notes and Limitations

This is a prototype, so a few shortcuts and limitations are expected:

- networking is local and manually configured
- there is no persistent storage
- there is no consensus beyond basic longest-chain replacement
- there is no transaction fee system
- error handling is minimal
- security and performance are not production-ready

One visible behavior in the sample run is that a received block may be rejected first and then accepted after a full chain sync. That is a limitation of the current synchronization flow, not the README.

## Learning Goals

This project is useful for understanding:

- blockchain data structures
- proof-of-work basics
- transaction signing and verification
- wallet/address generation
- peer-to-peer communication
- chain synchronization logic
