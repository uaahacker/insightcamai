from abc import ABC, abstractmethod
import json


class CipherService(ABC):
    """Abstract cipher service for encryption/decryption"""
    
    @abstractmethod
    def encrypt(self, plaintext: str) -> str:
        pass
    
    @abstractmethod
    def decrypt(self, ciphertext: str) -> str:
        pass


class SimpleCipherService(CipherService):
    """Simple cipher service using Fernet (from cryptography)"""
    
    def __init__(self, key: str = None):
        from django.conf import settings
        from cryptography.fernet import Fernet
        import base64
        
        self.key = key or settings.ENCRYPTION_KEY
        # Ensure key is 32 bytes for Fernet
        key_bytes = self.key.encode()
        if len(key_bytes) < 32:
            key_bytes = key_bytes.ljust(32)
        else:
            key_bytes = key_bytes[:32]
        
        self.fernet = Fernet(base64.urlsafe_b64encode(key_bytes))
    
    def encrypt(self, plaintext: str) -> str:
        if not plaintext:
            return ""
        encrypted = self.fernet.encrypt(plaintext.encode())
        return encrypted.decode()
    
    def decrypt(self, ciphertext: str) -> str:
        if not ciphertext:
            return ""
        decrypted = self.fernet.decrypt(ciphertext.encode())
        return decrypted.decode()


class CredentialManager:
    """Manages credential encryption/decryption"""
    
    def __init__(self):
        self.cipher = SimpleCipherService()
    
    def encrypt_password(self, password: str) -> str:
        return self.cipher.encrypt(password)
    
    def decrypt_password(self, encrypted_password: str) -> str:
        return self.cipher.decrypt(encrypted_password)
    
    def create_credential_dict(self, **kwargs) -> str:
        """Encrypt credential dictionary"""
        return self.cipher.encrypt(json.dumps(kwargs))
    
    def extract_credentials(self, encrypted_creds: str) -> dict:
        """Decrypt and extract credential dictionary"""
        decrypted = self.cipher.decrypt(encrypted_creds)
        return json.loads(decrypted)
