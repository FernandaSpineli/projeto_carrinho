from ast import NotIn
from pickle import NONE
from queue import Empty
from typing import List
from fastapi import FastAPI

from model import (
    Usuario, db_usuarios,
    Produto, db_produtos,
    Endereco, db_end, ListaDeEnderecosDoUsuario,
    CarrinhoDeCompras, db_carrinhos, TotalDoCarrinho
)

app = FastAPI()

OK = "OK"
FALHA = "FALHA"

@app.post("/usuarios")
async def criar_usuário(usuario: Usuario):    
    for user in db_usuarios.values():
      if user.id == usuario.id:
        return "Código de usuário já cadastrado"
      if user.email == usuario.email:
        return "E-mail já cadastrado"

    db_usuarios[usuario.id] = usuario

    return OK


@app.get("/usuarios")
async def retornar_usuario(id: int):
    if not id in db_usuarios:
      return FALHA
    
    return db_usuarios[id]
    
    
@app.get("/usuarios/nome")
async def retornar_usuario_com_nome(nome: str):
    for user in db_usuarios.values():
      if user.nome == nome:
        return user
    return FALHA


@app.delete("/usuarios/{id}")
async def deletar_usuario(id: int):
    if id not in db_usuarios:
      return FALHA

    excluirEnderecosDoUsuario(id)
    excluirCarrinhoDoUsuario(id)

    db_usuarios.pop(id)

    return OK


@app.get("/usuarios/{id_usuario}/enderecos")
async def retornar_enderecos_do_usuario(id_usuario: int):
    if not id_usuario in db_usuarios:
      return FALHA
    
    enderecos: List[Endereco] = []

    for item in db_end.values():
      eUsuario = (item.usuario.id == id_usuario)
      temEndereco = len(item.enderecos) > 0
      if eUsuario and temEndereco:
        enderecos.append(item.enderecos[0])

    return enderecos


@app.get("/usuarios/emails")
async def retornar_emails(dominio: str):
    emails = []
    for usuario in db_usuarios.values():
      dominioEmail = usuario.email.split("@")[1]
      if dominioEmail.find(dominio) > -1:
        emails.append(usuario.email)

    if len(emails) > 0:
      return emails

    return FALHA


@app.post("/usuarios/{id_usuario}/enderecos")
async def criar_endereco(endereco: Endereco, id_usuario: int):
    if not id_usuario in db_usuarios:
      return FALHA

    id_endereco = len(db_end) + 1

    usuario = db_usuarios[id_usuario]
    enderecos = [endereco]
    novo_endereco = ListaDeEnderecosDoUsuario(usuario=usuario, enderecos=enderecos)
    db_end[id_endereco] = novo_endereco

    return OK


@app.delete("/enderecos/{id_endereco}")
async def deletar_endereco(id_endereco: int):
    if not id_endereco in db_end:
      return FALHA

    db_end.pop(id_endereco)
    return OK


@app.post("/produtos")
async def criar_produto(produto: Produto):
    idProduto = produto.id

    if idProduto in db_produtos:
      return FALHA

    db_produtos[idProduto] = produto
    return OK


@app.delete("/produtos/{id_produto}")
async def deletar_produto(id_produto: int):
    if not id_produto in db_produtos:
      return FALHA

    for carrinho in db_carrinhos.values():
      excluirProdutoDoCarrinho(carrinho, id_produto)

    db_produtos.pop(id_produto)

    return OK


@app.post("/usuarios/{id_usuario}/carrinhos/produtos/{id_produto}")
async def adicionar_carrinho(id_usuario: int, id_produto: int):
    naoExisteUsuario = not id_usuario in db_usuarios
    naoExisteProduto = not id_produto in db_produtos

    if naoExisteUsuario or naoExisteProduto:
      return FALHA

    produto = db_produtos[id_produto]
    carrinho = buscaCarrinhoUsuario(id_usuario)

    if carrinho == None:
      carrinho = CarrinhoDeCompras(
        id_usuario=id_usuario,
        preco_total=0.0,
        quantidade_de_produtos=0
      )

    carrinho.produtos.append(produto)
    carrinho.quantidade_de_produtos += 1
    carrinho.preco_total += produto.preco

    db_carrinhos[id_usuario] = carrinho

    return OK


@app.get("/usuarios/{id_usuario}/carrinhos")
async def retornar_carrinho(id_usuario: int):
    carrinho = buscaCarrinhoUsuario(id_usuario)

    if carrinho != None:
      return carrinho

    return FALHA


@app.get("/usuarios/{id_usuario}/carrinhos/valor")
async def retornar_total_carrinho(id_usuario: int):
    carrinho = buscaCarrinhoUsuario(id_usuario)
    if carrinho != None:
      itens = carrinho.quantidade_de_produtos
      valor = carrinho.preco_total
      return TotalDoCarrinho(quantidade_de_itens=itens, valor_total=valor)

    return FALHA


@app.delete("/usuarios/{id_usuario}/carrinhos")
async def deletar_carrinho(id_usuario: int):
    carrinhoParaExcluir = -1

    for key in db_carrinhos:
      if db_carrinhos[key].id_usuario == id_usuario:
        carrinhoParaExcluir = key
        break
    
    if carrinhoParaExcluir > -1:
      db_carrinhos.pop(carrinhoParaExcluir)
      return OK

    return FALHA


@app.get("/")
async def bem_vinda():
    site = "Seja bem vinda"
    return site.replace('\n', '')


def buscaCarrinhoUsuario(id_usuario):
  for carrinho in db_carrinhos.values():
    if carrinho.id_usuario == id_usuario:
      return carrinho


def excluirProdutoDoCarrinho(carrinho: CarrinhoDeCompras, idProduto: int):
  produtos = carrinho.produtos
  produto = db_produtos[idProduto]
  while produto in produtos:
    produtos.remove(produto)
    carrinho.quantidade_de_produtos -= 1
    carrinho.preco_total -= produto.preco


def excluirEnderecosDoUsuario(id: int):
  enderecosParaDeletar: List[int] = []

  for index in db_end:
    item = db_end[index]
    if item.usuario.id == id:
      enderecosParaDeletar.append(index)

  for key in enderecosParaDeletar:
    db_end.pop(key)


def excluirCarrinhoDoUsuario(id: int):
  idCarrinho = -1
  for index in db_carrinhos:
    carrinho = db_carrinhos[index]
    if carrinho.id_usuario == id:
      idCarrinho = index
      break

  if idCarrinho > -1:
    db_carrinhos.pop(idCarrinho)

