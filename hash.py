import hashlib                           #   
from cryptography.fernet import Fernet   # 

# Please note that this script is only for providing hash values for authentication
dic1 = {}
md5 = b'X8lz9EecTPotGjwfna1e1DjnY37CHqrsEp9lG7u2GJU='
cipher_suite = Fernet(md5)
factor1 = 0
factor2 = 0


def hash_init():
    global factor1
    factor1 = b'gAAAAABmnJj4SGuSJ26isJDaHUtna7m2qCNVVG9WmCKjm92sQPa3ckD0-rQI1I9KgER8RrkfyLqGohQBPZkA0uK8B1-kjlpUTg=='
    global factor2
    factor2 = b'gAAAAABmnJkx7Jr6ZIZlxleS0ra9Ncw_fGzfJ2r1xN-Og5MppLbGJw57b0nWnsrxNyWe52BiDNJbbV2NHfzzNw81eH0aN4BjKw=='
    return cipher_suite.decrypt(factor1).decode('utf-8'), cipher_suite.decrypt(factor2).decode('utf-8')


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# If you want to generate your new password, you can use below code.
# After generation, don't forget to comment the lines below.

# new_psswd = input("Your new password:")
# print(hash_password(new_psswd))
