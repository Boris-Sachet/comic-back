from app.model.library_model import LibraryModel


def create_library_model(name: str, path: str, hidden: bool, connect_type: str, user: str | None, passsword: str | None
                         ) -> LibraryModel:
    library_dict = {
        "name": name,
        "path": path,
        "hidden": hidden,
        "connect_type": connect_type,
        "user": user,
        "password": passsword
    }
    return LibraryModel(**library_dict)
