import streamlit as st
import google.generativeai as genai
from google.generativeai import types

# Configuração da API Key e Modelo
genai.configure(api_key="AIzaSyBt5zfhvZY0wMhjS78U-QwRmmUEEOXpZok")
#não lembro como encripitar a chave, então vou deixar em branco, mas funciona se você colocar sua chave API aqui.
try:
    model = genai.GenerativeModel("gemini-2.0-flash")
except Exception as e:
    st.error(f"Erro ao carregar o modelo Gemini 'gemini-2.0-flash': {e}")
    st.info("Verifique se o nome do modelo está correto e se sua chave API tem acesso a ele.")
    st.stop()

def gerar_resposta_gemini(prompt_completo):
    try:
        response = model.generate_content(prompt_completo)
        if response.parts:
            return response.text
        else:
            if response.prompt_feedback:
                st.warning(f"O prompt foi bloqueado. Razão: {response.prompt_feedback.block_reason}")
                if response.prompt_feedback.safety_ratings:
                    for rating in response.prompt_feedback.safety_ratings:
                        st.caption(f"Categoria: {rating.category}, Probabilidade: {rating.probability}")
            return "A IA não pôde gerar uma resposta para este prompt."
    except Exception as e:
        st.error(f"Erro ao gerar resposta da IA: {str(e)}")
        if hasattr(e, 'message'):
            st.error(f"Detalhe da API Gemini: {e.message}")
        return None

# Título do aplicativo
st.title("Criador de Histórias Interativas com Gemini")
st.markdown("Crie sua história interativa com Inteligência Artificial!")

# Inicializa variáveis de sessão
if 'historia_completa' not in st.session_state:
    st.session_state.historia_completa = []
if 'aguardando_input' not in st.session_state:
    st.session_state.aguardando_input = False
if 'ultima_resposta' not in st.session_state:
    st.session_state.ultima_resposta = ""

# Entradas do usuário (mostradas só no início)
if not st.session_state.historia_completa:
    nome_protagonista = st.text_input("Qual o nome do seu Protagonista?")
    genero_literario = st.selectbox("Gênero da sua história:", 
                                   ["Aventura", "Ficção Científica", "Fantasia", "Romance", "Terror", "Mistério", "Comédia"])
    local_historia = st.radio("Local da História:", 
                             ["Uma floresta antiga", "Uma cidade futurista", "Um castelo assombrado", "Uma nave espacial à deriva"])
    frase_inicial = st.text_area("Digite a frase inicial da sua história:", "Era uma vez, em um lugar distante...")

    if st.button("Começar História"):
        if not nome_protagonista or not frase_inicial:
            st.error("Por favor, preencha todos os campos obrigatórios.")
        else:
            # Armazena no session_state
            st.session_state.nome_protagonista = nome_protagonista
            st.session_state.genero_literario = genero_literario
            st.session_state.local_historia = local_historia
            st.session_state.frase_inicial = frase_inicial

            prompt_completo = (
                f"Crie uma história interativa com o protagonista {nome_protagonista}, "
                f"no gênero {genero_literario}, ambientada em {local_historia}. "
                f"A história deve começar com: '{frase_inicial}'. "
                "Inclua um ponto de decisão no final onde o leitor pode influenciar a história. "
                "Termine com a pergunta: 'O que você quer fazer agora?'"
            )

            resposta = gerar_resposta_gemini(prompt_completo)

            if resposta:
                st.session_state.historia_completa.append(resposta)
                st.session_state.ultima_resposta = resposta
                st.session_state.aguardando_input = True

# Exibir história acumulada
if st.session_state.historia_completa:
    st.subheader("Sua História:")
    for parte in st.session_state.historia_completa:
        st.write(parte)
        st.markdown("---")

# Campo de input do usuário para interação
if st.session_state.aguardando_input:
    with st.form("user_input_form"):
        user_input = st.text_area("O que você quer fazer a seguir? (Descreva sua ação)", 
                                 placeholder="Ex: Decido explorar... ou Falo com o personagem...")
        enviar = st.form_submit_button("Enviar")

        if enviar and user_input:
            prompt_continuacao = (
                f"Continue a história baseada na seguinte ação do usuário: '{user_input}'. "
                f"Mantenha o protagonista {st.session_state.nome_protagonista}, no gênero {st.session_state.genero_literario}. "
                "Desenvolva a narrativa de forma coerente e inclua um novo ponto de decisão no final. "
                "Termine novamente com a pergunta: 'O que você quer fazer agora?'"
            )

            nova_resposta = gerar_resposta_gemini(prompt_continuacao)

            if nova_resposta:
                st.session_state.historia_completa.append(f"**Sua ação:** {user_input}\n\n{nova_resposta}")
                st.session_state.ultima_resposta = nova_resposta
                st.session_state.aguardando_input = True
                st.rerun()

# Botão para reiniciar a história
if st.session_state.historia_completa:
    if st.button("Começar uma nova história"):
        st.session_state.clear()
        st.rerun()
