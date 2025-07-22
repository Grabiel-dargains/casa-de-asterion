import random
import time
import tkinter as tk
import sys
import ctcsound
from Labirinto import * 

# --- Classes GUI ---
#Interface gráfica sem as mensagens de erro do console
class LogWindow(tk.Toplevel):
    def __init__(self, master=None, pos="0+0"):
        super().__init__(master)
        self.title("A Casa de Astérion")
        self.geometry(f"800x600+{pos}")
        self.protocol("WM_DELETE_WINDOW", self.master.destroy) # Garante que fechar o log fecha tudo

        self.text_area = tk.Text(self, wrap="word", state="disabled", bg="#1e1e1e", fg="#e0e0e0")
        self.text_area.pack(expand=True, fill="both")

        self.scrollbar = tk.Scrollbar(self.text_area, command=self.text_area.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.text_area.config(yscrollcommand=self.scrollbar.set)

    def log(self, message):
        self.text_area.config(state="normal")
        self.text_area.insert("end", message + "\n")
        self.text_area.see("end")
        self.text_area.config(state="disabled")
        self.update_idletasks() # Força a atualização da GUI

class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.original_stdout = sys.stdout

    def write(self, text):
        # Filtra mensagens do Csound ou erros de compilação
        if "error" not in text.lower() and "csound" not in text.lower() and "stopping on parser" not in text.lower():
            self.text_widget.log(text.strip())
        self.original_stdout.write(text)

    def flush(self):
        self.original_stdout.flush()


# --- Variáveis Globais para a Simulação ---
cs = None
perf_thread = None
labirinto = None
teseu = None
minotauro = None
logwin = None
root = None

TEMPO_MAXIMO_COMPOSICAO = 300
tempo_inicio_simulacao = 0
step_count = 0
INTERVALO_SIMULACAO_MS = 200 # Intervalo em milissegundos para cada passo da simulação (0.2 segundos)

# --- Função de Encerrar Aplicação ---
def on_closing():
    global cs, perf_thread, root
    if perf_thread and perf_thread.isRunning():
        perf_thread.stop()
        perf_thread.join()
    if cs:
        cs.cleanup()
    if sys.stdout != sys.__stdout__: # Restaurar stdout se foi redirecionado
        sys.stdout = sys.__stdout__
    if root:
        root.destroy() # Destrói a janela principal e encerra o Tkinter


# --- Função de Inicialização do Csound e Simulação ---
def initialize_csound_and_simulation():
    global cs, perf_thread, labirinto, teseu, minotauro, logwin, root, tempo_inicio_simulacao

    print("\n--- Inicializando Csound em tempo real ---")

    # Criar a janela principal do Tkinter
    root = tk.Tk()
    
    root.withdraw() # Esconde a janela principal vazia

    # Instanciar a janela de log
    logwin = LogWindow(root)
    loglab = LogWindow(root, "800+0")
    # Redirecionar stdout para a janela de log
    sys.stdout = StdoutRedirector(logwin)

    # Configurar o que acontece quando as janelas são fechadas
    logwin.protocol("WM_DELETE_WINDOW", on_closing)
    
    cs = ctcsound.Csound()

    # Essa aqui é a "partitura", o código do csound
    csd_code = """
<CsoundSynthesizer>
<CsOptions>
-o dac
</CsOptions>
<CsInstruments>
sr = 44100
ksmps = 32
nchnls = 2
0dbfs = 1

; --- DECLARAÇÕES DE CANAIS GLOBAIS E DE CONTROLE ---
gaRevL init 0 
gaRevR init 0 
gaWindL init 0 
gaWindR init 0 
gaDelayL init 0
gaDelayR init 0

gk_current_csound_time init 0 

; --- INSTRUMENTOS DE EFEITO ---

instr 99 ; REVERB GLOBAL
    aInL chnget "gaRevL"
    aInR chnget "gaRevR"
    aRevL, aRevR reverbsc aInL, aInR, 0.95, 9000
    outs aRevL * 0.5, aRevR * 0.5
    chnset gaRevL, "gaWindL"
    chnset gaRevR, "gaWindR"
    
    chnclear "gaRevL"
    chnclear "gaRevR"
endin

instr 98 ; RESSONADOR DE VENTO GLOBAL
    aInL chnget "gaWindL"
    aInR chnget "gaWindR"

    ; --- GERADOR DE VENTO ---
    kGustRate randh 0.1, 0.8, 5
    kGustAmt  randh 0.4, 1.0, 0.8
    aNoise    pinkish 0.2
    kWindFreq = kGustAmt * 80 + 350
    kWindBw   = kGustAmt * 10 + 50
    aWind     butterbp aNoise, kWindFreq, kWindBw

    ; --- FILTROS RESSONANTES ---
    kHowlRate randh 0.05, 0.2, 2
    kHowlFund randh 0.1, 0.8, 0.2
    aResL1 reson aInL, kHowlFund * 2, kHowlFund * 0.5, 1
    aResL2 reson aInL, kHowlFund * 3, kHowlFund * 0.8, 1
    aResL3 reson aInL, kHowlFund * 5, kHowlFund * 1.2, 1
    aResR1 reson aInR, kHowlFund * 2, kHowlFund * 0.5, 1
    aResR2 reson aInR, kHowlFund * 3, kHowlFund * 0.8, 1
    aResR3 reson aInR, kHowlFund * 5, kHowlFund * 1.2, 1
    aResonatedL = (aResL1 + aResL2 + aResL3) * 0.4
    aResonatedR = (aResR1 + aResR2 + aResR3) * 0.4

    aFinalL = aResonatedL * 0.3 + aWind * 0.8
    aFinalR = aResonatedR * 0.3 + aWind * 0.8
    outs aFinalL * 0.4, aFinalR * 0.4
    
    chnclear "gaWindL"
    chnclear "gaWindR"
    
endin

instr 97 ; Delay maneiro
    aDelL init 0
    aDelR init 0
    aInL chnget "gaDelayL"
    aInR chnget "gaDelayR"
    
    kTimeL = 640
    kTimeR = 860
    kFdbk = 0.65
    aDelL vdelay aInL + (aDelR * kFdbk), kTimeL, 3
    aDelR vdelay aDelL, kTimeR, 3
    
    chnset aDelL, "gaRevL" ; Envia para o reverb
    chnset aDelR, "gaRevR"

    chnclear "gaDelayL"
    chnclear "gaDelayR"

endin

; --- TABELAS DE FORMA DE ONDA ---
giTri       ftgen 0, 0, 2^10, 10, 1, 0, -1/9, 0, 1/25, 0, -1/49, 0, 1/81
giPulse     ftgen 0, 0, 8192, 7, -1, 4096, 1, 4096, -1
giDroneWav  ftgen 0, 0, 8192, 10, 1, 0.5, 0.3, 0.1
giSquare    ftgen 0, 0, 2^10, 10, 1, 0, 1/3, 0, 1/5, 0, 1/7, 0, 1/9
giSaw       ftgen 0, 0, 2^10, 10, 1,-1/2,1/3,-1/4,1/5,-1/6,1/7,-1/8,1/9


; --- INSTRUMENTO BASE (TESEU/MINOTAURO) ---
instr 100
    i_amp     = p4
    i_cps     = p5
    i_pan     = p6
    i_modrate = p7
    i_moddepth= p8
    i_revSend = p9
    i_windSend= p10
    i_delaySend = p11

    aenv      linseg 0, 0.2, 1, 0.2, 0.7, p3 - 0.55, 0.6, 0.3, 0
    amod      oscil i_moddepth, i_modrate, giTri
    asig      oscil aenv * i_amp, i_cps + amod, giTri
    aring     oscil aenv * i_amp * 0.2, i_cps * 4, giTri
    asig      = asig * 0.4 + aring * 0.4

    aL, aR pan2 asig, i_pan
    outs aL * 0.4, aR * 0.4

    chnmix aL * i_revSend, "gaRevL"
    chnmix aR * i_revSend, "gaRevR"
    chnmix aL * i_delaySend, "gaDelayL"
    chnmix aR * i_delaySend, "gaDelayR"
    
endin

; --- INSTRUMENTOS DE SALA (refatorados e corrigidos) ---
; p4=amp, p5=freq, p6=largura, p7=altura, p8=umidade, p9=rev, p10=wind
instr 200 ; TerraInst (Frio + Seco)
    i_amp = p4
    i_freq = p5 
    i_largura = p6 
    i_altura = p7 
    i_umidade = p8 
    i_revSend = p9
    i_windSend = p10
    i_delaySend = p11
    
    aenv        linseg 0, 0.5, 1, p3 - 2, 0.8, 0.1, 0
    a_drone     foscil aenv * i_amp, i_freq, 1.2, 0.5, 1.5, giDroneWav
    
    a_noise     noise (1 - i_umidade) * 0.1 * aenv, 0.5
    a_noise_f   butterlp a_noise, 800 + (i_altura * 5)
    
    asig = a_drone * 0.4 + a_noise_f * 0.4
    aL, aR pan2 asig, i_largura
    outs aL * 0.4, aR * 0.4

    chnmix aL * i_revSend, "gaRevL"
    chnmix aR * i_revSend, "gaRevR"
    chnmix aL * i_delaySend, "gaDelayL"
    chnmix aR * i_delaySend, "gaDelayR"
    
endin

instr 201 ; AguaInst (Frio + Úmido)
    i_amp = p4
    i_freq = p5
    i_largura = p6
    i_altura = p7
    i_umidade = p8
    i_revSend = p9
    i_windSend = p10
    i_delaySend = p11

    aenv        linseg 0, 0.8, 1, p3 - 1.5, 0.7, 0.2, 0
    kVibRate    = 0.5 + (i_umidade * 2)
    aVib        oscil i_freq * 0.01, kVibRate, giSaw
    kTremRate   = 0.8 + (i_umidade * 1.5)
    aTrem       oscil 0.3 * (1 - i_umidade), kTremRate, giSaw
    a_base      oscil aenv * i_amp * (1 - aTrem), i_freq + aVib, giSaw
    a_noise     noise i_umidade * 0.15 * aenv, 0.5
    a_noise_f   butterbp a_noise, 300 + (i_altura * 5), 200
    
    asig = a_base * 0.6 + a_noise_f * 0.6
    aL, aR pan2 asig, i_largura
    outs aL * 0.4, aR * 0.4

    chnmix aL * i_revSend, "gaRevL"
    chnmix aR * i_revSend, "gaRevR"
    chnmix aL * i_delaySend, "gaDelayL"
    chnmix aR * i_delaySend, "gaDelayR"
    
endin

instr 202 ; FogoInst (Quente + Seco)
    i_amp = p4
    i_freq = p5
    i_largura = p6
    i_altura = p7
    i_umidade = p8
    i_revSend = p9
    i_windSend = p10
    i_delaySend = p11

    aenv        linseg 0, 0.01, 1, 0.1, 0.3, p3-0.11, 0, 0.1, 0
    a_raw       oscil aenv * i_amp, i_freq, giPulse
    kCutoff     = 500 + (i_altura * 5)
    a_filt      moogladder a_raw, kCutoff, 0.5 + (i_largura * 0.2)
    k_dist      = 0.3 + (i_largura * 0.3)
    asig        distort1 a_filt, k_dist, 0.5 / (1 + k_dist), 0.1, 0.1

    aL, aR pan2 asig, i_largura
    outs aL * 0.4, aR * 0.4

    chnmix aL * i_revSend, "gaRevL"
    chnmix aR * i_revSend, "gaRevR"
    chnmix aL * i_delaySend, "gaDelayL"
    chnmix aR * i_delaySend, "gaDelayR"
    
endin

instr 203 ; ArInst (Quente + Úmido)
    i_amp = p4
    i_freq = p5
    i_largura = p6
    i_altura = p7
    i_umidade = p8
    i_revSend = p9
    i_windSend = p10
    i_delaySend = p11

    aenv        linseg 0, 0.8, 1, p3 - 3, 0.9, 0.5, 0
    a_base      oscil aenv * i_amp * 0.6, i_freq, giSquare
    a_noise     noise 0.15 * aenv, 0.5
    a_noise_f   butterlp a_noise, 1000 + (i_altura * 5)
    a_sopro     = a_base * 0.4 + a_noise_f * 0.4
    asig        phaser1 a_sopro, 0.3 + (i_largura * 0.5), 4000, 0.6, 0.6

    aL, aR pan2 asig, i_largura
    outs aL * 0.4, aR * 0.4

    chnmix aL * i_revSend, "gaRevL"
    chnmix aR * i_revSend, "gaRevR"
    chnmix aL * i_delaySend, "gaDelayL"
    chnmix aR * i_delaySend, "gaDelayR"
    
endin

</CsInstruments>
<CsScore>
; Ativa os instrumentos de efeito globais para que fiquem rodando
i 99 0 10800 ; Reverb
i 98 0 10800 ; Ressonador de Vento
i 97 0 10800 ; Delay Global

</CsScore>
</CsoundSynthesizer>
    """

    result = cs.compileCsdText(csd_code)

    if result != 0:
        sys.stdout.original_stdout.write(f"ERRO: Csound não conseguiu compilar o CSD. Código de erro: {result}\n")
        sys.stdout = sys.stdout.original_stdout
        on_closing() # Garante que o Tkinter seja encerrado
        return # Sai da função de inicialização

    cs.start()
    perf_thread = ctcsound.CsoundPerformanceThread(cs.csound())
    perf_thread.play()
    cs.setControlChannel("gk_current_csound_time", 0.0)

    # Inicializa o labirinto 
    labirinto = Labirinto(num_salas=14)
    logwin.log("Labirinto gerado:")
    loglab.log(labirinto.__str__())


    sala_minotauro_id = random.choice(list(labirinto.salas.keys()))
    minotauro = Minotauro(labirinto, sala_minotauro_id)

    possiveis_salas_teseu = [id for id in labirinto.salas.keys() if id != sala_minotauro_id]
    if not possiveis_salas_teseu:
        sala_teseu_id = sala_minotauro_id
    else:
        sala_teseu_id = random.choice(possiveis_salas_teseu)
    teseu = Teseu(labirinto, sala_teseu_id)

    logwin.log(f"\nMinotauro começa na: {minotauro.sala_atual.nome}")
    logwin.log(f"Teseu começa na: {teseu.sala_atual.nome}")


    tempo_inicio_simulacao = time.time() # Inicia o contador de tempo da simulação
    
    # Inicia o loop da simulação agendando o primeiro passo
    root.after(INTERVALO_SIMULACAO_MS, update_simulation)

# --- Função de Atualização da Simulação (chamada por root.after) ---
def update_simulation():
    global step_count, tempo_inicio_simulacao, teseu, minotauro, cs, perf_thread, root

    tempo_decorrido = time.time() - tempo_inicio_simulacao

    if tempo_decorrido >= TEMPO_MAXIMO_COMPOSICAO or (minotauro and not minotauro.sala_atual):
        logwin.log("\n--- Fim da Simulação: Tempo esgotado ou Minotauro derrotado! ---")
        on_closing() # Encerra a aplicação
        return # Sai da função de atualização

    step_count += 1
    logwin.log(f"\nPasso {step_count}: (Tempo decorrido: {tempo_decorrido:.1f}s / {TEMPO_MAXIMO_COMPOSICAO}s)")

    current_csound_time = cs.controlChannel("gk_current_csound_time")

    # Lógica do Teseu e Minotauro
    sala_atual_teseu = teseu.sala_atual
    if sala_atual_teseu:
        teseu.gerar_som_sala(sala_atual_teseu, 0.7, current_csound_time, perf_thread)

    if minotauro and minotauro.sala_atual: 
        acao_minotauro = random.choice(["correr", "contemplar"])
        if acao_minotauro == "correr":
            minotauro.correr(current_time=current_csound_time, perf_thread=perf_thread)
        elif acao_minotauro == "contemplar":
            minotauro.contemplar(current_time=current_csound_time, perf_thread=perf_thread)
    elif minotauro and not minotauro.sala_atual: # Se minotauro existe mas não tem sala (foi derrotado)
        logwin.log("Minotauro não existe mais.")

    if teseu.sala_atual:
        if not teseu.minotauro_encontrado:
            teseu.buscar_minotauro(current_time=current_csound_time, perf_thread=perf_thread)
        else:
            logwin.log("Teseu já encontrou o Minotauro!")
            if minotauro and minotauro.sala_atual and teseu.sala_atual == minotauro.sala_atual:
                teseu.matar_minotauro(minotauro, current_time=current_csound_time, perf_thread=perf_thread)
                logwin.log("\n--- Fim da Simulação: Teseu matou o Minotauro! ---")
                on_closing()
                return # Sai da função de atualização
            elif minotauro and minotauro.sala_atual:
                logwin.log(f"Teseu está perseguindo o Minotauro até a {minotauro.sala_atual.nome}.")
                teseu.mover(minotauro.sala_atual, tempo_acao=teseu.tempo_base_acao) 
                reverb_send = random.uniform(0.4, 0.8) 
                wind_send = random.uniform(0.3, 0.6)
                freq = random.uniform(40.0, 550.0)
                delay_send = random.uniform(0.2, 1.5)
                teseu.enviar_evento_csound(100, teseu.tempo_base_acao, 0.6, freq, 0.2, 3, 0.03, current_csound_time, reverb_send, wind_send, delay_send, perf_thread=perf_thread)
            else:
                logwin.log("Teseu está procurando o Minotauro, mas ele já foi derrotado.")
                on_closing()
                return # Sai da função de atualização

    # Agendar a próxima execução de update_simulation
    root.after(INTERVALO_SIMULACAO_MS, update_simulation)

# --- Início do Programa ---
if __name__ == "__main__":
    initialize_csound_and_simulation() # Inicializa tudo
    if root: # Garante que root foi criado antes de chamar mainloop
        root.mainloop() # Inicia o loop de eventos do Tkinter