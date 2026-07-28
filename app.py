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

# ============= TODOS OS ARQUIVOS NA MESMA PASTA =============
try:
    import FreeFire_pb2, main_pb2, AccountPersonalShow_pb2
    import GetOutfit_pb2
    print("✅ Arquivos Proto importados com sucesso")
except ImportError as e:
    print(f"❌ Erro na importação Proto: {e}")
    sys.exit(1)

# =============================================
# 🔧 CONFIGURAÇÃO
# =============================================

RELEASEVERSION = "OB54"
USERAGENT = "Dalvik/2.1.0 (Linux; U; Android 14; CPH2095 Build/RKQ1.211119.001)"

MAIN_KEY = base64.b64decode('WWcmdGMlREV1aDYlWmNeOA==')
MAIN_IV = base64.b64decode('Nm95WkRyMjJFM3ljaGpNJQ==')

# =============================================
# 🔑 API DE TOKEN JWT
# =============================================

JWT_API_URL = "http://leomdzjwtob54.vercel.app/token"

# =============================================
# 👤 CREDENCIAIS DA CONTA
# =============================================

ACCOUNT_CREDENTIALS = {
    "BD": {"uid": "5372860087", "password": "shappno_create-by-shappno_S7kkYNMy"},
    "IND": {"uid": "4269013803", "password": "MG24_GAMER_XSBOS_BY_SPIDEERIO_GAMING_TE5NG"},
    "ME": {"uid": "4269012488", "password": "MG24_GAMER_U27YB_BY_SPIDEERIO_GAMING_0PNCN"},
    "SG": {"uid": "4269012488", "password": "MG24_GAMER_U27YB_BY_SPIDEERIO_GAMING_0PNCN"},
    "ID": {"uid": "4269012488", "password": "MG24_GAMER_U27YB_BY_SPIDEERIO_GAMING_0PNCN"},
    "TH": {"uid": "4269012488", "password": "MG24_GAMER_U27YB_BY_SPIDEERIO_GAMING_0PNCN"},
    "VN": {"uid": "4269012488", "password": "MG24_GAMER_U27YB_BY_SPIDEERIO_GAMING_0PNCN"},
    "PK": {"uid": "4269012488", "password": "MG24_GAMER_U27YB_BY_SPIDEERIO_GAMING_0PNCN"},
    "BR": {"uid": "4269012488", "password": "MG24_GAMER_U27YB_BY_SPIDEERIO_GAMING_0PNCN"},
    "US": {"uid": "4269012488", "password": "MG24_GAMER_U27YB_BY_SPIDEERIO_GAMING_0PNCN"},
    "EU": {"uid": "4269012488", "password": "MG24_GAMER_U27YB_BY_SPIDEERIO_GAMING_0PNCN"}
}

# =============================================
# 🌍 CONFIGURAÇÃO DE REGIÃO
# =============================================

REGION_CONFIG = {
    "BD": {"server_url": "https://loginbp.ggblueshark.com", "release_version": "OB54", "client_version": "1.124.0"},
    "IND": {"server_url": "https://loginbp.ggpolarbear.com", "release_version": "OB54", "client_version": "1.124.0"},
    "ME": {"server_url": "https://loginbp.ggblueshark.com", "release_version": "OB54", "client_version": "1.124.0"},
    "SG": {"server_url": "https://loginbp.ggblueshark.com", "release_version": "OB54", "client_version": "1.124.0"},
    "ID": {"server_url": "https://loginbp.ggblueshark.com", "release_version": "OB54", "client_version": "1.124.0"},
    "TH": {"server_url": "https://loginbp.ggblueshark.com", "release_version": "OB54", "client_version": "1.124.0"},
    "VN": {"server_url": "https://loginbp.ggblueshark.com", "release_version": "OB54", "client_version": "1.124.0"},
    "PK": {"server_url": "https://loginbp.ggblueshark.com", "release_version": "OB54", "client_version": "1.124.0"},
    "BR": {"server_url": "https://loginbp.ggpolarbear.com", "release_version": "OB54", "client_version": "1.124.0"},
    "US": {"server_url": "https://loginbp.ggpolarbear.com", "release_version": "OB54", "client_version": "1.124.0"},
    "EU": {"server_url": "https://loginbp.ggblueshark.com", "release_version": "OB54", "client_version": "1.124.0"}
}

REGION_PRIORITY = ["BD", "IND", "ME", "SG", "ID", "TH", "VN", "PK", "BR", "US", "EU"]

# === Flask App ===
app = Flask(__name__)
CORS(app)

# =============================================
# 🏆 FUNÇÕES DE RANQUE (Atualizado OB54)
# =============================================

def get_br_rank(rp):
    """Ranque BR baseado no sistema de ranqueamento OB54"""
    if rp < 1000: return "Bronze I"
    if rp < 1100: return "Bronze II"
    if rp < 1200: return "Bronze III"
    if rp < 1300: return "Prata I"
    if rp < 1400: return "Prata II"
    if rp < 1500: return "Prata III"
    if rp < 1700: return "Ouro I"
    if rp < 1900: return "Ouro II"
    if rp < 2100: return "Ouro III"
    if rp < 2300: return "Platina I"
    if rp < 2500: return "Platina II"
    if rp < 2700: return "Platina III"
    if rp < 3000: return "Diamante I"
    if rp < 3250: return "Diamante II"
    if rp < 3500: return "Diamante III"
    if rp < 6300: return "Mestre"
    if rp < 7500: return "Elite 1★"
    if rp < 8500: return "Elite 2★"
    if rp < 9500: return "Elite 3★"
    if rp < 10000: return "Elite 4★"
    return "Elite 5★"

def get_cs_rank(rp):
    """Ranque do Contra Squad (CS) com Estrelas"""
    if rp < 500: return "Bronze I"
    if rp < 600: return "Bronze II"
    if rp < 700: return "Bronze III"
    if rp < 800: return "Prata I"
    if rp < 900: return "Prata II"
    if rp < 1000: return "Prata III"
    if rp < 1200: return "Ouro I"
    if rp < 1400: return "Ouro II"
    if rp < 1600: return "Ouro III"
    if rp < 1800: return "Platina I"
    if rp < 2000: return "Platina II"
    if rp < 2200: return "Platina III"
    if rp < 2500: return "Diamante I"
    if rp < 2700: return "Diamante II"
    if rp < 2900: return "Diamante III"
    if rp < 5400: return "Mestre"
    if rp < 6400: return "Elite 1★"
    if rp < 7400: return "Elite 2★"
    if rp < 8400: return "Elite 3★"
    if rp < 9400: return "Elite 4★"
    return "Elite 5★"


# =============================================
# 🔑 Função de Token JWT
# =============================================

async def get_jwt_token_from_api(region: str):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{JWT_API_URL}?region={region}")
            if response.status_code == 200:
                data = response.json()
                token = data.get("token")
                server_url = data.get("server_url")
                if token and server_url:
                    return {
                        "token": f"Bearer {token}",
                        "server_url": server_url,
                        "expires_at": time.time() + 25200
                    }
            return None
    except Exception as e:
        print(f"⚠️ Erro na API JWT para {region}: {e}")
        return None

# =============================================
# 🔄 Gerenciador de Tokens
# =============================================

class TokenManager:
    def __init__(self):
        self.tokens = {}
        self.lock = asyncio.Lock()
    
    async def get_token(self, region: str):
        async with self.lock:
            token_info = self.tokens.get(region)
            if token_info and token_info.get('expires_at', 0) > time.time():
                return token_info
            
            print(f"🔄 Obtendo token para {region} da API JWT...")
            
            token_info = await get_jwt_token_from_api(region)
            
            if not token_info:
                print(f"⚠️ API JWT falhou para {region}, usando backup...")
                token_info = await self.generate_token_backup(region)
            
            if token_info:
                self.tokens[region] = token_info
                return token_info
            
            return None
    
    async def generate_token_backup(self, region: str):
        try:
            cred = ACCOUNT_CREDENTIALS.get(region, ACCOUNT_CREDENTIALS["ME"])
            account = f"uid={cred['uid']}&password={cred['password']}"
            
            token_val, open_id = await get_access_token(account)
            
            if not token_val or not open_id:
                return None
            
            body = json.dumps({
                "open_id": open_id, 
                "open_id_type": "4", 
                "login_token": token_val, 
                "orign_platform_type": "4"
            })
            proto_bytes = await json_to_proto(body, FreeFire_pb2.LoginReq())
            payload = aes_cbc_encrypt(MAIN_KEY, MAIN_IV, proto_bytes)
            
            config = REGION_CONFIG.get(region, REGION_CONFIG["ME"])
            url = f"{config['server_url']}/MajorLogin"
            
            headers = {
                'User-Agent': USERAGENT,
                'Connection': "Keep-Alive",
                'Accept-Encoding': "gzip",
                'Content-Type': "application/octet-stream",
                'Expect': "100-continue",
                'X-Unity-Version': "2018.4.11f1",
                'X-GA': "v1 1",
                'ReleaseVersion': config['release_version']
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, data=payload, headers=headers)
                if resp.status_code != 200:
                    return None
                
                login_res = FreeFire_pb2.LoginRes()
                login_res.ParseFromString(resp.content)
                msg_json = json_format.MessageToJson(login_res)
                msg = json.loads(msg_json)
                
                token_info = {
                    'token': f"Bearer {msg.get('token','0')}",
                    'region': msg.get('lockRegion','0'),
                    'server_url': msg.get('serverUrl','0'),
                    'expires_at': time.time() + 25200
                }
                return token_info
                
        except Exception as e:
            print(f"❌ Erro no token de backup para {region}: {e}")
            return None

token_manager = TokenManager()

# === Funções Auxiliares ===
def pad(text: bytes) -> bytes:
    padding_length = AES.block_size - (len(text) % AES.block_size)
    return text + bytes([padding_length] * padding_length)

def aes_cbc_encrypt(key: bytes, iv: bytes, plaintext: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(plaintext))

async def json_to_proto(json_data: str, proto_message) -> bytes:
    json_format.ParseDict(json.loads(json_data), proto_message)
    return proto_message.SerializeToString()

async def get_access_token(account: str):
    url = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
    payload = account + "&response_type=token&client_type=2&client_secret=2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3&client_id=100067"
    headers = {'User-Agent': USERAGENT, 'Content-Type': "application/x-www-form-urlencoded"}
    
    for tentativa in range(3):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, data=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("access_token"), data.get("open_id")
                await asyncio.sleep(2)
        except:
            await asyncio.sleep(2)
    return None, None

async def GetAccountInformation(uid, region):
    try:
        token_info = await token_manager.get_token(region)
        if not token_info:
            return None
        
        token = token_info['token']
        server_url = token_info['server_url']
        config = REGION_CONFIG.get(region, REGION_CONFIG["ME"])
        
        payload = await json_to_proto(json.dumps({'a': uid, 'b': '7'}), main_pb2.GetPlayerPersonalShow())
        data_enc = aes_cbc_encrypt(MAIN_KEY, MAIN_IV, payload)
        
        headers = {
            'User-Agent': USERAGENT,
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/octet-stream",
            'Expect': "100-continue",
            'Authorization': token,
            'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1",
            'ReleaseVersion': config['release_version']
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(server_url + '/GetPlayerPersonalShow', data=data_enc, headers=headers)
            
            if resp.status_code != 200:
                return None
            
            account_info = AccountPersonalShow_pb2.AccountPersonalShowInfo()
            account_info.ParseFromString(resp.content)
            result = json.loads(json_format.MessageToJson(account_info))
            
            # 🔥 VERIFICAR STATUS DE BANIMENTO
            is_banned = result.get("isBanned", False)
            if isinstance(is_banned, bool):
                result["ban_status"] = "🟢 DESBANIDO" if not is_banned else "🔴 BANIDO"
            else:
                result["ban_status"] = "❓ DESCONHECIDO"
            
            # Adicionar informação da região
            result["_region_used"] = region
            
            return result
            
    except Exception as e:
        print(f"❌ Erro no GetAccountInformation: {e}")
        return None

# =============================================
# 🛠 FUNÇÕES AUXILIARES
# =============================================

def ts_to_bst(ts):
    try:
        if not ts or ts == 0:
            return "N/A"
        dt = datetime.fromtimestamp(int(ts)) + timedelta(hours=6)
        return dt.strftime("%d %b %Y às %I:%M:%S %p") + " (BST)"
    except:
        return "N/A"

# =============================================
# 🚀 API PRINCIPAL
# =============================================

@app.route('/info')
def get_full_info():
    uid = request.args.get('uid')
    
    if not uid:
        return jsonify({"error": "UID é obrigatório"}), 400
    
    try:
        uid_int = int(uid)
    except:
        return jsonify({"error": "UID inválido"}), 400
    
    # =============================================
    # 🎯 BD → IND → ME → Outros
    # =============================================
    
    account_data = None
    used_region = None
    
    for region in REGION_PRIORITY:
        print(f"🌍 Tentando {region}...")
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            data = loop.run_until_complete(GetAccountInformation(uid_int, region))
            loop.close()
            
            if data:
                account_data = data
                used_region = region
                print(f"✅ Sucesso com {region}")
                break
        except Exception as e:
            print(f"⚠️ Erro em {region}: {e}")
            continue
    
    if not account_data:
        return jsonify({"error": "Jogador não encontrado"}), 404
    
    basic = account_data.get("basicInfo", {})
    clan = account_data.get("clanBasicInfo", {})
    social = account_data.get("socialInfo", {})
    pet = account_data.get("petInfo", {})
    captain = account_data.get("captainBasicInfo", {})
    credit = account_data.get("creditScoreInfo", {})
    profile = account_data.get("profileInfo", {})
    
    # =============================================
    # 🔥 Obter AvatarId corretamente (ID do Personagem)
    # =============================================
    
    avatar_id = "N/A"
    try:
        # Primeiro, tenta profileInfo para avatarId
        if profile and "avatarId" in profile:
            avatar_id = profile.get("avatarId", "N/A")
        # Ou basicInfo para headPic
        elif basic and "headPic" in basic:
            avatar_id = basic.get("headPic", "N/A")
        # Ou avatarId diretamente
        elif basic and "avatarId" in basic:
            avatar_id = basic.get("avatarId", "N/A")
        else:
            avatar_id = "N/A"
    except:
        avatar_id = "N/A"
    
    # Pontos BR & CS
    br_points = basic.get("rankingPoints", 0)
    cs_points = basic.get("csRankingPoints", 0)
    
    # Pontos Máximos
    max_rank_points = basic.get("maxRankingPoints", 0)
    cs_max_points = basic.get("csMaxRankingPoints", 0)
    periodic_points = basic.get("periodicRankingPoints", 0)
    
    # =============================================
    # 🎨 Detalhes das Roupas
    # =============================================
    
    clothes_ids = profile.get("clothes", [])
    weapon_skins = basic.get("weaponSkinShows", [])
    
    outfit_categories = {
        "Head": [], "Top": [], "Mask": [], "Bottom": [], 
        "Hair": [], "Shoes": [], "Weapon": [], 
        "Emote": [], "Bundle": [], "Other": []
    }
    
    for idx, cid in enumerate(clothes_ids):
        if cid and cid != 0:
            if idx == 0: outfit_categories["Head"].append(cid)
            elif idx == 1: outfit_categories["Top"].append(cid)
            elif idx == 2: outfit_categories["Mask"].append(cid)
            elif idx == 3: outfit_categories["Bottom"].append(cid)
            elif idx == 4: outfit_categories["Hair"].append(cid)
            elif idx == 5: outfit_categories["Shoes"].append(cid)
            elif idx == 6: outfit_categories["Emote"].append(cid)
            elif idx == 7: outfit_categories["Bundle"].append(cid)
            else: outfit_categories["Other"].append(cid)
    
    for wid in weapon_skins:
        if wid and wid != 0:
            outfit_categories["Weapon"].append(wid)
    
    # =============================================
    # 🔥 Obter PrimeLevel corretamente
    # =============================================
    
    prime_level = "0"
    try:
        if "primeLevel" in basic:
            prime_data = basic.get("primeLevel")
            if isinstance(prime_data, dict):
                prime_level = str(prime_data.get("level", 0))
            elif isinstance(prime_data, (int, float)):
                prime_level = str(int(prime_data))
            elif isinstance(prime_data, str) and prime_data.isdigit():
                prime_level = prime_data
            elif isinstance(prime_data, str):
                prime_level = prime_data
            else:
                prime_level = "0"
        else:
            if "accountPrefers" in basic:
                prefs = basic.get("accountPrefers", {})
                if isinstance(prefs, dict):
                    if "primeLevel" in prefs:
                        prime_data = prefs.get("primeLevel")
                        if isinstance(prime_data, dict):
                            prime_level = str(prime_data.get("level", 0))
                        elif isinstance(prime_data, (int, float)):
                            prime_level = str(int(prime_data))
                        elif isinstance(prime_data, str):
                            prime_level = prime_data
                        else:
                            prime_level = "0"
                    elif "prime_level" in prefs:
                        prime_data = prefs.get("prime_level")
                        if isinstance(prime_data, dict):
                            prime_level = str(prime_data.get("level", 0))
                        elif isinstance(prime_data, (int, float)):
                            prime_level = str(int(prime_data))
                        elif isinstance(prime_data, str):
                            prime_level = prime_data
                        else:
                            prime_level = "0"
        
        if prime_level == "0" or prime_level == "":
            for key in basic:
                if "prime" in key.lower() and "level" in key.lower():
                    val = basic.get(key)
                    if isinstance(val, (int, float)):
                        prime_level = str(int(val))
                    elif isinstance(val, str):
                        prime_level = val
                    break
                    
    except Exception as e:
        print(f"⚠️ Erro no PrimeLevel: {e}")
        prime_level = "0"
    
    # =============================================
    # 📊 Dados formatados - Adicionar todos os IDs na API de Outfit
    # =============================================
    
    response = {
        "status": "success",
        "server_used": used_region,
        "BanStatus": account_data.get("ban_status", "❓ DESCONHECIDO"),
        "BasicInformation": {
            "PrimeLevel": prime_level,
            "Name": basic.get("nickname", "N/A"),
            "UID": uid,
            "Level": basic.get("level", "N/A"),
            "Exp": basic.get("exp", "N/A"),
            "Region": basic.get("region", "N/A"),
            "Likes": basic.get("liked", "N/A"),
            "HonorScore": credit.get("creditScore", "N/A") if credit.get("creditScore") else 0,
            "CelebrityStatus": "Sim" if basic.get("showBrRank") else "Não",
            "Title": basic.get("title", "N/A"),
            "Signature": social.get("signature", "N/A"),
            "AvatarId": avatar_id,
            "BannerId": basic.get("bannerId", "N/A"),
            "PinId": basic.get("pinId", "N/A"),
            "BadgeId": basic.get("badgeId", "N/A"),
            "BadgeCount": basic.get("badgeCnt", "N/A"),
            "AccountType": basic.get("accountType", "N/A"),
            "SeasonId": basic.get("seasonId", "N/A"),
            "ReleaseVersion": basic.get("releaseVersion", "N/A"),
            "ShowBrRank": basic.get("showBrRank", False),
            "ShowCsRank": basic.get("showCsRank", False),
            "GameBagShow": basic.get("gameBagShow", "N/A"),
            "SelectedItemSlots": basic.get("selectedItemSlots", [])
        },
        "RankInformation": {
            "BRRank": get_br_rank(br_points),
            "BRPoints": br_points,
            "BRMaxRank": get_br_rank(max_rank_points) if max_rank_points > 0 else get_br_rank(br_points),
            "BRMaxPoints": max_rank_points if max_rank_points > 0 else br_points,
            "BRRankPos": basic.get("peakRankPos", "N/A"),
            "BrPeriodicRank": get_br_rank(periodic_points) if periodic_points > 0 else get_br_rank(br_points),
            "BrPeriodicPoints": periodic_points if periodic_points > 0 else br_points,
            "CSRank": get_cs_rank(cs_points),
            "CSPoints": cs_points,
            "CSMaxRank": get_cs_rank(cs_max_points) if cs_max_points > 0 else get_cs_rank(cs_points),
            "CSMaxPoints": cs_max_points if cs_max_points > 0 else cs_points,
            "CSRankPos": basic.get("csPeakRankPos", "N/A"),
            "IsCsRankingBan": basic.get("isCsRankingBan", False)
        },
        "ActivityInformation": {
            "MostRecentOB": basic.get("releaseVersion", "N/A"),
            "BooyahPass": "Sim" if basic.get("hasElitePass") else "Não",
            "CurrentBpBadges": basic.get("badgeCnt", "N/A"),
            "CreatedAt": ts_to_bst(basic.get("createAt", 0)),
            "LastLogin": ts_to_bst(basic.get("lastLoginAt", 0)),
            "ReturnAt": ts_to_bst(basic.get("returnAt", 0)) if basic.get("returnAt") and basic.get("returnAt") != 0 else "N/A",
            "VeteranExpireTime": basic.get("veteranExpireTime", "N/A") if basic.get("veteranExpireTime") and basic.get("veteranExpireTime") != 0 else "N/A",
            "VeteranLeaveDaysTag": basic.get("veteranLeaveDaysTag", "N/A") if basic.get("veteranLeaveDaysTag") and basic.get("veteranLeaveDaysTag") != "VeteranLeaveDays_NONE" else "N/A"
        },
        "GuildInformation": {
            "GuildName": clan.get("clanName", "Sem Guild"),
            "GuildID": clan.get("clanId", "N/A"),
            "GuildLevel": clan.get("clanLevel", "N/A"),
            "LiveMembers": clan.get("memberNum", "N/A"),
            "MaxMembers": clan.get("capacity", "N/A"),
            "GuildBadgeId": clan.get("clanBadgeId", "N/A") if clan.get("clanBadgeId") else "N/A",
            "GuildFrameId": clan.get("clanFrameId", "N/A") if clan.get("clanFrameId") else "N/A",
            "CustomClanBadge": clan.get("customClanBadge", "N/A") if clan.get("customClanBadge") else "N/A",
            "UseCustomClanBadge": clan.get("useCustomClanBadge", False)
        },
        "PetDetails": {
            "Equipped": "Sim" if pet.get("isSelected") else "Não",
            "PetNick": pet.get("name", "N/A"),
            "PetType": pet.get("id", "N/A"),
            "PetSkill": pet.get("selectedSkillId", "N/A"),
            "PetSkin": pet.get("skinId", "N/A"),
            "PetExp": pet.get("exp", "N/A"),
            "PetLevel": pet.get("level", "N/A"),
            "IsMarkedStar": pet.get("isMarkedStar", False),
            "Actions": pet.get("actions", [])
        },
        "ProfileInformation": {
            "AvatarId": avatar_id,
            "SkinColor": profile.get("skinColor", "N/A"),
            "ClothesIDs": clothes_ids,
            "EquippedSkills": profile.get("equipedSkills", []),
            "IsSelected": profile.get("isSelected", False),
            "IsSelectedAwaken": profile.get("isSelectedAwaken", False),
            "ClothesTailorEffects": profile.get("clothesTailorEffects", [])
        },
        "OutfitDetails": {
            "Head": outfit_categories["Head"],
            "Top": outfit_categories["Top"],
            "Mask": outfit_categories["Mask"],
            "Bottom": outfit_categories["Bottom"],
            "Hair": outfit_categories["Hair"],
            "Shoes": outfit_categories["Shoes"],
            "Weapon": outfit_categories["Weapon"],
            "Emote": outfit_categories["Emote"],
            "Bundle": outfit_categories["Bundle"],
            "Other": outfit_categories["Other"],
            "TotalClothes": len(clothes_ids),
            "TotalWeapons": len(weapon_skins)
        },
        "SocialInformation": {
            "Gender": social.get("gender", "N/A"),
            "Language": social.get("language", "N/A"),
            "ModePrefer": social.get("modePrefer", "N/A"),
            "RankShow": social.get("rankShow", "N/A"),
            "Signature": social.get("signature", "N/A"),
            "SignatureBanExpireTime": social.get("signatureBanExpireTime", "N/A") if social.get("signatureBanExpireTime") and social.get("signatureBanExpireTime") != 0 else "N/A",
            "TimeOnline": social.get("timeOnline", "N/A"),
            "TimeActive": social.get("timeActive", "N/A"),
            "BattleTag": social.get("battleTag", []),
            "SocialTag": social.get("socialTag", []),
            "BattleTagCount": social.get("battleTagCount", [])
        },
        "LeaderInformation": {
            "Name": captain.get("nickname", "N/A"),
            "UID": captain.get("accountId", "N/A"),
            "Level": captain.get("level", "N/A"),
            "Region": captain.get("region", "N/A"),
            "BooyahPass": "Sim" if captain.get("hasElitePass") else "Não",
            "CreatedAt": ts_to_bst(captain.get("createAt", 0)),
            "LastLogin": ts_to_bst(captain.get("lastLoginAt", 0)),
            "MostRecentOB": captain.get("releaseVersion", "N/A"),
            "Title": captain.get("title", "N/A"),
            "BpBadges": captain.get("badgeCnt", "N/A"),
            "BRRank": get_br_rank(captain.get("rankingPoints", 0)),
            "BRPoints": captain.get("rankingPoints", 0)
        },
        "CreditScoreInformation": {
            "CreditScore": credit.get("creditScore", "N/A") if credit.get("creditScore") else 0,
            "IsInit": credit.get("isInit", False),
            "RewardState": credit.get("rewardState", "N/A") if credit.get("rewardState") else "N/A",
            "PeriodicSummaryLikeCnt": credit.get("periodicSummaryLikeCnt", "N/A") if credit.get("periodicSummaryLikeCnt") else "N/A",
            "PeriodicSummaryIllegalCnt": credit.get("periodicSummaryIllegalCnt", "N/A") if credit.get("periodicSummaryIllegalCnt") else "N/A",
            "WeeklyMatchCnt": credit.get("weeklyMatchCnt", "N/A") if credit.get("weeklyMatchCnt") else "N/A",
            "PeriodicSummaryStartTime": ts_to_bst(credit.get("periodicSummaryStartTime", 0)) if credit.get("periodicSummaryStartTime") and credit.get("periodicSummaryStartTime") != 0 else "N/A",
            "PeriodicSummaryEndTime": ts_to_bst(credit.get("periodicSummaryEndTime", 0)) if credit.get("periodicSummaryEndTime") and credit.get("periodicSummaryEndTime") != 0 else "N/A"
        },
        "Banner": {
            "BannerId": basic.get("bannerId", "N/A"),
            "AvatarId": avatar_id,
            "PinId": basic.get("pinId", "N/A"),
            "BadgeId": basic.get("badgeId", "N/A"),
            "BadgeCount": basic.get("badgeCnt", "N/A")
        },
        "After": {
            "Title": basic.get("title", "N/A"),
            "Signature": social.get("signature", "N/A"),
            "Region": basic.get("region", "N/A"),
            "ReleaseVersion": basic.get("releaseVersion", "N/A"),
            "SeasonId": basic.get("seasonId", "N/A"),
            "AccountType": basic.get("accountType", "N/A"),
            "ShowBrRank": basic.get("showBrRank", False),
            "ShowCsRank": basic.get("showCsRank", False),
            "GameBagShow": basic.get("gameBagShow", "N/A"),
            "SelectedItemSlots": basic.get("selectedItemSlots", [])
        }
    }
    
    return jsonify(response)

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "version": "OB54",
        "endpoint": "/info?uid=UID",
        "example": "/info?uid=2084018498",
        "priority": "BD → IND → ME → Outros",
        "credit": "@LEO MODZ"
    })

@app.route('/status')
def token_status():
    status = {}
    for region, info in token_manager.tokens.items():
        expires_in = info['expires_at'] - time.time()
        status[region] = {"has_token": True, "expires_in": f"{expires_in/3600:.1f} horas"}
    return jsonify({"total_tokens": len(token_manager.tokens), "tokens": status})

@app.route('/refresh')
def refresh_tokens():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    for region in ["BD", "IND", "ME"]:
        loop.run_until_complete(token_manager.get_token(region))
    loop.close()
    return jsonify({"status": "atualizado", "count": len(token_manager.tokens)})

if __name__ == '__main__':
    import threading
    def start_background():
        global token_manager
        token_manager = TokenManager()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        for region in ["BD", "IND", "ME"]:
            try:
                loop.run_until_complete(token_manager.get_token(region))
            except:
                pass
        loop.run_forever()
    
    bg_thread = threading.Thread(target=start_background, daemon=True)
    bg_thread.start()
    app.run(host='0.0.0.0', port=5002, debug=False)
