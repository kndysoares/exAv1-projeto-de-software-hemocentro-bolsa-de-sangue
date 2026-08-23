from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Iterable


class SemBolsaCompativel(Exception):
    """Exceção de domínio: nenhuma bolsa pode atender a requisição."""
    pass


@dataclass(frozen=True)
class Volume:
    """Bônus (b): Volume como Objeto de Valor imutável."""
    valor_ml: int

    def __post_init__(self) -> None:
        if self.valor_ml < 0:
            raise ValueError("Volume não pode ser negativo")

    def __add__(self, other: Volume) -> Volume:
        return Volume(self.valor_ml + other.valor_ml)

    def __sub__(self, other: Volume) -> Volume:
        return Volume(self.valor_ml - other.valor_ml)

    def __lt__(self, other: Volume) -> bool:
        return self.valor_ml < other.valor_ml

    def __le__(self, other: Volume) -> bool:
        return self.valor_ml <= other.valor_ml

    def __ge__(self, other: Volume) -> bool:
        return self.valor_ml >= other.valor_ml


@dataclass(frozen=True)
class Requisicao:
    codigo: str
    tipo_sanguineo: str
    volume_ml: int


class Bolsa:
    def __init__(self, codigo: str, tipo_sanguineo: str, volume_ml: int, data_validade: date):
        self.codigo = codigo
        self.tipo_sanguineo = tipo_sanguineo
        self.volume_ml = volume_ml
        self.data_validade = data_validade
        self._reservas: set[Requisicao] = set()

    @property
    def volume_reservado(self) -> int:
        """Soma dos volumes das requisições já reservadas nesta bolsa."""
        return sum(req.volume_ml for req in self._reservas)

    @property
    def volume_disponivel(self) -> int:
        """Volume coletado menos volume reservado."""
        return self.volume_ml - self.volume_reservado

    def esta_vencida(self, hoje: date) -> bool:
        return self.data_validade < hoje

    def pode_atender(self, requisicao: Requisicao, hoje: date) -> bool:
        """Regras R1, R2 e R3."""
        if self.esta_vencida(hoje):
            return False
        if self.tipo_sanguineo != requisicao.tipo_sanguineo:
            return False
        # R4: Se a requisição já foi reservada, ela continua sendo atendida sem somar novo volume
        if requisicao in self._reservas:
            return True
        return self.volume_disponivel >= requisicao.volume_ml

    def reservar(self, requisicao: Requisicao, hoje: date) -> None:
        """Regra R4: reservar a mesma requisição duas vezes não desconta duas vezes."""
        if self.pode_atender(requisicao, hoje):
            self._reservas.add(requisicao)

    def cancelar_reserva(self, requisicao: Requisicao) -> None:
        """Regra R5: cancelar reserva inexistente não é erro."""
        self._reservas.discard(requisicao)

    def __hash__(self) -> int:
        return hash(self.codigo)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Bolsa):
            return False
        return self.codigo == other.codigo

    def __lt__(self, other: Bolsa) -> bool:
        """Regra R6: FEFO (data_validade) com desempate alfabético por código."""
        if self.data_validade == other.data_validade:
            return self.codigo < other.codigo
        return self.data_validade < other.data_validade


def reservar_para(requisicao: Requisicao, bolsas: Iterable[Bolsa], hoje: date) -> str:
    """Reserva a requisição na melhor bolsa disponível (R6) e devolve o código dessa bolsa.
    Levanta SemBolsaCompativel se nenhuma bolsa puder atender (R7).
    """
    bolsas_candidatas = [b for b in bolsas if b.pode_atender(requisicao, hoje)]
    if not bolsas_candidatas:
        raise SemBolsaCompativel()

    melhor_bolsa = min(bolsas_candidatas)
    melhor_bolsa.reservar(requisicao, hoje)
    return melhor_bolsa.codigo
