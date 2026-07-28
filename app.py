import asyncio
import time
import httpx
import json
import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64
from datetime import datetime, timedelta
from google.protobuf import json_format

# ============= TODOS OS PROTO NA MESMA PASTA =============
try:
    import FreeFire_pb2
    import main_pb2
    import AccountPersonalShow_pb2
    import GetOutfit_pb2
    print("✅ Protos importados com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar protos: {e}")
    sys.exit(1)

# =============================================
# 🔧 CONFIGURAÇÕES
# =============================================

VERSAO_LANCAMENTO = "OB54"
AGENTE_USUARIO = "Dalvik/2.1.0 (Linux; U; Android 14; CPH2095 Build/RKQ1.211119.001)"

CHAVE_PRINCIPAL = base64.b64decode('WWcmdGMlREV1aDYlWmNeOA==')
IV_PRINCIPAL = base64.b64decode('Nm95WkRyMjJFM3ljaGpNJQ==')

# =============================================
# 🔑 API DE TOKEN JWT
# =============================================

URL_API_JWT = "http://shappno-jwt-api-ob54.vercel.app/token"

# =============================================
# 👤 CREDENCIAIS DAS CONTAS
# =============================================

CREDENCIAIS_CONTAS = {
    "BD": {"uid": "5372860087", "senha": "shappno_create-by-shappno_S7kkYNMy"},
    "IND": {"uid": "4269013803", "senha": "MG24_GAMER_XSBOS_BY_SPIDEERIO_GAMING_TE5NG"},
    "ME": {"uid": "4269012488", "senha": "MG24_GAMER_U27YB_BY_SPIDEERIO_GAMING_0PNCN"},
    "SG": {"uid": "4269012488", "senha": "MG24_GAMER_U27YB_BY_SPIDEERIO_GAMING_0PNCN"},
    "ID": {"uid": "4269012488", "senha": "MG24_GAMER_U27YB_BY_SPIDEERIO_GAMING_0PNCN"},
    "TH": {"uid": "4269012488", "senha": "MG24_GAMER_U27YB_BY_SPIDEERIO_GAMING_0PNCN"},
    "VN": {"uid": "4269012488", "senha": "MG24_GAMER_U27YB_BY_SPIDEERIO_GAMING_0PNCN"},
    "PK": {"uid": "4269012488", "senha": "MG24_GAMER_U27YB_BY_SPIDEERIO_GAMING_0PNCN"},
    "BR": {"uid": "4269012488", "senha": "MG24_GAMER_U27YB_BY_SPIDEERIO_GAMING_0PNCN"},
    "US": {"uid": "4269012488", "senha": "MG24_GAMER_U27YB_BY_SPIDEERIO_GAMING_0PNCN"},
    "EU": {"uid": "4269012488", "senha": "MG24_GAMER_U27YB_BY_SPIDEERIO_GAMING_0PNCN"}
}

# =============================================
# 🌍 CONFIGURAÇÃO DAS REGIÕES
# =============================================

CONFIG_REGIAO = {
    "BD": {"url_servidor": "https://loginbp.ggblueshark.com", "versao_lancamento": "OB54", "versao_cliente": "1.124.0"},
    "IND": {"url_servidor": "https://loginbp.ggpolarbear.com", "versao_lancamento": "OB54", "versao_cliente": "1.124.0"},
    "ME": {"url_servidor": "https://loginbp.ggblueshark.com", "versao_lancamento": "OB54", "versao_cliente": "1.124.0"},
    "SG": {"url_servidor": "https://loginbp.ggblueshark.com", "versao_lancamento": "OB54", "versao_cliente": "1.124.0"},
    "ID": {"url_servidor": "https://loginbp.ggblueshark.com", "versao_lancamento": "OB54", "versao_cliente": "1.124.0"},
    "TH": {"url_servidor": "https://loginbp.ggblueshark.com", "versao_lancamento": "OB54", "versao_cliente": "1.124.0"},
    "VN": {"url_servidor": "https://loginbp.ggblueshark.com", "versao_lancamento": "OB54", "versao_cliente": "1.124.0"},
    "PK": {"url_servidor": "https://loginbp.ggblueshark.com", "versao_lancamento": "OB54", "versao_cliente": "1.124.0"},
    "BR": {"url_servidor": "https://loginbp.ggpolarbear.com", "versao_lancamento": "OB54", "versao_cliente": "1.124.0"},
    "US": {"url_servidor": "https://loginbp.ggpolarbear.com", "versao_lancamento": "OB54", "versao_cliente": "1.124.0"},
    "EU": {"url_servidor": "https://loginbp.ggblueshark.com", "versao_lancamento": "OB54", "versao_cliente": "1.124.0"}
}

PRIORIDADE_REGIAO = ["BD", "IND", "ME", "SG", "ID", "TH", "VN", "PK", "BR", "US", "EU"]

# === Aplicativo Flask ===
app = Flask(__name__)
CORS(app)

# =============================================
# 🏆 FUNÇÕES DE RANQUE (Atualizadas OB54)
# =============================================

def obter_ranque_br(pontos):
    """Ranque BR baseado no sistema de ranqueamento OB54"""
    if pontos < 1000: return "Bronze I"
    if pontos < 1100: return "Bronze II"
    if pontos < 1200: return "Bronze III"
    if pontos < 1300: return "Prata I"
    if pontos < 1400: return "Prata II"
    if pontos < 1500: return "Prata III"
    if pontos < 1700: return "Ouro I"
    if pontos < 1900: return "Ouro II"
    if pontos < 2100: return "Ouro III"
    if pontos < 2300: return "Platina I"
    if pontos < 2500: return "Platina II"
    if pontos < 2700: return "Platina III"
    if pontos < 3000: return "Diamante I"
    if pontos < 3250: return "Diamante II"
    if pontos < 3500: return "Diamante III"
    if pontos < 6300: return "Mestre"
    if pontos < 7500: return "Elite 1★"
    if pontos < 8500: return "Elite 2★"
    if pontos < 9500: return "Elite 3★"
    if pontos < 10000: return "Elite 4★"
    return "Elite 5★"


def obter_ranque_cs(pontos):
    """Ranque do Contra Squad (CS) com estrelas"""
    if pontos < 500: return "Bronze I"
    if pontos < 600: return "Bronze II"
    if pontos < 700: return "Bronze III"
    if pontos < 800: return "Prata I"
    if pontos < 900: return "Prata II"
    if pontos < 1000: return "Prata III"
    if pontos < 1200: return "Ouro I"
    if pontos < 1400: return "Ouro II"
    if pontos < 1600: return "Ouro III"
    if pontos < 1800: return "Platina I"
    if pontos < 2000: return "Platina II"
    if pontos < 2200: return "Platina III"
    if pontos < 2500: return "Diamante I"
    if pontos < 2700: return "Diamante II"
    if pontos < 2900: return "Diamante III"
    if pontos < 5400: return "Mestre"
    if pontos < 6400: return "Elite 1★"
    if pontos < 7400: return "Elite 2★"
    if pontos < 8400: return "Elite 3★"
    if pontos < 9400: return "Elite 4★"
    return "Elite 5★"


# =============================================
# 🔑 Obter token JWT da API
# =============================================

async def obter_token_jwt_da_api(regiao: str):
    try:
        async with httpx.AsyncClient(timeout=10.0) as cliente:
            resposta = await cliente.get(f"{URL_API_JWT}?region={regiao}")
            if resposta.status_code == 200:
                dados = resposta.json()
                token = dados.get("token")
                url_servidor = dados.get("server_url")
                if token and url_servidor:
                    return {
                        "token": f"Bearer {token}",
                        "url_servidor": url_servidor,
                        "expira_em": time.time() + 25200
                    }
            return None
    except Exception as e:
        print(f"⚠️ Erro na API de JWT para {regiao}: {e}")
        return None

# =============================================
# 🔄 Gerenciador de Tokens
# =============================================

class GerenciadorTokens:
    def __init__(self):
        self.tokens = {}
        self.trava = asyncio.Lock()

    async def obter_token(self, regiao: str):
        async with self.trava:
            info_token = self.tokens.get(regiao)
            if info_token and info_token.get('expira_em', 0) > time.time():
                return info_token

            print(f"🔄 Obtendo token para {regiao} da API JWT...")

            info_token = await obter_token_jwt_da_api(regiao)

            if not info_token:
                print(f"⚠️ API JWT falhou para {regiao}, usando backup...")
                info_token = await self.gerar_token_backup(regiao)

            if info_token:
                self.tokens[regiao] = info_token
                return info_token

            return None

    async def gerar_token_backup(self, regiao: str):
        try:
            cred = CREDENCIAIS_CONTAS.get(regiao, CREDENCIAIS_CONTAS["ME"])
            conta = f"uid={cred['uid']}&password={cred['senha']}"

            valor_token, id_aberto = await obter_token_acesso(conta)

            if not valor_token or not id_aberto:
                return None

            corpo = json.dumps({
                "open_id": id_aberto,
                "open_id_type": "4",
                "login_token": valor_token,
                "orign_platform_type": "4"
            })
            bytes_proto = await json_para_proto(corpo, FreeFire_pb2.LoginReq())
            carga_util = aes_cbc_criptografar(CHAVE_PRINCIPAL, IV_PRINCIPAL, bytes_proto)

            config = CONFIG_REGIAO.get(regiao, CONFIG_REGIAO["ME"])
            url = f"{config['url_servidor']}/MajorLogin"

            cabecalhos = {
                'User-Agent': AGENTE_USUARIO,
                'Connection': "Keep-Alive",
                'Accept-Encoding': "gzip",
                'Content-Type': "application/octet-stream",
                'Expect': "100-continue",
                'X-Unity-Version': "2018.4.11f1",
                'X-GA': "v1 1",
                'ReleaseVersion': config['versao_lancamento']
            }

            async with httpx.AsyncClient(timeout=30.0) as cliente:
                resp = await cliente.post(url, data=carga_util, headers=cabecalhos)
                if resp.status_code != 200:
                    return None

                login_res = FreeFire_pb2.LoginRes()
                login_res.ParseFromString(resp.content)
                msg_json = json_format.MessageToJson(login_res)
                msg = json.loads(msg_json)

                info_token = {
                    'token': f"Bearer {msg.get('token', '0')}",
                    'regiao': msg.get('lockRegion', '0'),
                    'url_servidor': msg.get('serverUrl', '0'),
                    'expira_em': time.time() + 25200
                }
                return info_token

        except Exception as e:
            print(f"❌ Erro ao gerar token de backup para {regiao}: {e}")
            return None


gerenciador_tokens = GerenciadorTokens()


# === Funções Auxiliares ===
def aplicar_padding(texto: bytes) -> bytes:
    tamanho_padding = AES.block_size - (len(texto) % AES.block_size)
    return texto + bytes([tamanho_padding] * tamanho_padding)


def aes_cbc_criptografar(chave: bytes, iv: bytes, texto_claro: bytes) -> bytes:
    cifra = AES.new(chave, AES.MODE_CBC, iv)
    return cifra.encrypt(aplicar_padding(texto_claro))


async def json_para_proto(dados_json: str, mensagem_proto) -> bytes:
    json_format.ParseDict(json.loads(dados_json), mensagem_proto)
    return mensagem_proto.SerializeToString()


async def obter_token_acesso(conta: str):
    url = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
    carga = conta + "&response_type=token&client_type=2&client_secret=2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3&client_id=100067"
    cabecalhos = {
        'User-Agent': AGENTE_USUARIO,
        'Content-Type': "application/x-www-form-urlencoded"
    }

    for tentativa in range(3):
        try:
            async with httpx.AsyncClient(timeout=30.0) as cliente:
                resp = await cliente.post(url, data=carga, headers=cabecalhos)
                if resp.status_code == 200:
                    dados = resp.json()
                    return dados.get("access_token"), dados.get("open_id")
                await asyncio.sleep(2)
        except:
            await asyncio.sleep(2)
    return None, None


async def obter_informacoes_conta(uid, regiao):
    try:
        info_token = await gerenciador_tokens.obter_token(regiao)
        if not info_token:
            return None

        token = info_token['token']
        url_servidor = info_token['url_servidor']
        config = CONFIG_REGIAO.get(regiao, CONFIG_REGIAO["ME"])

        carga = await json_para_proto(
            json.dumps({'a': uid, 'b': '7'}),
            main_pb2.GetPlayerPersonalShow()
        )
        dados_cripto = aes_cbc_criptografar(CHAVE_PRINCIPAL, IV_PRINCIPAL, carga)

        cabecalhos = {
            'User-Agent': AGENTE_USUARIO,
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/octet-stream",
            'Expect': "100-continue",
            'Authorization': token,
            'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1",
            'ReleaseVersion': config['versao_lancamento']
        }

        async with httpx.AsyncClient(timeout=30.0) as cliente:
            resp = await cliente.post(
                url_servidor + '/GetPlayerPersonalShow',
                data=dados_cripto,
                headers=cabecalhos
            )

            if resp.status_code != 200:
                return None

            info_conta = AccountPersonalShow_pb2.AccountPersonalShowInfo()
            info_conta.ParseFromString(resp.content)
            resultado = json.loads(json_format.MessageToJson(info_conta))

            # 🔥 Verificar status de banimento
            esta_banido = resultado.get("isBanned", False)
            if isinstance(esta_banido, bool):
                resultado["status_banimento"] = "🟢 DESBANIDO" if not esta_banido else "🔴 BANIDO"
            else:
                resultado["status_banimento"] = "❓ DESCONHECIDO"

            # Adicionar região usada
            resultado["_regiao_usada"] = regiao

            return resultado

    except Exception as e:
        print(f"❌ Erro ao obter informações da conta: {e}")
        return None


# =============================================
# 🛠 FUNÇÕES AUXILIARES
# =============================================

def timestamp_para_bst(ts):
    try:
        if not ts or ts == 0:
            return "N/D"
        dt = datetime.fromtimestamp(int(ts)) + timedelta(hours=6)
        return dt.strftime("%d %b %Y às %I:%M:%S %p") + " (Horário de Bangladesh)"
    except:
        return "N/D"


# =============================================
# 🚀 API PRINCIPAL
# =============================================

@app.route('/info')
def informacoes_completas():
    uid = request.args.get('uid')

    if not uid:
        return jsonify({"erro": "O UID é obrigatório"}), 400

    try:
        uid_int = int(uid)
    except:
        return jsonify({"erro": "UID inválido"}), 400

    # =============================================
    # 🎯 BD → IND → ME → Outros
    # =============================================

    dados_conta = None
    regiao_usada = None

    for regiao in PRIORIDADE_REGIAO:
        print(f"🌍 Tentando {regiao}...")
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            dados = loop.run_until_complete(obter_informacoes_conta(uid_int, regiao))
            loop.close()

            if dados:
                dados_conta = dados
                regiao_usada = regiao
                print(f"✅ Sucesso com {regiao}")
                break
        except Exception as e:
            print(f"⚠️ Erro em {regiao}: {e}")
            continue

    if not dados_conta:
        return jsonify({"erro": "Jogador não encontrado"}), 404

    info_basica = dados_conta.get("basicInfo", {})
    info_cla = dados_conta.get("clanBasicInfo", {})
    info_social = dados_conta.get("socialInfo", {})
    info_mascote = dados_conta.get("petInfo", {})
    capitao = dados_conta.get("captainBasicInfo", {})
    credito = dados_conta.get("creditScoreInfo", {})
    perfil = dados_conta.get("profileInfo", {})

    # =============================================
    # 🔥 Obter AvatarId corretamente (ID do personagem)
    # =============================================

    id_avatar = "N/D"
    try:
        if perfil and "avatarId" in perfil:
            id_avatar = perfil.get("avatarId", "N/D")
        elif info_basica and "headPic" in info_basica:
            id_avatar = info_basica.get("headPic", "N/D")
        elif info_basica and "avatarId" in info_basica:
            id_avatar = info_basica.get("avatarId", "N/D")
        else:
            id_avatar = "N/D"
    except:
        id_avatar = "N/D"

    # Pontos BR e CS
    pontos_br = info_basica.get("rankingPoints", 0)
    pontos_cs = info_basica.get("csRankingPoints", 0)

    # Pontos máximos
    pontos_max_rank = info_basica.get("maxRankingPoints", 0)
    pontos_max_cs = info_basica.get("csMaxRankingPoints", 0)
    pontos_periodicos = info_basica.get("periodicRankingPoints", 0)

    # =============================================
    # 🎨 Detalhes das roupas
    # =============================================

    ids_roupas = perfil.get("clothes", [])
    skins_armas = info_basica.get("weaponSkinShows", [])

    categorias_roupa = {
        "Cabeca": [], "Torso": [], "Mascara": [], "Calca": [],
        "Cabelo": [], "Sapato": [], "Arma": [],
        "Emote": [], "Pacote": [], "Outro": []
    }

    for idx, cid in enumerate(ids_roupas):
        if cid and cid != 0:
            if idx == 0:
                categorias_roupa["Cabeca"].append(cid)
            elif idx == 1:
                categorias_roupa["Torso"].append(cid)
            elif idx == 2:
                categorias_roupa["Mascara"].append(cid)
            elif idx == 3:
                categorias_roupa["Calca"].append(cid)
            elif idx == 4:
                categorias_roupa["Cabelo"].append(cid)
            elif idx == 5:
                categorias_roupa["Sapato"].append(cid)
            elif idx == 6:
                categorias_roupa["Emote"].append(cid)
            elif idx == 7:
                categorias_roupa["Pacote"].append(cid)
            else:
                categorias_roupa["Outro"].append(cid)

    for wid in skins_armas:
        if wid and wid != 0:
            categorias_roupa["Arma"].append(wid)

    # =============================================
    # 🔥 Obter PrimeLevel corretamente
    # =============================================

    nivel_prime = "0"
    try:
        if "primeLevel" in info_basica:
            dados_prime = info_basica.get("primeLevel")
            if isinstance(dados_prime, dict):
                nivel_prime = str(dados_prime.get("level", 0))
            elif isinstance(dados_prime, (int, float)):
                nivel_prime = str(int(dados_prime))
            elif isinstance(dados_prime, str) and dados_prime.isdigit():
                nivel_prime = dados_prime
            elif isinstance(dados_prime, str):
                nivel_prime = dados_prime
            else:
                nivel_prime = "0"
        else:
            if "accountPrefers" in info_basica:
                preferencias = info_basica.get("accountPrefers", {})
                if isinstance(preferencias, dict):
                    if "primeLevel" in preferencias:
                        dados_prime = preferencias.get("primeLevel")
                        if isinstance(dados_prime, dict):
                            nivel_prime = str(dados_prime.get("level", 0))
                        elif isinstance(dados_prime, (int, float)):
                            nivel_prime = str(int(dados_prime))
                        elif isinstance(dados_prime, str):
                            nivel_prime = dados_prime
                        else:
                            nivel_prime = "0"
                    elif "prime_level" in preferencias:
                        dados_prime = preferencias.get("prime_level")
                        if isinstance(dados_prime, dict):
                            nivel_prime = str(dados_prime.get("level", 0))
                        elif isinstance(dados_prime, (int, float)):
                            nivel_prime = str(int(dados_prime))
                        elif isinstance(dados_prime, str):
                            nivel_prime = dados_prime
                        else:
                            nivel_prime = "0"

        if nivel_prime == "0" or nivel_prime == "":
            for chave in info_basica:
                if "prime" in chave.lower() and "level" in chave.lower():
                    valor = info_basica.get(chave)
                    if isinstance(valor, (int, float)):
                        nivel_prime = str(int(valor))
                    elif isinstance(valor, str):
                        nivel_prime = valor
                    break

    except Exception as e:
        print(f"⚠️ Erro ao obter PrimeLevel: {e}")
        nivel_prime = "0"

    # =============================================
    # 📊 Montar resposta completa em português
    # =============================================

    resposta = {
        "status": "sucesso",
        "servidor_usado": regiao_usada,
        "StatusBanimento": dados_conta.get("status_banimento", "❓ DESCONHECIDO"),
        "InformacoesBasicas": {
            "NivelPrime": nivel_prime,
            "Nome": info_basica.get("nickname", "N/D"),
            "UID": uid,
            "Nivel": info_basica.get("level", "N/D"),
            "Experiencia": info_basica.get("exp", "N/D"),
            "Regiao": info_basica.get("region", "N/D"),
            "Curtidas": info_basica.get("liked", "N/D"),
            "PontuacaoHonra": credito.get("creditScore", "N/D") if credito.get("creditScore") else 0,
            "StatusCelebridade": "Sim" if info_basica.get("showBrRank") else "Nao",
            "Titulo": info_basica.get("title", "N/D"),
            "Assinatura": info_social.get("signature", "N/D"),
            "IdAvatar": id_avatar,
            "IdBanner": info_basica.get("bannerId", "N/D"),
            "IdPin": info_basica.get("pinId", "N/D"),
            "IdDistintivo": info_basica.get("badgeId", "N/D"),
            "QuantidadeDistintivos": info_basica.get("badgeCnt", "N/D"),
            "TipoConta": info_basica.get("accountType", "N/D"),
            "IdTemporada": info_basica.get("seasonId", "N/D"),
            "VersaoLancamento": info_basica.get("releaseVersion", "N/D"),
            "ExibirRankBR": info_basica.get("showBrRank", False),
            "ExibirRankCS": info_basica.get("showCsRank", False),
            "ExibirMochilaJogo": info_basica.get("gameBagShow", "N/D"),
            "SlotsItensSelecionados": info_basica.get("selectedItemSlots", [])
        },
        "InformacoesRank": {
            "RankBR": obter_ranque_br(pontos_br),
            "PontosBR": pontos_br,
            "RankBRMaximo": obter_ranque_br(pontos_max_rank) if pontos_max_rank > 0 else obter_ranque_br(pontos_br),
            "PontosBRMaximo": pontos_max_rank if pontos_max_rank > 0 else pontos_br,
            "PosicaoRankBR": info_basica.get("peakRankPos", "N/D"),
            "RankBRPeriodico": obter_ranque_br(pontos_periodicos) if pontos_periodicos > 0 else obter_ranque_br(pontos_br),
            "PontosBRPeriodico": pontos_periodicos if pontos_periodicos > 0 else pontos_br,
            "RankCS": obter_ranque_cs(pontos_cs),
            "PontosCS": pontos_cs,
            "RankCSMaximo": obter_ranque_cs(pontos_max_cs) if pontos_max_cs > 0 else obter_ranque_cs(pontos_cs),
            "PontosCSMaximo": pontos_max_cs if pontos_max_cs > 0 else pontos_cs,
            "PosicaoRankCS": info_basica.get("csPeakRankPos", "N/D"),
            "EstaBanidoRankCS": info_basica.get("isCsRankingBan", False)
        },
        "InformacoesAtividade": {
            "OBMaisRecente": info_basica.get("releaseVersion", "N/D"),
            "BooyahPass": "Sim" if info_basica.get("hasElitePass") else "Nao",
            "DistintivosBPAtais": info_basica.get("badgeCnt", "N/D"),
            "CriadaEm": timestamp_para_bst(info_basica.get("createAt", 0)),
            "UltimoLogin": timestamp_para_bst(info_basica.get("lastLoginAt", 0)),
            "RetornoEm": timestamp_para_bst(info_basica.get("returnAt", 0)) if info_basica.get("returnAt") and info_basica.get("returnAt") != 0 else "N/D",
            "TempoExpiracaoVeterano": info_basica.get("veteranExpireTime", "N/D") if info_basica.get("veteranExpireTime") and info_basica.get("veteranExpireTime") != 0 else "N/D",
            "TagDiasAusenciaVeterano": info_basica.get("veteranLeaveDaysTag", "N/D") if info_basica.get("veteranLeaveDaysTag") and info_basica.get("veteranLeaveDaysTag") != "VeteranLeaveDays_NONE" else "N/D"
        },
        "InformacoesCla": {
            "NomeCla": info_cla.get("clanName", "Sem Clã"),
            "IDCla": info_cla.get("clanId", "N/D"),
            "NivelCla": info_cla.get("clanLevel", "N/D"),
            "MembrosAtivos": info_cla.get("memberNum", "N/D"),
            "MaximoMembros": info_cla.get("capacity", "N/D"),
            "IdDistintivoCla": info_cla.get("clanBadgeId", "N/D") if info_cla.get("clanBadgeId") else "N/D",
            "IdMolduraCla": info_cla.get("clanFrameId", "N/D") if info_cla.get("clanFrameId") else "N/D",
            "DistintivoPersonalizadoCla": info_cla.get("customClanBadge", "N/D") if info_cla.get("customClanBadge") else "N/D",
            "UsarDistintivoPersonalizado": info_cla.get("useCustomClanBadge", False)
        },
        "DetalhesMascote": {
            "Equipado": "Sim" if info_mascote.get("isSelected") else "Nao",
            "ApelidoMascote": info_mascote.get("name", "N/D"),
            "TipoMascote": info_mascote.get("id", "N/D"),
            "HabilidadeMascote": info_mascote.get("selectedSkillId", "N/D"),
            "PeleMascote": info_mascote.get("skinId", "N/D"),
            "ExperienciaMascote": info_mascote.get("exp", "N/D"),
            "NivelMascote": info_mascote.get("level", "N/D"),
            "EstaMarcadoEstrela": info_mascote.get("isMarkedStar", False),
            "Acoes": info_mascote.get("actions", [])
        },
        "InformacoesPerfil": {
            "IdAvatar": id_avatar,
            "CorPele": perfil.get("skinColor", "N/D"),
            "IDsRoupas": ids_roupas,
            "HabilidadesEquipadas": perfil.get("equipedSkills", []),
            "EstaSelecionado": perfil.get("isSelected", False),
            "EstaSelecionadoDespertar": perfil.get("isSelectedAwaken", False),
            "EfeitosCosturaRoupas": perfil.get("clothesTailorEffects", [])
        },
        "DetalhesRoupas": {
            "Cabeca": categorias_roupa["Cabeca"],
            "Torso": categorias_roupa["Torso"],
            "Mascara": categorias_roupa["Mascara"],
            "Calca": categorias_roupa["Calca"],
            "Cabelo": categorias_roupa["Cabelo"],
            "Sapato": categorias_roupa["Sapato"],
            "Arma": categorias_roupa["Arma"],
            "Emote": categorias_roupa["Emote"],
            "Pacote": categorias_roupa["Pacote"],
            "Outro": categorias_roupa["Outro"],
            "TotalRoupas": len(ids_roupas),
            "TotalArmas": len(skins_armas)
        },
        "InformacoesSociais": {
            "Genero": info_social.get("gender", "N/D"),
            "Idioma": info_social.get("language", "N/D"),
            "PreferenciaModo": info_social.get("modePrefer", "N/D"),
            "ExibicaoRank": info_social.get("rankShow", "N/D"),
            "Assinatura": info_social.get("signature", "N/D"),
            "ExpiracaoBanimentoAssinatura": info_social.get("signatureBanExpireTime", "N/D") if info_social.get("signatureBanExpireTime") and info_social.get("signatureBanExpireTime") != 0 else "N/D",
            "TempoOnline": info_social.get("timeOnline", "N/D"),
            "TempoAtivo": info_social.get("timeActive", "N/D"),
            "TagBatalha": info_social.get("battleTag", []),
            "TagSocial": info_social.get("socialTag", []),
            "QuantidadeTagBatalha": info_social.get("battleTagCount", [])
        },
        "InformacoesCapitao": {
            "Nome": capitao.get("nickname", "N/D"),
            "UID": capitao.get("accountId", "N/D"),
            "Nivel": capitao.get("level", "N/D"),
            "Regiao": capitao.get("region", "N/D"),
            "BooyahPass": "Sim" if capitao.get("hasElitePass") else "Nao",
            "CriadoEm": timestamp_para_bst(capitao.get("createAt", 0)),
            "UltimoLogin": timestamp_para_bst(capitao.get("lastLoginAt", 0)),
            "OBMaisRecente": capitao.get("releaseVersion", "N/D"),
            "Titulo": capitao.get("title", "N/D"),
            "DistintivosBP": capitao.get("badgeCnt", "N/D"),
            "RankBR": obter_ranque_br(capitao.get("rankingPoints", 0)),
            "PontosBR": capitao.get("rankingPoints", 0)
        },
        "InformacoesPontuacaoHonra": {
            "PontuacaoHonra": credito.get("creditScore", "N/D") if credito.get("creditScore") else 0,
            "EstaInicializado": credito.get("isInit", False),
            "EstadoRecompensa": credito.get("rewardState", "N/D") if credito.get("rewardState") else "N/D",
            "QtdCurtidasResumoPeriodico": credito.get("periodicSummaryLikeCnt", "N/D") if credito.get("periodicSummaryLikeCnt") else "N/D",
            "QtdIlegivelResumoPeriodico": credito.get("periodicSummaryIllegalCnt", "N/D") if credito.get("periodicSummaryIllegalCnt") else "N/D",
            "QtdPartidasSemanais": credito.get("weeklyMatchCnt", "N/D") if credito.get("weeklyMatchCnt") else "N/D",
            "InicioResumoPeriodico": timestamp_para_bst(credito.get("periodicSummaryStartTime", 0)) if credito.get("periodicSummaryStartTime") and credito.get("periodicSummaryStartTime") != 0 else "N/D",
            "FimResumoPeriodico": timestamp_para_bst(credito.get("periodicSummaryEndTime", 0)) if credito.get("periodicSummaryEndTime") and credito.get("periodicSummaryEndTime") != 0 else "N/D"
        },
        "Banner": {
            "IdBanner": info_basica.get("bannerId", "N/D"),
            "IdAvatar": id_avatar,
            "IdPin": info_basica.get("pinId", "N/D"),
            "IdDistintivo": info_basica.get("badgeId", "N/D"),
            "QuantidadeDistintivos": info_basica.get("badgeCnt", "N/D")
        },
        "Complemento": {
            "Titulo": info_basica.get("title", "N/D"),
            "Assinatura": info_social.get("signature", "N/D"),
            "Regiao": info_basica.get("region", "N/D"),
            "VersaoLancamento": info_basica.get("releaseVersion", "N/D"),
            "IdTemporada": info_basica.get("seasonId", "N/D"),
            "TipoConta": info_basica.get("accountType", "N/D"),
            "ExibirRankBR": info_basica.get("showBrRank", False),
            "ExibirRankCS": info_basica.get("showCsRank", False),
            "ExibirMochilaJogo": info_basica.get("gameBagShow", "N/D"),
            "SlotsItensSelecionados": info_basica.get("selectedItemSlots", [])
        }
    }

    return jsonify(resposta)


@app.route('/')
def inicio():
    return jsonify({
        "status": "executando",
        "versao": "OB54",
        "endpoint": "/info?uid=UID",
        "exemplo": "/info?uid=2084018498",
        "prioridade": "BD → IND → ME → Outros",
        "creditos": "@LEO MODZ"
    })


@app.route('/status')
def status_tokens():
    status = {}
    for regiao, info in gerenciador_tokens.tokens.items():
        expira_em = info['expira_em'] - time.time()
        status[regiao] = {
            "possui_token": True,
            "expira_em": f"{expira_em / 3600:.1f} horas"
        }
    return jsonify({
        "total_tokens": len(gerenciador_tokens.tokens),
        "tokens": status
    })


@app.route('/refresh')
def atualizar_tokens():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    for regiao in ["BD", "IND", "ME"]:
        loop.run_until_complete(gerenciador_tokens.obter_token(regiao))
    loop.close()
    return jsonify({
        "status": "atualizado",
        "quantidade": len(gerenciador_tokens.tokens)
    })


if __name__ == '__main__':
    import threading

    def iniciar_em_segundo_plano():
        global gerenciador_tokens
        gerenciador_tokens = GerenciadorTokens()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        for regiao in ["BD", "IND", "ME"]:
            try:
                loop.run_until_complete(gerenciador_tokens.obter_token(regiao))
            except:
                pass
        loop.run_forever()

    thread_fundo = threading.Thread(target=iniciar_em_segundo_plano, daemon=True)
    thread_fundo.start()
    app.run(host='0.0.0.0', port=5002, debug=False)
