"""
Serviço de Autenticação e Gestão de Atletas
Supabase Auth + PostgreSQL + Token Persistente para Mobile/PWA
"""

from typing import Optional, Tuple, Dict, Any, List
import time
import uuid
import streamlit as st
from supabase import create_client, Client

from config import get_secret_val


import os
import re
from collections.abc import Mapping
from supabase import create_client, Client

from config import get_secret_val


_supabase_client_inst: Optional[Client] = None
_supabase_admin_inst: Optional[Client] = None


def get_supabase_credentials() -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Recupera URL, Chave Pública e Chave de Serviço do Supabase em qualquer formato nos Secrets ou Environ."""
    url, key, secret = None, None, None

    url_keys = [
        "supabase_url", "supabase_project_url", "url", "endpoint",
        "supabase_endpoint", "project_url", "supabase_base_url", "base_url", "host"
    ]
    key_keys = [
        "supabase_key", "supabase_anon_key", "supabase_publishable_key",
        "anon_key", "publishable_key", "public_key", "key", "supabase_public_key",
        "anon", "publishable", "public"
    ]
    sec_keys = [
        "supabase_secret_key", "supabase_service_role_key", "supabase_service_key",
        "supabase_secret", "service_role_key", "secret_key", "service_key",
        "secret", "service_role", "role_key"
    ]

    def walk_all(obj):
        if isinstance(obj, Mapping):
            for k, v in obj.items():
                yield str(k), v
                yield from walk_all(v)
        elif isinstance(obj, (list, tuple)):
            for item in obj:
                yield from walk_all(item)

    all_pairs = []
    try:
        all_pairs.extend(list(walk_all(st.secrets)))
    except Exception:
        pass

    try:
        all_pairs.extend([(k, v) for k, v in os.environ.items()])
    except Exception:
        pass

    # 1. Busca direta por nome de chave
    for k, v in all_pairs:
        if not isinstance(v, str):
            continue
        val = v.strip().strip("\"'")
        if not val:
            continue
        k_lower = k.lower()
        if not url and k_lower in url_keys:
            url = val
        if not key and k_lower in key_keys:
            key = val
        if not secret and k_lower in sec_keys:
            secret = val

    # 2. Busca heurística inteligente por formato do conteúdo
    for _, v in all_pairs:
        if not isinstance(v, str):
            continue
        val = v.strip().strip("\"'")
        if not val:
            continue
        if not url:
            if "supabase.co" in val:
                url = val
            elif "supabase.com/dashboard/project/" in val:
                m = re.search(r"supabase\.com/dashboard/project/([a-zA-Z0-9_-]+)", val)
                if m:
                    url = f"https://{m.group(1)}.supabase.co"
        if not key:
            if val.startswith("sb_publishable_"):
                key = val
        if not secret:
            if val.startswith("sb_secret_"):
                secret = val

    # 3. Normalização e sanitização da URL
    if url:
        if "supabase.com/dashboard/project/" in url:
            m = re.search(r"supabase\.com/dashboard/project/([a-zA-Z0-9_-]+)", url)
            if m:
                url = f"https://{m.group(1)}.supabase.co"
        url = re.sub(r"/rest/v1/?$", "", url)
        url = url.rstrip("/")
        if not url.startswith("http"):
            url = f"https://{url}"

    return url, key, secret


def reset_supabase_client_cache():
    """Limpa a instância em cache do cliente Supabase."""
    global _supabase_client_inst, _supabase_admin_inst
    _supabase_client_inst = None
    _supabase_admin_inst = None


def get_supabase_client() -> Optional[Client]:
    """Cria ou retorna o cliente Supabase padrão (anon)."""
    global _supabase_client_inst
    if _supabase_client_inst is not None:
        return _supabase_client_inst

    url, key, secret = get_supabase_credentials()
    effective_key = key or secret
    if not url or not effective_key:
        return None

    try:
        _supabase_client_inst = create_client(url, effective_key)
        return _supabase_client_inst
    except Exception as e:
        st.error(f"Erro ao inicializar conexão com o banco de dados: {e}")
        return None


def get_supabase_admin() -> Optional[Client]:
    """Cria cliente Supabase com service_role_key para bypass de RLS."""
    global _supabase_admin_inst
    if _supabase_admin_inst is not None:
        return _supabase_admin_inst

    url, key, secret = get_supabase_credentials()
    effective_secret = secret or key
    if not url or not effective_secret:
        return None

    try:
        _supabase_admin_inst = create_client(url, effective_secret)
        return _supabase_admin_inst
    except Exception:
        return None


def get_current_user() -> Optional[Dict[str, Any]]:
    """Retorna os dados do atleta autenticado na sessão atual."""
    return st.session_state.get("auth_user", None)


def get_current_user_id() -> Optional[str]:
    """Retorna o UUID do atleta logado."""
    user = get_current_user()
    return user.get("id") if user else None


def get_user_profile(user_id: str) -> Dict[str, Any]:
    """Retorna o perfil do atleta diretamente do Supabase."""
    sb = get_supabase_admin() or get_supabase_client()
    if not sb:
        return {}
    try:
        res = sb.table("profiles").select("*").eq("id", user_id).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]
    except Exception:
        pass
    return {}


def update_user_profile(user_id: str, updates: Dict[str, Any]) -> bool:
    """Atualiza o perfil do atleta no Supabase e sincroniza o session_state."""
    sb = get_supabase_admin() or get_supabase_client()
    if not sb:
        return False
    try:
        sb.table("profiles").upsert({"id": user_id, **updates}).execute()
        if "auth_profile" in st.session_state and st.session_state["auth_profile"]:
            st.session_state["auth_profile"].update(updates)
        else:
            st.session_state["auth_profile"] = updates
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar perfil do atleta: {e}")
        return False


def get_athlete_profile() -> Dict[str, Any]:
    """Retorna o perfil do atleta logado."""
    user = get_current_user()
    if not user:
        return {
            "esportes_ativos": ["Corrida de Rua"],
            "dias_disponiveis": 4,
            "nivel_experiencia": "Intermediário",
            "objetivo_principal": "Meia Maratona",
            "onboarding_concluido": False,
            "pwa_aviso_dispensado": False,
        }

    if "auth_profile" not in st.session_state or not st.session_state["auth_profile"]:
        st.session_state["auth_profile"] = get_user_profile(user["id"])

    p = st.session_state["auth_profile"]
    return {
        "esportes_ativos": p.get("esportes_ativos") or ["Corrida de Rua"],
        "dias_disponiveis": p.get("dias_disponiveis", 4),
        "nivel_experiencia": p.get("nivel_experiencia", "Intermediário"),
        "objetivo_principal": p.get("objetivo_principal", "Meia Maratona"),
        "onboarding_concluido": p.get("onboarding_concluido", False),
        "pwa_aviso_dispensado": p.get("pwa_aviso_dispensado", False),
        "nome": p.get("nome", user.get("nome", "Atleta")),
    }


def dismiss_pwa_banner():
    """Marca o banner de instalação mobile como dispensado."""
    st.session_state["pwa_aviso_dispensado"] = True
    user = get_current_user()
    if user:
        update_user_profile(user["id"], {"pwa_aviso_dispensado": True})


def generate_and_save_session_token(user_id: str) -> str:
    """Gera um token persistente único e salva no Supabase e na URL (PWA / Mobile)."""
    token = uuid.uuid4().hex
    sb_admin = get_supabase_admin() or get_supabase_client()
    if sb_admin:
        try:
            sb_admin.table("profiles").update({"auth_token": token}).eq("id", user_id).execute()
        except Exception:
            pass

    try:
        st.query_params["token"] = token
    except Exception:
        pass
    return token


def restore_user_from_token() -> bool:
    """Restaura a sessão do atleta se houver um token válido nos parâmetros da URL."""
    if st.session_state.get("auth_user"):
        return True

    token = None
    try:
        token = st.query_params.get("token")
    except Exception:
        pass

    if not token:
        return False

    sb_admin = get_supabase_admin() or get_supabase_client()
    if not sb_admin:
        return False

    try:
        res = sb_admin.table("profiles").select("*").eq("auth_token", token).execute()
        if res.data and len(res.data) > 0:
            profile = res.data[0]
            uid = profile["id"]
            user_data = {
                "id": uid,
                "email": profile.get("email", ""),
                "nome": profile.get("nome", "Atleta"),
            }
            st.session_state["auth_user"] = user_data
            st.session_state["auth_profile"] = profile
            return True
    except Exception:
        pass
    return False


def auth_sign_in(email: str, password: str, remember: bool = True) -> Tuple[bool, str]:
    """Autentica o atleta por e-mail e senha no Supabase Auth com suporte a token persistente."""
    sb = get_supabase_client()
    if not sb:
        url, key, secret = get_supabase_credentials()
        faltantes = []
        if not url:
            faltantes.append("'supabase_url'")
        if not (key or secret):
            faltantes.append("'supabase_key'")
        motivo = f" (ausente em Secrets: {', '.join(faltantes)})" if faltantes else ""
        return False, f"Serviço de autenticação não configurado no servidor{motivo}. Verifique em App Settings > Secrets."

    try:
        res = sb.auth.sign_in_with_password({"email": email.strip(), "password": password})
        if res.user:
            user_data = {
                "id": str(res.user.id),
                "email": res.user.email,
                "nome": res.user.user_metadata.get("nome", res.user.email.split("@")[0]),
            }
            st.session_state["auth_user"] = user_data

            sb_admin = get_supabase_admin() or sb
            try:
                p_res = sb_admin.table("profiles").select("*").eq("id", res.user.id).execute()
                if p_res.data and len(p_res.data) > 0:
                    st.session_state["auth_profile"] = p_res.data[0]
                else:
                    initial_profile = {
                        "id": str(res.user.id),
                        "nome": user_data["nome"],
                        "email": user_data["email"],
                        "esportes_ativos": ["Corrida de Rua"],
                        "dias_disponiveis": 4,
                        "nivel_experiencia": "Intermediário",
                        "objetivo_principal": "Meia Maratona",
                    }
                    sb_admin.table("profiles").insert(initial_profile).execute()
                    st.session_state["auth_profile"] = initial_profile
            except Exception:
                pass

            if remember:
                generate_and_save_session_token(str(res.user.id))

            return True, "Login realizado com sucesso!"
        return False, "Credenciais inválidas."
    except Exception as e:
        err_msg = str(e)
        if "Invalid login credentials" in err_msg:
            return False, "E-mail ou senha incorretos."
        return False, f"Erro ao autenticar: {err_msg}"


def auth_sign_up(email: str, password: str, name: str, remember: bool = True) -> Tuple[bool, str]:
    """Cadastra um novo atleta no Supabase Auth e registra perfil inicial."""
    sb_admin = get_supabase_admin()
    sb = get_supabase_client()
    if not (sb or sb_admin):
        url, key, secret = get_supabase_credentials()
        faltantes = []
        if not url:
            faltantes.append("'supabase_url'")
        if not (key or secret):
            faltantes.append("'supabase_key'")
        motivo = f" (ausente em Secrets: {', '.join(faltantes)})" if faltantes else ""
        return False, f"Serviço de autenticação não configurado no servidor{motivo}. Verifique em App Settings > Secrets."

    try:
        target_client = sb_admin or sb
        res = target_client.auth.sign_up({
            "email": email.strip(),
            "password": password,
            "options": {"data": {"nome": name.strip() or "Atleta"}},
        })

        if res.user:
            uid = str(res.user.id)
            user_data = {
                "id": uid,
                "email": res.user.email,
                "nome": name.strip() or "Atleta",
            }
            st.session_state["auth_user"] = user_data

            try:
                writer = sb_admin or sb
                writer.table("profiles").upsert({
                    "id": uid,
                    "nome": name.strip() or "Atleta",
                    "email": email.strip(),
                    "esportes_ativos": ["Corrida de Rua"],
                    "dias_disponiveis": 4,
                    "nivel_experiencia": "Intermediário",
                    "objetivo_principal": "Meia Maratona",
                    "onboarding_concluido": False,
                }).execute()
            except Exception:
                pass

            if remember:
                generate_and_save_session_token(uid)

            return True, "Conta criada com sucesso! Bem-vindo à sua assessoria."
        return False, "Não foi possível criar a conta. Tente novamente."
    except Exception as e:
        err_msg = str(e)
        if "already registered" in err_msg or "already exists" in err_msg:
            return False, "Este e-mail já está cadastrado. Faça login na aba ao lado."
        if "rate limit" in err_msg.lower():
            return False, "Limite temporário de cadastros atingido. Tente novamente em alguns minutos."
        return False, f"Erro ao criar conta: {err_msg}"


def auth_sign_out():
    """Encerra a sessão do atleta e limpa o estado e tokens do aparelho."""
    user = get_current_user()
    if user:
        sb_admin = get_supabase_admin() or get_supabase_client()
        if sb_admin:
            try:
                sb_admin.table("profiles").update({"auth_token": None}).eq("id", user["id"]).execute()
            except Exception:
                pass

    sb = get_supabase_client()
    if sb:
        try:
            sb.auth.sign_out()
        except Exception:
            pass

    try:
        st.query_params.clear()
    except Exception:
        pass

    for key in ["auth_user", "auth_profile", "chat_messages", "ultimo_treino", "plano_estruturado", "onboarding_shown"]:
        if key in st.session_state:
            del st.session_state[key]
    st.cache_data.clear()


def render_login_screen():
    """
    Renderiza tela de login limpa e profissional sem expor logs de depuração.
    """
    col_l1, col_center, col_l3 = st.columns([1, 2, 1])

    with col_center:
        st.write("")
        st.write("")

        url_t, key_t, sec_t = get_supabase_credentials()
        if not url_t or not (key_t or sec_t):
            with st.container(border=True):
                st.warning(
                    "⚠️ **Configuração do Banco de Dados Pendente no Streamlit Cloud:**\n\n"
                    "O aplicativo não detectou as chaves de conexão. Verifique se foram salvas em "
                    "**App Settings ➔ Secrets** no seguinte formato:\n\n"
                    "```toml\n"
                    "supabase_url = \"https://seu-id.supabase.co\"\n"
                    "supabase_key = \"sb_publishable_...\"\n"
                    "supabase_secret_key = \"sb_secret_...\"\n"
                    "```"
                )
                if st.button("Recarregar Conexão", icon=":material/refresh:", use_container_width=True):
                    reset_supabase_client_cache()
                    st.rerun()

        with st.container(border=True):
            st.title("Coach AI")
            st.caption("Consultoria esportiva e periodização inteligente personalizada")
            st.divider()

            tab_in, tab_up = st.tabs(["Entrar", "Criar Conta"])

            with tab_in:
                with st.form("form_login_main"):
                    login_email = st.text_input("E-mail", placeholder="seu@email.com", key="login_main_email")
                    login_pass = st.text_input("Senha", type="password", placeholder="••••••••", key="login_main_pass")
                    lembrar_login = st.checkbox(
                        "Manter conectado neste aparelho",
                        value=True,
                        help="Salva o acesso no aparelho para abrir direto nas próximas vezes.",
                    )
                    btn_do_login = st.form_submit_button(
                        "Entrar",
                        type="primary",
                        use_container_width=True,
                        icon=":material/login:",
                    )

                    if btn_do_login:
                        if not login_email or not login_pass:
                            st.warning("Informe seu e-mail e senha cadastrados.")
                        else:
                            with st.spinner("Autenticando..."):
                                ok_in, msg_in = auth_sign_in(login_email, login_pass, remember=lembrar_login)
                                if ok_in:
                                    st.success("Login realizado com sucesso!")
                                    time.sleep(0.4)
                                    st.rerun()
                                else:
                                    st.error(msg_in)

            with tab_up:
                with st.form("form_register_main"):
                    reg_nome = st.text_input("Nome Completo", placeholder="Ex: Carlos Oliveira", key="reg_main_nome")
                    reg_email = st.text_input("E-mail", placeholder="seu@email.com", key="reg_main_email")
                    reg_pass1 = st.text_input("Senha (mínimo 6 dígitos)", type="password", placeholder="••••••••", key="reg_main_pass1")
                    reg_pass2 = st.text_input("Confirmar Senha", type="password", placeholder="••••••••", key="reg_main_pass2")
                    btn_do_register = st.form_submit_button(
                        "Criar Conta Gratuita",
                        type="primary",
                        use_container_width=True,
                        icon=":material/person_add:",
                    )

                    if btn_do_register:
                        if not reg_email or not reg_pass1:
                            st.warning("Preencha os campos obrigatórios.")
                        elif len(reg_pass1) < 6:
                            st.warning("A senha deve conter pelo menos 6 caracteres.")
                        elif reg_pass1 != reg_pass2:
                            st.error("As senhas digitadas não coincidem.")
                        else:
                            with st.spinner("Criando sua conta na nuvem..."):
                                ok_reg, msg_reg = auth_sign_up(reg_email, reg_pass1, reg_nome or "Atleta", remember=True)
                                if ok_reg:
                                    st.success(msg_reg)
                                    time.sleep(0.5)
                                    st.rerun()
                                else:
                                    st.error(msg_reg)

            st.caption("Acesso protegido com criptografia e isolamento individual de dados por atleta.")
