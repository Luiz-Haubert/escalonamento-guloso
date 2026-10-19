from dataclasses import dataclass
from itertools import combinations


@dataclass
class Tarefa:
    nome: str
    prazo: int
    multa: int


@dataclass
class Resultado:
    agenda: list
    no_prazo: list
    atrasadas: list
    multa_total: int
    passos: list


def escalonar_guloso(tarefas, registrar_passos=False):
    n = len(tarefas)

    ordenadas = sorted(tarefas, key=lambda t: t.multa, reverse=True)

    horarios = [None] * (n + 1)
    atrasadas = []
    passos = []

    for tarefa in ordenadas:
        limite = min(tarefa.prazo, n)
        h = limite
        while h >= 1 and horarios[h] is not None:
            h -= 1

        if h >= 1:
            horarios[h] = tarefa
            if registrar_passos:
                passos.append(f"{tarefa.nome} (multa {tarefa.multa}, prazo {tarefa.prazo}) "
                              f"-> encaixada no horário {h}")
        else:
            atrasadas.append(tarefa)
            if registrar_passos:
                passos.append(f"{tarefa.nome} (multa {tarefa.multa}, prazo {tarefa.prazo}) "
                              f"-> horários 1..{limite} ocupados, DESCARTADA (vai atrasar)")


    no_prazo = [t for t in horarios[1:] if t is not None]
    multa_total = sum(t.multa for t in atrasadas)
    return Resultado(no_prazo + atrasadas, no_prazo, atrasadas, multa_total, passos)


def conjunto_viavel(subconjunto):

    prazos = sorted(t.prazo for t in subconjunto)
    return all(prazo >= i for i, prazo in enumerate(prazos, start=1))


def escalonar_forca_bruta(tarefas):
    melhor_soma = -1
    for tamanho in range(len(tarefas) + 1):
        for sub in combinations(tarefas, tamanho):
            soma = sum(t.multa for t in sub)
            if soma > melhor_soma and conjunto_viavel(sub):
                melhor_soma = soma
    return sum(t.multa for t in tarefas) - melhor_soma


def escalonar_por_prazo(tarefas):
    n = len(tarefas)
    horarios = [None] * (n + 1)
    multa_total = 0
    for tarefa in sorted(tarefas, key=lambda t: t.prazo):
        h = min(tarefa.prazo, n)
        while h >= 1 and horarios[h] is not None:
            h -= 1
        if h >= 1:
            horarios[h] = tarefa
        else:
            multa_total += tarefa.multa
    return multa_total
