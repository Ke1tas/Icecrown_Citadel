from constants import (
    ALPHABET,
    ENCODED_MESSAGE_TXT,
    ENCRYPTION_KEY_TXT,
    ORIGINAL_MESSAGE_TXT,
)


def create_polybius_square(_key: str) -> str:
    """
    a function for creating a Polybius square using a key
    :param _key: encryption key
    :return: Polybius square
    """
    _key = ''.join(sorted(set(_key), key=_key.index))
    _key = _key.upper()
    square_key = _key + ''.join(ch for ch in ALPHABET if ch not in _key)

    return square_key


def square_to_pos(square: str) -> dict:
    """
    converts a Polybius square into a dictionary with a letter and a tuple of its coordinates
    :param square: Polybius square
    :return: dictionary with a letter and a tuple of its coordinates
    """
    return {char: (i // 6 + 1, i % 6 + 1) for i, char in enumerate(square)}


def encode_message(_message: str, square: str) -> str:
    """
    a function for encoding text using Polybius square
    :param _message: text to encrypt
    :param square: Polybius square
    :return: encrypted text
    """
    _encoded_message = ''
    encoder = square_to_pos(square)
    for char in _message.upper():
        if char in encoder:
            row, col = encoder[char]
            _encoded_message += f'{row}{col}'
        else:
            _encoded_message += char

    return _encoded_message


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
        print(f"File not found: {path}")
        raise
    except IOError as e:
        print(f"Input/output error: {e}")
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
        print(f"Error writing to file: {e}")
        raise


if __name__ == "__main__":
    try:
        key = read_file(ENCRYPTION_KEY_TXT)
        message = read_file(ORIGINAL_MESSAGE_TXT)

        polybius_square = create_polybius_square(key)

        encoded_message = encode_message(message, polybius_square)

        write_file(ENCODED_MESSAGE_TXT, encoded_message)
    except Exception as e:
        print(f"Error: {e}")
