#import "cover.typ": cover
#import "template.typ": *
#import "@preview/codly:1.2.0": *
#import "@preview/codly-languages:0.1.1": *

#show: project

#show: codly-init.with()

// INFO CAPA
#cover(title: "Construção de um Compilador para Fortran 77 
Standard", 
  authors: (
  (name: "Carlos Araújo", number: "A106845"),
  (name: "Vitor Senra", number: "A106921"),
  (name: "Hugo Soares", number: "A107293")
),
  datetime.today().display("[month repr:long] [day], [year]"))

#set page(numbering: "i", number-align: center)
#counter(page).update(1)

#show outline: it => {
    show heading: set text(size: 18pt)
    it
}

// INDICE, FIGURAS, TABELAS
#{  show outline.entry.where(level: 1): it => {
    v(9pt)
    strong(it)
  }

  outline(
    title: [Índice], 
    indent: 5pt + 7%, 
  )
}

// Reset ao número de página
#set page(numbering: "1", number-align: center)
#counter(page).update(1)

#set enum(indent: 2em)
#set enum(numbering: "1.1.", full: true)
#set list(indent: 2em)
#set par(first-line-indent: 1em)

#codly(
  languages: (
    bash: (name: "bash", color: rgb("#000000")),
    xml: (name: "python", color: rgb("#00599C")),
  )
)

#include "01-introducao.typ"
#include "02-arquitetura.typ"
#include "03-lexico.typ"
#include "04-sintatico.typ"
#include "05-semantico.typ"
#include "06-ast.typ"
#include "07-codegen.typ"
#include "08-testes.typ"
#include "09-conclusoes.typ"
