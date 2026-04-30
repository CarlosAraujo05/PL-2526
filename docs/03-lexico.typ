= Análise Léxica

A análise léxica é o primeiro passo da conduta, garantindo a decomposição da fonte Fortran num fluxo contínuo de _tokens_ validados. Desenvolvida no módulo `lexer.py` usando `ply.lex`, garante o tratamento nativo do *Fixed-Format* do Fortran 77:
- *Colunas 1-5*: Reservadas unicamente para numeração de identificação local de instruções (Labels/GOTO targets).
- *Coluna 6*: Reservada como caracter de controlo de contiguidade de linha ou denotação de comentário (quando `C` ou `*`).
- *Colunas 7-72*: Espaço principal para a escrita do corpo sintático.

A nível preparatório, o pré-processador interno normaliza o source _in memory_ para remover os comentários explícitos e unir quebras formatadas contíguas. 

Os Tokens emitidos para o Parser incluem as _keywords_ base da norma (`PROGRAM`, `IF`, `DO`, `CONTINUE`), operadores lógicos nativos e transacionais (`.GT.`, `.AND.`, `**`), literais de múltiplas tipagens (Inteiros, Reais com formato `E`, literais String entre aspas isoladas, ou lógicos como `.TRUE.`).
Como estipulado, todos os identificadores (tendo tamanho limite de 6 caracteres alfanuméricos começados por letra) são recolhidos e sistematicamente transformados em letras maiúsculas (`.upper()`), respeitando a *Case-Insensitivity* fundamental do Fortran 77. Em caso de divergência ortográfica na formação, o lexer atira uma `LexerError` reportando a posição.