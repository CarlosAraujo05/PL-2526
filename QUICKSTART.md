# 🚀 Quick Start - Context-Free Grammar Fortran 77

## 30 Segundos para Começar

```bash
# Ver um exemplo da gramática
python src/fortran77_cfg.py hello.for

# Ver todos os exemplos
python src/fortran77_cfg.py --all

# Ver a gramática completa em BNF
python src/fortran77_cfg.py --grammar
```

---

## 5 Minutos de Exploração

### 1. Ler a Visão Geral
```bash
head -50 README.md
```

### 2. Ver um Exemplo Prático
```bash
# Código Fortran
cat tests/hello.for

# Tokens gerados
python src/lexer.py tests/hello.for

# Derivação pela gramática
python src/fortran77_cfg.py hello.for
```

### 3. Explorar Testes
```bash
python tests/test_cfg_validation.py
```

---

## Estrutura em Uma Linha por Tipo

| O que? | Onde? | Comando |
|--------|-------|---------|
| Visão Geral | README.md | `cat README.md` |
| Gramática Completa | FORTRAN77_CFG.md | `python src/fortran77_cfg.py --grammar` |
| Validação | CFG_VALIDATION.md | `cat CFG_VALIDATION.md` |
| Referência Rápida | CFG_QUICK_REFERENCE.md | `cat CFG_QUICK_REFERENCE.md` |
| Índice Completo | INDEX.md | `cat INDEX.md` |

---

## Exemplos Principais

### Exemplo 1: Programa Simples
```bash
python src/fortran77_cfg.py hello.for
```

**O que você aprende:**
- Estrutura básica: `PROGRAM ... END`
- PRINT statement
- Uso de strings

### Exemplo 2: DO Loops
```bash
python src/fortran77_cfg.py fatorial.for
```

**O que você aprende:**
- Declaração de tipo: `INTEGER`
- DO loops: `DO LABEL ... LABEL CONTINUE`
- Expressões aritméticas com precedência

### Exemplo 3: Controle Complexo
```bash
python src/fortran77_cfg.py primo.for
```

**O que você aprende:**
- IF/THEN/ELSEIF/ENDIF
- Operadores lógicos: `.AND.`, `.LE.`
- GOTO para loops backwards
- Precedência de operadores

### Exemplo 4: Arrays
```bash
python src/fortran77_cfg.py somaarr.for
```

**O que você aprende:**
- Declaração com DIMENSION: `INTEGER NUMS(5)`
- Acesso a arrays: `NUMS(I)`
- Arrays em I/O

### Exemplo 5: Funções
```bash
python src/fortran77_cfg.py conversor.for
```

**O que você aprende:**
- Definição de função: `INTEGER FUNCTION`
- Parâmetros e RETURN
- Chamada de função
- Funções intrínsecas como MOD()

---

## Validação Visual

```bash
# Rodar todos os testes de validação
python tests/test_cfg_validation.py

# Teste específico
python tests/test_cfg_validation.py hello.for
python tests/test_cfg_validation.py fatorial_fragment
python tests/test_cfg_validation.py primo_fragment
python tests/test_cfg_validation.py array_fragment
```

---

## Análise de Tokens

```bash
# Ver tokens do lexer para cada programa
python src/lexer.py tests/hello.for
python src/lexer.py tests/fatorial.for
python src/lexer.py tests/primo.for
python src/lexer.py tests/somaarr.for
python src/lexer.py tests/conversor.for
```

---

## Estrutura da Gramática em 30 Segundos

```
program → PROGRAM ID 
          declaration_block 
          statement_block 
          END

Cada bloco contém:
• declaration_block: declarações de tipo (INTEGER, REAL, etc.)
• statement_block: statements (IF, DO, PRINT, atribuições, etc.)

Exemplo:
      PROGRAM HELLO              ← PROGRAM ID
      INTEGER X                  ← declaration_block
      PRINT *, 'Ola'             ← statement_block
      END                         ← END
```

---

## Categorias Principais

1. **Programa Principal** - PROGRAM ... END
2. **Declarações** - INTEGER, REAL, LOGICAL, CHARACTER, DIMENSION
3. **Atribuições** - var = expr, array(i) = expr
4. **Expressões** - Arithmetic, Logical, Relational
5. **Controle de Fluxo** - IF/THEN/ENDIF, DO loops, GOTO
6. **I/O** - PRINT, READ, WRITE
7. **Funções** - FUNCTION, SUBROUTINE
8. **Operadores** - 60+ tokens suportados

---

## Cheat Sheet de Operadores

| Tipo | Operadores |
|------|-----------|
| Aritmética | `+` `-` `*` `/` `**` |
| Relacional | `.LT.` `.LE.` `.GT.` `.GE.` `.EQ.` `.NE.` |
| Lógica | `.AND.` `.OR.` `.NOT.` |
| Constantes | `.TRUE.` `.FALSE.` |

---

## Próximos Passos

1. **Implementar um Parser**
   ```bash
   # Use a gramática em FORTRAN77_CFG.md
   # como base para um parser PLY/yacc
   ```

2. **Gerar Árvore Sintática**
   ```bash
   # Defina classes Node para cada produção
   ```

3. **Análise Semântica**
   ```bash
   # Adicione verificação de tipos e escopo
   ```

---

## Arquivo para Cada Nível

| Nível | Arquivo | Tempo |
|-------|---------|-------|
| **Iniciante** | README.md | 5 min |
| **Intermediário** | FORTRAN77_CFG.md | 20 min |
| **Avançado** | CFG_VALIDATION.md | 30 min |
| **Referência** | CFG_QUICK_REFERENCE.md | On-demand |
| **Completo** | INDEX.md | 1-2 horas |

---

## Exemplos Executáveis

Todos os exemplos funcionam:

```bash
# Mostrar exemplo com código + derivação
python src/fortran77_cfg.py <nome_do_arquivo>

# Exemplos disponíveis:
# • hello.for
# • fatorial.for
# • primo.for
# • somaarr.for
# • conversor.for
```

---

## Validação ✅

✅ 5 programas Fortran 77 reais
✅ 50+ produções da gramática
✅ 18 construções principais
✅ 100% de cobertura
✅ 9 níveis de precedência
✅ 60+ tokens suportados

---

## Contato e Suporte

- **Gramática detalhada?** → `FORTRAN77_CFG.md`
- **Exemplos?** → `python src/fortran77_cfg.py --all`
- **Validação?** → `python tests/test_cfg_validation.py`
- **Referência?** → `CFG_QUICK_REFERENCE.md`
- **Tudo?** → `INDEX.md`

---

**Última atualização:** 7 de abril de 2026
**Versão:** 1.0
**Status:** ✅ Pronto para uso
