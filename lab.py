import argparse
import secrets
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding as sym_padding


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


class SymmetricEncryption:
    """Class for working with symmetric encryption (IDEA)"""

    @staticmethod
    def generate_key() -> bytes:
        """Generating a symmetric key"""
        try:
            symmetric_key = secrets.token_bytes(16)
            print("Сгенерирован симметричный ключ IDEA (128 бит)")
            return symmetric_key
        except Exception as e:
            raise RuntimeError(f"Ошибка генерации симметричного ключа: {str(e)}")

    @staticmethod
    def add_padding(plaintext: bytes) -> bytes:
        """Adding padding to data"""
        try:
            padder = sym_padding.PKCS7(64).padder()
            padded_data = padder.update(plaintext) + padder.finalize()
            return padded_data
        except Exception as e:
            raise RuntimeError(f"Ошибка добавления padding: {str(e)}")

    @staticmethod
    def remove_padding(padded_data: bytes) -> bytes:
        """Removing padding from data"""
        try:
            unpadder = sym_padding.PKCS7(64).unpadder()
            data = unpadder.update(padded_data) + unpadder.finalize()
            return data
        except Exception as e:
            raise RuntimeError(f"Ошибка удаления padding: {str(e)}")

    @staticmethod
    def encrypt(padded_data: bytes, symmetric_key: bytes, iv: bytes) -> bytes:
        """IDEA Data Encryption"""
        try:
            cipher = Cipher(
                algorithms.IDEA(symmetric_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            return ciphertext
        except Exception as e:
            raise RuntimeError(f"Ошибка шифрования IDEA: {str(e)}")

    @staticmethod
    def decrypt(encrypted_data: bytes, symmetric_key: bytes) -> bytes:
        """IDEA Data Decryption"""
        try:
            iv = encrypted_data[:8]
            ciphertext = encrypted_data[8:]
            cipher = Cipher(
                algorithms.IDEA(symmetric_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
            return decrypted_data
        except Exception as e:
            raise RuntimeError(f"Ошибка дешифрования IDEA: {str(e)}")


class FileHandler:
    """Class for working with files"""

    @staticmethod
    def read_file(file_path: str) -> bytes:
        """Reading a file"""
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except IOError as e:
            raise RuntimeError(f"Ошибка чтения файла {file_path}: {str(e)}")

    @staticmethod
    def write_file(data: bytes, file_path: str) -> None:
        """Write to file"""
        try:
            with open(file_path, 'wb') as f:
                f.write(data)
        except IOError as e:
            raise RuntimeError(f"Ошибка записи в файл {file_path}: {str(e)}")


class HybridEncryptionSystem:
    """Main class for managing hybrid encryption"""

    @staticmethod
    def generate_keys(encrypted_key_path: str, public_key_path: str,
                      private_key_path: str) -> None:
        """Generate all keys"""
        print("Генерация ключей...")
        try:
            symmetric_key = SymmetricEncryption.generate_key()
            private_key, public_key = AsymmetricEncryption.generate_keys()

            AsymmetricEncryption.serialize_keys(
                public_key, public_key_path,
                private_key, private_key_path
            )
            AsymmetricEncryption.encrypt_symmetric_key(
                symmetric_key, public_key,
                encrypted_key_path
            )
            print("Генерация ключей завершена успешно!")
        except Exception as e:
            raise RuntimeError(f"Ошибка в процессе генерации ключей: {str(e)}")

    @staticmethod
    def encrypt_file(input_file_path: str, private_key_path: str,
                     encrypted_key_path: str, output_file_path: str) -> None:
        """File encryption"""
        print(f"Шифрование файла {input_file_path}...")
        try:
            private_key = AsymmetricEncryption.load_private_key(private_key_path)
            encrypted_symmetric_key = FileHandler.read_file(encrypted_key_path)
            symmetric_key = AsymmetricEncryption.decrypt_symmetric_key(
                encrypted_symmetric_key, private_key
            )

            plaintext = FileHandler.read_file(input_file_path)
            padded_data = SymmetricEncryption.add_padding(plaintext)
            iv = secrets.token_bytes(8)
            ciphertext = SymmetricEncryption.encrypt(padded_data, symmetric_key, iv)

            FileHandler.write_file(iv + ciphertext, output_file_path)
            print(f"Файл успешно зашифрован и сохранен в {output_file_path}")
        except Exception as e:
            raise RuntimeError(f"Ошибка шифрования файла: {str(e)}")

    @staticmethod
    def decrypt_file(input_file_path: str, private_key_path: str,
                     encrypted_key_path: str, output_file_path: str) -> None:
        """File decryption"""
        print(f"Дешифрование файла {input_file_path}...")
        try:
            private_key = AsymmetricEncryption.load_private_key(private_key_path)
            encrypted_symmetric_key = FileHandler.read_file(encrypted_key_path)
            symmetric_key = AsymmetricEncryption.decrypt_symmetric_key(
                encrypted_symmetric_key, private_key
            )

            encrypted_text = FileHandler.read_file(input_file_path)
            decrypted_padded_data = SymmetricEncryption.decrypt(
                encrypted_text, symmetric_key
            )
            decrypted_data = SymmetricEncryption.remove_padding(decrypted_padded_data)

            FileHandler.write_file(decrypted_data, output_file_path)
            print(f"Файл успешно расшифрован и сохранен в {output_file_path}")
        except Exception as e:
            raise RuntimeError(f"Ошибка дешифрования файла: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description='Гибридная система шифрования (IDEA + RSA)')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-g', '--generate-keys', action='store_true', help='Генерация ключей')
    group.add_argument('-e', '--encrypt', action='store_true', help='Шифрование файла')
    group.add_argument('-d', '--decrypt', action='store_true', help='Дешифрование файла')

    parser.add_argument('-pr-k', '--private-key', help='Путь к закрытому ключу')
    parser.add_argument('-e-k', '--encrypted-key', help='Путь к зашифрованному симметричному ключу')
    parser.add_argument('-pub-k', '--public-key', help='Путь к открытому ключу (только для генерации)')
    parser.add_argument('-in-f', '--input-file', help='Путь к входному файлу')
    parser.add_argument('-out-f', '--output-file', help='Путь к выходному файлу')

    args = parser.parse_args()

    try:
        if args.generate_keys:
            if not all([args.encrypted_key, args.public_key, args.private_key]):
                parser.error("Для генерации ключей требуются --encrypted-key, --public-key и --private-key")
            HybridEncryptionSystem.generate_keys(
                args.encrypted_key, args.public_key, args.private_key
            )
        elif args.encrypt:
            if not all([args.input_file, args.private_key, args.encrypted_key, args.output_file]):
                parser.error("Для шифрования требуются --input-file, --private-key, --encrypted-key и --output-file")
            HybridEncryptionSystem.encrypt_file(
                args.input_file, args.private_key, args.encrypted_key, args.output_file
            )
        elif args.decrypt:
            if not all([args.input_file, args.private_key, args.encrypted_key, args.output_file]):
                parser.error("Для дешифрования требуются --input-file, --private-key, --encrypted-key и --output-file")
            HybridEncryptionSystem.decrypt_file(
                args.input_file, args.private_key, args.encrypted_key, args.output_file
            )
    except Exception as e:
        print(f"Ошибка: {str(e)}")


if __name__ == "__main__":
    main()
