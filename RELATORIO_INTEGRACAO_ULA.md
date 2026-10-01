# Relatório de integração da ULA

A integração foi implementada em circuitos BDF e símbolos BSF, com `TOP` como entidade principal e `ULA` como núcleo. O QPF foi preservado; o QSF cadastra a hierarquia completa, seleciona EP4CE115F29C7 e atribui os 96 pinos usados da DE2-115. Os requisitos seguem o guia local e o prompt executado; o enunciado original não estava disponível. A pinagem vem das tabelas 4-1, 4-3 e 4-4 do [manual oficial Terasic](https://www.terasic.com.tw/wiki/images/f/ff/DE2_115_User_manual_2013.pdf), considerando JP6 em 3,3 V e JP7 em 2,5 V.

Foram reaproveitados o somador de um bit, a hierarquia de muxes, os comparadores e os decodificadores diretos de magnitude. O somador de cinco bits foi consolidado, preservando o segundo nome como invólucro de compatibilidade. Corrigiram-se o BSF que declarava Cin inexistente, a interface de quatro bits do comparador de magnitude, a comparação estrita de negativos e zeros, o mapeamento AND/XOR e os nomes/referências dos decodificadores. Os símbolos e terminais das instâncias foram sincronizados. As VWF conservam os estímulos, com caminhos e projetos de mux corrigidos.

`Complemento_2.bdf` foi corrigido no próprio bloco, conservando a cadeia de inversores e somadores e completando seis estágios. Em 010, repete-se B4 antes de inverter e somar um, entregando os seis bits brutos em F. +0 e -0 são iguais na aritmética e comparação; a entrada 10000 permanece bruta em 010. Foram acrescentados conversores SM/C2, soma/subtração, controle, habilitação dos displays e agrupamentos de integração.

Passaram 33.521 casos das netlists estruturais exportadas pelo Quartus, incluindo 8.192 combinações da ULA e 8.192 do TOP, LEDs e displays. A compilação completa passou sem erros. O Questa recusou a licença; os testes usam interpretação combinacional reproduzível das netlists, sem atrasos. Avisos sobre saídas constantes, parâmetros elétricos padrão e ausência de restrições temporais estão documentados no guia. Não houve programação ou teste físico. A conferência visual no editor Quartus foi dispensada pelo usuário.

Estado: integração lógica compilada e testada; conferência visual e validação na placa ficam com o usuário.
