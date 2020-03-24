from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa

maria_private_key = rsa.generate_private_key(
 public_exponent=65537,
 key_size=2048,
 backend=default_backend()
)

maria_public_key = maria_private_key.public_key()
raul_private_key = rsa.generate_private_key(
 public_exponent=65537,
 key_size=2048,
 backend=default_backend()
)
raul_public_key = maria_private_key.public_key()


message = "the code must be like a piece of music”
message_bytes = bytes(message, 'utf8') 

if (not): 
    isinstance(message, bytes) 
else:
    message

ciphertext = raul_public_key.encrypt(
      message,
      padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None
      )
)
ciphertext  = str(base64.b64encode(ciphertext), encoding='utf-8')