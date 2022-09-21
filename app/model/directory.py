from os.path import basename
from app.enums.type_model import TypeModel


class Directory:

    def __init__(self, path: str):
        self.path = path
        self.name = basename(self.path)
        self.type = TypeModel.DIR
