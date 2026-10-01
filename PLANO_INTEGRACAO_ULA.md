# Plano de integração da ULA

Análise realizada em 01/10/2026, atualizada após receber `Complemento_2.bdf`. Este documento prepara a execução por outro agente. O arquivo recebido foi incorporado sem alterações; as correções e a integração do circuito permanecem como trabalho planejado.

## Referência e correção do requisito 010

O único PDF encontrado é `Guia_Visual_ULA_Montagem_Manual.pdf`, com 35 páginas. Ele é um guia de uma arquitetura proposta, não o enunciado original. Na página 34, cita `Projeto_Primeira_Unidade_2026_2.pdf`, ausente na pasta, e informa que sua interpretação de `010` difere da implementação anterior.

O usuário esclareceu que `010` calcula o complemento de dois do padrão bruto de B: inverter os bits e somar 1 na largura definida. Essa instrução prevalece sobre a negação numérica em sinal e magnitude proposta no guia. Não usar `NEG_SM`, troca de sinal ou conversão do resultado para sinal e magnitude nesse caminho. Depois, sugeriu, com ressalva, que B seja estendido antes do cálculo e forneceu `Complemento_2.bdf` para reaproveitamento. A proposta atual é adaptar esse arquivo para calcular em seis bits após extensão; confirmar se o bit acrescentado é 0 ou B4 e se F recebe os seis bits brutos diretamente. O arquivo recebido não resolve essa decisão. Se o enunciado original for fornecido, conferir também placa, pinagem e restrições de implementação. Não afirmar que todos os requisitos do enunciado foram verificados enquanto ele não estiver disponível.

A prioridade solicitada é reaproveitar os BDF e BSF existentes, corrigindo-os. Portanto, a lista de blocos do guia serve como referência funcional e de organização; não justifica trocar uma biblioteca funcional por outra inteira.

## Estado encontrado

| Área | Evidência no repositório | Trabalho necessário |
| --- | --- | --- |
| Projeto | `projeto-ula.qsf` aponta para `BIN_DC6bits`, família Cyclone IV E e dispositivo `auto`. | Configurar o esquema principal integrado; confirmar a placa e configurar o dispositivo correspondente. |
| Resultado antigo | Relatórios de 24/09/2026 mostram compilação de `somador_5bit`, com 12 elementos lógicos, usando EP4CE6E22C6. | Gerar evidência atual da ULA completa. Esses relatórios não validam o estado atual. |
| Cadastro de fontes | QSF não inclui muxes, decodificadores de display nem `Maior_4bits.bdf`; cita `Somador_1bit.bdf`, enquanto o arquivo tem nome `somador_1bit.bdf`. | Revisar a hierarquia inteira e os caminhos, inclusive capitalização consistente. |
| Somador | Existem `somador_5bit.bdf` e `Somador_5bits.bdf`, ambos com cinco somadores de 1 bit e carry inicial em GND. | Conferir diferenças, escolher uma versão canônica e atualizar referências; não tratar soma binária bruta como soma de sinal e magnitude. |
| Símbolo do somador | `somador_5bit.bsf` declara `Cin`, mas seu BDF não tem essa entrada. | Ajustar a interface conforme o uso aprovado e regenerar o símbolo. |
| Somador de 1 bit | `somador_1bit.bdf/.bsf` tem A, B, Cin, S e Cout; contém 2 XOR, 2 AND e 1 OR. | Validar as oito combinações e reutilizar como célula aritmética. |
| Complemento de dois recebido | `Complemento_2.bdf` tem entrada B[4..0], saída F[4..0], quatro NOT, quatro `somador_1bit`, um VCC e quatro GND. Foi copiado integralmente do arquivo fornecido pelo usuário. | Reaproveitar e corrigir esse esquema para 010; gerar `Complemento_2.bsf` depois de definir a interface e cadastrar o BDF no QSF durante a integração. |
| Limites do complemento atual | A cadeia inverte apenas B0..B3, soma 1 via VCC no primeiro estágio e propaga carry pelos terminais B dos estágios seguintes, com Cin=0. Cout final não tem fio. Não há estágio de B4 nem sexto bit. | Não considerar esse arquivo um complemento de dois completo de cinco ou seis bits. Se aprovada a extensão antes do cálculo, ampliar a cadeia existente para seis estágios. Carry aplicado em B com Cin=0 é válido para esta soma; não é, por si só, um erro. |
| Conexão suspeita no complemento | O fio rotulado B[4] vai de (424,480) até (640,480), ponto onde também termina a derivação F[0]. Não há derivação identificada como F[4]. | Conferir no Quartus o conflito entre B4 e a saída do bit 0 e a falta do quinto bit de saída. Separar as redes e atribuir cada bit ao terminal correto antes de validar. |
| Seleção | `MUX1`, `MUX2_6` e `MUX8_6` existem com símbolos; o último instancia sete `MUX2_6`. | Validar ordem D0/D1 e S0/S1/S2. Rever uso de conexões por nome em seletores distantes. |
| Lógica | `And_5bits` e `Xor_5bits` têm saída de seis bits, resultado bruto nos bits F4..F0 e GND em F5. | Para seguir o guia, reposicionar o bit de sinal lógico em F5 e colocar zero em F4, reaproveitando as portas. |
| Comparação | `Igual_5bits`, `Maior_1bit`, `Maior_4bits`, `Maior_5bits` e `Menor_5bits` existem. | Verificar comparação numérica em sinal e magnitude, incluindo negativos e os dois zeros. Corrigir falhas mantendo os blocos. |
| Largura de comparador | `Maior_4bits.bdf/.bsf` usa entradas `A[4..0]` e `B[4..0]`, mas a lógica interna usa os bits 3..0. | Conferir a intenção e corrigir interface e instâncias para quatro bits se for o comparador de magnitudes. |
| Conversor decimal | `BIN_DC6bits.bdf` tem F, D, U e `LED_SINAL`; o BSF omite `LED_SINAL`. | Validar magnitude, separação de sinal e saída decimal; sincronizar o símbolo. |
| Displays | `decof7_unidade.bdf` e `decof7_dezena.bdf` recebem `MAG[4..0]` diretamente. Não têm BSF correspondente. | Validar os 32 valores e gerar símbolos; corrigir `decof7` para um nome coerente, como `decod_7seg_unidade` e `decod_7seg_dezena`. |
| Par de displays | `decod_7seg_base.bdf` instancia `seg_unidades` e `seg_dezenas`, sem BDF correspondente na pasta. | Reaproveitar esse esquema, corrigindo os tipos de símbolo para os decodificadores existentes e acrescentando habilitação. |
| Simulação | Há três VWF de muxes. Seus comandos contêm caminhos antigos em `D:/Users/mesa2/...` e projeto `mulitplexador`. | Corrigir referências e criar testes da integração. A existência de VWF não prova execução bem-sucedida. |
| Integração | Não há esquema geral da ULA nem esquema da interface com a placa. | Criar os níveis restantes e conectá-los à biblioteca corrigida. |

As constatações acima vêm da leitura das fontes, comparação das interfaces BDF/BSF e inspeção do PDF. Não foi executada compilação nem simulação funcional nesta análise. Estar encostado em uma linha ou ter a mesma legenda não foi considerado prova de conexão elétrica.

O Quartus 21.1 está instalado em `C:/intelFPGA_lite/21.1/quartus/bin64`, embora seus executáveis não apareçam no PATH consultado. Há também a pasta `questa_fse`; a disponibilidade operacional e a licença do simulador ainda precisam ser verificadas.

## Comportamento de referência, com a correção do usuário

Para soma, subtração e comparação, A e B são cinco bits em sinal e magnitude, com sinal no bit 4 e magnitude nos bits 3..0; faixa numérica -15..+15. Nessas operações aritméticas, F tem sinal em F5 e magnitude em F4..F0. Soma e diferença alcançam -30..+30. Soma, subtração e comparação tratam +0 e -0 como o mesmo número. Em `010`, B é tratado como padrão de bits, e F contém o resultado binário segundo o mapeamento ainda a confirmar; não impor a interpretação de sinal e magnitude a esse resultado.

| S2 S1 S0 | Operação | F | STATUS | Displays de F |
| --- | --- | --- | --- | --- |
| 000 | A+B | Resultado em sinal e magnitude | 0 | Magnitude decimal |
| 001 | A-B | Resultado em sinal e magnitude | 0 | Magnitude decimal |
| 010 | Complemento de dois dos bits brutos de B | NOT(B) + 1, na largura e no mapeamento em F a confirmar | 0 | Apagados |
| 011 | A=B | 000000 | Resultado da igualdade | Apagados |
| 100 | A>B | 000000 | Resultado da comparação | Apagados |
| 101 | A<B | 000000 | Resultado da comparação | Apagados |
| 110 | AND dos cinco bits brutos | `{L4,0,L3,L2,L1,L0}` | 0 | Apagados |
| 111 | XOR dos cinco bits brutos | `{L4,0,L3,L2,L1,L0}` | 0 | Apagados |

Nos caminhos lógicos, não normalizar o padrão de zero com sinal: o guia conserva o resultado bit a bit. A e B permanecem visíveis nos displays em todas as operações. Segmentos são ativos em zero, com ordem `[6..0]=gfedcba`; apagado é `1111111`.

Para `010`, na largura n, calcular `C2(B) = ((NOT B) + 1) mod 2^n`. A inversão é limitada aos n bits e a soma propaga carry; não é uma inversão independente de cada bit de saída. A extensão de entrada e o mapeamento da saída fazem parte do contrato funcional, portanto devem ser definidos antes de montar esse caminho.

Com a hipótese mais recente de cálculo após extensão para seis bits, a ordem importa: primeiro formar B6, depois inverter os seis bits e somar 1, descartando o carry além do bit 5. Confirmar uma das extensões:

| Regra candidata | B=00011 | B=10011 | B=10000 |
| --- | --- | --- | --- |
| B6={0,B[4..0]} | F=111101 | F=101101 | F=110000 |
| B6={B4,B[4..0]} | F=111101 | F=001101 | F=010000 |

As duas linhas pressupõem que F receba o resultado bruto de seis bits diretamente. São exemplos para decidir e testar, não requisitos já aprovados. Em ambos os casos, não interpretar `10000` como zero antes do cálculo. O comportamento atual de `Complemento_2.bdf` é diferente das duas propostas e precisa de correção.

## Execução por etapas

### 1. Fechar as decisões que afetam o comportamento

Aplicar o esclarecimento do usuário sobre `010` e tratar a extensão antes do cálculo como a proposta atual. Confirmar o valor do bit acrescentado e a entrega dos seis bits brutos em F. Não converter o "acho" do usuário em especificação definitiva. Conferir o enunciado original, se disponível. Confirmar se o alvo é a DE2-115: o guia indica EP4CE115F29C7, diferente do dispositivo dos relatórios antigos. Obter a pinagem de fonte confiável; não inventar pinos a partir dos nomes SW/HEX/LED.

Apresentar uma proposta curta de reaproveitamento antes de substituir estruturas existentes. A proposta preferida é corrigir e usar comparadores e decodificadores atuais. O caminho de comparação pela diferença e o decoder BCD compartilhado do guia são alternativas de otimização, cuja adoção exige avaliar a perda de reaproveitamento e validar a decisão com o usuário.

### 2. Corrigir a biblioteca e a hierarquia

Comparar as duas versões do somador, definir a versão canônica e evitar duas implementações concorrentes. Uniformizar arquivo, entidade do BSF, referências dos símbolos inseridos e QSF. Regenerar os símbolos após alterações de porta e atualizar suas instâncias nos BDF pais: trocar somente o nome do arquivo não resolve interfaces antigas embutidas no desenho.

Corrigir os nomes dos decodificadores e as referências ausentes em `decod_7seg_base`. Incluir `Complemento_2.bdf` no mapa da biblioteca, preservar seu nome e corrigir suas conexões e largura conforme a regra aprovada. Validar muxes, somador de 1 bit, complemento, lógica, comparadores e displays antes de integrá-los. Um bloco que já passa nos testes deve ser mantido; reparar somente a parte com defeito ou incompatibilidade comprovada.

### 3. Completar a aritmética assinada

Criar uma célula soma/subtração com XOR em Y e uma instância do `somador_1bit`. Construir uma cadeia de seis bits com `C0=SUB` e cada carry ligado ao próximo estágio. Reaproveitar o desenho e o padrão de encadeamento dos somadores existentes, sem duplicar portas que já estão encapsuladas.

Criar conversões reutilizáveis de sinal e magnitude para complemento de dois e de volta, ou adaptar a estrutura existente se uma solução menor atender ao mesmo comportamento. Na proposta do guia: `SM_C2` calcula `0 ± {0,0,M}` conforme o sinal; a operação usa um `ADD_SUB6`; `C2_SM` obtém a magnitude de R por `0 ± R`, conforme R5. Carry final não é sinal nem o bit extra de magnitude.

Completar 010 no próprio `Complemento_2.bdf`, depois de confirmar extensão e mapeamento. Não criar `C2_B` ou outro esquema paralelo que substitua o arquivo recebido. Se aprovado o cálculo em seis bits, manter B[4..0] como entrada externa, montar B6 dentro do bloco com a extensão escolhida, completar seis inversões e seis estágios reutilizando `somador_1bit`, e entregar F[5..0]. Preservar o padrão da cadeia aproveitável e corrigir a conexão de B4 com F0. Somar 1 no estágio menos significativo e garantir que a propagação alcance todos os seis bits. Não aplicar conversão SM→C2 ao operando desse caminho, C2→SM ao resultado ou normalização do padrão -0. Gerar `Complemento_2.bsf` sem comentários explicativos, atualizar suas instâncias e cadastrar o BDF no QSF quando integrado.

Os demais blocos possíveis são `ADD_SUB_BIT`, `ADD_SUB6`, `SM_C2` e `C2_SM`, todos com BDF e BSF quando instanciados. Os conversores SM/C2 continuam úteis para soma e subtração, mas são funções distintas da operação 010. Esses nomes são uma proposta, não obrigação de renomear blocos bons.

### 4. Completar controle e seleção

Criar `CONTROLE` e `STATUS`. Para a arquitetura do guia: `SUB=S0 OR S2`; `ENF=NOT S2 AND NOT S1`; `STATUS=(D3 AND EQ) OR (D4 AND GT) OR (D5 AND LT)`.

Reutilizar `MUX8_6` com D0=D1=resultado aritmético, D2=saída do `Complemento_2` corrigido segundo a regra confirmada, D3=D4=D5=zero, D6=AND e D7=XOR. A cadeia do complemento deve receber sua soma de 1 independentemente do SUB do caminho aritmético. As comparações devem alimentar STATUS, não F. Só criar decodificação necessária; não é preciso gerar oito saídas decodificadas se apenas D3/D4/D5 forem usadas.

Instanciar os comparadores existentes corrigidos se passarem na verificação numérica. Se for aprovada comparação pelo R=A6-B6 compartilhado, usar `EQ=(R=0)`, `LT=R5` e `GT=NOT R5 AND (R!=0)`, mantendo clara a destinação dos arquivos existentes. Não trocar a estratégia silenciosamente.

### 5. Completar os displays com reaproveitamento real

Primeiro validar os decodificadores diretos de magnitude existentes. Se estiverem corretos, corrigir suas referências e usar `decod_7seg_base` como o par decimal reutilizável, acrescentando EN e o apagamento dos dois dígitos. Isso evita criar em paralelo outra cadeia completa de conversão decimal.

Se os decodificadores tiverem falhas, corrigi-los no próprio arquivo. Só propor a alternativa `BIN_BCD5` + decoder BCD compartilhado quando houver razão concreta, respeitando a validação do usuário para mudança de arquitetura. A presença de `BIN_DC6bits` não obriga a encaixá-lo junto com decodificadores que já recebem a magnitude: verificar as interfaces para não converter duas vezes.

Instanciar três pares: A com MAG={0,A3..A0} e EN=1; B com MAG={0,B3..B0} e EN=1; F com MAG=F4..F0 e EN=ENF. Nomes possíveis para blocos novos: `ENABLE7` e, se necessário, um invólucro `DISPLAY_DEC2`; não duplicar o papel já atendido por `decod_7seg_base`.

### 6. Criar a integração e a interface com a placa

Criar `ULA.bdf/.bsf` com A[4..0], B[4..0], S[2..0] e saídas F[5..0], STATUS e ENF. Criar `TOP.bdf` para instanciar a ULA e os três pares de displays, mantendo o núcleo independente da pinagem.

Segundo a página 30 do guia:

| Origem | Destino |
| --- | --- |
| SW[4..0] | A[4..0] |
| SW[9..5] | B[4..0], preservando a ordem dos bits |
| SW[12..10] | S[2..0] |
| SW[12..0] | LEDR[12..0] |
| F[5..0] | LEDG[5..0] |
| STATUS | LEDG6 |
| Par A | Dezena em HEX5; unidade em HEX4 |
| Par B | Dezena em HEX3; unidade em HEX2 |
| Par F | Dezena em HEX1; unidade em HEX0 |
| VCC | Todos os segmentos de HEX7/HEX6 |
| GND | LEDG8..7 e LEDR17..13 |

Atualizar `TOP_LEVEL_ENTITY` e fontes no QSF. Usar apenas pinos verificados da placa confirmada. Sem pinagem validada, entregar a integração lógica e registrar claramente que a programação da placa ainda não foi validada.

### 7. Verificar funcionamento e apresentação

Abrir os BDF no Quartus, validar interfaces e conexões e compilar a hierarquia atual. Corrigir erros e avisos de entrada flutuante, largura incompatível, múltiplos drivers, entidade ausente ou sinal necessário desconectado. Gerar netlist dos BDF para simulação e comparar com um modelo independente; testar só as fórmulas de um script não valida os esquemas.

Cobertura desejada: oito casos do somador de 1 bit; seleção completa dos muxes com padrões distinguíveis e todos os bits; 32×32 casos para cada comparador; 32 magnitudes dos displays com EN=0/1; 32×32×8=8192 combinações da ULA integrada. Incluir zeros de ambos os sinais, extremos ±15, resultados ±30 e transições de decimal 9/10, 19/20 e 29/30.

Verificar `Complemento_2` corrigido e 010 para todos os 32 padrões brutos de B, usando a extensão e o mapeamento confirmados, sem interpretar os padrões como valores em sinal e magnitude. Incluir B=00000, 00001, 00011, 01111, 10000, 10011 e 11111 para detectar erros de carry e do bit superior. Corrigir o modelo de referência: os exemplos de negação numérica da página 33 do guia não valem para essa operação.

Conferir fisicamente a ligação fonte-porta em cada ramificação e saída. Cruzamentos e junções devem distinguir conexão de mera passagem. Não inserir comentários ou textos explicativos nos BDF/BSF. Entradas à esquerda, saídas à direita, barramentos agrupados, carry em uma direção, controle separado e espaço regular entre instâncias. Usar rótulos de rede apenas para identificação e derivação; evitar que substituam fios próximos. Exceções para ligações muito distantes devem ficar documentadas fora do desenho.

### 8. Entregar um relatório curto

Entregar fontes e símbolos coerentes, QSF/QPF utilizáveis, testes reproduzíveis e `RELATORIO_INTEGRACAO_ULA.md`. O relatório deve explicar, em linguagem simples, quais blocos foram reaproveitados, o que foi corrigido ou criado, como a ULA ficou integrada e quais verificações realmente passaram. Declarar pendências concretas, sem dizer que houve teste na placa ou simulação quando isso não ocorreu.

## Critério de conclusão

A entrega fica concluída quando o projeto abre e compila no Quartus com o top integrado; os testes do circuito real confirmam as oito operações e os displays; os desenhos têm conexões físicas e apresentação limpa; e não há dependências ausentes nem símbolos incompatíveis. Se requisitos, pinagem ou ferramentas impedirem algum desses pontos, identificar exatamente a parte validada e a parte pendente.

## Resumo desta análise

Li o guia e examinei os esquemas, símbolos, configuração e relatórios existentes. Incorporei `Complemento_2.bdf` exatamente como recebido e revisei o plano para corrigir e integrar esse bloco, sem criar um substituto paralelo. A leitura das conexões mostrou uma cadeia de apenas quatro bits e uma ligação suspeita de B4 com F0; não há extensão de B implementada. O cálculo em seis bits após extensão é a proposta atual, pendente de definir o bit acrescentado e o mapeamento em F. Os esquemas preexistentes, BSF, QSF e QPF não foram alterados, e o arquivo recebido ainda não foi corrigido nem compilado.
