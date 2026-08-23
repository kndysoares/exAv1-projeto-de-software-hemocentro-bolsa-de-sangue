from datetime import date, timedelta
import pytest
from dominio import Bolsa, Requisicao, SemBolsaCompativel, Volume, reservar_para

HOJE = date(2026, 8, 20)


# --- OS 9 TESTES OBRIGATÓRIOS (Parte 3) ---

def test_reservar_reduz_o_volume_disponivel():
    bolsa = Bolsa("BOLSA-01", "A+", 500, HOJE + timedelta(days=10))
    req = Requisicao("REQ-01", "A+", 200)

    bolsa.reservar(req, HOJE)

    assert bolsa.volume_disponivel == 300


def test_nao_atende_quando_o_volume_e_insuficiente():
    bolsa = Bolsa("BOLSA-01", "A+", 300, HOJE + timedelta(days=10))
    req = Requisicao("REQ-01", "A+", 400)

    assert bolsa.pode_atender(req, HOJE) is False


def test_nao_atende_quando_o_tipo_sanguineo_e_diferente():
    bolsa = Bolsa("BOLSA-01", "A+", 500, HOJE + timedelta(days=10))
    req = Requisicao("REQ-01", "O-", 200)

    assert bolsa.pode_atender(req, HOJE) is False


def test_nao_atende_quando_a_bolsa_esta_vencida():
    bolsa = Bolsa("BOLSA-01", "A+", 500, HOJE - timedelta(days=1))
    req = Requisicao("REQ-01", "A+", 200)

    assert bolsa.pode_atender(req, HOJE) is False


def test_reservar_a_mesma_requisicao_duas_vezes_e_idempotente():
    bolsa = Bolsa("BOLSA-01", "A+", 500, HOJE + timedelta(days=10))
    req = Requisicao("REQ-01", "A+", 200)

    bolsa.reservar(req, HOJE)
    bolsa.reservar(req, HOJE)

    assert bolsa.volume_disponivel == 300


def test_cancelar_reserva_inexistente_nao_altera_o_volume():
    bolsa = Bolsa("BOLSA-01", "A+", 500, HOJE + timedelta(days=10))
    req = Requisicao("REQ-01", "A+", 200)

    bolsa.cancelar_reserva(req)

    assert bolsa.volume_disponivel == 500


def test_bolsas_com_o_mesmo_codigo_sao_iguais_mesmo_com_volumes_diferentes():
    bolsa1 = Bolsa("BOLSA-01", "A+", 500, HOJE + timedelta(days=10))
    bolsa2 = Bolsa("BOLSA-01", "A+", 300, HOJE + timedelta(days=10))

    assert bolsa1 == bolsa2


def test_requisicoes_com_os_mesmos_dados_sao_iguais():
    req1 = Requisicao("REQ-01", "A+", 200)
    req2 = Requisicao("REQ-01", "A+", 200)

    assert req1 == req2


def test_prefere_a_bolsa_que_vence_primeiro():
    bolsa_longa = Bolsa("BOLSA-01", "A+", 500, HOJE + timedelta(days=20))
    bolsa_curta = Bolsa("BOLSA-02", "A+", 500, HOJE + timedelta(days=5))
    req = Requisicao("REQ-01", "A+", 200)

    codigo_reservado = reservar_para(req, [bolsa_longa, bolsa_curta], HOJE)

    assert codigo_reservado == "BOLSA-02"


# --- OS 2 TESTES ADICIONAIS (Parte 4) ---

def test_levanta_sem_bolsa_compativel_quando_nenhuma_bolsa_atende():
    bolsa = Bolsa("BOLSA-01", "O-", 500, HOJE + timedelta(days=10))
    req = Requisicao("REQ-01", "A+", 200)

    with pytest.raises(SemBolsaCompativel):
        reservar_para(req, [bolsa], HOJE)


def test_ignora_bolsa_vencida_mesmo_que_ela_vencesse_antes():
    bolsa_vencida = Bolsa("BOLSA-01", "A+", 500, HOJE - timedelta(days=2))
    bolsa_valida = Bolsa("BOLSA-02", "A+", 500, HOJE + timedelta(days=5))
    req = Requisicao("REQ-01", "A+", 200)

    codigo_reservado = reservar_para(req, [bolsa_vencida, bolsa_valida], HOJE)

    assert codigo_reservado == "BOLSA-02"


# --- TESTES DO BÔNUS (b) ---

def test_volume_suporta_operacoes_matematicas_e_comparacao():
    v1 = Volume(300)
    v2 = Volume(200)

    assert (v1 + v2) == Volume(500)
    assert (v1 - v2) == Volume(100)
    assert v2 < v1


def test_volume_recusa_valores_negativos():
    with pytest.raises(ValueError):
        Volume(-50)
