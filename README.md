# A Casa de Astérion - uma peça para computador.
##### Gabriel Dargains
2025.1 - Seminários Avançados de Composição (UNIRIO)
profs: Alexandre Fenerich e Marcelo Carneiro.

🎴🔊🎧
### I.
A peça é uma composição generativa em Python/Csound em tempo real, usando o módulo ctcsound para o Python (que permite que o Python leia e interprete a sintaxe do Csound). A ideia foi articular alguns conceitos dos paradigmas de programação para criar uma estrutura lógica e simbólica integrando Csound para disparar sons que fossem gerados a partir do desdobramento da estrutura. Escolhi alguns simbolismos no conto A Casa de Astérion(1947) de Jorge Luis Borges para pensar na montagem do código, que é uma releitura do mito do Minotauro a partir do próprio como protagonista. Não é uma reconstrução do conto, porque o interesse foi esboçar um sistema de composições a ser refinado. A ideia foi me aproximar de uma composição baseada em processos e elaborar uma ecologia simbólica dos atores no conto - com a programação orientada a objetos (POO ou OOP), foi criado um esquema para formação de um labirinto, o Astérion e o Teseu. Astérion e Teseu percorrem o labirinto, cada ação cria um evento no Csound que dispara sons de acordo com qualidades da sala do labirinto. A composição tem duração máxima de 5 minutos e pode acabar antes caso Teseu encontre e mate Astérion.
#### Labirinto
O labirinto é formado aleatoriamente com 14 salas conectadas que possuem comprimento, largura, altura, nome de cômodo, um adjetivo, referencia de temperatura e de umidade. Os valores das dimensões são escolhidos de forma aleatória garantindo que a sala não seja pequena demais. O nome do cômodo e o adjetivo são escolhidos aleatoriamente a partir dessa lista: 
NOMES_COMODO = ["Saguão", "Cozinha", "Quarto", "Corredor", "Jardim", "Sala", "Varanda", "Porão", "Sótão"]
ADJETIVOS_SALA = [ " de Verão", " de Inverno", " Primaveril", " Outonal", " Principal", " Reserva", " de Hóspedes"," em Construção", " em Ruínas"]

Os parâmetros de temperatura e umidade são escolhas de quente ou frio e úmido ou seco, dessa forma a combinação dos dois me permite atribuir um dos elementos aristotélicos (água, fogo, terra e ar) a cada sala (uma maneira de combinar o esoterismo pragmático do Borges com uma categorização simbólica que me ajuda a criar os timbres da composição). Um algoritmo numera as salas e as conecta para que haja um percurso com escolhas. 
Um exemplo de um labirinto formado ao início de uma das execuções:
Labirinto com 14 salas:
- Porão de Hóspedes (ID: 0) - Dimensões: 81.6x108.5x13.3 | Temp: quente, Umid: úmido, Elemento: Ar. Vizinhos: [2, 3, 4, 7]
- Jardim de Verão (ID: 1) - Dimensões: 91.8x46.3x4.8 | Temp: frio, Umid: seco, Elemento: Terra. Vizinhos: [4, 8]
- Cozinha Primaveril (ID: 2) - Dimensões: 39.3x133.0x6.6 | Temp: frio, Umid: seco, Elemento: Terra. Vizinhos: [0, 11, 6]
- Sala em Construção (ID: 3) - Dimensões: 122.4x74.1x11.2 | Temp: quente, Umid: seco, Elemento: Fogo. Vizinhos: [0, 9, 7]
- Corredor de Verão (ID: 4) - Dimensões: 85.6x124.7x11.8 | Temp: frio, Umid: seco, Elemento: Terra. Vizinhos: [1, 0, 5]
- Sala Primaveril (ID: 5) - Dimensões: 70.3x94.5x11.4 | Temp: frio, Umid: úmido, Elemento: Água. Vizinhos: [4]
- Cozinha de Verão (ID: 6) - Dimensões: 44.5x15.8x5.1 | Temp: quente, Umid: seco, Elemento: Fogo. Vizinhos: [2, 7, 13]
- Quarto Primaveril (ID: 7) - Dimensões: 122.0x124.6x3.7 | Temp: frio, Umid: seco, Elemento: Terra. Vizinhos: [6, 3, 0, 9, 10]
- Quarto Primaveril (ID: 8) - Dimensões: 109.4x35.8x9.3 | Temp: frio, Umid: seco, Elemento: Terra. Vizinhos: [13, 1, 9]
- Varanda de Inverno (ID: 9) - Dimensões: 9.3x81.0x10.5 | Temp: quente, Umid: úmido, Elemento: Ar. Vizinhos: [3, 7, 8, 11]
- Saguão Outonal (ID: 10) - Dimensões: 71.1x57.9x11.2 | Temp: quente, Umid: seco, Elemento: Fogo. Vizinhos: [7, 12]
- Quarto de Hóspedes (ID: 11) - Dimensões: 101.7x78.5x13.5 | Temp: frio, Umid: úmido, Elemento: Água. Vizinhos: [2, 9, 13, 12]
- Cozinha Reserva (ID: 12) - Dimensões: 112.3x46.3x10.8 | Temp: frio, Umid: úmido, Elemento: Água. Vizinhos: [10, 11]
- Sala em Construção (ID: 13) - Dimensões: 130.5x25.4x4.8 | Temp: frio, Umid: seco, Elemento: Terra. Vizinhos: [8, 11, 6]

Os elementos de cada sala decidem um timbre e limiar de envelopes generativos para cada momento em que uma entidade entra ou age no espaço. A princípio cada elemento lida com um limiar diferente, onde 'terra' e 'fogo' são notas mais curtas e secas, 'água' e 'ar' são notas um pouco mais longas. Além disso, cada elemento usa um instrumento com um formato de onda diferente: água usa uma onda serrilhada, fogo um pulso, ar usa uma onda quadrada e terra usa um formato de onda customizado para ressaltar inarmônicos. Um instrumento dedicado a marcar o movimento de Astérion e Teseu utiliza uma onda triangular.

Astérion e Teseu são colocados em salas diferentes após iniciação, para que a execução não termine no primeiro turno. Cada entidade possui tempo de deslocamento e tempo para ações possíveis na sala. O Minotauro pode contemplar, correr e Teseu apenas busca e mata o minotauro, fazendo a peça acabar. A cada deslocamento ou ação, é disparado um evento sonoro que é decidido com escolhas aleatórias dentro de um limiar específico para a ação ou deslocamento - a cada momento que Teseu percorre uma sala, dispara também o "som da sala", que é um evento sonoro de um dos instrumentos dedicados aos elementos, com parâmetros ligados a valores das dimensões da sala e a umidade/temperatura.

Todos os instrumentos enviam os sons para um instrumento que serve para inserir delay e reverb. Temos mais um instrumento que criei para gerar sons de vento, para aumentar a ambiência de um espaço grande e vazio. Por fim, criei duas janelas que se assemelham ao terminal do Python para rotear as mensagens que pertencem ao universo simbólico da peça, uma removendo os eventos do Csound, mostrando a linha do tempo dos personagens se movendo pelas salas e a outra mostrando a inicialização do labirinto com as suas salas nomeadas, suas dimensões, elementos, vizinhos, como um tipo de lista que também é um mapa em potencial.

A peça é um protótipo, que pode crescer em qualquer direção, seja acrescentar mais comportamentos, mais entidades habitando o labirinto, o labirinto em si e seus parâmetros. É interessante a possibilidade de tornar mais complexa e incorporar mais questões e símbolos do mito e do conto, mas ela já funciona bem para articular as ideias principais da composição.

#### II. 
O pensamento composicional desse sistema gira em torno de dois pilares: a indissociabilidade entre as estruturas de ordem lógica, simbólica e sonora; e o uso dessa relação como suporte de mídia. Em primeiro lugar, me interessa que aqui a peça não faça sentido isolada de seu contexto, seu acesso se dá por um terminal de programação e seus sons são novos a cada execução, significados pelos movimentos lidos na perseguição de Teseu. A peça inicialmente foi pensada para ter seu código lido (mesmo que a versão apresentada não esteja tão organizada quanto eu gostaria) de maneira que o leitor encontra os símbolos e recebe informações sobre os mecanismos do que está sendo executado. A leitura do código com os comentários, a leitura do terminal em tempo real e os sons gerados compõem o total da recepção da peça.

O som aqui age como uma forma abstrata de acompanhar o comportamento dos personagens em ação - "o som é meio de transporte" (Caesar, p.22), nesse caso das ações das entidades que se deslocam pelas salas, deixando vestígio sonoro e escrito dos seus movimentos. Apenas com familiaridade ao mecanismo e confirmação nas mensagens do console é possível ao certo confirmar qual som veio de qual entidade e de que tipo de sala, mas se torna uma tarefa de quebra cabeça em tempo real. As janelas se fecham quando Astérion morre e a única maneira de acessar o histórico se torna o terminal e não é possível executar a mesma instância novamente. O som transporta partes de seus símbolos impressos no terminal, uma história e uma marca tecnográfica de um som sintetizado por uma pessoa só e iniciante nas ferramentas (longe de uma grande produção com equipe, programas, plugins ou instrumentos refinados). 

Muitas coisas ficam por conta da imaginação do espectador, uma "arqueologia" do código, a escuta e a leitura que talvez não consigam construir com precisão a expectativa da execução. Para quem não possui fluência em todos os suportes, a peça movimenta símbolos arcanos e toma uma vida própria. Isso traz em jogo a força da imagem do sistema e do processo, na definição abrangente do Caesar (p.50) que inclui som e, pela mesma lógica, outras sensações. A quimera Astérion, que é perseguida até esgotar o tempo e o resultado sonoro menos incrível que a imaginação sobre o resultado (ou sobre o processo): Teseu com seu fio de prata se gaba de matar o Minotauro com facilidade no final do conto do Borges (como o comentário inevitável de qualquer produtor que afirme que é mais fácil compor em uma DAW). Acontece que para além das linhas do terminal, não sobra nenhum registro da execução da peça e a mistura das plataformas cria uma sensação de caixa preta, diferente de trabalhar em um projeto em DAW - onde mesmo que possa ficar complexo e emaranhado, a interface do programa garante que a expectativa faça sentido com a realidade.

A ausência de vestígios sonoros da execução assemelha o código à performance ao vivo, mas ainda retendo as qualidades de uma peça reproduzível. Pois sua morfologia passa pelos processos lógicos, narrativos, parâmetros de criação sonora e estes sim, são a peça. A criação da peça está encapsulada em um programa que também detém a reprodução, não há execução em outra plataforma ou tradução possível; o que me remete à fetichização de tecnologias antigas, únicas ou abandonadas, uma busca por um tipo de autenticidade na escolha consciente do suporte/mídia (Newton, 2016)¹ e sua marca tecnográfica, comum em gêneros de expressão artística atual em nichos da internet².

Presenciamos uma relação de reprodução da obra de arte que é diferente da comodificação: o valor de culto aumenta pela busca de uma “autenticidade” através desses meios incomuns e o valor de exposição acaba sendo sacrificado pelas limitações desses meios. Uma obra como a apresentada pode ser reproduzida inúmeras vezes e os requisitos não são proibitivos, mas não possui a mesma dinâmica de escuta e nem pode estar convenientemente agrupada com outras peças em plataformas dedicadas a distribuição massificada (diferente dos exemplos das notas de rodapé, que tensionam os valores de culto e exposição sem romper com a busca por espaço comercial, não abrem mão dos meios de reprodução padrão).

Talvez o controle do programa (como a definição de Flusser, 2009) seja uma forma de tomar poder criativo, uma tentativa de regular os valores de culto e exposição numa época regida pela reprodução quase ilimitada. Tecer a obra e os temas me aponta para obras baseadas em processos e a criação de dispositivos na expressão, num jogo interdisciplinar e intermídia. 

**notas de rodapé**:

¹  Elizabeth Newton (2016) toma o exemplo da produção musical indie “Lofi” como uma maneira de expressão mais ativa diante das estratégias criativas, levando em consideração o suporte e suas limitações como meio expressivo.

²  Como o Webcore, Frutiger Aero, Barber beats, low poly, a lista é enorme, mas passam por algum resgate de nostalgia tecnológica para atribuir valor à estética. Isso pode contar com uso de trackers, programas ou dispositivos arcaicos na produção musical que não sejam comuns, gráficos 3D que imitam limitações antigas de hardware (como gráficos de videogame de alguma geração em particular).

³  Walter Benjamin, A obra de arte na era de sua reprodutibilidade técnica. 2ª Edição. Porto Alegre, RS: L&PM, 2023. p.63. "Seria possível apresentar a história da arte por meio do conflito entre duas polaridades na própria obra de arte, e ver assim como história de seu percurso nos deslocamentos alternados do peso de um polo da obra de arte para o outro. Esses dois polos são seu valor de culto e seu valor de exposição".

#### Referências

BENJAMIN, Walter. A obra de arte na era de sua reprodutibilidade técnica. 2ª Edição. Porto Alegre, RS: L&PM, 2023.

BORGES, Jorge Luis. O aleph. 1949; tradução Davi Arrigucci Jr. São Paulo, SP: Companhia das Letras, 2008. p.60-64 

CAESAR, Rodolfo. Fábulas para a escuta. Rio de Janeiro, RJ: Numa Editora, 2024.

CAESAR, Rodolfo. Som não é uma coisa em si, e sim o transporte de coisas que vazam. Revista Música, v. 20, n. 1, p. 295–308, 9 jul. 2020. 

FLUSSER, Vilém. Filosofia da caixa preta: ensaios para uma futura filosofia da fotografia. Rio de Janeiro, RJ: Sinergia Relume Dumará, 2009.

NEWTON, Elizabeth. Lo-fi Listening as Active Reception. Leonardo Music Journal, v. 26, p. 53–55, dez. 2016.

O módulo de Csound para Python. https://github.com/csound/ctcsound

link do repositório da composição. https://github.com/Grabiel-dargains/casa-de-asterion









