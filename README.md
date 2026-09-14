*This project was built as part of the 42 curriculum by vicdos-s and kasoares.*

# A-Maze-ing

Projeto desenvolvido por `vicdos-s` e `kasoares`.

Este README descreve a entrega do projeto conforme o enunciado do PDF da 42. O escopo implementado corresponde ao que foi pedido na avaliação principal; não inclui os itens bônus.

## Visão geral

O projeto consiste em gerar e resolver labirintos em Python, com:

- geração de labirintos perfeitos e variações com múltiplos caminhos
- resolução do caminho mínimo via BFS
- representação da grade usando máscaras de bits
- exportação do labirinto em arquivo de texto
- renderização visual no terminal em ASCII/cores
- empacotamento do módulo `mazegen` como biblioteca reutilizável

A lógica principal está na classe `MazeGenerator`, localizada em `mazegen/generator.py`, e o fluxo principal da aplicação fica em `a_maze_ing.py`.

## Requisitos

- Python 3.10 ou superior
- `pip` atualizado
- `make` opcional, mas útil para automatizar a execução e a validação

## Instalação

### 1) Instalar dependências locais

```bash
make install
```

Esse comando instala as ferramentas de validação (`mypy`, `flake8`, `pytest`, `build`) e também instala o pacote em modo editável.

### 2) Instalar o pacote `build`

Caso o ambiente da 42 bloqueie a instalação do pacote `build`, use:

```bash
python3 -m pip install build -i https://pypi.org/simple
```

Essa instrução garante a instalação da ferramenta fora do limite do ambiente da 42.

### 3) Instalar o projeto localmente

```bash
python3 -m pip install -e .
```

## Execução

### Rodar com o arquivo de configuração padrão

```bash
make run
```

Ou manualmente:

```bash
python3 a_maze_ing.py config.txt
```

O programa lê o arquivo `config.txt`, gera o labirinto, calcula a solução e exibe a visualização interativa.

## Arquivo de configuração

O projeto usa um arquivo de configuração no formato `CHAVE=VALOR`. Linhas em branco e linhas começando com `#` são ignoradas.

Exemplo:

```ini
WIDTH=30
HEIGHT=20
ENTRY=0,0
EXIT=29,19
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
```

A chave `SEED` é opcional. Quando ela existe, o programa usa esse valor para tornar a geração determinística.

### Como a seed funciona no código

A seed não "cria um labirinto especial"; ela apenas define o estado inicial do gerador de números aleatórios do Python. O projeto usa a função global `random` da biblioteca padrão.

Em [mazegen/generator.py](mazegen/generator.py), o construtor da classe faz:

```python
if self.seed is not None:
    random.seed(self.seed)
```

E também, dentro de `generate()`, há outra chamada equivalente:

```python
if self.seed is not None:
    random.seed(self.seed)
```

Isso significa que, para a mesma semente e os mesmos parâmetros do labirinto, a sequência de chamadas a `random.choice()` será exatamente a mesma. Como o algoritmo de geração usa `random.choice(unvisited)` para decidir qual direção percorrer, o caminho escolhido em cada passo será idêntico.

Em termos práticos:

- mesma `seed`
- mesmo `width`, `height`, `entry`, `exit_pos`, `perfect`
- mesmo algoritmo
- mesmo ambiente Python

resultam no mesmo labirinto.

A mesma ideia vale para o arquivo de configuração: em [a_maze_ing.py](a_maze_ing.py), o código verifica se existe `SEED` e executa:

```python
random.seed(int(config["SEED"]))
```

Assim, toda a geração que vier depois usa a mesma sequência pseudoaleatória.

### Por que funciona

O Python usa um gerador pseudoaleatório determinístico. O estado interno do RNG depende do valor inicial da semente. Se você inicializar o RNG com o mesmo valor, ele produz a mesma sequência de números. Como a geração do labirinto usa essa seqüência para escolher caminhos vazios, o labirinto final também fica igual.

Isso é exatamente o que permite reproduzir um comportamento: o mesmo código com a mesma seed produz a mesma grade.

### Exemplos de reprodução

```python
from mazegen import MazeGenerator

m1 = MazeGenerator(20, 20, (0, 0), (19, 19), seed=42, perfect=True)
m1.generate()

m2 = MazeGenerator(20, 20, (0, 0), (19, 19), seed=42, perfect=True)
m2.generate()

print(m1.get_grid() == m2.get_grid())
```

A saída será `True`.

Outra forma é pelo arquivo de configuração:

```ini
WIDTH=20
HEIGHT=20
ENTRY=0,0
EXIT=19,19
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
```

Executando:

```bash
python3 a_maze_ing.py config.txt
```

você obterá o mesmo labirinto sempre que usar a mesma configuração e a mesma semente.

### Quando a seed não é usada

Se você remover `seed` ou `SEED`, o programa usa o estado aleatório padrão do Python, que normalmente depende do tempo do sistema. Nesse caso, cada execução gera um labirinto diferente.

### Chaves obrigatórias

- `WIDTH`: largura do labirinto
- `HEIGHT`: altura do labirinto
- `ENTRY`: coordenada da entrada no formato `X,Y`
- `EXIT`: coordenada da saída no formato `X,Y`
- `OUTPUT_FILE`: nome do arquivo em que a grade será exportada
- `PERFECT`: se o labirinto deve ser perfeito (`True`) ou mais aberto (`False`)

## Sistema de seed e reprodução de labirintos

O gerador aceita um parâmetro opcional chamado `seed` na construção da classe `MazeGenerator`:

```python
maze = MazeGenerator(
    width=20,
    height=20,
    entry=(0, 0),
    exit_pos=(19, 19),
    seed=42,
    perfect=True,
)
```

Quando a semente é informada, o código chama `random.seed(self.seed)` antes da geração do labirinto. O mesmo vale quando a chave `SEED` aparece no arquivo de configuração: o programa executa `random.seed(int(config["SEED"]))` antes de criar o gerador.

Isso faz com que a sequência de escolhas aleatórias do algoritmo de DFS seja determinística para aquela combinação de configuração.

Em outras palavras:

- mesmo `width`, `height`, `entry`, `exit_pos`, `perfect` e `seed`
- geram o mesmo labirinto
- para a mesma versão do algoritmo e do ambiente Python

Se você quiser reproduzir exatamente a mesma estrutura, basta reaproveitar os mesmos valores de entrada e a mesma semente.

Exemplo de reprodução:

```python
from mazegen import MazeGenerator

config = {
    "width": 20,
    "height": 20,
    "entry": (0, 0),
    "exit_pos": (19, 19),
    "perfect": True,
    "seed": 42,
}

maze_1 = MazeGenerator(**config)
maze_1.generate()

maze_2 = MazeGenerator(**config)
maze_2.generate()

print(maze_1.get_grid() == maze_2.get_grid())
```

Esse código imprime `True` porque ambos os labirintos foram gerados a partir da mesma semente.

Se o objetivo for gerar uma nova configuração aleatória, basta:

- remover o parâmetro `seed`,
- remover a chave `SEED` do arquivo de configuração, ou
- usar outro número inteiro

O algoritmo da solução (`solve`) não depende diretamente da seed; ele depende da estrutura do labirinto gerado. Assim, para um mesmo labirinto, o caminho calculado pelo BFS será sempre o mesmo.

Também é possível reproduzir o mesmo labirinto via arquivo de configuração:

```ini
WIDTH=20
HEIGHT=20
ENTRY=0,0
EXIT=19,19
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
```

Ao rodar `python3 a_maze_ing.py config.txt`, o programa gera o mesmo labirinto sempre que a mesma configuração e a mesma semente forem usadas.

## Estrutura do projeto

```text
.
├── a_maze_ing.py        # CLI principal
├── config.txt           # configuração de exemplo
├── parse.py             # leitura e parsing do arquivo de configuração
├── render.py            # renderização visual do labirinto
├── pyproject.toml       # configuração do pacote
├── Makefile             # atalhos de build, execução e validação
├── mazegen/
│   ├── __init__.py
│   └── generator.py     # geração e solução do labirinto
├── dist/                # artefatos gerados pela construção
├── README.md            # documentação do projeto
└── maze.txt             # arquivo exportado pela aplicação
```

## Como o algoritmo funciona

### Geração com DFS e backtracking

A geração usa DFS com backtracking, explorando profundidade e removendo paredes entre células conectadas. Quando não há vizinhos não visitados, o algoritmo retrocede e continua em outra rota.

### Resolução com BFS

A solução é calculada com BFS, que garante encontrar o menor caminho entre a entrada e a saída.

A classe `MazeGenerator.solve()` retorna uma string com instruções em letras:

- `N`: norte
- `S`: sul
- `E`: leste
- `W`: oeste

## Representação em bits

Cada célula da matriz é representada por um inteiro que guarda o estado das paredes usando bits:

- bit 0: norte = 1
- bit 1: leste = 2
- bit 2: sul = 4
- bit 3: oeste = 8

O valor inicial `15` significa que todas as paredes estão fechadas. Ao abrir uma passagem, o código usa operações bit a bit, como:

```python
grid[y][x] &= ~NORTH
```

Essa operação é feita também na célula vizinha para manter a estrutura coerente.

## Exemplos de uso do módulo

### Exemplo básico

```python
from mazegen import MazeGenerator

maze = MazeGenerator(
    width=12,
    height=8,
    entry=(0, 0),
    exit_pos=(11, 7),
    perfect=True,
)

maze.generate()
path = maze.solve((0, 0), (11, 7))
print(path)
print(maze.get_grid())
```

### Com seed fixa

```python
from mazegen import MazeGenerator

maze = MazeGenerator(
    width=20,
    height=15,
    entry=(0, 0),
    exit_pos=(19, 14),
    seed=42,
    perfect=True,
)

maze.generate()
solution = maze.solve((0, 0), (19, 14))
print(f"Solução: {solution}")
```

Como a geração usa `random.choice()` durante o DFS, usar a mesma semente gera a mesma sequência de decisões e, portanto, o mesmo labirinto. Isso permite reproduzir exatamente um comportamento para fins de depuração, teste ou comparação visual.

### Exportação da grade para arquivo

```python
from mazegen import MazeGenerator

maze = MazeGenerator(10, 10, (0, 0), (9, 9), perfect=True)
maze.generate()

with open("maze.txt", "w", encoding="utf-8") as file:
    for row in maze.get_grid():
        file.write("".join(f"{cell:x}" for cell in row) + "\n")
```

## Empacotamento do módulo

A configuração do pacote está em `pyproject.toml` e usa `setuptools.build_meta`.

### Instalar a versão local do pacote

```bash
python3 -m pip install -e .
```

### Construir a distribuição

```bash
python3 -m build
```

Esse comando gera artefatos em `dist/` com extensões `.whl` e `.tar.gz`.

### Instalar a wheel em outro ambiente

```bash
python3 -m pip install dist/mazegen-1.0.0-py3-none-any.whl
```

## Validar o projeto

```bash
make lint
make lint-strict
make package
```

## Observações importantes

- Este projeto não implementa os itens bônus do enunciado.
- O foco da entrega corresponde ao requisito principal do projeto 42.
- O módulo foi desenvolvido como uma biblioteca reutilizável, mantendo a lógica de geração e resolução separada da interface.

## Comandos úteis

```bash
make install
make run
make package
make lint
make lint-strict
make clean
```

## Conclusão

O A-Maze-ing é um projeto de geração e resolução de labirintos em Python, com foco em algoritmo, estrutura de dados e representação eficiente de paredes. O projeto foi desenvolvido por `vicdos-s` e `kasoares` e corresponde ao escopo principal pedido no projeto da 42, sem os bônus opcionais.
