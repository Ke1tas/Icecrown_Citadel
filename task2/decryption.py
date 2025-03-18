import collections

from constants import (
    ENCRYPTED_TEXT_TXT,
    DECRYPTED_TEXT_TXT,
    DECRYPTION_KEY_TXT,
    TABLE_FREQUENCY_TXT
)


def read_file(path: str) -> str:
    """
    returns the text contained in the file
    :param path: file path
    :return: sting with text
    """
    try:
        with open(path, 'r', encoding='utf-8') as key_file:
            return key_file.read()
    except FileNotFoundError:
        print(f"Файл не найден: {path}")
        raise
    except IOError as e:
        print(f"Ошибка ввода-вывода: {e}")
        raise


def write_file(path: str, text: str) -> None:
    """
    writes the contents of a string to a file
    :param path: file path
    :param text: written text
    :return: None
    """
    try:
        with open(path, 'w', encoding='utf-8') as file:
            file.write(text)
    except IOError as e:
        print(f"Ошибка записи в файл: {e}")
        raise


def read_dict(path: str) -> dict:
    """
    returns the dictionary contained in the file
    :param path: file path
    :return: dictionary from the file
    """
    key = {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '->' in line:
                    k, v = line.split('->')
                    if v.strip() == '':
                        key[k.strip()] = ' '
                    elif k.strip() == '':
                        key[' '] = v.strip()
                    else:
                        key[k.strip()] = v.strip()
    except FileNotFoundError:
        print(f"Файл не найден: {path}")
        raise
    except IOError as e:
        print(f"Ошибка ввода-вывода: {e}")
        raise
    return key


def frequency_analysis(text: str) -> dict:
    """
    analyzes the frequency of occurrence of characters in the text
    :param text: text being analyzed
    :return: dictionary with symbols and their frequencies
    """
    text = text.replace("\n", "")
    total_chars = len(text)
    freq_counter = collections.Counter(text)
    frequency = {char: count / total_chars for char, count in freq_counter.items()}
    return frequency


def decrypt(text: str, key: dict) -> str:
    """
    decrypts text by key
    :param text: text to decrypt
    :param key: encryption key
    :return: decrypted text
    """
    decrypted_text = ''.join(key.get(char, char) for char in text)
    return decrypted_text


if __name__ == "__main__":
    try:
        frequency_table = read_dict(TABLE_FREQUENCY_TXT)
        print(frequency_table)

        encrypted_text = read_file(ENCRYPTED_TEXT_TXT)

        freq = frequency_analysis(encrypted_text)
        sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        print(sorted_freq)

        key = read_dict(DECRYPTION_KEY_TXT)

        decrypted_text = decrypt(encrypted_text, key)
        write_file(DECRYPTED_TEXT_TXT, decrypted_text)
    except Exception as e:
        print(f"Error: {e}")
