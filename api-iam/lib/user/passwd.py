from cryptography.fernet import Fernet
import base64
import hashlib


# 生成密钥
def generate_key(password):
    # 使用SHA256对密码进行哈希
    key = hashlib.sha256(password.encode()).digest()
    # 将字节转换为base64格式
    return base64.urlsafe_b64encode(key)


# 加密字符串
def encrypt_string(data, password):
    key = generate_key(password)
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data.encode())
    # 将加密结果转换为字符串
    return encrypted_data.decode('utf-8')


# 解密字符串
def decrypt_string(encrypted_data, password):
    key = generate_key(password)
    fernet = Fernet(key)
    # 需要将字符串转换回字节
    decrypted_data = fernet.decrypt(encrypted_data.encode()).decode()
    return decrypted_data


# 示例使用
if __name__ == "__main__":
    password = "admin"
    original_string = "963852aa"

    # 加密
    encrypted = encrypt_string(original_string, password)
    print(f"Encrypted: {encrypted}")

    # 解密
    decrypted = decrypt_string(encrypted, password)
    print(f"Decrypted: {decrypted}")
