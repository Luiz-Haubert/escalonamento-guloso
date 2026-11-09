"""
Testes da parte 2 do trabalho (Aula 10: Programação Dinâmica).

Como usar:
    python main_pd.py                         -> roda tudo
    python main_pd.py --teste 1               -> instância pequena, passo a passo (tabela e decisões)
    python main_pd.py --teste 2               -> instância média (guloso x PD)
    python main_pd.py --teste 3               -> instâncias grandes (tempo de execução)
    python main_pd.py --validar               -> confere a PD com a força bruta em várias instâncias
    python main_pd.py --arquivo minhas.csv    -> roda com um CSV (nome,duracao,prazo,multa)
"""

import argparse
import csv
import os
import platform
import random
import sys
import time

from programacao_dinamica import (
    TarefaD,
    pd_recursiva_simples,
    pd_bottom_up,
    guloso_adaptado,
    forca_bruta,
    cabe_no_prazo,
)
from escalonamento import Tarefa, escalonar_guloso   # guloso original do trabalho anterior

SEMENTE = 2026
PASTA = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------- entrada de dados

def carregar_csv(caminho):
    tarefas = []
    with open(caminho, newline="", encoding="utf-8") as arquivo:
        for linha in csv.DictReader(arquivo):
            duracao = int(linha.get("duracao") or 1)   # CSV do trabalho anterior não tem duração
            tarefas.append(TarefaD(linha["nome"], duracao, int(linha["prazo"]), int(linha["multa"])))
    return tarefas


def gerar_tarefas(n, semente=SEMENTE):
    """
    n tarefas aleatórias: duração de 1 a 10, multa de 1 a 1000 e prazo de 1 até
    metade da soma das durações. Assim nunca dá pra fazer todas no prazo e o
    algoritmo precisa escolher quais deixar atrasar.
    """
    rng = random.Random(semente)
    duracoes = [rng.randint(1, 10) for _ in range(n)]
    prazo_max = max(1, sum(duracoes) // 2)
    return [TarefaD(f"T{i + 1}", duracoes[i], rng.randint(1, prazo_max), rng.randint(1, 1000))
            for i in range(n)]


# ---------------------------------------------------------------- saída

def titulo(texto):
    print("\n" + "=" * 72)
    print(texto)
    print("=" * 72)


def imprimir_agenda(resultado):
    print(f"  {'início':>6} | {'fim':>4} | {'tarefa':<6} | {'dur':>3} | {'prazo':>5} | {'multa':>5} | situação")
    print("  " + "-" * 60)
    tempo = 0
    for t in resultado.agenda:
        inicio, tempo = tempo, tempo + t.duracao
        situacao = "no prazo" if tempo <= t.prazo else "ATRASADA"
        print(f"  {inicio:>6} | {tempo:>4} | {t.nome:<6} | {t.duracao:>3} | {t.prazo:>5} | {t.multa:>5} | {situacao}")
    print(f"\n  Multa total: {resultado.multa_total}")


def cronometrar(funcao, tarefas, repeticoes=3):
    melhor, resultado = float("inf"), None
    for _ in range(repeticoes):
        inicio = time.perf_counter()
        resultado = funcao(tarefas)
        melhor = min(melhor, (time.perf_counter() - inicio) * 1000)
    return melhor, resultado


# ---------------------------------------------------------------- testes

def teste_pequeno():
    titulo("TESTE 1 - instância pequena (5 tarefas com durações diferentes)")
    tarefas = carregar_csv(os.path.join(PASTA, "entradas", "pd_teste1.csv"))
    print("\nEntrada:")
    for t in tarefas:
        print(f"  {t.nome}: duração {t.duracao}, prazo {t.prazo}, multa {t.multa}")

    r = pd_bottom_up(tarefas, guardar_tabela=True)
    ordem, T, tabela = r.info["ordem"], r.info["T"], r.info["tabela"]
    print("\nOrdem por prazo (i = 0, 1, 2...): " + ", ".join(f"{i}:{t.nome}" for i, t in enumerate(ordem)))

    print(f"\nTabela bottom-up: melhor[i][t] = maior multa evitada com as tarefas i..{len(ordem) - 1}")
    print("(t = até onde a agenda já está ocupada; a tabela é preenchida de baixo pra cima)\n")
    print("        " + "".join(f"t={t:<4}" for t in range(T + 1)))
    for i, linha in enumerate(tabela):
        nome = ordem[i].nome if i < len(ordem) else "-"
        print(f"  i={i} {nome:<3}" + "".join(f"{v:<6}" for v in linha))

    print("\nDecisões (seguindo a tabela a partir de i=0, t=0):")
    t = 0
    soma_total = sum(x.multa for x in tarefas)
    for i, tarefa in enumerate(ordem):
        pular = tabela[i + 1][t]
        if t + tarefa.duracao <= tarefa.prazo:
            incluir = tarefa.multa + tabela[i + 1][t + tarefa.duracao]
            if incluir > pular:
                print(f"  {tarefa.nome}: incluir vale {incluir}, pular vale {pular} -> INCLUI (roda de {t} a {t + tarefa.duracao})")
                t += tarefa.duracao
            else:
                print(f"  {tarefa.nome}: incluir vale {incluir}, pular vale {pular} -> pula (vai atrasar)")
        else:
            print(f"  {tarefa.nome}: não termina no prazo começando em {t} -> pula (vai atrasar)")
    print(f"\n  Multa evitada: {r.info['evitada']} de {soma_total}")

    print("\nAgenda da PD:")
    imprimir_agenda(r)

    g = guloso_adaptado(tarefas)
    print("\nAgenda do guloso (maior multa primeiro):")
    imprimir_agenda(g)

    print(f"\n  Força bruta: multa mínima = {forca_bruta(tarefas)}")
    simples, chamadas = pd_recursiva_simples(tarefas)
    print(f"  Recursão simples (sem tabela): multa {simples}, {chamadas} chamadas")
    print(f"  PD bottom-up: multa {r.multa_total}, {len(ordem)} x {T + 1} = {r.info['estados']} estados, cada um calculado uma vez")

    titulo("TESTE 1b - recursão simples x tabela (quanto trabalho cada uma faz)")
    print(f"  {'n':>4} | {'chamadas da recursão':>20} | {'estados da tabela':>17}")
    print("  " + "-" * 50)
    for n in [5, 10, 15, 20, 22]:
        inst = gerar_tarefas(n)
        _, chamadas = pd_recursiva_simples(inst)
        bu = pd_bottom_up(inst)
        print(f"  {n:>4} | {chamadas:>20} | {bu.info['estados']:>17}")

    titulo("TESTE 1c - mesmas 8 tarefas de duração 1 do trabalho anterior")
    unit = carregar_csv(os.path.join(PASTA, "entradas", "teste1_pequeno.csv"))
    r = pd_bottom_up(unit)
    print(f"  PD bottom-up: multa {r.multa_total}  |  guloso adaptado: {guloso_adaptado(unit).multa_total}"
          f"  |  força bruta: {forca_bruta(unit)}")
    print("  No prazo pela PD: " + ", ".join(t.nome for t in r.no_prazo))


def teste_medio():
    n = 500
    titulo(f"TESTE 2 - instância média ({n} tarefas aleatórias, semente {SEMENTE})")
    tarefas = gerar_tarefas(n)
    print("\nPrimeiras 5 tarefas:")
    for t in tarefas[:5]:
        print(f"  {t.nome}: duração {t.duracao}, prazo {t.prazo}, multa {t.multa}")

    tempo_bu, r = cronometrar(pd_bottom_up, tarefas)
    tempo_g, g = cronometrar(guloso_adaptado, tarefas)
    soma = sum(t.multa for t in tarefas)

    print(f"\n  Estados da tabela (n x (T+1)): {n} x {r.info['T'] + 1} = {r.info['estados']}")
    print(f"\n  {'':<18} | {'no prazo':>8} | {'multa':>8} | {'tempo (ms)':>10}")
    print("  " + "-" * 54)
    print(f"  {'PD bottom-up':<18} | {len(r.no_prazo):>8} | {r.multa_total:>8} | {tempo_bu:>10.2f}")
    print(f"  {'Guloso adaptado':<18} | {len(g.no_prazo):>8} | {g.multa_total:>8} | {tempo_g:>10.2f}")
    print(f"\n  Multa se tudo atrasasse: {soma}")
    print(f"  Diferença guloso - PD: {g.multa_total - r.multa_total} "
          f"({100 * (g.multa_total - r.multa_total) / r.multa_total:.1f}% a mais de multa no guloso)")
    print(f"  Agenda da PD é viável? {cabe_no_prazo(r.no_prazo)} | Agenda do guloso é viável? {cabe_no_prazo(g.no_prazo)}")

    # mesma comparação com durações iguais, usando a instância média do trabalho anterior
    rng = random.Random(SEMENTE)
    unit = [TarefaD(f"T{i}", 1, rng.randint(1, 500), rng.randint(1, 1000)) for i in range(1, 1001)]
    original = escalonar_guloso([Tarefa(t.nome, t.prazo, t.multa) for t in unit])
    print(f"\n  Instância média do trabalho anterior (1000 tarefas de duração 1):")
    print(f"  guloso original = {original.multa_total} | PD = {pd_bottom_up(unit).multa_total}")


def teste_grande():
    titulo("TESTE 3 - instâncias grandes (tempo de execução)")
    print(f"Python {platform.python_version()} | {platform.system()} {platform.release()} | "
          f"{platform.processor() or platform.machine()}")
    print("Tempo em ms, menor de 3 execuções (1 execução a partir de 2.000 tarefas).\n")
    tamanhos = [500, 1000, 2000, 4000, 8000]
    linhas = []
    print(f"  {'n':>6} | {'T':>6} | {'estados':>11} | {'PD (ms)':>10} | {'guloso (ms)':>11} | {'multa PD':>9} | {'multa gul.':>10}")
    print("  " + "-" * 82)
    for n in tamanhos:
        tarefas = gerar_tarefas(n)
        rep = 3 if n < 2000 else 1
        tempo_pd, r = cronometrar(pd_bottom_up, tarefas, rep)
        tempo_g, g = cronometrar(guloso_adaptado, tarefas, rep)
        print(f"  {n:>6} | {r.info['T']:>6} | {r.info['estados']:>11} | {tempo_pd:>10.2f} | {tempo_g:>11.2f} | "
              f"{r.multa_total:>9} | {g.multa_total:>10}")
        sys.stdout.flush()
        linhas.append([n, r.info["T"], r.info["estados"], f"{tempo_pd:.2f}", f"{tempo_g:.2f}",
                       r.multa_total, g.multa_total])
    with open("resultados_tempos_pd.csv", "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["n", "T", "estados", "pd_ms", "guloso_ms", "multa_pd", "multa_guloso"])
        escritor.writerows(linhas)
    print("\n  (tabela salva em resultados_tempos_pd.csv)")


def validar(quantidade=500):
    titulo(f"VALIDAÇÃO - PD x força bruta e guloso em {quantidade} instâncias aleatórias (n de 1 a 12)")
    rng = random.Random(SEMENTE)
    erros_pd = diferentes_guloso = 0
    pior_diferenca = 0
    for _ in range(quantidade):
        n = rng.randint(1, 12)
        tarefas = [TarefaD(f"T{i}", rng.randint(1, 5), rng.randint(1, 3 * n), rng.randint(1, 50))
                   for i in range(1, n + 1)]
        otimo = forca_bruta(tarefas)
        if pd_bottom_up(tarefas).multa_total != otimo:
            erros_pd += 1
        multa_guloso = guloso_adaptado(tarefas).multa_total
        if multa_guloso != otimo:
            diferentes_guloso += 1
            pior_diferenca = max(pior_diferenca, multa_guloso - otimo)
    print(f"  Instâncias em que a PD NÃO achou o ótimo: {erros_pd} de {quantidade}")
    print(f"  Instâncias em que o guloso NÃO achou o ótimo: {diferentes_guloso} de {quantidade} "
          f"(pior caso: {pior_diferenca} de multa a mais)")


def rodar_arquivo(caminho):
    titulo(f"Arquivo: {caminho}")
    tarefas = carregar_csv(caminho)
    print("PD:")
    imprimir_agenda(pd_bottom_up(tarefas))
    print("\nGuloso:")
    imprimir_agenda(guloso_adaptado(tarefas))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Escalonamento com duração, prazo e multa (Programação Dinâmica)")
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
