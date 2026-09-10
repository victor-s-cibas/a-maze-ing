# Roadmap — Projeto A-Maze-ing

Análise completa do estado atual do projeto com base no **subject** e na
**régua de avaliação**. Cada seção mostra o que já existe, o que falta e
exatamente o que precisa ser feito.

> **Legenda:**
> 🔴 **CRÍTICO** — Sem isso, nota 0 ou projeto marcado como incompleto
> 🟡 **OBRIGATÓRIO** — Exigido pela régua para pontuar
> 🟢 **BÔNUS** — Pontos extras opcionais
> ✅ **PRONTO** — Implementado e funcional

---

##  Status

| Área | Estado | Concluído |
|---|---|---|
| Gerador de labirintos | 🔴 Quebrado | ~10% |
| Pathfinding (solve) | 🔴 Mockado | 0% |
| Padrão "42" | 🔴 Ausente | 0% |
| Script principal (I/O) | ✅ Pronto | 90% |
| Visualização + menu | ✅ Pronto | 95% |
| Makefile | ✅ Pronto | 100% |
| Empacotamento (.tar.gz/.whl) | 🔴 Ausente | 0% |
| LICENSE.md | 🔴 Ausente | 0% |
| Lint (flake8/mypy) | 🟡 Pendente | — |
| README final | 🟡 Este é o roadmap | 0% |

---

## Estrutura Atual do Projeto

```
maze/
├── a_maze_ing.py          # Script principal (entry point)
├── config.txt             # Arquivo de configuração de exemplo
├── Makefile               # Regras: install, run, debug, clean, lint, package
├── maze.txt               # Arquivo de saída gerado (hex)
├── pyproject.toml         # Config de empacotamento Python
├── mazegen/               # Pacote reutilizável
│   ├── __init__.py        #   Exporta MazeGenerator
│   └── generator.py       #   Classe MazeGenerator (⚠️ incompleta)
└── README.md              # Este arquivo (roadmap)
```

**Arquivos que FALTAM e são exigidos pela régua:**

| Arquivo | Por quê |
|---|---|
| `LICENSE.md` | Subject exige licença que permita reutilização do gerador |
| `mazegen-*.tar.gz` | Régua exige pacote pré-compilado na raiz |
| `mazegen-*.whl` | Régua exige pacote pré-compilado na raiz |

---

## 🔴 1. Gerador de Labirintos — `mazegen/generator.py`

Este é o coração do projeto. **O gerador atual não funciona corretamente.**

### O que existe hoje

**`generate()`** — algoritmo ingênuo que NÃO gera labirinto válido:
```python
for y in range(self.height):
    for x in range(self.width):
        direction, nx, ny = random.choice(candidates)  # sorteia E ou S
        self.grid[y][x] &= ~direction                  # remove parede
```
- Cada célula decide independentemente → ilhas desconectadas
- Não é spanning tree → pode ter múltiplos caminhos onde deveria ter um só
- Nunca remove paredes N ou W → comportamento assimétrico
- Não respeita modo PERFECT vs PLAYABLE

**`solve()`** — completamente falso:
```python
while cx < ex: path += "E"  # Anda em linha reta IGNORANDO paredes
while cy < ey: path += "S"
```
- Retorna caminhos que atravessam paredes
- O avaliador vai cruzar com a visualização → vai falhar

### 🔴 O que precisa ser feito — Algoritmo de geração
- [ ] Substituir `generate()` por **Recursive Backtracker** (ou Kruskal/Prim)
- [ ] Garantir conectividade total (spanning tree) quando `PERFECT=True`
- [ ] Usar `random.seed()` para reprodutibilidade com mesma seed
- [ ] Modo **PLAYABLE** (`PERFECT=False`):
  - Braiding — remover paredes de dead-ends para criar loops
  - Mínimo de **2 rotas independentes** (1 loop não é aceitável)
  - **4 cantos e centro** devem ser corredores abertos
  - Dead-ends devem ser raros (máximo ~2)

### 🔴 O que precisa ser feito — Padrão "42"
- [ ] Injetar células totalmente bloqueadas formando "42" no centro
- [ ] Grid pequeno demais → imprimir aviso e pular
- [ ] Únicas células que podem ficar desconectadas

### 🔴 O que precisa ser feito — Restrição 3×3
- [ ] Nenhuma área aberta pode ser maior que 2×2
- [ ] Corredores 3×3+ são expressamente proibidos
- [ ] O avaliador vai perguntar: *"Como isso foi verificado?"*

### 🔴 O que precisa ser feito — Pathfinding (`solve()`)
- [ ] Substituir por **BFS** (ou Dijkstra/A*) respeitando paredes
- [ ] Usar bits de parede para determinar vizinhos acessíveis
- [ ] Retornar string de direções: `N`, `E`, `S`, `W`
- [ ] Resultado deve coincidir com a visualização

### 🟡 O que precisa ser feito — Validação de parâmetros
- [ ] ENTRY/EXIT fora dos limites do maze
- [ ] WIDTH ou HEIGHT <= 0
- [ ] ENTRY == EXIT (devem ser diferentes)
- [ ] Garantir paredes externas em todo o perímetro

---

## ✅ 2. Script Principal — `a_maze_ing.py`

Este arquivo está **quase completo**. Estrutura atual:

| Componente | Estado | Detalhes |
|---|---|---|
| `parse_config()` | ✅ | Lê KEY=VALOR, ignora `#`, valida chaves obrigatórias |
| `parse_tuple()` | ✅ | Converte "X,Y" em Tuple[int, int] |
| `export_maze()` | ✅ | Escreve hex + footer no OUTPUT_FILE |
| `render_ascii()` | ✅ | Renderização ANSI com temas, caminho, padrão "42" |
| Menu interativo | ✅ | Gerar / Mostrar caminho / Mudar cores / Sair |
| `main()` | ✅ | Trata WIDTH/HEIGHT <= 0, suporta SEED |

### 🟡 Ajustes necessários
- [ ] Validar se ENTRY/EXIT estão dentro dos limites do maze
- [ ] Tratar `int()` falhando com letras no WIDTH/HEIGHT
- [ ] Tratar tuple malformado no ENTRY/EXIT (ex: `"abc"`)
- [ ] Tratar booleano inválido no PERFECT (ex: `"maybe"`)
- [ ] O programa **nunca pode crashar** — se crashar, nota é 0

### Formato do arquivo de saída (`maze.txt`)
```
d3bd53d3bd5553d5553d3bbbbd53d3   ← HEIGHT linhas de WIDTH chars hex
baabd43ac55552d553abac442bd2d2
...
d44445555455545545455445545546
                                 ← linha em branco
0,0                              ← ENTRY
29,19                            ← EXIT
EEEEEEEEE...SSSSSSSSS            ← caminho mais curto (N/E/S/W)
```

---

## 🔴 3. Empacotamento Reutilizável

### Pacote na raiz
- [ ] Gerar o pacote e copiar para a raiz:
  ```bash
  make package
  cp dist/mazegen-*.tar.gz .
  ```
- [ ] O avaliador vai: virtualenv → instalar pacote → rodar `a_maze_ing.py`
      → verificar se funciona

### LICENSE.md
- [ ] Criar `LICENSE.md` na raiz com **MIT License** (já declarada no
      `pyproject.toml`)
- [ ] A licença deve permitir explicitamente reutilização e distribuição

---

## 🟡 4. Qualidade de Código

### Linting obrigatório (régua)

| Verificação | Comando | Estado |
|---|---|---|
| flake8 | `flake8 .` | ⚠️ Não verificado |
| mypy | `mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs` | ⚠️ Não verificado |

### Checklist por arquivo

| Arquivo | Docstrings | Type Hints | Observação |
|---|---|---|---|
| `a_maze_ing.py` | ✅ Sim | ✅ Sim | Revisar após mudanças no gerador |
| `mazegen/__init__.py` | ✅ Sim | ✅ Sim | OK |
| `mazegen/generator.py` | ❌ **Falta** | ✅ Sim | Adicionar docstrings PEP 257 |

### O que fazer
- [ ] Rodar `make lint` e corrigir **todos** os erros
- [ ] Adicionar docstrings em `generator.py` (Google ou NumPy style)
- [ ] Garantir type hints em todas as funções
- [ ] Adicionar `.gitignore` para excluir `__pycache__`, `.mypy_cache`, `dist/`

---

## 🟡 5. README Final (reescrever quando o projeto estiver pronto)

Este arquivo é o roadmap atual. **Quando tudo estiver completo**, reescrever
com o formato exigido pela régua:

- [ ] **Linha 1** — itálico:
  `*This project has been created as part of the 42 curriculum by <login1>, <login2>.*`
- [ ] **Description** — objetivo e visão geral
- [ ] **Instructions** — como instalar, compilar e executar
- [ ] **Resources** — referências + descrição de uso de IA
- [ ] **Config format** — estrutura completa do arquivo de configuração
- [ ] **Algorithm** — algoritmo escolhido + justificativa
- [ ] **Reusable module** — o que é reutilizável e como usar
- [ ] **Team management** — papéis, planejamento, retrospectiva, ferramentas

---

## 🟢 6. Bônus Opcionais

- [ ] **Braiding perfeito** — maze sem dead-ends (`--max-dead-ends 0`)
- [ ] **Múltiplos algoritmos** — Recursive Backtracker, Kruskal, Prim via
      configuração (`ALGORITHM=backtracker`)
- [ ] **Animação** — mostrar labirinto sendo gerado passo a passo

---

## 🗺️ Ordem de Implementação

```
FASE 1 — Core (sem isso, nota 0)
│
├─ 1.1  Reescrever generate() com Recursive Backtracker
├─ 1.2  Implementar padrão "42" (células bloqueadas no centro)
├─ 1.3  Implementar modo PERFECT (spanning tree, sem loops)
├─ 1.4  Implementar modo PLAYABLE (braiding, loops, cantos+centro abertos)
├─ 1.5  Implementar verificação de espaços abertos (sem 3×3)
├─ 1.6  Reescrever solve() com BFS real
└─ 1.7  Testar com maze_analyzer.py e output_validator.py

FASE 2 — Empacotamento (exigido na régua)
│
├─ 2.1  Criar LICENSE.md (MIT)
├─ 2.2  make package → copiar .tar.gz/.whl para a raiz
└─ 2.3  Testar instalação em virtualenv limpo

FASE 3 — Qualidade de código (exigido na régua)
│
├─ 3.1  make lint → corrigir todos os erros flake8 + mypy
├─ 3.2  Docstrings PEP 257 em generator.py
└─ 3.3  Adicionar .gitignore

FASE 4 — README e documentação (exigido na régua)
│
├─ 4.1  Reescrever este arquivo como README final
├─ 4.2  Documentar módulo reutilizável (exemplo de uso)
└─ 4.3  Documentar uso de IA no projeto

FASE 5 — Bônus (opcional)
│
├─ 5.1  Braiding perfeito (zero dead-ends)
├─ 5.2  Múltiplos algoritmos
└─ 5.3  Animação de geração
```