from app.model.library_model import LibraryModel


def create_library_model(name: str, path: str, hidden: bool, connect_type: str) -> LibraryModel:
    library_dict = {
        "name": name,
        "path": path,
        "hidden": hidden,
        "connect_type": connect_type
    }
    return LibraryModel(**library_dict)
