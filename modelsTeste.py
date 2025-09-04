from config import *

db = Database()

class UsuarioTeste(db.Entity):
    id = PrimaryKey(int, auto=True) 
    nome = Required(str)
    sobrenome = Required(str)
    username = Required(str, unique=True)
    email = Required(str, unique=True)
    senha = Required(str)

db.bind(provider='sqlite', filename='teste.sqlite', create_db=True)
db.generate_mapping(create_tables=True)