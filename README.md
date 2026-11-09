# Escalonamento de Tarefas com Prazo e Multa (Algoritmo Guloso)

Trabalho da disciplina Análise e Projeto de Algoritmos (2026/2), Aula 9: Algoritmos Gulosos.
Equipe: Luiz Eduardo e Murilo Teribele.

## O problema

Temos várias tarefas, todas levam 1 unidade de tempo, e cada uma tem um **prazo** e uma **multa**.
Só uma tarefa roda por vez. Se uma tarefa termina depois do prazo, pagamos a multa dela.
O objetivo é montar a ordem de execução com a **menor multa total** possível.

## A ideia gulosa

1. Ordena as tarefas pela multa, da maior pra menor.
2. Para cada tarefa, coloca ela no **último horário livre que ainda respeita o prazo**.
3. Se não tem nenhum horário livre até o prazo, a tarefa vai atrasar: ela é descartada e vai pro final.

## Arquivos

| Arquivo | O que tem |
|---|---|
| `escalonamento.py` | o algoritmo guloso, a força bruta (pra conferir) e o critério errado (pra comparação) |
| `main.py` | roda os testes e mede os tempos |
| `entradas/teste1_pequeno.csv` | instância do Teste 1 (8 tarefas) |
| `entradas/exemplo_cormen.csv` | exemplo da seção 16.5 do Cormen (multa ótima = 50) |

## Como rodar

Precisa só do Python 3 (sem biblioteca externa).

```
python main.py              # roda tudo
python main.py --teste 1    # instância pequena, passo a passo
python main.py --teste 2    # instância média (1.000 tarefas)
python main.py --teste 3    # instâncias grandes + tabela de tempos
python main.py --validar    # compara com força bruta em 500 instâncias pequenas
python main.py --arquivo entradas/exemplo_cormen.csv
```

O CSV de entrada precisa ter o cabeçalho `nome,prazo,multa`.

## Parte 2: Programação Dinâmica (Aula 10)

Variante com **duração** diferente para cada tarefa (um processador, prazo e multa). Nesse caso o guloso deixa de ser sempre ótimo, então implementamos Programação Dinâmica.

Arquivos novos:

- `programacao_dinamica.py`: PD bottom-up (tabela), recursão simples (sem tabela, só pra comparar), guloso adaptado e força bruta
- `main_pd.py`: testes da parte 2
- `entradas/pd_teste1.csv`: instância pequena do Teste 1 (colunas `nome,duracao,prazo,multa`)

Estado da PD é `(i, t)`, com as tarefas em ordem de prazo:

```
f(i, t) = max( f(i+1, t),  multa[i] + f(i+1, t + duracao[i]) )   # a segunda só se t + duracao[i] <= prazo[i]
f(n, t) = 0
```

Como rodar:

```
python main_pd.py              # todos os testes
python main_pd.py --teste 1    # pequeno, passo a passo
python main_pd.py --teste 2    # médio (500 tarefas)
python main_pd.py --teste 3    # grande (500 a 8000 tarefas), salva resultados_tempos_pd.csv
python main_pd.py --validar    # compara PD e guloso com a força bruta em 500 instâncias
python main_pd.py --arquivo entradas/pd_teste1.csv
```

Precisa de Python 3.10 ou mais novo (usa `insort` com `key=`).
