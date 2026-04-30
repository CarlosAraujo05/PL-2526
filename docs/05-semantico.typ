= Análise Semântica e Tabela de Símbolos

Durante a passadeira sintática LALR(1), o compilador invoca assíncronamente os métodos expostos na sua *Tabela de Símbolos*. O `symbol_table.py` materializa-se como uma pilha encadeada LIFO suportando um modelo rigoroso de Nested Scopes (Escopos Aninhados). No entanto, o global assume prioridade total com reuso partilhado quando em escopo principal e declaração estrita via Subprogramas, alocando a cada nó global uma `Dataclass Symbol` que preserva toda a metainformação crucial do código-fonte (Tipagem - se Integer, Logical, Array dimensional com indexação de limites, número de linhas e origens de declaração).

A validação de conflitos (lançada internamente na aplicação como _exceptions_ de natureza tipológica `SemanticError`) ocorre de maneira natural perante as regras:
- Verificação restrita de re-declarações (`declare()`), não permitindo sombras ou conflitos em variáveis na mesma _frame_.
- Obrigatoriedade de pré-declaração em invocações implícitas (`lookup()`).
- O acesso fora de limite em dimensões (index bounds restritos) por sub-rotinas array-oriented (`check_array_access()`).
- Casting implícito ou limitação inter-tipológica: o motor suporta a limitação natural do Fortran, no qual a alocação `REAL` num bloco associado de memórica `INTEGER` gera truncação intrínseca, mas `LOGICAL` para tipos matemáticos acusa colisão imediata.