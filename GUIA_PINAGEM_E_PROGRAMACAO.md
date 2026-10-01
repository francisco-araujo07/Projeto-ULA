# Pinagem e programação da DE2-115

## 1. Abrir o projeto correto

Os circuitos, a configuração, os testes e o SOF compilado estão na branch [feature/integracao-ula](https://github.com/francisco-araujo07/Projeto-ULA/tree/feature/integracao-ula). Use essa branch para abrir e programar o projeto. A branch `docs/relatorios-ula` acrescenta somente a documentação e os resultados da verificação à base original.

No Quartus, use **File → Open Project** e abra `projeto-ula.qpf` nesta pasta. A revisão é `projeto-ula`, o top é `TOP` e o dispositivo é **EP4CE115F29C7**. As fontes da entrega são BDF; os Verilog em `verificacao/netlist` servem somente aos testes.

**A pinagem já está aplicada no QSF.** Não é necessário atribuir os pinos manualmente. Abra **Assignments → Pin Planner** para conferir `Location` e `I/O Standard`. A relação completa, com todos os 101 pinos, está em [pinagem_de2_115.csv](https://github.com/francisco-araujo07/Projeto-ULA/blob/feature/integracao-ula/verificacao/pinagem_de2_115.csv). Todas as atribuições foram conferidas com o [manual DE2-115 enviado pelo usuário](https://drive.google.com/file/d/1oxiqKtVPTX-NDUOqMl7d9wLqDDCVz0Y6/view).

Se precisar refazer uma atribuição, procure o nome exato da porta no CSV e copie a coluna `pin` para `Location` e `io_standard` para `I/O Standard`. Preserve a ordem dos índices: HEX0[0] é o segmento a; HEX0[6] é g. O top declara SW[17..0], mas SW3..7 são ignoradas pela ULA; LEDR3..7 são saídas constantes em zero.

## 2. Conferir as tensões da placa

O QSF usa os padrões publicados no [manual oficial Terasic](https://www.terasic.com.tw/wiki/images/f/ff/DE2_115_User_manual_2013.pdf), tabelas 4-1, 4-3 e 4-4:

- **JP6: 3,3 V**, jumper nos pinos 7–8, configuração padrão do manual; alimenta o banco 4.
- **JP7: 2,5 V**, jumper nos pinos 5–6, configuração padrão do manual; alimenta os bancos 5 e 6.
- LEDs e HEX0[2..0] usam bancos fixos de 2,5 V. HEX7[6] usa banco fixo de 3,3 V.

Confira os jumpers com a placa desligada. Se a sua placa estiver configurada para outras tensões, faça o padrão elétrico e a tensão física coincidirem antes da programação. Não aplique 3,3-V LVTTL indiscriminadamente a todas as portas: os recursos ocupam bancos com tensões diferentes.

## 3. Compilar

Use **Processing → Start Compilation**. A compilação deve terminar sem erros. O arquivo para programação volátil é:

`output_files/integracao/projeto-ula.sof`

Para testar o binário publicado, baixe [ULA_DE2_115_REMAPEADA.sof](https://github.com/francisco-araujo07/Projeto-ULA/blob/feature/integracao-ula/output_files/integracao/ULA_DE2_115_REMAPEADA.sof). Ele é uma cópia do SOF regenerado em uma pasta nova, sem caches anteriores do Quartus. Use **Change File** no Programmer para selecionar explicitamente esse arquivo. Se recompilar o projeto localmente, use o `projeto-ula.sof` resultante da sua compilação.

Ao recompilar, o Quartus gera os relatórios na mesma pasta do SOF. Os resultados da verificação publicada estão na branch `docs/relatorios-ula`.

Há avisos esperados: HEX2/3 apagados e LEDs não usados têm saídas constantes; alguns segmentos das dezenas de A/B também são constantes porque suas magnitudes ficam em 0..15. SW3..7 não têm fan-out porque são ignoradas pela ULA. O projeto não define requisitos de tempo e não tem clock: os avisos de SDC ausente e de ausência de clocks não representam teste temporal aprovado. O Fitter também usa valores padrão de corrente e slew rate; não foram inventadas restrições do professor. O aviso de LogicLock decorre da configuração herdada em uma instalação Lite. Erros, entradas flutuantes, múltiplos drivers ou entidades ausentes devem ser resolvidos antes de programar.

## 4. Carregar o SOF por JTAG

1. Alimente a DE2-115 e conecte o computador à porta **USB-Blaster** da placa.
2. Deixe a chave de programação **SW19 em RUN**. Para a cadeia padrão, sem placa filha HSMC, JP3 fica nos pinos 1–2, conforme o manual/FAQ da Terasic.
3. No Quartus, abra **Tools → Programmer**.
4. Em **Hardware Setup**, selecione o cabo **USB-Blaster**. Se ele não aparecer, confira o cabo USB, a alimentação e o driver no Gerenciador de Dispositivos. O driver da instalação está em `C:/intelFPGA_lite/21.1/quartus/drivers/usb-blaster`.
5. Selecione **Mode: JTAG** e use **Auto Detect**. Confira se aparece o dispositivo **EP4CE115**. Se houver outro dispositivo ou cadeia inesperada, verifique o alvo antes de continuar.
6. Associe `output_files/integracao/projeto-ula.sof` ou o arquivo publicado `ULA_DE2_115_REMAPEADA.sof` ao EP4CE115, usando **Change File** ou **Add File**, conforme a lista apresentada. Evite duas entradas para o mesmo FPGA.
7. Marque **Program/Configure** e clique **Start**. Aguarde **100% (Successful)**.

Esse procedimento carrega a SRAM do FPGA: a configuração é perdida quando a placa é desligada. Este guia não cobre gravação permanente em memória de configuração. Nenhuma placa foi programada pelo agente.

## 5. Usar as chaves e interpretar as saídas

| Recurso | Função |
| --- | --- |
| SW17 | Sinal de A: 0 positivo, 1 negativo |
| SW16..13 | Magnitude de A, de 0 a 15; SW13 é o bit menos significativo |
| SW12 | Sinal de B |
| SW11..8 | Magnitude de B; SW8 é o bit menos significativo |
| SW2..0 | Seleção da operação; SW0 é S0 |
| SW7..3 | Ignoradas |
| LEDR17..13 | Espelho dos cinco bits de A em SW17..13 |
| LEDR12..8 | Espelho dos cinco bits de B em SW12..8 |
| LEDR2..0 | Espelho da seleção em SW2..0 |
| LEDR7..3 | Apagados |
| LEDG5..0 | Os seis bits de F |
| LEDG6 | STATUS nas comparações |
| HEX7/HEX6 | Dezena/unidade da magnitude de A |
| HEX5/HEX4 | Dezena/unidade da magnitude de B |
| HEX1/HEX0 | Dezena/unidade da magnitude de F em soma/subtração |
| HEX3/HEX2 | Apagados |

| SW2 SW1 SW0 | Operação | Saída |
| --- | --- | --- |
| 000 | A+B | Sinal em LEDG5, magnitude em LEDG4..0; displays F ligados |
| 001 | A−B | Mesmo formato da soma |
| 010 | Complemento bruto de B em seis bits | F bruto nos LEDs; displays F apagados |
| 011 | A=B | LEDG6 indica a igualdade; F=0 |
| 100 | A>B | LEDG6 indica maior que; F=0 |
| 101 | A<B | LEDG6 indica menor que; F=0 |
| 110 | AND dos cinco bits | Bit lógico 4 vai para LEDG5; LEDG4=0 |
| 111 | XOR dos cinco bits | Mesmo mapeamento do AND |

A e B são sinal e magnitude, não complemento de dois. Por exemplo, −3 em A é `10011`: SW17=1, SW14=1, SW13=1 e SW16=SW15=0. Para −3 em B, SW12=1, SW9=1, SW8=1 e SW11=SW10=0. +0=`00000` e −0=`10000` são iguais para soma, subtração e comparação. O zero aritmético sai com sinal positivo.

Em 010, a regra é `F = (-{B4,B[4..0]}) mod 64`. Não interprete LEDG5 como sinal e magnitude nesse caminho: é apenas o bit superior do resultado bruto. Em particular, B=`10000` gera F=`010000`.

## 6. Teste rápido na placa

Defina primeiro A em **SW17..13** e B em **SW12..8**, depois a seleção em **SW2..0**. Leia F na ordem **LEDG5..LEDG0** e STATUS em LEDG6. Espere as chaves estabilizarem: a ULA é combinacional e não contém debounce nem registradores. Mudar SW3..7 não deve alterar nenhuma saída.

| A bruto | B bruto | S | F esperado | STATUS | HEX1/HEX0 |
| --- | --- | --- | --- | --- | --- |
| 01111 | 01111 | 000 | 011110 | 0 | 30 |
| 11111 | 11111 | 000 | 111110 | 0 | 30 |
| 00011 | 10100 | 000 | 100001 | 0 | 01 |
| 10011 | 00100 | 001 | 100111 | 0 | 07 |
| 00011 | 10100 | 001 | 000111 | 0 | 07 |
| 10000 | 00000 | 011 | 000000 | 1 | Apagados |
| 10011 | 10100 | 100 | 000000 | 1 | Apagados |
| 10100 | 10011 | 101 | 000000 | 1 | Apagados |
| 10011 | 10101 | 110 | 100001 | 0 | Apagados |
| 10011 | 10101 | 111 | 000110 | 0 | Apagados |
| 00000 | 00011 | 010 | 111101 | 0 | Apagados |
| 00000 | 10000 | 010 | 010000 | 0 | Apagados |
| 00000 | 10011 | 010 | 001101 | 0 | Apagados |

Os displays A/B permanecem ligados em todas as operações e mostram apenas magnitude. Sete segmentos são ativos em zero: apagar corresponde a `1111111`, não `0000000`.

## 7. Reproduzir a verificação lógica

No PowerShell, dentro da pasta do projeto:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File verificacao/executar_verificacao.ps1 -Compilar
```

O script exporta novamente os BDF pelo Quartus, confere BDF/BSF e terminais das instâncias, compara as netlists combinacionais com um modelo independente e compila. Precisa do Python e do Quartus no caminho indicado; aceita `-Python` e `-QuartusBin` para outras instalações.

As contagens e casos explícitos estão em `verificacao/resultados_testes.json`. O simulador Questa instalado recusou a licença; a verificação entregue interpreta as netlists estruturais, sem simulação de atrasos. A revisão visual no editor Quartus foi deixada para você por solicitação expressa.

## 8. Conferir o download do SOF

O SHA-256 do arquivo publicado está em [ULA_DE2_115_REMAPEADA.sof.sha256](https://github.com/francisco-araujo07/Projeto-ULA/blob/feature/integracao-ula/output_files/integracao/ULA_DE2_115_REMAPEADA.sof.sha256). No computador que fará a programação, rode na pasta do download:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath .\ULA_DE2_115_REMAPEADA.sof
```

O hash deve coincidir com o arquivo `.sha256`. Esse SHA-256 verifica o download; o campo **Checksum** no Programmer usa outro formato. O registro da recompilação, com dispositivo, mapeamento, checksum do Programmer e hashes, está em `verificacao/regeneracao_sof.json` na branch de relatórios. Compilar e testar logicamente o SOF não confirma que a transferência JTAG foi concluída na placa.
