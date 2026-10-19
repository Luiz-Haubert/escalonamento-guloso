"""
Escalonamento de tarefas unitárias com prazo e multa (algoritmo guloso).

Problema:
  - temos n tarefas, cada uma leva exatamente 1 unidade de tempo;
  - cada tarefa i tem um prazo d_i (inteiro >= 1) e uma multa w_i (>= 0);
  - só existe um processador, então só uma tarefa roda por vez;
  - se a tarefa i termina depois do prazo, pagamos a multa w_i.
Objetivo: achar uma ordem de execução que deixe a multa total a menor possível.

Estratégia gulosa: ordenar as tarefas pela multa (maior primeiro) e tentar
encaixar cada uma no ÚLTIMO horário livre que ainda respeite o prazo dela.
Se não tiver horário livre, a tarefa vai atrasar de qualquer jeito, então ela
é "descartada" e vai pro final da agenda.

Além do guloso, tem duas funções usadas só nos testes:
  - escalonar_forca_bruta: testa todos os subconjuntos (só pra n pequeno, pra conferir o resultado)
  - escalonar_por_prazo:   um critério guloso errado, pra mostrar na análise crítica
"""

from dataclasses import dataclass
from itertools import combinations


@dataclass
class Tarefa:
    nome: str
    prazo: int   # até qual unidade de tempo a tarefa precisa terminar
    multa: int   # quanto pagamos se ela atrasar


@dataclass
class Resultado:
    agenda: list            # ordem final de execução (no prazo primeiro, atrasadas depois)
    no_prazo: list          # tarefas que terminam dentro do prazo
    atrasadas: list         # tarefas descartadas (vão atrasar)
    multa_total: int        # soma das multas das atrasadas
    passos: list            # texto explicando cada decisão (usado no teste pequeno)


def escalonar_guloso(tarefas, registrar_passos=False):
    n = len(tarefas)

    # 1) ordena pela multa, da maior pra menor.
    #    sorted() é estável: com multas iguais, mantém a ordem da entrada.
    ordenadas = sorted(tarefas, key=lambda t: t.multa, reverse=True)

    # horarios[h] guarda a tarefa que roda no intervalo (h-1, h]; o índice 0 não é usado.
    # Nenhum prazo precisa passar de n, porque com n tarefas a agenda termina no tempo n.
    horarios = [None] * (n + 1)
    atrasadas = []
    passos = []

    for tarefa in ordenadas:
        # 2) procura o último horário livre que ainda respeita o prazo,
        #    descendo de um em um a partir do prazo
        limite = min(tarefa.prazo, n)
        h = limite
        while h >= 1 and horarios[h] is not None:
            h -= 1

        if h >= 1:
            # achou vaga: a tarefa é selecionada e fica nesse horário
            horarios[h] = tarefa
            if registrar_passos:
                passos.append(f"{tarefa.nome} (multa {tarefa.multa}, prazo {tarefa.prazo}) "
                              f"-> encaixada no horário {h}")
        else:
            # 3) não tem vaga até o prazo: vai atrasar de qualquer jeito, então é descartada
            atrasadas.append(tarefa)
            if registrar_passos:
                passos.append(f"{tarefa.nome} (multa {tarefa.multa}, prazo {tarefa.prazo}) "
                              f"-> horários 1..{limite} ocupados, DESCARTADA (vai atrasar)")

    # 4) monta a resposta: as tarefas no prazo já estão na ordem dos horários,
    #    e as atrasadas vão no final (em qualquer ordem, a multa é a mesma)
    no_prazo = [t for t in horarios[1:] if t is not None]
    multa_total = sum(t.multa for t in atrasadas)
    return Resultado(no_prazo + atrasadas, no_prazo, atrasadas, multa_total, passos)


def conjunto_viavel(subconjunto):
    """
    Um conjunto de tarefas consegue terminar todo no prazo se, ordenando por prazo,
    a i-ésima tarefa (contando de 1) tem prazo >= i.
    Ex.: três tarefas com prazo 2 não cabem, só existem 2 horários antes do instante 2.
    """
    prazos = sorted(t.prazo for t in subconjunto)
    return all(prazo >= i for i, prazo in enumerate(prazos, start=1))


def escalonar_forca_bruta(tarefas):
    """Testa todos os 2^n subconjuntos e pega o viável de maior multa evitada. Só pra n pequeno."""
    melhor_soma = -1
    for tamanho in range(len(tarefas) + 1):
        for sub in combinations(tarefas, tamanho):
            soma = sum(t.multa for t in sub)
            if soma > melhor_soma and conjunto_viavel(sub):
                melhor_soma = soma
    return sum(t.multa for t in tarefas) - melhor_soma


def escalonar_por_prazo(tarefas):
    """
    Critério guloso ERRADO, usado só pra comparação na análise crítica:
    pega as tarefas pelo prazo mais cedo, sem olhar a multa.
    """
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
