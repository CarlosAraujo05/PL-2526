= Análise Semântica e Tabela de Símbolos
// - Implementação da tabela de símbolos (symbol_table.py)
// - Verificação de tipos e compatibilidade
// - Deteção de erros: variáveis não declaradas, duplicados, acessos inválidos
// - Gestão de escopos (subprogramas)

O `symbol_table.py` implementa escopos aninhados (pilha de dicionários). Cada `Symbol` tem: nome, tipo (`variable`/`array`/`function`), dtype (`INTEGER`/`REAL`/`LOGICAL`/`CHARACTER`), dimensões e linha.

Verificações: declarações duplicadas (`declare()`), variáveis não declaradas (`lookup()`), acessos inválidos a arrays (`check_array_access()`), e compatibilidade de tipos (`is_type_compatible()`). O Fortran 77 permite conversões implícitas (ex: REAL para INTEGER trunca).