from app.model.library_model import LibraryModel


def create_library_model(name: str, path: str, hidden: bool) -> LibraryModel:
    library_dict = {
        "name": name,
        "path": path,
        "hidden": hidden
    }
    return LibraryModel(**library_dict)
