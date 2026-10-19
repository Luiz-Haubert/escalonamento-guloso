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
