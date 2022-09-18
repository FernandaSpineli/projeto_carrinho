from typing import List
from pydantic import BaseModel

class Endereco(BaseModel):
    rua: str
    cep: str
    cidade: str
    estado: str

class Usuario(BaseModel):
    id: int
    nome: str
    email: str
    senha: str

class ListaDeEnderecosDoUsuario(BaseModel):
    usuario: Usuario
    enderecos: List[Endereco] = []

class Produto(BaseModel):
    id: int
    nome: str
    descricao: str
    preco: float

class CarrinhoDeCompras(BaseModel):
    id_usuario: int
    produtos: List[Produto] = [] 
    preco_total: float
    quantidade_de_produtos: int

class TotalDoCarrinho(BaseModel):
    quantidade_de_itens: int
    valor_total: float


db_usuarios = {}
db_produtos = {}
db_end = {} # enderecos_dos_usuarios
db_carrinhos = {}
