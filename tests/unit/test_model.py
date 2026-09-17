#Testes unitários para o agregado cliente
#Primeiro teste: verificar se um cliente consegue cadastrar um veículo

from uuid import uuid4

import estacionamento.domain.model


def test_cliente_pode_cadastrar_um_veiculo():
    cliente = estacionamento.domain.model.Cliente(
        id_cliente=uuid4(),
        nome="João",
        cpf="11111111111",
        telefone="21999999999",
        email="joao@email.com",
    )

    veiculo = estacionamento.domain.model.Veiculo(
        id_veiculo=uuid4(),
        placa=estacionamento.domain.model.Placa("ABC1D23"),
        tipo="Carro",
    )

    cliente.cadastrar_veiculo(veiculo)

    assert veiculo in cliente.veiculos
    
#Fim do primeiro teste no agregado cliente
  
