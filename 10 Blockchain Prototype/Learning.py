import hashlib

data = "Hello Blockchain"

hash_value = hashlib.sha256(data.encode()).hexdigest()

print(hash_value)


from ecdsa import SigningKey, SECP256k1

# Generate private key
private_key = SigningKey.generate(curve=SECP256k1)

# Generate public key
public_key = private_key.get_verifying_key()

print("Private Key:", private_key.to_string().hex())
print("Public Key:", public_key.to_string().hex())

message = b"Send 10 coins to Bob"

# Sign
signature = private_key.sign(message)

# Verify
print(public_key.verify(signature, message))

import hashlib

public_key_bytes = public_key.to_string()

address = hashlib.sha256(public_key_bytes).hexdigest()

print("Wallet Address:", address)