"""公式データのライダー → riders.csv の id 対応付け"""
import csv, json, re, unicodedata
from era import key, fold
from maps import nat_ja
import os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data') + os.sep

def slug(s):
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', fold(s).replace("'", ''))).strip('-')

# 表記ゆれ（公式名 → riders.csv の name_en）
ALIAS = {"daniel pedrosa": "Dani Pedrosa", "esteve rabat": "Tito Rabat", "kenny roberts": "Kenny Roberts Jr.",
         "alex marquez": "Álex Márquez", "alex rins": "Álex Rins", "randy krummenache": "Randy Krummenacher",
         "jarno vd marel": "Jarno van der Marel", "jarno van der marel": "Jarno van der Marel",
         "kenny roberts jr": "Kenny Roberts Jr.", "david de gea": "José David de Gea", "georg froehlich": "Georg Fröhlich",
         "eric hubsch": "Eric Hübsch", "eric huebsch": "Eric Hübsch", "robin lasser": "Robin Lässer", "robin laesser": "Robin Lässer",
         "adri": "Adri den Bekker", "adri den bekker": "Adri den Bekker", "thierry vd bosch": "Thierry van den Bosch",
         "henk vd lagemaat": "Henk van de Lagemaat", "patrick vd waarsenburg": "Patrick van de Waarsenburg",
         "chirstophe rastel": "Christophe Rastel", "noboyuki ohsaki": "Nobuyuki Ohsaki", "blake leigh-smith": "Blake Leigh-Smith"}
NAT_FIX = {"Adri den Bekker": "NL"}
ALIAS.update({"norick abe": "Norifumi Abe", "jurgen vd goorbergh": "Jurgen van den Goorbergh", "jean michel bayle": "Jean-Michel Bayle"})
ALIAS.update({"apiwat wongthananon": "Apiwath Wongthananon", "joshua hook": "Josh Hook", "juanfran guevara": "Juan Francisco Guevara",
              "maximillian kappler": "Maximilian Kappler", "xavi fores": "Javier Forés", "philipp oettl": "Philipp Öttl",
              "hikari ookubo": "Hikari Okubo", "zonta vd goorbergh": "Zonta van den Goorbergh"})
ALIAS.update({"alfonso gonzalez nieto": "Fonsi Nieto", "alfonso gonzalez": "Fonsi Nieto", "alfonso nieto": "Fonsi Nieto",
    "daijiro katoh": "Daijiro Kato", "jascha buch": "Jascha Buech", "jason disalvo": "Jason Di Salvo", "jesus perez g": "Jesús Perez",
    "john mcguinnes": "John McGuinness", "john mcguinness": "John McGuinness", "johnny wickstroem": "Johnny Wickström",
    "jurgen van": "Jurgen van den Goorbergh", "lucas oliver bulto": "Lucas Oliver", "kuang meng heng": "Meng Heng Kuan",
    "nobuyuki osaki": "Nobuyuki Ohsaki", "noboiuki wakai": "Nobuyuki Wakai", "patrick vd goorbergh": "Patrick van den Goorbergh",
    "peter oettl": "Peter Öttl", "s. prein": "Stefan Prein", "niggi schmassman": "Nicholas Schmassmann",
    "suhathai chamsub": "Suhathai Chaemsap", "yuzy shahrol": "Shahrol Yuzy"})
NAT_FIX.update({"Bohumil Stasa": "CZ", "Enrique de Juan": "ES", "Stefan Prein": "DE"})
ALIAS.update({"hideyuki nakajo": "Hideyuki Nakajoh", "luis maurel": "Luis Carlos Maurel", "yasumasa hatakeyama": "Yasu Hatakeyama"})
ALIAS.update({"armando ericco": "Armando Errico", "bent slydal": "Bengt Slydal", "dimitris papandreou": "Dimitrios Papandreou",
    "fernando gonzales de n.": "Fernando González de Nicolás", "fernando gonzales de n": "Fernando González de Nicolás",
    "fernando gonzalez de nicolas": "Fernando González de Nicolás", "gabriel gabria": "Gabriel Grabia", "georg jung": "Georg-Robert Jung",
    "george looijensteijn": "George Looijesteijn", "george looijesteyn": "George Looijesteijn", "george looijestyn": "George Looijesteijn",
    "peter looijensteijn": "Peter Looijesteijn", "peter looijestein": "Peter Looijesteijn", "gerold fisher": "Gerold Fischer",
    "graeme mcgregoer": "Graeme McGregor", "graeme mcgregor": "Graeme McGregor", "herbert bessendorfer": "Herbert Besendorfer",
    "herbert haul": "Herbert Hauf", "jacky hutteau": "Jacques Hutteau", "jan olof odeholm": "Jan-Olof Odeholm",
    "jean-claude selini": "Jean Claude Selini", "jean-philippe ruggia": "Jean Philippe Ruggia", "jikka jaakkola": "Ilkka Jaakkola",
    "johan auer": "Johann Auer", "jussi hautanimi": "Jussi Hautaniemi", "lars-erik kallesoe": "Lars-Erik Kallesö",
    "leandro beccheroni": "Leandro Becheroni", "bojan miklos": "Miklos Bojan", "niel robinson": "Neil Robinson",
    "paul tinker": "Paul Tinkler", "per-edward carlson": "Per Edward Carlsson", "peter somer": "Peter Sommer",
    "pierpaolo bianchi": "Pier Paolo Bianchi", "svend andersson": "Svend Andersen", "thomas moller-pedersen": "Thomas Møller-Pedersen",
    "walter magliorati": "Walter Migliorati", "zbynek havdra": "Zbyněk Havrda", "titer balaz": "Peter Balaz",
    "rolf ruttimann†": "Rolf Rüttimann", "maurice coq": "Maurice Coq", "jonnie ekerold": "Jon Ekerold"})
ALIAS.update({"franck gross": "Frank Gross", "graeme geddes": "Greame Geddes", "mar schouten": "Marc Schouten", "peter verbic": "P. Verbic",
              "zdravko ljeljak": "Z. Ljeljak"})
ALIAS.update({"michel frutschi†": "Michel Frutschi", "adu celso": "Adu Celso-Santos", "f. granon": "Francois Granon", "gyula marsovsky": "Gyula Marsovszky",
    "j.f. lecureux": "Jean Francois Lecureux", "j.t. findlay": "Jack Findlay", "jean vivesse bordons": "Juan Bordons", "j. bordens vives": "Juan Bordons",
    "m. cortes": "Miguel Cortes", "patrick herouard": "P. Herouard", "peter ruttjeroth": "P. Rüttjeroth", "stefan janssen": "S. Janssen",
    "paul eickleberg": "Paul Eickelberg", "ted jansen": "Ted Janssen", "per edvard carlsson": "Per Edward Carlsson",
    "pierluigi conforti": "Pier Luigi Conforti", "piet vd goorbergh": "Piet van den Goorbergh", "w. mccosh": "Billy McCosh",
    "yves le tourmelin": "Yves le Toumelin", "william-a smith": "Bill Smith"})
ALIAS.update({"carlo ubbialia": "Carlo Ubbiali", "cecyl sandford": "Cecil Sandford", "fritz masserli": "Fritz Messerli",
    "hans gunter jaeger": "Hans-Günter Jäger", "hans-gunther jager": "Hans-Günter Jäger", "jaques collot": "Jacques Collot",
    "joop vegelzang": "Joop Vogelzang", "jose antonio elizalde": "Antonio Elizalde", "juan bertrand": "Juan Bertran",
    "mike duff": "Michelle Duff", "nikolaj sevastyanov": "Nikolai Sevostianov", "rudolf glaeser": "Rudolf Gläser",
    "rudolf schmalzle": "Rudolf Schmälzle", "rudolf schmalze": "Rudolf Schmälzle", "shimazaki sadao": "Sadao Shimazaki",
"horoshi hasegawa": "Hiroshi Hasegawa", "bob mcintyre": "Bob McIntyre", "iean noel burne": "Jean Noel Burne",
    "kuninitsu takahashi": "Kunimitsu Takahashi"})
ALIAS.update({"walter zeller †": "Walter Zeller", "jean-pierre bayle": "Jean Pierre Bayle", "robin fitton": "Rob Fitton",
    "derek powell": "D.T. Powell", "malcolm templeton": "M. Templeton", "george catlin": "G.A. Catlin", "maurice low": "Morry Low",
    "harald karlsson": "H. Karlsson", "casper swart": "Cas Swart", "john grace": "Johnny Grace", "frantisek stastny": "Franta Stastny",
    "syd mizen": "Sid Mizen", "ladislaus richter": "Ladi Richter", "malcolm stanton": "Malcom Stanton", "len atlee": "Leonard Atlee",
    "osmo hansen": "O. Hansen", "alan lawton": "A.T. Lawton"})
UUID_FIX = {"9cb1d90f-bcca-4e81-90ed-59d97b857bb3": ("kenny-roberts", "Kenny Roberts", "US")}
SPLITLOG = []
ID_FIX = {"marc2 garcia": ("marc-garcia-fr", "Marc Garcia", "FR")}
KEYLOG = []

class Resolver:
    def __init__(self):
        self.riders = list(csv.DictReader(open(R + 'riders.csv', encoding='utf-8-sig')))
        for r in self.riders:
            for c in ("birth_date", "birthplace", "api_id"):
                r.setdefault(c, "")
        self.by_api = {r['api_id']: r['id'] for r in self.riders if r.get('api_id')}
        self.by_name = {fold(r['name_en']): r['id'] for r in self.riders if r.get('name_en')}
        self.by_key = {}
        for r in self.riders:
            if r.get('name_en'):
                self.by_key.setdefault(key(r['name_en']), []).append(r['id'])
        self.ids = {r['id'] for r in self.riders}
        self.nat = {r['id']: r.get('nationality', '') for r in self.riders}
        self.new = {}   # id -> dict(name_en, nat)

    INFO = None
    def differ(self, u1, u2):
        """公式の生年月日が両方あり、異なる場合のみ別人とみなす"""
        if Resolver.INFO is None:
            from gindex import build
            Resolver.INFO = build()[1]
        b1 = (Resolver.INFO.get(u1) or {}).get("birth_date"); b2 = (Resolver.INFO.get(u2) or {}).get("birth_date")
        return bool(b1 and b2 and b1 != b2)

    def api_of(self, rid):
        for k, v in self.by_api.items():
            if v == rid: return k
        return None

    def get(self, name, uuid=None, nat=""):
        if uuid and uuid in self.by_api:
            return self.by_api[uuid]
        fx = UUID_FIX.get(uuid) or ID_FIX.get(fold(name).strip())
        if fx:
            rid, n2, nt = fx
            if rid not in self.ids:
                self.new[rid] = dict(id=rid, name_en=n2, nat=nat_ja(nt)); self.ids.add(rid); self.nat[rid] = nat_ja(nt)
            if uuid: self.by_api[uuid] = rid
            return rid
        name = name.replace("†", "").strip()
        n = ALIAS.get(fold(name).strip().rstrip("."), name)
        nat = NAT_FIX.get(n, nat)
        rid = self.by_name.get(fold(n))
        if rid and uuid and self.api_of(rid) and self.api_of(rid) != uuid and self.differ(self.api_of(rid), uuid):
            # 同名の別人（親子など）：公式IDが異なる
            SPLITLOG.append((n, rid, uuid)); rid = None
        if not rid:
            ks = [k for k in self.by_key.get(key(n), []) if not nat or not self.nat.get(k) or self.nat.get(k) == nat_ja(nat)]
            if len(ks) == 1 and KEYLOG is not None:
                KEYLOG.append((n, ks[0]))   # 候補のみ記録（自動では統合しない）
        if not rid:
            n = re.sub(r"([-'])([a-z])", lambda m: m.group(1) + m.group(2).upper(), n)
            rid = slug(n)
            if rid in self.ids and rid not in self.new:
                rid = rid + '-2'
            if rid not in self.new and rid not in self.ids:
                self.new[rid] = dict(id=rid, name_en=n, nat=nat_ja(nat)); self.nat[rid] = nat_ja(nat)
                self.ids.add(rid); self.by_name[fold(n)] = rid
                self.by_key.setdefault(key(n), []).append(rid)
        if uuid:
            self.by_api[uuid] = rid
        return rid
