"""
Programa principal: roda os testes do trabalho de Algoritmos Gulosos.

Como usar:
    python main.py                        -> roda tudo (testes 1, 2, 3 e validação)
    python main.py --teste 1              -> só o teste pequeno (passo a passo)
    python main.py --teste 2              -> só o teste médio
    python main.py --teste 3              -> só o teste grande (tabela de tempos)
    python main.py --validar              -> compara o guloso com a força bruta em várias instâncias aleatórias
    python main.py --arquivo minhas.csv   -> roda com tarefas de um arquivo CSV (nome,prazo,multa)
"""

import argparse
import csv
import os
import platform
import random
import sys
import time

from escalonamento import (
    Tarefa,
    escalonar_guloso,
    escalonar_forca_bruta,
    escalonar_por_prazo,
    conjunto_viavel,
)

SEMENTE = 2026  # semente fixa pra todo mundo gerar as mesmas instâncias
PASTA = os.path.dirname(os.path.abspath(__file__))  # pra achar a pasta entradas/ de qualquer lugar


# ---------------------------------------------------------------- entrada de dados

def carregar_csv(caminho):
    tarefas = []
    with open(caminho, newline="", encoding="utf-8") as arquivo:
        for linha in csv.DictReader(arquivo):
            tarefas.append(Tarefa(linha["nome"], int(linha["prazo"]), int(linha["multa"])))
    return tarefas


def gerar_tarefas(n, semente=SEMENTE):
    """
    Gera n tarefas aleatórias. O prazo vai de 1 até n/2, então sempre tem mais tarefa
    do que tempo disponível e o algoritmo é obrigado a descartar várias (fica mais
    interessante do que um caso em que tudo cabe). A multa vai de 1 a 1000.
    """
    rng = random.Random(semente)
    prazo_max = max(1, n // 2)
    return [Tarefa(f"T{i}", rng.randint(1, prazo_max), rng.randint(1, 1000)) for i in range(1, n + 1)]


# ---------------------------------------------------------------- saída

def imprimir_agenda(resultado):
    print(f"  {'tempo':>7} | {'tarefa':<8} | {'prazo':>5} | {'multa':>5} | situação")
    print("  " + "-" * 48)
    for tempo, t in enumerate(resultado.agenda, start=1):
        situacao = "no prazo" if tempo <= t.prazo else "ATRASADA"
        print(f"  {tempo:>7} | {t.nome:<8} | {t.prazo:>5} | {t.multa:>5} | {situacao}")
    print(f"\n  Multa total: {resultado.multa_total}")


def cronometrar(tarefas, repeticoes=3):
    """Roda o guloso algumas vezes e devolve o menor tempo em ms (menos ruído do SO)."""
    melhor = float("inf")
    resultado = None
    for _ in range(repeticoes):
        inicio = time.perf_counter()
        resultado = escalonar_guloso(tarefas)
        fim = time.perf_counter()
        melhor = min(melhor, (fim - inicio) * 1000)
    return melhor, resultado


def titulo(texto):
    print("\n" + "=" * 70)
    print(texto)
    print("=" * 70)


# ---------------------------------------------------------------- testes

def teste_pequeno():
    titulo("TESTE 1 - instância pequena (8 tarefas), passo a passo")
    tarefas = carregar_csv(os.path.join(PASTA, "entradas", "teste1_pequeno.csv"))

    print("\nEntrada:")
    for t in tarefas:
        print(f"  {t.nome}: prazo {t.prazo}, multa {t.multa}")

    print("\nOrdem depois de ordenar pela multa (maior primeiro):")
    print("  " + ", ".join(f"{t.nome}({t.multa})" for t in sorted(tarefas, key=lambda t: t.multa, reverse=True)))

    resultado = escalonar_guloso(tarefas, registrar_passos=True)
    print("\nDecisões do algoritmo:")
    for i, passo in enumerate(resultado.passos, start=1):
        print(f"  {i}. {passo}")

    print("\nAgenda final:")
    imprimir_agenda(resultado)

    multa_otima = escalonar_forca_bruta(tarefas)
    print(f"\n  Conferência com força bruta (2^{len(tarefas)} = {2 ** len(tarefas)} subconjuntos): "
          f"multa mínima = {multa_otima} -> {'IGUAL' if multa_otima == resultado.multa_total else 'DIFERENTE'}")
    print(f"  Comparação: se o critério fosse 'menor prazo primeiro', a multa seria {escalonar_por_prazo(tarefas)}")


def teste_medio():
    n = 1000
    titulo(f"TESTE 2 - instância média ({n} tarefas aleatórias, semente {SEMENTE})")
    tarefas = gerar_tarefas(n)

    print("\nPrimeiras 5 tarefas geradas:")
    for t in tarefas[:5]:
        print(f"  {t.nome}: prazo {t.prazo}, multa {t.multa}")

    tempo, _ = cronometrar(tarefas)
    resultado = escalonar_guloso(tarefas, registrar_passos=True)

    print("\nPrimeiras 10 decisões:")
    for passo in resultado.passos[:10]:
        print("  " + passo)

    multa_maxima = sum(t.multa for t in tarefas)
    print("\nResultado:")
    print(f"  Tarefas no prazo:  {len(resultado.no_prazo)} de {n}")
    print(f"  Tarefas atrasadas: {len(resultado.atrasadas)}")
    print(f"  Multa total:       {resultado.multa_total}")
    print(f"  Multa se tudo atrasasse: {multa_maxima} "
          f"(o guloso evitou {100 * (1 - resultado.multa_total / multa_maxima):.1f}% dela)")
    print(f"  Multa média das atrasadas: {resultado.multa_total / len(resultado.atrasadas):.1f} "
          f"(média geral: {multa_maxima / n:.1f})")
    print(f"  Agenda das tarefas no prazo é viável? {conjunto_viavel(resultado.no_prazo)}")
    print(f"\n  Tempo de execução: {tempo:.3f} ms")


def teste_grande():
    titulo("TESTE 3 - instâncias grandes (tempo de execução)")
    print(f"Python {platform.python_version()} | {platform.system()} {platform.release()} | "
          f"{platform.processor() or platform.machine()}")
    print("Tempo em ms, inclui a ordenação (menor de 3 execuções até 10.000; 1 execução acima disso).\n")

    tamanhos = [1_000, 5_000, 10_000, 20_000, 50_000]
    linhas = []

    print(f"  {'n':>8} | {'tempo (ms)':>12} | {'no prazo':>9} | {'atrasadas':>9} | {'multa total':>12}")
    print("  " + "-" * 64)
    for n in tamanhos:
        tarefas = gerar_tarefas(n)
        tempo, r = cronometrar(tarefas, 3 if n <= 10_000 else 1)
        print(f"  {n:>8} | {tempo:12.2f} | {len(r.no_prazo):>9} | {len(r.atrasadas):>9} | {r.multa_total:>12}")
        sys.stdout.flush()
        linhas.append([n, f"{tempo:.2f}", len(r.no_prazo), len(r.atrasadas), r.multa_total])

    with open("resultados_tempos.csv", "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["n", "tempo_ms", "no_prazo", "atrasadas", "multa_total"])
        escritor.writerows(linhas)
    print("\n  (tabela salva em resultados_tempos.csv)")


def validar(quantidade=500):
    titulo(f"VALIDAÇÃO - guloso x força bruta em {quantidade} instâncias aleatórias (n de 1 a 12)")
    rng = random.Random(SEMENTE)
    erros = 0
    for _ in range(quantidade):
        n = rng.randint(1, 12)
        tarefas = [Tarefa(f"T{i}", rng.randint(1, n), rng.randint(1, 50)) for i in range(1, n + 1)]
        if escalonar_guloso(tarefas).multa_total != escalonar_forca_bruta(tarefas):
            erros += 1
    print(f"  Instâncias em que o guloso NÃO achou o ótimo: {erros} de {quantidade}")


def rodar_arquivo(caminho):
    titulo(f"Arquivo: {caminho}")
    resultado = escalonar_guloso(carregar_csv(caminho), registrar_passos=True)
    for i, passo in enumerate(resultado.passos, start=1):
        print(f"  {i}. {passo}")
    print()
    imprimir_agenda(resultado)


# ---------------------------------------------------------------- main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Escalonamento de tarefas com prazo e multa (guloso)")
    parser.add_argument("--teste", type=int, choices=[1, 2, 3])
    parser.add_argument("--validar", action="store_true")
    parser.add_argument("--arquivo")
    args = parser.parse_args()

    if args.arquivo:
        rodar_arquivo(args.arquivo)
    elif args.teste == 1:
        teste_pequeno()
    elif args.teste == 2:
        teste_medio()
    elif args.teste == 3:
        teste_grande()
    elif args.validar:
        validar()
    else:
        teste_pequeno()
        validar()
        teste_medio()
        teste_grande()
