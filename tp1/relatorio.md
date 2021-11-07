# Relatório

Para realizar as modificações em um ficheiro chamamos r`solve(author_name,INPUT_FILENAME=BIB_EXAMPLE_FILENAME)`, passando o nome do autor que queremos conforme (R5).

Em `solve` temos a váriavel `htlm_str_ls` que é uma lista de strings que iremos concatenar. Usamos uma lista ao invés de ir concatenando uma váriavel string porque em python strings são imutáveis, cada concatenação requer que todos os caracteres sejam copiados. Por outro lado, appends numa lista são $\cal{O}(1)$ e no final concatenamos só uma vez as strings na lista para formar o código html.

Em `bib_str` salvamos o texto inteiro que está em `INPUT_FILENAME`. `get_bib_str()` é utilizada para abrir o ficheiro.g
