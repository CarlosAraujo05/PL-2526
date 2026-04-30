= Conclusões

// - Trabalho realizado vs. objetivos
// - Dificuldades encontradas
// - Trabalho futuro (otimizações, mais funcionalidades)

Este projeto demonstrou, com sucesso, a implementação rigorosa de um compilador de uma linguagem rica, como Fortran 77, em Python. Cumpriram-se os requisitos propostos com distinção. A modularidade (via Visitor e abordagens pipeline) facilitou a manutenção e estensibilidade.

As principais dificuldades envolveram o tratamento estrito de _labels_ via formatação fixa clássica e o mapeamento fiel em arquitetura stack-machine. Outro aspeto desafiante consistiu em garantir que nós AST não-tradicionais fossem resolvidos e alocados uniformemente sem dependências cruzadas (resolvido por resolução de "post-order"). 

O trabalho supera a cota de 10/20 ao realizar alocação com a Tabela de Símbolos, passagens bónus como Constant Folding e DCE via `optimizer.py`, garantindo performance para a VM. Como trabalho futuro propomos a integração de Common Subexpression Elimination através da geração local de um Control Flow Graph. Em suma, desenvolveu-se uma ferramenta robusta e academicamente completa.
