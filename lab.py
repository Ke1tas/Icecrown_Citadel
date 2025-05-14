import argparse
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding as sym_padding
import secrets


def symm_key_gen() -> bytes:
    symmetric_key = secrets.token_bytes(16)
    print("Сгенерирован симметричный ключ IDEA (128 бит)")
    return symmetric_key


def asymm_keys_gen() -> tuple:
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    print("Сгенерирована пара ключей RSA (2048 бит)")
    return private_key, public_key


def asymm_key_serialize(public_key, public_key_path, private_key, private_key_path) -> None:
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


def symm_key_encryption(symmetric_key, public_key, encrypted_key_path) -> None:
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


def private_key_load(private_key_path) -> RSAPrivateKey:
    with open(private_key_path, 'rb') as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )
    return private_key


def read_file(file_path):
    with open(file_path, 'rb') as f:
        file = f.read()
    return file


def write_file(text, file_path):
    with open(file_path, 'wb') as f:
        f.write(text)


def symm_key_decrypt(encrypted_symmetric_key, private_key):
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


def add_padding(plaintext):
    padder = sym_padding.PKCS7(64).padder()
    padded_data = padder.update(plaintext) + padder.finalize()
    return padded_data


def delete_padding(decrypted_padded_data):
    unpadder = sym_padding.PKCS7(64).unpadder()
    decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()
    return decrypted_data


def encrypt_text(padded_data, symmetric_key, iv):
    cipher = Cipher(
        algorithms.IDEA(symmetric_key),
        modes.CBC(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return ciphertext


def dencrypt_text(encrypted_text, symmetric_key):
    iv = encrypted_text[:8]
    ciphertext = encrypted_text[8:]
    cipher = Cipher(
        algorithms.IDEA(symmetric_key),
        modes.CBC(iv),
        backend=default_backend()
    )
    decryptor = cipher.decryptor()
    decrypted_padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    return decrypted_padded_data


def generate_keys(encrypted_key_path, public_key_path, private_key_path) -> None:
    print("Генерация ключей...")
    symmetric_key = symm_key_gen()
    private_key, public_key = asymm_keys_gen()

    asymm_key_serialize(public_key, public_key_path, private_key, private_key_path)
    print("Генерация ключей завершена успешно!")

    symm_key_encryption(symmetric_key, public_key, encrypted_key_path)


def encrypt_file(input_file_path, private_key_path, encrypted_key_path, output_file_path):
    """Шифрование файла гибридной системой"""
    print(f"Шифрование файла {input_file_path}...")
    private_key = private_key_load(private_key_path)
    encrypted_symmetric_key = read_file(encrypted_key_path)

    symmetric_key = symm_key_decrypt(encrypted_symmetric_key, private_key)

    plaintext = read_file(input_file_path)

    padded_data = add_padding(plaintext)

    iv = secrets.token_bytes(8)

    ciphertext = encrypt_text(padded_data, symmetric_key, iv)

    write_file(iv + ciphertext, output_file_path)
    print(f"Файл успешно зашифрован и сохранен в {output_file_path}")


def decrypt_file(input_file_path, private_key_path, encrypted_key_path, output_file_path):
    """Дешифрование файла гибридной системой"""
    print(f"Дешифрование файла {input_file_path}...")

    private_key = private_key_load(private_key_path)
    encrypted_symmetric_key = read_file(encrypted_key_path)

    symmetric_key = symm_key_decrypt(encrypted_symmetric_key, private_key)

    encrypted_text = read_file(input_file_path)

    decrypted_padded_data = dencrypt_text(encrypted_text, symmetric_key)

    decrypted_data = delete_padding(decrypted_padded_data)

    write_file(decrypted_data, output_file_path)

    print(f"Файл успешно расшифрован и сохранен в {output_file_path}")


def main():
    parser = argparse.ArgumentParser(description='Гибридная система шифрования (IDEA + RSA)')

    # Создаем группу взаимоисключающих параметров
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--generate-keys', action='store_true', help='Генерация ключей')
    group.add_argument('--encrypt', action='store_true', help='Шифрование файла')
    group.add_argument('--decrypt', action='store_true', help='Дешифрование файла')

    # Общие параметры
    parser.add_argument('--private-key', help='Путь к закрытому ключу')
    parser.add_argument('--encrypted-key', help='Путь к зашифрованному симметричному ключу')

    # Параметры для генерации ключей
    parser.add_argument('--public-key', help='Путь к открытому ключу (только для генерации)')

    # Параметры для шифрования/дешифрования
    parser.add_argument('--input-file', help='Путь к входному файлу')
    parser.add_argument('--output-file', help='Путь к выходному файлу')

    # Парсинг аргументов
    args = parser.parse_args()

    try:
        if args.generate_keys:
            if not all([args.encrypted_key, args.public_key, args.private_key]):
                parser.error("Для генерации ключей требуются --encrypted-key, --public-key и --private-key")
            generate_keys(args.encrypted_key, args.public_key, args.private_key)
        elif args.encrypt:
            if not all([args.input_file, args.private_key, args.encrypted_key, args.output_file]):
                parser.error("Для шифрования требуются --input-file, --private-key, --encrypted-key и --output-file")
            encrypt_file(args.input_file, args.private_key, args.encrypted_key, args.output_file)
        elif args.decrypt:
            if not all([args.input_file, args.private_key, args.encrypted_key, args.output_file]):
                parser.error("Для дешифрования требуются --input-file, --private-key, --encrypted-key и --output-file")
            decrypt_file(args.input_file, args.private_key, args.encrypted_key, args.output_file)
    except Exception as e:
        print(f"Ошибка: {str(e)}")


if __name__ == "__main__":
    main()
