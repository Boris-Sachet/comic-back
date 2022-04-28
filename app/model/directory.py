from os.path import basename
from app.model import TypeModel


class Directory:

    def __init__(self, path: str):
        self.path = path
        self.name = basename(self.path)
        self.type = TypeModel.DIR
