= Análise Semântica e Tabela de Símbolos

Durante a passadeira sintática LALR(1), o compilador invoca sincronamente e _inline_ os métodos expostos na sua *Tabela de Símbolos*. O `symbol_table.py` materializa-se como uma pilha LIFO suportando Nested Scopes (escopos aninhados), com o global como raiz partilhada. Cada símbolo é representado por uma `Dataclass Symbol` que preserva a metainformação essencial: nome, tipo (`INTEGER`, `REAL`, `LOGICAL`, `CHARACTER`), espacialidade (escalar ou array unidimensional), linha de declaração, e flag de inicialização.

A validação de conflitos (lançada como `SemanticError`) ocorre perante as seguintes regras:
- **Pré-declaração obrigatória**: todas as variáveis, arrays e parâmetros devem ser declarados antes do uso (`lookup()`).
- **Sem re-declarações** (`declare()`): sombras ou duplicados na mesma _frame_ são rejeitados.
- **Parâmetros (`PARAMETER`)**: constantes imutáveis declaradas via `PARAMETER`. O compilador rejeita duplicados, atribuições a parâmetros, e aplicações de `PARAMETER` a arrays.
- **Acesso a arrays**: verificação de dimensionalidade (`check_array_access()`) — o subscrito deve ser único e, quando possível, os índices literais são validados em tempo de compilação contra os limites declarados.
- **Compatibilidade de tipos**: atribuições `REAL` → `INTEGER` admitem truncação implícita; `LOGICAL` → numérico (ou vice-versa) é rejeitado.