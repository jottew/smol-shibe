class Config:
    def __init__(self, file: str):
        self._file = __import__(file)

    def __getattr__(self, attr):
        return getattr(self._file, attr)

    def get(self, attr):
        return self.__getattr__(attr)

    def __getitem__(self, attr):
        return self.__getattr__(attr)
