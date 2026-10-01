# Prompt para o agente que concluirá a ULA

Você trabalhará no projeto Quartus em `C:/Users/mathe/Downloads/projeto_ula`. Conclua os arquivos pendentes e a integração da ULA, respeitando o comportamento do projeto e reaproveitando os esquemas e símbolos existentes. Leia primeiro `AGENTS.md`, se houver, `PLANO_INTEGRACAO_ULA.md`, o PDF e as fontes atuais. O plano contém evidências de uma análise em 01/10/2026; confira-as novamente, pois o repositório pode ter mudado.

## Antes de implementar

O PDF consultado localmente é `Guia_Visual_ULA_Montagem_Manual.pdf`. Ele cita um enunciado original, `Projeto_Primeira_Unidade_2026_2.pdf`, ausente durante a análise. O guia propõe negação numérica de B em sinal e magnitude para 010; o usuário corrigiu expressamente esse ponto e confirmou a regra completa: formar `B6={B[4],B[4..0]}`, calcular `F=(NOT(B6)+1) mod 64` e entregar os seis bits brutos diretamente em F[5..0]. Essa correção prevalece sobre o guia. Reaproveite o arquivo fornecido `Complemento_2.bdf`, corrigindo-o para essa regra. Não solicite nova confirmação da função, extensão ou mapeamento de 010. Se o enunciado original estiver disponível, confronte os demais requisitos com ele. Se o guia não estiver na cópia remota, use o inventário e os requisitos transcritos no plano para avançar e solicite a fonte para resolver divergências; não invente seu conteúdo.

O usuário prefere validar decisões. Apresente uma proposta curta antes de trocar a arquitetura, substituir blocos existentes ou escolher algo que altere o comportamento. Não decida silenciosamente que a biblioteca do guia deve substituir a do repositório. O objetivo é terminar o projeto atual. Reparos concretos já descritos neste pedido fazem parte do trabalho; conserve o usuário informado e peça esclarecimento quando uma correção admitir comportamentos diferentes.

## Regras obrigatórias de implementação

1. Entregue circuitos reais em `.bdf` e símbolos coerentes em `.bsf`. Não substitua o projeto esquemático por HDL. HDL pode servir como apoio de simulação e verificação, sem substituir as fontes BDF da entrega.
2. Use os BDF e BSF existentes. Se tiverem erro, corrija-os e reaproveite-os. Crie um novo bloco somente para função ausente ou agrupamento que reduza repetição de maneira clara. Não mantenha uma implementação nova paralela à antiga sem justificar e validar essa decisão.
3. Não adicione comentários, notas, legendas explicativas ou caixas de texto aos esquemas e símbolos. Preserve identificadores funcionais de portas, redes e instâncias, e os cabeçalhos legais automáticos existentes. Explicações pertencem ao relatório externo.
4. Use barramentos onde representem naturalmente vetores, com largura, ordem e derivações corretas. Um barramento precisa de conexão válida e seleção de bit; uma linha escalar apenas encostada nele não comprova essa ligação.
5. Ligue verdadeiramente os fios entre origens e destinos. Não use conexão exclusivamente por nome quando for possível uma ligação curta e clara. Só use a exceção para uma rede realmente distante; registre brevemente a razão no relatório, sem comentário no desenho. Rótulos para identificar fios já conectados e selecionar bits são permitidos.
6. Desenhe de forma legível: entradas à esquerda, saídas à direita, componentes alinhados, espaços regulares, fios ortogonais, poucos cruzamentos e junções somente onde houver ligação. Agrupe dados em barramentos e organize controles em uma faixa separada. Dê nomes funcionais às instâncias, sem acrescentar texto explicativo.
7. Corrija nomes errados ou incoerentes em conjunto: arquivo BDF, arquivo BSF, entidade do símbolo, símbolos inseridos nos BDF pais, QSF e simulações. Mantenha grafia e capitalização consistentes. Não renomeie blocos corretos só por preferência estética.
8. Após mudar portas, gere novamente o símbolo e atualize as instâncias dos esquemas pais, conferindo a posição de cada terminal e os fios. Um BSF novo não garante que as cópias já inseridas estejam sincronizadas.
9. Não invente pinagem, restrições do professor nem resultados de teste. Não programe a placa sem autorização específica. Não apague trabalho existente nem faça commit/publicação sem pedido.

## O que já existe e precisa ser aproveitado

- `somador_1bit.bdf/.bsf`: base de todas as cadeias aritméticas; validar as oito combinações.
- `somador_5bit.bdf` e `Somador_5bits.bdf`: versões semelhantes que precisam ser comparadas e consolidadas sem perda de trabalho. A primeira não tem Cin externo, embora seu BSF declare Cin.
- `Complemento_2.bdf`: arquivo fornecido pelo usuário e incorporado sem alterações. Reaproveitá-lo obrigatoriamente para 010, corrigindo o circuito no próprio arquivo; não criar `C2_B` ou outra implementação paralela. Atualmente recebe B[4..0] e entrega F[4..0], usa quatro NOT e quatro `somador_1bit`, soma 1 via VCC no primeiro estágio e mantém Cin de todos os estágios em zero. Nos seguintes, o carry chega ao terminal B: isso é válido para a soma e não deve ser apontado isoladamente como erro. Não existe inversão/célula para B4 nem sexto bit. Cout final está sem fio. A ligação rotulada B[4] termina em (640,480), onde também termina a derivação F[0]; conferir e corrigir esse conflito e a ausência de derivação F[4]. O nome do arquivo não é evidência de correção funcional. Após definir a largura, gerar `Complemento_2.bsf` e incluir o BDF no QSF durante a integração.
- `MUX1`, `MUX2_6` e `MUX8_6`: reutilizar a hierarquia. Conferir D0/D1 e os níveis S0, S1, S2. Há conexões por nome nos seletores de `MUX8_6`; substituir por fios físicos onde a disposição permitir.
- `And_5bits` e `Xor_5bits`: reutilizar as cinco portas. Hoje o quinto bit bruto vai para F4 e F5 está em zero; no guia, o bit bruto de sinal deve ir para F5 e F4 deve ficar em zero.
- `Igual_5bits`, `Maior_1bit`, `Maior_4bits`, `Maior_5bits` e `Menor_5bits`: validar numericamente, incluindo sinais e os dois zeros. A interface de `Maior_4bits` tem cinco bits apesar de usar internamente apenas 3..0; conferir e corrigir também suas instâncias.
- `BIN_DC6bits`: validar antes de integrar. O BDF tem saída `LED_SINAL` ausente no BSF. Não confundir sinal, magnitude e carry, nem colocar esse conversor em série com um decoder que já espera magnitude binária sem necessidade.
- `decof7_unidade.bdf`, `decof7_dezena.bdf` e `decod_7seg_base.bdf`: corrigir os nomes para uma convenção coerente, gerar os símbolos ausentes e reutilizar os circuitos. O esquema base referencia `seg_unidades` e `seg_dezenas`, entidades sem fonte na pasta; corrigir as referências para os blocos reais. Os decodificadores atuais recebem MAG[4..0], não um dígito BCD.
- VWF dos muxes: corrigir os caminhos absolutos antigos e a revisão `mulitplexador`; aproveitar os estímulos úteis.
- QSF/QPF atuais: manter o projeto utilizável. O top atual é `BIN_DC6bits`; faltam fontes da hierarquia. Os relatórios antigos compilam apenas um somador e não comprovam a ULA completa.

## Comportamento funcional de referência

Usar as páginas 2, 30, 31 e 33 do guia como referência dos demais comportamentos, com a seguinte correção obrigatória em 010:

| Seleção S[2..0] | Função | F[5..0] | STATUS | Displays F |
| --- | --- | --- | --- | --- |
| 000 | A+B | Sinal e magnitude | 0 | Ligados |
| 001 | A-B | Sinal e magnitude | 0 | Ligados |
| 010 | Complemento de dois após repetir B4 na extensão | `(NOT({B4,B[4..0]})+1) mod 64`, diretamente em F[5..0], usando Complemento_2 corrigido | 0 | Apagados |
| 011 | A=B | 000000 | EQ | Apagados |
| 100 | A>B | 000000 | GT | Apagados |
| 101 | A<B | 000000 | LT | Apagados |
| 110 | AND bit a bit | `{L4,0,L3,L2,L1,L0}` | 0 | Apagados |
| 111 | XOR bit a bit | `{L4,0,L3,L2,L1,L0}` | 0 | Apagados |

Para soma, subtração e comparação, A e B são sinal e magnitude: bit 4 de sinal e quatro bits de magnitude. Nessas operações aritméticas, F tem sinal no bit 5 e cinco bits de magnitude. Entradas representam -15..+15; soma/diferença representam -30..+30. Comparações são numéricas, não comparação sem sinal dos padrões binários. +0 e -0 são iguais nesse tratamento numérico; soma e subtração com resultado zero devem sair com sinal positivo. AND/XOR atuam nos cinco bits brutos e conservam o resultado, inclusive eventual zero com sinal.

Em 010, primeiro formar B6={B4,B4,B3,B2,B1,B0}, depois inverter os seis bits e somar 1, descartando o carry além do bit 5. A soma de 1 propaga carry. Não inverter em quatro ou cinco bits e somente depois ampliar o resultado. Não substituir essa operação por troca do sinal, conversão da entrada de sinal e magnitude para C2 ou negação numérica seguida de conversão para sinal e magnitude. Não normalizar a entrada `10000` por ela representar -0 em outro caminho. F contém diretamente o resultado bruto de seis bits nessa operação.

Exemplos confirmados para os testes: B=00000→F=000000; B=00011→F=111101; B=01111→F=110001; B=10000→F=010000; B=10011→F=001101; B=11111→F=000001. O arquivo recebido ainda não implementa essa regra completa e precisa ser corrigido.

Displays A/B sempre mostram magnitude. Displays F mostram magnitude apenas em soma/subtração. Sete segmentos são ativos em zero, `[6..0]=gfedcba`; desligar é produzir `1111111`, e não `0000000`. Confirme 0=`1000000`, 1=`1111001`, 8=`0000000` e 9=`0010000`.

## Caminho de execução

1. Faça inventário e mapa da hierarquia, das interfaces e dos requisitos, incluindo `Complemento_2.bdf`. Distinga erro confirmado de suspeita. A função, a extensão repetindo B4 e a saída bruta de seis bits de 010 já estão definidas. Confirme somente as demais informações ainda ausentes, como a placa e sua pinagem, antes das partes dependentes.
2. Corrija a biblioteca existente, os símbolos desatualizados, nomes e dependências ausentes. Reutilize comparadores e decodificadores quando atendam ao comportamento após as correções.
3. Complete a aritmética assinada e o complemento de dois bruto de B como funções distintas. Para soma/subtração, a arquitetura de referência usa `somador_1bit` dentro de uma célula soma/subtração, cadeias de seis bits e conversões reutilizáveis SM→C2 e C2→SM. SUB inverte Y por XOR, C0=SUB, e os carries seguintes vêm do estágio anterior. Para 010, corrija `Complemento_2.bdf`: preserve B[4..0] como entrada externa, forme B6={B4,B[4..0]} internamente, complete seis inversões e seis estágios reaproveitando `somador_1bit`, corrija o conflito B4/F0 e exponha o resultado bruto em F[5..0]. Aproveite a cadeia existente, sem conversões de sinal e magnitude nem NEG_SM. Gere o BSF com a interface corrigida, atualize instâncias e cadastro no QSF. Nunca use carry final como sinal de F.
4. Complete controle, STATUS e fontes do `MUX8_6`. D0=D1=resultado aritmético; D2=saída do `Complemento_2` corrigido; D3=D4=D5=zero; D6=AND6; D7=XOR6. Os três bits S controlam a árvore de muxes diretamente. Na arquitetura do guia, SUB=S0 OR S2 e ENF=NOT S2 AND NOT S1. A cadeia própria do complemento recebe sua soma de 1 independentemente do SUB aritmético. Qualquer compartilhamento que elimine o bloco recebido exige justificativa e validação prévia do usuário. Decodifique somente os termos necessários para STATUS.
5. Complete um único par de displays reutilizável a partir de `decod_7seg_base`, dos decodificadores atuais e de habilitação ativa corretamente. Instancie-o três vezes. Não crie automaticamente outro conversor/decoder BCD para substituir circuitos aproveitáveis; proponha essa mudança somente com justificativa concreta e validação do usuário.
6. Crie `ULA.bdf/.bsf` para o núcleo e `TOP.bdf` para placa e displays, ou nomes equivalentes aprovados. Organize o nível superior em poucos blocos claros e fios físicos. Atualize fontes e top no QSF, preservando o QPF.
7. Valide os desenhos no Quartus, compile a hierarquia integrada, simule o circuito derivado dos BDF e confira visualmente os esquemas. Corrija as falhas encontradas e repita somente as verificações afetadas.
8. Entregue todos os arquivos necessários e um relatório curto, sem deixar a integração para o usuário montar manualmente.

Para o núcleo, uma interface proposta é A[4..0], B[4..0], S[2..0] → F[5..0], STATUS, ENF. Os blocos novos devem representar funções ausentes, como conversões, soma/subtração, controle e integração. O complemento de B já tem seu arquivo-base, `Complemento_2.bdf`; sua correção faz parte da entrega. Não crie `C2_B`, `NEG_SM`, um segundo somador completo de 1 bit ou um segundo mux funcionalmente igual ao existente para substituir os blocos aproveitáveis.

Se desejar compartilhar o caminho aritmético para comparação, a diferença R=A6-B6 cabe em seis bits: EQ=(R=0), LT=R5 e GT=NOT R5 AND (R!=0). Essa otimização compete com o reaproveitamento dos comparadores atuais; explique a escolha antes de substituir sua utilização. Não deixe blocos atuais abandonados silenciosamente.

## Ligações da placa, condicionadas à confirmação do alvo

O guia especifica DE2-115, dispositivo EP4CE115F29C7. A configuração atual é Cyclone IV E com dispositivo automático; relatórios antigos usam outro dispositivo. Não reutilize essa escolha antiga como evidência do alvo correto.

- SW[4..0] → A[4..0]; SW[9..5] → B[4..0]; SW[12..10] → S[2..0], preservando a ordem.
- SW[12..0] → LEDR[12..0]. LEDR[17..13]=0.
- F[5..0] → LEDG[5..0]; STATUS → LEDG6. LEDG[8..7]=0.
- A: magnitude `{0,A[3..0]}`, EN=1, dezena HEX5 e unidade HEX4.
- B: magnitude `{0,B[3..0]}`, EN=1, dezena HEX3 e unidade HEX2.
- F: magnitude F[4..0], EN=ENF, dezena HEX1 e unidade HEX0.
- HEX7 e HEX6 apagados, com sete saídas em 1 cada.

Obtenha pinos físicos e padrões elétricos do enunciado, configuração validada da placa ou documentação oficial. Se a pinagem não estiver disponível, peça somente essa informação e avance no núcleo independente. Declare a pendência; não apresente um projeto com pinos arbitrários como pronto para a placa.

## Validação obrigatória

Use o Quartus instalado, se disponível, sem sobrescrever evidência útil com resultados parciais apresentados como finais. O caminho encontrado na análise foi `C:/intelFPGA_lite/21.1/quartus/bin64`. Há `questa_fse`, mas ainda é necessário verificar execução e licença.

Abra os desenhos e confira que símbolos, posições de portas e conexões físicas correspondem ao circuito. Os fios devem terminar nos terminais corretos; cruzamentos não devem criar curtos acidentais; barramentos devem ter derivações válidas. Uma inspeção textual é complementar. Corrija erros e avisos funcionais de entidade ausente, largura incompatível, entrada flutuante e múltiplos drivers; explique avisos remanescentes relevantes.

Compile o top integrado. Gere netlist para simular os BDF reais contra um modelo independente, com:

- Somador de 1 bit: 8 combinações; muxes: todas as seleções e todos os bits, usando entradas distinguíveis.
- Comparadores usados: 32×32 padrões por função, incluindo -0/+0 e negativos.
- Conversões usadas: todos os padrões de entrada e toda a faixa -30..+30 de saída.
- `Complemento_2` corrigido e operação 010: todos os 32 padrões brutos de B, com extensão, inversão, soma de 1 e mapeamento em F verificados; modelo independente sem interpretação em sinal e magnitude. Incluir 00000, 00001, 00011, 01111, 10000, 10011 e 11111 para conferir carry e bit superior.
- Displays: magnitudes 0..31 e habilitação 0/1; se houver decoder BCD, verificar 10..15 conforme seu contrato.
- ULA integrada: 32×32×8=8192 combinações, conferindo F, STATUS, ENF, LEDs e os seis displays.

Casos mínimos explícitos: +15+15→+30 (`011110`); (-15)+(-15)→-30 (`111110`); +3+(-4)→-1 (`100001`); -3-(+4)→-7 (`100111`); +3-(-4)→+7 (`000111`); -0=+0 verdadeiro; -3>-4 verdadeiro; -4<-3 verdadeiro. Para lógica, A=`10011`, B=`10101`: AND→`100001`; XOR→`000110`. Para 010, utilizar exemplos de padrões binários e a regra confirmada de largura e mapeamento; os exemplos de negação numérica da página 33 do guia não são expectativas válidas dessa operação.

Não declare sucesso por repetir as equações do guia em um script. A validação deve cobrir os esquemas implementados. Se compilação, simulação ou teste físico não puderem ser executados, diga exatamente o que foi feito, o motivo e o que falta; nunca fabrique aprovação.

## Entrega e relatório final

Entregue os BDF/BSF corrigidos e novos, QSF/QPF coerentes, testes reproduzíveis e `RELATORIO_INTEGRACAO_ULA.md`. Não inclua comentários nos desenhos para explicar a entrega.

Escreva o relatório em português claro, aproximadamente 200 a 350 palavras, ajustando o tamanho se houver uma pendência importante. Explique o que foi reaproveitado, incluindo `Complemento_2.bdf`, quais erros e nomes foram corrigidos, quais blocos faltantes foram criados, como foram integrados e quais testes realmente passaram. Informe a fonte de requisitos adotada, a correção de 010 para complemento de dois bruto, a regra de extensão efetivamente aprovada e eventuais limitações de pinagem ou ferramenta. Evite diário de comandos e explicações genéricas. Termine com uma frase objetiva sobre o estado da entrega: pronta no Quartus, validada na placa ou com a pendência específica restante.
