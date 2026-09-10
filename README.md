*This project has been created as part of the 42 curriculum by <login1>, <login2>.*

# Roadmap: Projeto A-Maze-ing

Este documento apresenta a análise completa do estado atual do projeto e o roadmap
detalhado de tudo que falta implementar.

> **Legenda de prioridade:**
> 🔴 **CRÍTICO** — Sem isso o projeto é nota 0 ou incompleto
> 🟡 **IMPORTANTE** — Necessário para passar na avaliação
> 🟢 **BONUS** — Pontos extras opcionais

---

## 1. Gerador de Labirintos — `mazegen/generator.py`

### Estado Atual
- Existe uma classe `MazeGenerator` com `generate()` e `solve()`.
- **`generate()`**: abordagem ingênua — para cada célula, sorteia aleatoriamente
  uma direção (E ou S) e remove a parede. **Não garante conectividade**, não é
  spanning tree, pode criar ilhas desconectadas e loops indesejados.
- **`solve()`**: completamente mockado — apenas move E e depois S, ignorando
  paredes. Retorna caminhos impossíveis de atravessar.

### 🔴 Algoritmo de geração correto
- [ ] Substituir `generate()` por algoritmo real (Recursive Backtracker, Kruskal
  ou Prim). Deve garantir conectividade total quando `PERFECT=True` e usar
  `random.seed()` para reprodutibilidade.
- [ ] **Modo PERFECT**: spanning tree — sem loops, um único caminho entre
  quaisquer duas células. Exceto padrão "42", todas acessíveis.
- [ ] **Modo PLAYABLE**: braiding para criar loops. Mínimo 2 rotas independentes.
  4 cantos e centro devem ser corredores abertos. Becos sem saída raros (~2 max).

### 🔴 Padrão "42"
- [ ] Injetar células totalmente bloqueadas formando "42" no centro do grid.
- [ ] Se grid pequeno demais, imprimir aviso no terminal e pular.
- [ ] Células do "42" são a única exceção à conectividade.

### 🔴 Restrição 3x3
- [ ] Verificação que impeça áreas abertas maiores que 2x2. Corredores 3x3+
  são expressamente proibidos pelo subject.

### 🔴 Pathfinding real
- [ ] Substituir `solve()` mockado por BFS/Dijkstra/A* respeitando paredes.
- [ ] Retornar sequência de direções (N, E, S, W) do caminho mais curto.
- [ ] Resultado deve bater com a representação visual.

### 🟡 Validação de parâmetros
- [ ] ENTRY/EXIT fora dos limites, WIDTH/HEIGHT <= 0, ENTRY == EXIT.
- [ ] Garantir paredes externas em todo o perímetro.

---

## 2. Script Principal — `a_maze_ing.py`

### Estado Atual
- ✅ Parse de config com tratamento de erros.
- ✅ Exportação hexadecimal.
- ✅ Renderização ASCII com cores ANSI e temas.
- ✅ Menu interativo (gerar, mostrar/esconder caminho, mudar cores, sair).

### 🟡 O que falta verificar/ajustar
- [ ] Garantir que **todas as exceções** são tratadas — programa nunca deve crashar.
- [ ] Mensagens de erro claras para: chave faltando, formato inválido, números
  substituídos por letras, booleano inválido no PERFECT, tuple inválido no
  ENTRY/EXIT.
- [ ] Confirmar formato do OUTPUT_FILE:
  - `HEIGHT` linhas de `WIDTH` chars hexadecimais
  - Linha em branco
  - Coordenadas ENTRY e EXIT
  - String do caminho mais curto (N, E, S, W)
  - Todas as linhas terminam com `\n`
- [ ] Usar `output_validator.py` (fornecido com o subject) para validar.

---

## 3. Empacotamento Reutilizável

### 🔴 Arquivo de pacote na raiz
- [ ] Gerar `mazegen-*.tar.gz` e/ou `.whl` na raiz do repositório:
  `make package && cp dist/mazegen-*.tar.gz .`
- [ ] Avaliador vai re-gerar o pacote em virtualenv, instalar e testar.

### 🔴 LICENSE.md
- [ ] Criar `LICENSE.md` na raiz com licença que permita reutilização e
  distribuição do gerador (MIT recomendada, já declarada no pyproject.toml).

### 🟡 Documentação do módulo reutilizável
- [ ] Como instanciar e usar `MazeGenerator` (exemplo básico).
- [ ] Como passar parâmetros customizados (size, seed, perfect).
- [ ] Como acessar a estrutura gerada e a solução.

---

## 4. README.md — Formato Obrigatório (Régua)

O avaliador verifica item por item. Tudo abaixo é **obrigatório**:

- [ ] **Primeira linha** em itálico:
  `*This project has been created as part of the 42 curriculum by <login1>, <login2>.*`
- [ ] Seção **"Description"**: objetivo e visão geral do projeto.
- [ ] Seção **"Instructions"**: compilação, instalação, execução.
- [ ] Seção **"Resources"**: referências clássicas + descrição de como a IA foi usada.
- [ ] Formato completo do arquivo de configuração (todas as chaves, exemplos).
- [ ] Algoritmo de geração escolhido + justificativa.
- [ ] Qual parte do código é reutilizável e como.
- [ ] Gestão de equipe: papéis, planejamento, o que funcionou, ferramentas usadas.

---

## 5. Qualidade de Código — Linting e Tipagem

### 🟡 Obrigatório na régua
- [ ] `flake8` — passar sem erros.
- [ ] `mypy` com flags do subject:
  `mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports
  --disallow-untyped-defs --check-untyped-defs`
- [ ] Docstrings PEP 257 em todas as funções e classes.
- [ ] Type hints em todos os parâmetros e retornos.

### Checklist por arquivo:

| Arquivo | Docstrings | Type Hints | flake8 | mypy |
|---|---|---|---|---|
| `a_maze_ing.py` | ⚠️ Parcial | ✅ | ⚠️ Verificar | ⚠️ Verificar |
| `mazegen/__init__.py` | ✅ | ✅ | ✅ | ✅ |
| `mazegen/generator.py` | ❌ Sem docstrings | ✅ | ⚠️ Verificar | ⚠️ Verificar |
| `maze_analyzer.py` | ✅ | ✅ | ⚠️ Verificar | ⚠️ Verificar |
| `colors.py` | ❌ Sem docstrings | ❌ Sem hints | ⚠️ Verificar | ❌ |

---

## 6. Arquivos Exigidos na Avaliação

| Arquivo | Status | Ação |
|---|---|---|
| `README.md` | ⚠️ Formato errado | Reescrever com seções obrigatórias |
| `a_maze_ing.py` | ✅ Existe | Corrigir dependência do gerador |
| `mazegen.tar.gz` | ❌ **Não existe** | `make package` + copiar para raiz |
| `mazegen-*.whl` | ❌ **Não existe** | `make package` + copiar para raiz |
| `config.txt` | ✅ Existe | — |
| `LICENSE.md` | ❌ **Não existe** | Criar com licença MIT |
| `pyproject.toml` | ✅ Existe | — |
| `Makefile` | ✅ Existe | Verificar flags do lint |

---

## 7. Bônus Opcionais

- [ 🟢 ] Labirinto sem dead-ends (`--max-dead-ends 0`): braiding perfeito.
- [ 🟢 ] Múltiplos algoritmos de geração (via configuração).
- [ 🟢 ] Animação durante geração no terminal.

---

## 8. Ordem de Implementação Sugerida

```
FASE 1 — Core (sem isso o projeto é nota 0)
├── 1.1  Corrigir MazeGenerator.generate() com algoritmo real
├── 1.2  Implementar padrão "42"
├── 1.3  Implementar MazeGenerator.solve() com BFS real
├── 1.4  Verificar restrição 3x3
└── 1.5  Testar com maze_analyzer.py e output_validator.py

FASE 2 — Empacotamento (exigido na régua)
├── 2.1  Criar LICENSE.md
├── 2.2  Gerar mazegen.tar.gz e .whl na raiz
└── 2.3  Testar instalação em virtualenv limpo

FASE 3 — Qualidade de código (exigido na régua)
├── 3.1  Passar flake8 sem erros
├── 3.2  Passar mypy com flags do subject
├── 3.3  Adicionar docstrings PEP 257 em tudo
└── 3.4  Adicionar type hints em tudo

FASE 4 — README e documentação (exigido na régua)
├── 4.1  Reescrever README.md com formato obrigatório
├── 4.2  Documentar módulo reutilizável
└── 4.3  Documentar uso de IA

FASE 5 — Bônus (opcional)
├── 5.1  Braiding perfeito (zero dead-ends)
├── 5.2  Múltiplos algoritmos
└── 5.3  Animação de geração
```