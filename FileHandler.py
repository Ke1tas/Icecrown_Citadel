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
