"""
颐康管家 - 数据加密工具模块
基于 cryptography 库的 Fernet (AES-128-CBC + HMAC) 对敏感字段进行字段级加密。
密钥保存在本地文件中，不上传云端，确保医疗数据的本地化安全。
"""
import os
import base64
import hashlib
from cryptography.fernet import Fernet, InvalidToken

from config import KEY_PATH


class CryptoManager:
    """字段级加密管理器，采用对称加密保护敏感医疗数据。"""

    _instance = None
    _fernet = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._fernet is None:
            self._load_or_create_key()

    def _load_or_create_key(self):
        """加载或创建主密钥，密钥文件权限设为仅所有者可读写。"""
        if os.path.exists(KEY_PATH):
            with open(KEY_PATH, "rb") as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(KEY_PATH, "wb") as f:
                f.write(key)
            try:
                os.chmod(KEY_PATH, 0o600)
            except OSError:
                pass
        self._fernet = Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        """加密明文字符串，返回 base64 编码的密文字符串。"""
        if plaintext is None:
            return None
        if not isinstance(plaintext, str):
            plaintext = str(plaintext)
        token = self._fernet.encrypt(plaintext.encode("utf-8"))
        return "ENC::" + token.decode("utf-8")

    def decrypt(self, ciphertext: str) -> str:
        """解密密文字符串，返回原始明文。"""
        if ciphertext is None:
            return None
        if not isinstance(ciphertext, str):
            ciphertext = str(ciphertext)
        if not ciphertext.startswith("ENC::"):
            return ciphertext
        token = ciphertext[5:].encode("utf-8")
        try:
            return self._fernet.decrypt(token).decode("utf-8")
        except InvalidToken:
            return ciphertext

    def encrypt_bytes(self, data: bytes) -> bytes:
        """加密二进制数据（如图片），返回加密后的字节。"""
        if data is None:
            return None
        return self._fernet.encrypt(data)

    def decrypt_bytes(self, token: bytes) -> bytes:
        """解密二进制数据。"""
        if token is None:
            return None
        try:
            return self._fernet.decrypt(token)
        except (InvalidToken, Exception):
            return token

    @staticmethod
    def derive_key(passphrase: str) -> bytes:
        """从口令派生密钥（用于扩展场景）。"""
        digest = hashlib.sha256(passphrase.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest)


crypto = CryptoManager()
