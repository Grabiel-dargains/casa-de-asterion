import random
import time

# Listas de nomes e adjetivos para as salas
NOMES_COMODO = ["Saguão", "Cozinha", "Quarto", "Corredor", "Jardim", "Sala", "Varanda", "Porão", "Sótão"]
ADJETIVOS_SALA = [
    " de Verão", " de Inverno", " Primaveril", " Outonal", " Principal", " Reserva", " de Hóspedes",
    " em Construção", " em Ruínas"
]

# Mapeamento para elementos aristotélicos
MAPA_ELEMENTAL = {
    ("frio", "seco"): "Terra",
    ("frio", "úmido"): "Água",
    ("quente", "seco"): "Fogo",
    ("quente", "úmido"): "Ar",
}

INSTRUMENTOS_ELEMENTOS = {
    "Terra": 200,
    "Água": 201,
    "Fogo": 202,
    "Ar": 203,
}

# --- Classe Sala ---
class Sala:
    def __init__(self, id_sala, largura, comprimento, altura):
        self.id = id_sala
        self.largura = largura
        self.comprimento = comprimento
        self.altura = altura
        
        # Gerar nome composto aleatório
        comodo_base = random.choice(NOMES_COMODO)
        adjetivo_nome = random.choice(ADJETIVOS_SALA)
        self.nome = f"{comodo_base}{adjetivo_nome}"
        
        # As características adicionais foram removidas daqui, conforme solicitado.
        
        # Indicadores de temperatura e umidade
        self.temperatura = random.choice(["quente", "frio"])
        self.umidade = random.choice(["úmido", "seco"])
        
        # Atribuir marcador elemental
        self.elemento_aristotelico = MAPA_ELEMENTAL[(self.temperatura, self.umidade)]

        self.vizinhos = []
        self.ocupantes = []

    def __str__(self):
        # A string de retorno agora reflete a remoção das características adicionais.
        return (f"{self.nome} (ID: {self.id}) - Dimensões: {self.largura:.1f}x{self.comprimento:.1f}x{self.altura:.1f} | "
                f"Temp: {self.temperatura}, Umid: {self.umidade}, Elemento: {self.elemento_aristotelico}")

    def adicionar_vizinho(self, sala):
        if sala not in self.vizinhos:
            self.vizinhos.append(sala)
            sala.vizinhos.append(self)

    def entrar_ocupante(self, entidade):
        self.ocupantes.append(entidade)

    def sair_ocupante(self, entidade):
        if entidade in self.ocupantes:
            self.ocupantes.remove(entidade)

# --- Classe Labirinto ---
class Labirinto:
    def __init__(self, num_salas=14):
        self.num_salas = num_salas
        self.salas = {}
        self._criar_salas()
        self._conectar_salas()

    def _criar_salas(self):
        for i in range(self.num_salas):
            largura = random.uniform(5, 140)
            comprimento = random.uniform(5, 140)
            altura = random.uniform(3, 14)
            self.salas[i] = Sala(i, largura, comprimento, altura)

    def _conectar_salas(self):
        for sala_id, sala in self.salas.items():
            num_conexoes = random.randint(1, 2)
            possiveis_vizinhos = [s for s_id, s in self.salas.items() if s_id != sala_id and s not in sala.vizinhos]
            
            if not possiveis_vizinhos:
                continue
            
            num_conexoes = min(num_conexoes, len(possiveis_vizinhos))
            
            vizinhos_escolhidos = random.sample(possiveis_vizinhos, num_conexoes)
            for vizinho in vizinhos_escolhidos:
                sala.adicionar_vizinho(vizinho)

    def obter_sala(self, id_sala):
        return self.salas.get(id_sala)

    def __str__(self):
        info = f"Labirinto com {self.num_salas} salas:\n"
        for sala_id, sala in self.salas.items():
            info += f"- {sala}\n"
            vizinhos_ids = [v.id for v in sala.vizinhos]
            info += f"  Vizinhos: {vizinhos_ids}\n"
        return info

# --- Classe Entidade (Base para Minotauro e Teseu) ---
class Entidade:
    def __init__(self, nome, labirinto, sala_inicial_id):
        self.nome = nome
        self.labirinto = labirinto
        self.sala_atual = labirinto.obter_sala(sala_inicial_id)
        if self.sala_atual:
            self.sala_atual.entrar_ocupante(self)
        else:
            raise ValueError("Sala inicial inválida para a entidade.")

    def mover(self, nova_sala=None, tempo_acao=2):
        if not self.sala_atual:
            print(f"{self.nome} não está em nenhuma sala para se mover.")
            return

        if nova_sala and nova_sala in self.sala_atual.vizinhos:
            self.sala_atual.sair_ocupante(self)
            self.sala_atual = nova_sala
            self.sala_atual.entrar_ocupante(self)
            print(f"{self.nome} moveu-se para {self.sala_atual.nome}.")
        elif not nova_sala and self.sala_atual.vizinhos:
            proxima_sala = random.choice(self.sala_atual.vizinhos)
            self.sala_atual.sair_ocupante(self)
            self.sala_atual = proxima_sala
            self.sala_atual.entrar_ocupante(self)
            print(f"{self.nome} moveu-se para {self.sala_atual.nome}.")
        else:
            print(f"{self.nome} não tem para onde se mover da {self.sala_atual.nome}.")
        
        time.sleep(tempo_acao)

    def enviar_evento_csound(self, instr_id, dur, amp, freq, pan, mod_rate, mod_depth, current_time, rev, wind, delay, perf_thread):
        
        event_str = f"i{instr_id} 0 {dur:.2f} {amp:.2f} {freq:.2f} {pan:.2f} {mod_rate:.2f} {mod_depth:.2f} {rev:.2f} {wind:.2f} {delay:.2f}"
        perf_thread.inputMessage(event_str)

# --- Classe Minotauro ---
class Minotauro(Entidade):
    def __init__(self, labirinto, sala_inicial_id):
        super().__init__("Minotauro", labirinto, sala_inicial_id)
        self.contemplacao_level = 0

    def contemplar(self, tempo_acao=4, current_time=0.0, perf_thread=None):
        print(f"Minotauro está contemplando em {self.sala_atual.nome}.")
        for i in range(self.contemplacao_level):
            # FIX: Usando valores de reverb e wind mais sensatos (0-1)
            reverb_send = random.uniform(0.3, 0.7)
            wind_send = random.uniform(0.2, 0.8)
            delay_send = random.uniform(0.2, 1.5)
            self.enviar_evento_csound(100, 6, 0.4, 50 + self.contemplacao_level * 10, 0.5, 0.2, 0.01, current_time, reverb_send, wind_send, delay_send, perf_thread)
        
        time.sleep(tempo_acao)

    def correr(self, tempo_acao=2, current_time=0.0, perf_thread=None):
        print(f"Minotauro está correndo em {self.sala_atual.nome}.")
        self.mover(tempo_acao=tempo_acao)
        freq = random.randint(30, 500)
        # FIX: Usando valores de reverb e wind mais sensatos (0-1)
        reverb_send = random.uniform(0.2, 0.5)
        wind_send = random.uniform(0.1, 0.4)
        delay_send = random.uniform(0.2, 1.5)
        self.enviar_evento_csound(100, tempo_acao, 0.6, freq, 0.7, 5, 0.05, current_time, reverb_send, wind_send, delay_send, perf_thread)

    def assustar_humanos(self, tempo_acao=1, current_time=0.0, perf_thread=None):
        humanos_na_sala = [o for o in self.sala_atual.ocupantes if isinstance(o, Teseu)]
        reverb_send = random.uniform(0.4, 0.8) # Salas têm bastante reverb
        wind_send = random.uniform(0.3, 0.6)
        delay_send = random.uniform(0.2, 1.5)
        if humanos_na_sala:
            print(f"Minotauro assusta {', '.join([h.nome for h in humanos_na_sala])} na {self.sala_atual.nome}!")
            self.enviar_evento_csound(100, tempo_acao, 0.6, 50, 0.5, 10, 0.1, current_time, reverb_send, wind_send, delay_send, perf_thread)
        else:
            print(f"Minotauro tenta assustar, mas não há humanos em {self.sala_atual.nome}.")
        time.sleep(tempo_acao)

    def atacar_humano(self, humano, tempo_acao=2, current_time=0.0, perf_thread=None):
        if humano in self.sala_atual.ocupantes:
            print(f"Minotauro ataca {humano.nome} em {self.sala_atual.nome}!")
            freq = random.randint(30, 500)
            reverb_send = random.uniform(0.2, 0.5)
            wind_send = random.uniform(0.1, 0.4)
            delay_send = random.uniform(0.2, 1.5)
            self.enviar_evento_csound(100, tempo_acao, 0.6, freq, 0.5, 20, 0.2, current_time, reverb_send, wind_send, delay_send, perf_thread)
            time.sleep(tempo_acao)
            return True
        return False

# --- Classe Teseu ---
class Teseu(Entidade):
    def __init__(self, labirinto, sala_inicial_id):
        super().__init__("Teseu", labirinto, sala_inicial_id)
        self.minotauro_encontrado = False
        self.caminho_percorrido = [self.sala_atual]
        self.tempo_base_acao = 1

    def buscar_minotauro(self, current_time=0.0, perf_thread=None):
        print(f"Teseu está buscando o Minotauro em {self.sala_atual.nome}.")
        self.gerar_som_sala(self.sala_atual, 1, current_time, perf_thread)
        
        self.mover(tempo_acao=self.tempo_base_acao)
        self.caminho_percorrido.append(self.sala_atual)
        freq = random.randint(30, 460) 
        reverb_send = random.uniform(0.4, 0.8) # Salas têm bastante reverb
        wind_send = random.uniform(0.3, 0.6)
        delay_send = random.uniform(0.2, 1.5)
        self.enviar_evento_csound(100, self.tempo_base_acao, 0.6, freq, 0.3, 1, 0.01, current_time, reverb_send, wind_send, delay_send, perf_thread)

        for ocupante in self.sala_atual.ocupantes:
            if isinstance(ocupante, Minotauro):
                self.minotauro_encontrado = True
                print(f"Teseu encontrou o Minotauro em {self.sala_atual.nome}!")
                self.enviar_evento_csound(100, 1.0, 0.5, freq, 0.5, 8, 0.08, current_time, reverb_send, wind_send, delay_send, perf_thread)
                return True
        return False

    def matar_minotauro(self, minotauro, tempo_acao=5, current_time=0.0, perf_thread=None):
        if self.minotauro_encontrado and self.sala_atual == minotauro.sala_atual:
            print(f"Teseu mata o Minotauro em {self.sala_atual.nome}!")
            freq = random.randint(30, 670)
            reverb_send = 0.2
            wind_send = 0.1
            delay_send = 0.4
            self.enviar_evento_csound(100, self.tempo_base_acao, 0.6, freq, 0.3, 1, 0.01, current_time, reverb_send, wind_send, delay_send, perf_thread)
            time.sleep(tempo_acao)
            return True
        return False
    
    def gerar_som_sala(self, sala, duracao_evento, current_time, perf_thread):
        instr_id = INSTRUMENTOS_ELEMENTOS[sala.elemento_aristotelico]
        amp = 0.3
        
        freq = random.randint(100, 700) / (sala.altura) + (sala.id * 2) 
        
        largura_norm = (sala.largura - 5) / 15 
        
        altura_norm = (sala.altura - 3) / 5 

        umidade_val = 1 if sala.umidade == "úmido" else 0
        reverb_send = random.uniform(0.4, 0.8) # Salas têm bastante reverb
        wind_send = random.uniform(0.3, 0.6) if sala.elemento_aristotelico == "Ar" else 0.3
        delay_send = random.uniform(0.2, 1.5)
        

        event_str = f"i{instr_id} 0 {duracao_evento:.2f} {amp:.2f} {freq:.2f} {largura_norm:.2f} {altura_norm:.2f} {umidade_val:.2f} {reverb_send:.2f} {wind_send:.2f} {delay_send:.2f}"
        perf_thread.inputMessage(event_str)