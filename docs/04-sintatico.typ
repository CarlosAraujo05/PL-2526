= Análise Sintática

A análise sintática baseou-se na implementação rigorosa da Context-Free Grammar (CFG) desenvolvida para a norma em questão (ver anexo em formato `CFG.md`). A sua base é LALR(1) suportada diretamente pelas implementações estritas da engine PLY Yacc via módulo `parser.py`.

A priorização operacional de expressões avaliadas obedece estritamente às tabelas da linguagem: primeiramente operações lógicas, relacionais, até à base aritmética (`logical_or` → `logical_and` → `relational` → `additive` → `multiplicative` → `power` → `unary` → `primary`).

Concomitantemente à validação gramatical da cadeia, o módulo sintático invoca sincronamente a infraestrutura Semântica, abortando imediatamente se as regras de alocação forem violadas (variáveis declaradas, acessos a arrays unidimensionais, blocos aninhados e validação de destinos `GOTO`). No final da verificação descendente com sucesso em cada regra gramatical (`p_[rule]`), instanciam-se _Dataclasses_ para a construção da *Abstract Syntax Tree (AST)*. Em caso de divergência estrita (falta de parêntesis, terminação incorreta de loop `DO`, etc.), é lançada uma `ParserSyntaxError` capturada em `main.py` com mensagem legível.