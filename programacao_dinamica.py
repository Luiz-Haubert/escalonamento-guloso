"""
Escalonamento de tarefas com DURAÇÃO, prazo e multa (Programação Dinâmica).

Continuação do trabalho de Algoritmos Gulosos. Agora cada tarefa pode levar um tempo
diferente pra ser feita:
  - cada tarefa i tem duração p_i, prazo d_i e multa w_i;
  - só existe um processador, então uma tarefa roda por vez, sem interromper;
  - se a tarefa termina depois do prazo, pagamos a multa dela.
Objetivo: a menor multa total possível.

Ideia usada na PD: as tarefas que ficam no prazo sempre podem ser feitas em ordem
de prazo (a de prazo menor primeiro). Então a gente ordena tudo por prazo e decide,
uma por uma, se a tarefa entra na agenda (no prazo) ou se fica pro final (atrasada).

Estado: (i, t)
  i = qual tarefa estamos decidindo (na ordem de prazo)
  t = até que instante a agenda já está ocupada pelas tarefas que ficaram no prazo
Valor: a maior soma de multas que dá pra EVITAR com as tarefas i, i+1, ..., n-1.
Multa paga = soma de todas as multas - multa evitada.

Funções:
  - pd_recursiva_simples: recursão sem guardar nada (só pra mostrar quantas chamadas repete)
  - pd_bottom_up:         tabela preenchida de baixo pra cima, sem recursão
  - guloso_adaptado:      o guloso do trabalho anterior adaptado pra durações diferentes
  - forca_bruta:          testa todos os subconjuntos (só pra n pequeno, pra conferir)
"""

from bisect import insort
from dataclasses import dataclass
from itertools import combinations


@dataclass
class TarefaD:
    nome: str
    duracao: int  # quanto tempo a tarefa leva
    prazo: int    # até quando ela precisa terminar
    multa: int    # quanto pagamos se ela atrasar


@dataclass
class ResultadoD:
    agenda: list        # ordem de execução (no prazo primeiro, atrasadas depois)
    no_prazo: list
    atrasadas: list
    multa_total: int
    info: dict          # coisas extras pra mostrar nos testes (tabela, chamadas, etc.)


# ------------------------------------------------------------------ funções de apoio

def ordenar_por_prazo(tarefas):
    # sorted() é estável: se dois prazos forem iguais, mantém a ordem da entrada
    return sorted(tarefas, key=lambda t: t.prazo)


def cabe_no_prazo(conjunto):
    """Faz as tarefas em ordem de prazo e vê se todas terminam a tempo."""
    tempo = 0
    for tarefa in sorted(conjunto, key=lambda t: t.prazo):
        tempo += tarefa.duracao
        if tempo > tarefa.prazo:
            return False
    return True


def montar_resultado(no_prazo, todas, info):
    nomes_no_prazo = {id(t) for t in no_prazo}
    atrasadas = [t for t in todas if id(t) not in nomes_no_prazo]
    no_prazo = ordenar_por_prazo(no_prazo)
    multa_total = sum(t.multa for t in atrasadas)
    return ResultadoD(no_prazo + atrasadas, no_prazo, atrasadas, multa_total, info)


# ------------------------------------------------------------------ 1) recursão simples

def pd_recursiva_simples(tarefas):
    """
    Resolve com recursão pura, sem guardar nenhum resultado.
    Funciona, mas recalcula o mesmo estado (i, t) várias vezes. Serve pra comparar.
    Devolve (multa mínima, quantidade de chamadas).
    """
    ordem = ordenar_por_prazo(tarefas)
    n = len(ordem)
    chamadas = 0

    def melhor(i, t):
        nonlocal chamadas
        chamadas += 1
        if i == n:                      # caso básico: não sobrou tarefa
            return 0
        tarefa = ordem[i]
        pular = melhor(i + 1, t)        # decisão 1: a tarefa atrasa
        incluir = -1
        if t + tarefa.duracao <= tarefa.prazo:   # decisão 2: só se ainda termina no prazo
            incluir = tarefa.multa + melhor(i + 1, t + tarefa.duracao)
        return max(pular, incluir)

    evitada = melhor(0, 0)
    return sum(t.multa for t in tarefas) - evitada, chamadas


# ------------------------------------------------------------------ 2) bottom-up com tabela

def pd_bottom_up(tarefas, guardar_tabela=False):
    """
    Preenche a tabela melhor[i][t] da última tarefa pra primeira, sem recursão.

    melhor[i][t] = maior multa que dá pra evitar com as tarefas i..n-1,
                   sabendo que a agenda já está ocupada até o instante t.

    Pra economizar memória, os VALORES ficam só em duas linhas (a atual e a de baixo),
    e a escolha de cada estado (incluir ou não) fica numa matriz de bytes, que ocupa
    bem menos que uma matriz de números do Python. Com guardar_tabela=True a tabela
    inteira é guardada também, pra mostrar no teste pequeno.
    """
    ordem = ordenar_por_prazo(tarefas)
    n = len(ordem)
    # nenhuma tarefa no prazo passa do maior prazo, e o total não passa da soma das durações
    T = min(max((t.prazo for t in ordem), default=0), sum(t.duracao for t in ordem))
    T = max(T, 0)

    proxima = [0] * (T + 1)           # linha i+1 (começa como o caso básico i = n)
    escolheu = [None] * n             # escolheu[i][t] = 1 se incluir a tarefa i foi melhor
    tabela = [proxima[:]] if guardar_tabela else None

    for i in range(n - 1, -1, -1):
        tarefa = ordem[i]
        atual = proxima[:]            # decisão "pular": mesmo valor da linha de baixo
        marca = bytearray(T + 1)
        limite = min(tarefa.prazo, T) - tarefa.duracao   # maior t em que ela ainda cabe
        for t in range(0, limite + 1):
            incluir = tarefa.multa + proxima[t + tarefa.duracao]
            if incluir > atual[t]:
                atual[t] = incluir
                marca[t] = 1
        escolheu[i] = marca
        proxima = atual
        if guardar_tabela:
            tabela.append(atual[:])

    if guardar_tabela:
        tabela.reverse()              # deixa a linha 0 em cima

    # reconstrução da solução: começa em (0, 0) e segue as decisões guardadas
    no_prazo = []
    t = 0
    for i, tarefa in enumerate(ordem):
        if escolheu[i][t]:
            no_prazo.append(tarefa)
            t += tarefa.duracao

    info = {"T": T, "estados": n * (T + 1), "evitada": proxima[0] if n else 0,
            "tabela": tabela, "ordem": ordem}
    return montar_resultado(no_prazo, tarefas, info)


# ------------------------------------------------------------------ guloso adaptado

def guloso_adaptado(tarefas):
    """
    O guloso do trabalho anterior, só que pra durações diferentes:
    pega as tarefas da maior multa pra menor e aceita a tarefa se, junto com as que
    já foram aceitas, todo mundo ainda termina no prazo. Nunca volta atrás.
    Com todas as durações iguais a 1, ele é o mesmo guloso de antes (e acerta sempre).
    """
    aceitas = []                      # mantida em ordem de prazo
    for tarefa in sorted(tarefas, key=lambda t: t.multa, reverse=True):
        teste = aceitas[:]
        insort(teste, tarefa, key=lambda t: t.prazo)
        tempo = 0
        cabe = True
        for x in teste:
            tempo += x.duracao
            if tempo > x.prazo:
                cabe = False
                break
        if cabe:
            aceitas = teste
    return montar_resultado(aceitas, tarefas, {})


# ------------------------------------------------------------------ força bruta

def forca_bruta(tarefas):
    """Testa todos os 2^n subconjuntos. Só pra conferir com n pequeno."""
    melhor_evitada = 0
    for tamanho in range(1, len(tarefas) + 1):
        for sub in combinations(tarefas, tamanho):
            soma = sum(t.multa for t in sub)
            if soma > melhor_evitada and cabe_no_prazo(sub):
                melhor_evitada = soma
    return sum(t.multa for t in tarefas) - melhor_evitada
