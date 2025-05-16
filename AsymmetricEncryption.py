from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.backends import default_backend


class AsymmetricEncryption:
    """Class for working with asymmetric encryption (RSA)"""

    @staticmethod
    def generate_keys() -> tuple[RSAPrivateKey, rsa.RSAPublicKey]:
        """Generate RSA key pair"""
        try:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            public_key = private_key.public_key()
            print("Сгенерирована пара ключей RSA (2048 бит)")
            return private_key, public_key
        except Exception as e:
            raise RuntimeError(f"Ошибка генерации ключей RSA: {str(e)}")

    @staticmethod
    def serialize_keys(public_key: rsa.RSAPublicKey, public_key_path: str,
                       private_key: RSAPrivateKey, private_key_path: str) -> None:
        """Serializing keys to files"""
        try:
            with open(public_key_path, 'wb') as f:
                f.write(public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ))
            print(f"Открытый ключ сохранен в {public_key_path}")

            with open(private_key_path, 'wb') as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            print(f"Закрытый ключ сохранен в {private_key_path}")
        except IOError as e:
            raise RuntimeError(f"Ошибка записи ключей в файл: {str(e)}")

    @staticmethod
    def encrypt_symmetric_key(symmetric_key: bytes, public_key: rsa.RSAPublicKey,
                              encrypted_key_path: str) -> None:
        """RSA Symmetric Key Encryption"""
        try:
            with open(encrypted_key_path, 'wb') as f:
                f.write(public_key.encrypt(
                    symmetric_key,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                ))
            print(f"Зашифрованный симметричный ключ сохранен в {encrypted_key_path}")
        except Exception as e:
            raise RuntimeError(f"Ошибка шифрования симметричного ключа: {str(e)}")

    @staticmethod
    def load_private_key(private_key_path: str) -> RSAPrivateKey:
        """Loading private key from file"""
        try:
            with open(private_key_path, 'rb') as f:
                private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
            return private_key
        except Exception as e:
            raise RuntimeError(f"Ошибка загрузки закрытого ключа: {str(e)}")

    @staticmethod
    def decrypt_symmetric_key(encrypted_symmetric_key: bytes,
                              private_key: RSAPrivateKey) -> bytes:
        """Decrypting a symmetric key"""
        try:
            symmetric_key = private_key.decrypt(
                encrypted_symmetric_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            print("Симметричный ключ успешно расшифрован")
            return symmetric_key
        except Exception as e:
            raise RuntimeError(f"Ошибка дешифрования симметричного ключа: {str(e)}")
