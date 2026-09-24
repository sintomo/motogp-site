# -*- coding: utf-8 -*-
"""表記の対応表（国・グランプリ・メーカー）"""
ISO2 = {"IT": "イタリア", "ES": "スペイン", "JP": "日本", "FR": "フランス", "DE": "ドイツ", "US": "米国", "GB": "英国",
        "CZ": "チェコ", "AU": "豪州", "HU": "ハンガリー", "SM": "サンマリノ", "NL": "オランダ", "CH": "スイス", "BR": "ブラジル",
        "AR": "アルゼンチン", "FI": "フィンランド", "SE": "スウェーデン", "CO": "コロンビア", "CN": "中国", "MY": "マレーシア",
        "TH": "タイ", "AT": "オーストリア", "SK": "スロバキア", "SI": "スロベニア", "PT": "ポルトガル", "ID": "インドネシア",
        "CA": "カナダ", "BE": "ベルギー", "DK": "デンマーク", "NO": "ノルウェー", "ZA": "南アフリカ", "NZ": "ニュージーランド",
        "MX": "メキシコ", "VE": "ベネズエラ", "PL": "ポーランド", "HR": "クロアチア", "IE": "アイルランド", "RU": "ロシア",
        "UA": "ウクライナ", "EE": "エストニア", "LV": "ラトビア", "LT": "リトアニア", "IN": "インド", "AD": "アンドラ",
        "IL": "イスラエル", "KR": "韓国", "PH": "フィリピン", "QA": "カタール", "TR": "トルコ", "TW": "台湾", "HK": "香港",
        "SG": "シンガポール", "AE": "アラブ首長国連邦", "RS": "セルビア", "YU": "ユーゴスラビア", "ZW": "ジンバブエ",
        "RH": "ローデシア", "CL": "チリ", "PE": "ペルー", "UY": "ウルグアイ", "EC": "エクアドル", "CU": "キューバ",
        "MC": "モナコ", "LU": "ルクセンブルク", "GR": "ギリシャ", "BG": "ブルガリア", "RO": "ルーマニア", "EG": "エジプト",
        "MA": "モロッコ", "KE": "ケニア", "IR": "イラン", "SA": "サウジアラビア", "BH": "バーレーン", "CY": "キプロス",
        "MT": "マルタ", "IS": "アイスランド", "LI": "リヒテンシュタイン", "KZ": "カザフスタン", "GT": "グアテマラ",
        "DO": "ドミニカ共和国", "PR": "プエルトリコ", "JM": "ジャマイカ", "VN": "ベトナム", "PK": "パキスタン",
        "SU": "ソ連", "DD": "東ドイツ", "CS": "チェコスロバキア", "GE": "ジョージア", "BO": "ボリビア", "PY": "パラグアイ",
        "CR": "コスタリカ", "PA": "パナマ", "SV": "エルサルバドル", "AM": "アルメニア", "BA": "ボスニア・ヘルツェゴビナ",
        "MK": "北マケドニア", "ME": "モンテネグロ", "NG": "ナイジェリア", "SN": "セネガル", "TN": "チュニジア", "DZ": "アルジェリア"}
IOC = {"ITA": "IT", "SPA": "ES", "ESP": "ES", "JPN": "JP", "FRA": "FR", "GER": "DE", "USA": "US", "GBR": "GB", "CZE": "CZ",
       "AUS": "AU", "HUN": "HU", "RSM": "SM", "SMR": "SM", "NED": "NL", "SWI": "CH", "SUI": "CH", "BRA": "BR", "ARG": "AR",
       "FIN": "FI", "SWE": "SE", "COL": "CO", "CHN": "CN", "MAL": "MY", "THA": "TH", "AUT": "AT", "SVK": "SK", "SLO": "SI",
       "POR": "PT", "INA": "ID", "CAN": "CA", "BEL": "BE", "DEN": "DK", "NOR": "NO", "RSA": "ZA", "ZAF": "ZA", "NZL": "NZ",
       "MEX": "MX", "VEN": "VE", "POL": "PL", "CRO": "HR", "IRL": "IE", "RUS": "RU", "UKR": "UA", "EST": "EE", "LAT": "LV",
       "LTU": "LT", "IND": "IN", "AND": "AD", "ISR": "IL", "KOR": "KR", "PHI": "PH", "QAT": "QA", "TUR": "TR", "TPE": "TW",
       "HKG": "HK", "SIN": "SG", "UAE": "AE", "YUG": "YU", "RHO": "RH", "GDR": "DD", "FRG": "DE", "URS": "SU", "TCH": "CS",
       "CHI": "CL", "PER": "PE", "URU": "UY", "ECU": "EC", "CUB": "CU", "MON": "MC", "LUX": "LU", "GRE": "GR", "BUL": "BG",
       "ROM": "RO", "ROU": "RO", "EGY": "EG", "MAR": "MA", "KEN": "KE", "IRI": "IR", "KSA": "SA", "BHR": "BH", "SRB": "RS",
       "CYP": "CY", "MLT": "MT", "ISL": "IS", "LIE": "LI", "KAZ": "KZ", "ZIM": "ZW"}

def nat_ja(code):
    if not code: return ""
    code = code.upper()
    if len(code) == 3: code = IOC.get(code, code)
    return ISO2.get(code, code)

GP = {"SPA": "スペインGP", "JPN": "日本GP", "RSA": "南アフリカGP", "FRA": "フランスGP", "ITA": "イタリアGP",
      "CAT": "カタルーニャGP", "NED": "オランダTT", "GBR": "イギリスGP", "GER": "ドイツGP", "CZE": "チェコGP",
      "POR": "ポルトガルGP", "RIO": "リオGP", "PAC": "パシフィックGP", "MAL": "マレーシアGP", "AUS": "オーストラリアGP",
      "VAL": "バレンシアGP", "QAT": "カタールGP", "CHN": "中国GP", "TUR": "トルコGP", "USA": "アメリカズGP",
      "RSM": "サンマリノGP", "INP": "インディアナポリスGP", "AMS": "アメリカズGP", "ARA": "アラゴンGP", "ARG": "アルゼンチンGP",
      "AUT": "オーストリアGP", "THA": "タイGP", "EUR": "ヨーロッパGP", "STY": "シュタイアーマルクGP", "ANC": "アンダルシアGP",
      "EMI": "エミリア・ロマーニャGP", "TER": "テルエルGP", "DOH": "ドーハGP", "ALR": "アルガルヴェGP", "INA": "インドネシアGP",
      "IND": "インドGP", "KAZ": "カザフスタンGP", "HUN": "ハンガリーGP", "SOL": "ソリダリティGP", "BRA": "ブラジルGP",
      "BEL": "ベルギーGP", "SWE": "スウェーデンGP", "FIN": "フィンランドGP", "AUT": "オーストリアGP", "YUG": "ユーゴスラビアGP",
      "IOM": "マン島TT", "ULS": "アルスターGP", "NAT": "ネイションズGP", "CSK": "チェコスロバキアGP", "VEN": "ベネズエラGP",
      "ARG": "アルゼンチンGP", "SAL": "ザルツブルクGP", "DDR": "東ドイツGP", "EST": "エステルライヒGP", "CAN": "カナダGP",
      "MEX": "メキシコGP", "SUI": "スイスGP", "LEM": "ル・マンGP", "YOR": "ヨーロッパGP", "BUE": "ブエノスアイレスGP"}
# 年代でアメリカGPの呼び名が異なるので year で調整
def gp_ja(code, name, year):
    if code == "USA" and year < 2013: return "アメリカGP"
    if code == "GER" and year < 1991 and "WEST" in (name or "").upper(): return "西ドイツGP"
    return GP.get(code) or (name or code).title()

MAKER = {"honda": "ホンダ", "yamaha": "ヤマハ", "suzuki": "スズキ", "kawasaki": "カワサキ", "ducati": "ドゥカティ",
         "aprilia": "アプリリア", "ktm": "KTM", "mv agusta": "MVアグスタ", "gilera": "ジレラ", "kalex": "カレックス",
         "derbi": "デルビ", "proton kr": "プロトンKR", "kr211v": "プロトンKR", "kr212v": "プロトンKR", "moriwaki": "モリワキ",
         "md211vf proto": "モリワキ", "wcm": "WCM", "harris wcm": "WCM", "blata": "ブラタ", "ilmor x3": "イルモア", "ilmor": "イルモア",
         "bmw": "BMW", "suter": "ズッター", "speed up": "スピードアップ", "boscoscuro": "ボスコスクーロ", "tech 3": "テック3",
         "motobi": "モトビ", "ftr": "FTR", "mz": "MZ", "husqvarna": "ハスクバーナ", "mahindra": "マヒンドラ", "gasgas": "ガスガス",
         "gas gas": "ガスガス", "cfmoto": "CFMoto", "malaguti": "マラグーティ", "loncin": "ローンチン", "italjet": "イタルジェット",
         "fantic": "ファンティック", "seel": "セール", "haojue": "ハオジュエ", "sabre v4": "セイバー", "roc yamaha": "ROCヤマハ",
         "tsr": "TSR", "fgr": "FGR", "friba": "フリバ"}
NEW_MAKERS = [["マラグーティ", "malaguti", "イタリア", "#5a7d2b", "125ccに参戦したイタリアのメーカー"],
              ["ローンチン", "loncin", "中国", "#b0302a", "中国のメーカー。2000年代に125ccへ参戦"],
              ["イタルジェット", "italjet", "イタリア", "#2a6fb0", "イタリアのメーカー。125ccに参戦"],
              ["ファンティック", "fantic", "イタリア", "#e05a1a", "イタリアのメーカー"],
              ["セール", "seel", "—", "#777777", "公式リザルト上の表記「Seel」"],
              ["ハオジュエ", "haojue", "中国", "#aa2233", "中国のメーカー"],
              ["セイバー", "sabre", "英国", "#556677", "公式リザルト上の表記「Sabre V4」"],
              ["ROCヤマハ", "roc-yamaha", "フランス", "#3a5f9e", "ROC製車体にヤマハのエンジン"],
              ["TSR", "tsr", "日本", "#224488", "テクニカル・スポーツ・レーシング（鈴鹿）"],
              ["FGR", "fgr", "—", "#666666", "公式リザルト上の表記「FGR」"],
              ["フリバ", "friba", "—", "#888888", "公式リザルト上の表記「Friba」"]]

MAKER.update({"pons kalex": "ポンス・カレックス", "i.c.p.": "ICP", "rsv": "RSV", "bimota": "ビモータ", "promoharris": "プロモハリス",
    "adv": "ADV", "bqr-moto2": "BQR", "bqr": "BQR", "bqr-ftr": "BQR-FTR", "force gp210": "フォースGP210", "mz-re honda": "MZ",
    "mz ftr": "MZ-FTR", "ajr": "AJR", "mir racing": "MIRレーシング", "mir honda": "MIRホンダ", "rbb": "RBB", "lambretta": "ランブレッタ",
    "ten kate": "テンケイト", "tsr 6": "TSR", "art": "ART", "ioda": "イオダ", "ioda-suter": "イオダ・ズッター", "apr": "APR", "bcl": "BCL",
    "inmotec": "インモテック", "ftr honda": "FTRホンダ", "kalex ktm": "カレックスKTM", "suter honda": "ズッターホンダ",
    "tsr honda": "TSRホンダ", "oral": "オラル", "fgr honda": "FGRホンダ", "krp honda": "KRPホンダ", "ftr kawasaki": "FTRカワサキ",
    "pbm": "PBM", "s&b suter": "S&Bズッター", "mistral 610": "テック3", "transfiormers": "トランスフォーマーズ",
    "transformiers": "トランスフォーマーズ", "tech3": "テック3", "bakker honda": "バッカーホンダ", "bullet": "ブレット",
    "forward yamaha": "フォワード・ヤマハ", "yamaha forward": "フォワード・ヤマハ", "avintia": "アビンティア", "forward klx": "フォワードKLX",
    "caterham suter": "ケータハム・ズッター", "taylor made": "テイラーメイド", "nts": "NTS", "ftr ktm": "FTR KTM", "tvr": "TVR",
    "peugeot": "プジョー", "tm racing": "TM", "tm": "TM", "energica": "エネルジカ", "forward": "フォワード", "iamt": "IAMT",
    "triumph": "トライアンフ", "mv agusta": "MVアグスタ"})
_NEW2 = [("ポンス・カレックス","pons-kalex","スペイン/ドイツ","公式表記「Pons Kalex」（2010〜11年Moto2）"),("ICP","icp","イタリア","公式表記「I.C.P.」"),
 ("RSV","rsv","—","公式表記「RSV」"),("ビモータ","bimota","イタリア","イタリアのコンストラクター。Moto2に参戦"),("プロモハリス","promoharris","英国","公式表記「Promoharris」"),
 ("ADV","adv","—","公式表記「ADV」"),("BQR","bqr","スペイン","ブルー・ミッショネス／BQR（CRT・Moto2）"),("BQR-FTR","bqr-ftr","スペイン","公式表記「BQR-FTR」"),
 ("フォースGP210","force-gp210","—","公式表記「Force GP210」"),("MZ-FTR","mz-ftr","—","公式表記「MZ FTR」"),("AJR","ajr","スペイン","公式表記「AJR」"),
 ("MIRレーシング","mir-racing","スペイン","公式表記「MIR Racing」"),("MIRホンダ","mir-honda","スペイン","公式表記「MIR Honda」"),("RBB","rbb","—","公式表記「RBB」"),
 ("ランブレッタ","lambretta","イタリア","2010年125ccに参戦"),("テンケイト","ten-kate","オランダ","公式表記「Ten Kate」"),("ART","art","イタリア","アプリリア・レーシング・テクノロジー（CRT、RSV4ベース）"),
 ("イオダ","ioda","イタリア","公式表記「Ioda」"),("イオダ・ズッター","ioda-suter","イタリア/スイス","公式表記「Ioda-Suter」"),("APR","apr","—","公式表記「APR」"),
 ("BCL","bcl","—","公式表記「BCL」"),("インモテック","inmotec","スペイン","公式表記「Inmotec」"),("FTRホンダ","ftr-honda","英国/日本","公式表記「FTR Honda」"),
 ("カレックスKTM","kalex-ktm","ドイツ/オーストリア","公式表記「Kalex KTM」（2012〜13年Moto3）"),("ズッターホンダ","suter-honda","スイス/日本","公式表記「Suter Honda」"),
 ("TSRホンダ","tsr-honda","日本","公式表記「TSR Honda」"),("オラル","oral","イタリア","公式表記「Oral」"),("FGRホンダ","fgr-honda","—","公式表記「FGR Honda」"),
 ("KRPホンダ","krp-honda","英国","公式表記「KRP Honda」"),("FTRカワサキ","ftr-kawasaki","英国/日本","公式表記「FTR Kawasaki」（CRT）"),("PBM","pbm","英国","ポール・バード・モータースポーツ（CRT）"),
 ("S&Bズッター","sb-suter","—","公式表記「S&B Suter」"),("トランスフォーマーズ","transfiormers","—","公式表記「Transfiormers」"),("バッカーホンダ","bakker-honda","オランダ","公式表記「Bakker Honda」"),
 ("ブレット","bullet","—","公式表記「Bullet」"),("フォワード・ヤマハ","forward-yamaha","スイス/日本","公式表記「Forward Yamaha」（Open）"),("アビンティア","avintia","スペイン","公式表記「Avintia」（CRT）"),
 ("フォワードKLX","forward-klx","スイス","公式表記「Forward KLX」"),("ケータハム・ズッター","caterham-suter","マレーシア/スイス","公式表記「Caterham Suter」"),("テイラーメイド","taylor-made","—","公式表記「Taylor Made」"),
 ("NTS","nts","日本","NTSのMoto2シャシー"),("FTR KTM","ftr-ktm","英国/オーストリア","公式表記「FTR KTM」"),("TVR","tvr","—","公式表記「TVR」"),("プジョー","peugeot","フランス","Moto3に参戦（2016〜17年）"),
 ("TM","tm","イタリア","TMレーシング"),("エネルジカ","energica","イタリア","MotoE（2019〜22年）のワンメイク車両"),("フォワード","forward","スイス","フォワード・レーシングのMoto2シャシー"),
 ("IAMT","iamt","—","公式表記「IAMT」"),("トライアンフ","triumph","英国","Moto2のエンジン供給（2019年〜）")]
NEW_MAKERS += [[a, b, c, "#888888", d] for a, b, c, d in _NEW2]
GP.update({"AME": "アメリカズGP"})

def maker_ja(name):
    if not name: return ""
    k = name.split("  ")[0].strip().lower()
    return MAKER.get(k, "")

MAKER.update({"cagiva": "カジバ", "roc yamaha": "ROCヤマハ", "roc-yamaha": "ROCヤマハ", "roc": "ROCヤマハ", "harris yamaha": "ハリス・ヤマハ",
    "harris-yamaha": "ハリス・ヤマハ", "tsr-honda": "TSRホンダ", "modenas kr3": "モデナスKR3", "modenas": "モデナスKR3",
    "jj cobas": "JJコバス", "jj": "JJコバス", "paton": "パトン", "gazzaniga": "ガッツァニーガ", "rieju": "リエフ", "elf 500": "ELF",
    "elf": "ELF", "muz weber": "MuZ", "muz": "MuZ", "rotax": "ロータックス", "librenti": "リブレンティ", "pulse": "パルス",
    "erp honda": "ERPホンダ", "casal": "カザル", "t.s.": "T.S.", "rumi": "ルミ", "plaisir": "プレジール", "vrp": "VRP", "agv": "AGV",
    "chevallier": "シュヴァリエ", "emc-honda": "EMCホンダ", "norton": "ノートン", "yamaha-bartol": "ヤマハ・バルトル", "maico": "マイコ",
    "tohatsu": "トーハツ", "johnson yamaha": "ジョンソン・ヤマハ"})
_NEW3 = [("カジバ", "cagiva", "イタリア", "#c8102e", "1980〜90年代の500ccに参戦したイタリアのメーカー"),
 ("ハリス・ヤマハ", "harris-yamaha", "英国", "#556b8f", "ハリス製車体にヤマハのエンジン（公式表記「Harris Yamaha」）"),
 ("モデナスKR3", "modenas-kr3", "マレーシア/米国", "#6b4f2a", "チームKRの3気筒500cc（公式表記「Modenas KR3」）"),
 ("JJコバス", "jj-cobas", "スペイン", "#b5651d", "スペインのコンストラクター"), ("パトン", "paton", "イタリア", "#8b0000", "イタリアの小規模メーカー"),
 ("ガッツァニーガ", "gazzaniga", "イタリア", "#777777", "公式表記「Gazzaniga」"), ("リエフ", "rieju", "スペイン", "#777777", "公式表記「Rieju」"),
 ("ELF", "elf", "フランス", "#1f4e9e", "エルフの500cc実験車"), ("MuZ", "muz", "ドイツ", "#3a5a3a", "旧MZ。公式表記「Muz Weber」など"),
 ("ロータックス", "rotax", "オーストリア", "#777777", "公式表記「Rotax」"), ("リブレンティ", "librenti", "イタリア", "#777777", "公式表記「Librenti」"),
 ("パルス", "pulse", "英国", "#777777", "公式表記「Pulse」"), ("ERPホンダ", "erp-honda", "—", "#777777", "公式表記「ERP Honda」"),
 ("カザル", "casal", "ポルトガル", "#777777", "公式表記「Casal」"), ("T.S.", "ts", "—", "#777777", "公式表記「T.S.」"), ("ルミ", "rumi", "イタリア", "#777777", "公式表記「Rumi」"),
 ("プレジール", "plaisir", "—", "#777777", "公式表記「Plaisir」"), ("VRP", "vrp", "—", "#777777", "公式表記「VRP」"), ("AGV", "agv", "イタリア", "#777777", "公式表記「AGV」"),
 ("シュヴァリエ", "chevallier", "フランス", "#777777", "公式表記「Chevallier」"), ("EMCホンダ", "emc-honda", "—", "#777777", "公式表記「EMC-Honda」"),
 ("ノートン", "norton", "英国", "#333333", "英国の名門"), ("ヤマハ・バルトル", "yamaha-bartol", "—", "#777777", "公式表記「Yamaha-Bartol」"),
 ("マイコ", "maico", "ドイツ", "#777777", "ドイツのメーカー"), ("トーハツ", "tohatsu", "日本", "#777777", "日本のメーカー"),
 ("ジョンソン・ヤマハ", "johnson-yamaha", "—", "#777777", "公式表記「Johnson Yamaha」")]
NEW_MAKERS += [[a, b, c, col, d] for a, b, c, col, d in _NEW3]
GP.update({"NAT": "ネイションズGP", "WGER": "西ドイツGP", "JUG": "ユーゴスラビアGP", "TCH": "チェコスロバキアGP", "VDU": "ヴィテス・デュ・マンGP",
           "EUR": "ヨーロッパGP", "FIM": "FIM GP", "BRA": "ブラジルGP", "MAD": "マドリードGP", "IMO": "イモラGP", "RIO": "リオGP",
           "INA": "インドネシアGP", "SWE": "スウェーデンGP", "HUN": "ハンガリーGP", "BEL": "ベルギーGP", "AUT": "オーストリアGP"})

# 車名（型式）→ メーカー
MODEL = [(r"^(RG|RGV|RGB|XR)\d*", "スズキ"), (r"^(YZR|TZ|OW)\d*", "ヤマハ"), (r"^(NS|NSR|RS|NR)\d+", "ホンダ"), (r"^KR\d+", "カワサキ"),
         (r"^C\d{3}", "カジバ"), (r"^GP500$", "カジバ")]
MAKER.update({"kobas-rotax": "JJコバス", "cobas-rotax": "JJコバス", "cobas": "JJコバス", "kobas": "JJコバス", "zundapp": "ツェンダップ", "zündapp": "ツェンダップ",
    "garelli": "ガレリ", "bultaco": "ブルタコ", "motul bultaco": "ブルタコ", "kreidler": "クライドラー", "kreidler van veen": "クライドラー",
    "krauser": "クラウザー", "morbidelli": "モルビデリ", "mba": "MBA", "chevallier-yamaha": "シュヴァリエ", "elf-honda": "ELF",
    "fior-rs500": "フィオール", "fior": "フィオール", "elf5-rs500": "ELF", "real-rotax": "リアル", "real": "リアル", "bakker-ns500": "ホンダ",
    "ns500/nsr500": "ホンダ", "emc-rotax": "EMC", "fkn-kreidler": "FKN", "huvo-casal": "カザル", "mig": "MIG"})
import re as _re
def maker_or_raw(name):
    """対応表にあれば日本語名、型式ならメーカー、なければ英字のまま"""
    m = maker_ja(name)
    if m: return m
    n = (name or "").split("  ")[0].strip()
    for pat, mk in MODEL:
        if _re.match(pat, n): return mk
    if not n or len(n) <= 1 or n.upper() in ("NED", "P", "AD", "ES", "MOTO"): return ""
    return n

MAKER.update({"motobécane": "Motobecane", "siroko rotax": "Siroko", "siroko-rotax": "Siroko", "siroco": "Siroko", "rotax kobas": "JJコバス",
    "rotax real": "リアル", "massa-real": "リアル", "rotax armstrong": "Armstrong", "rotax waddon": "Waddon", "morena-rotax": "Morena",
    "monnet bartol": "Monnet", "bartol-yamaha": "Bartol", "bimota-yamaha": "ビモータ", "zanella": "Zanella"})

GP.update({"TT": "マン島TT", "EGER": "東ドイツGP", "ULST": "アルスターGP", "VEN": "ベネズエラGP", "FIN": "フィンランドGP"})

MAKER.update({"mv": "MVアグスタ", "mv agusta": "MVアグスタ", "moto guzzi": "モトグッツィ", "guzzi": "モトグッツィ", "velocette": "ヴェロセット",
    "ajs": "AJS", "arter-ajs": "AJS", "benelli": "ベネリ", "ossa": "オッサ", "könig": "ケーニッヒ", "koenig": "ケーニッヒ", "mz-re": "MZ",
    "aermacchi": "アエルマッキ", "matchless": "マッチレス", "seeley-matchless": "マッチレス", "manx": "ノートン", "bultaco": "ブルタコ",
    "jamathi": "ヤマティ", "van veen": "クライドラー", "derbi": "デルビ", "montesa": "モンテサ", "cz": "CZ", "jawa": "ヤワ", "gilera": "ジレラ"})
NEW_MAKERS += [["モトグッツィ", "moto-guzzi", "イタリア", "#8a1c1c", "1950年代の350ccで活躍したイタリアのメーカー"],
               ["ヴェロセット", "velocette", "英国", "#333333", "英国の名門。1949〜50年の350cc王者"],
               ["AJS", "ajs", "英国", "#333333", "1949年の500cc王者メーカー"], ["ベネリ", "benelli", "イタリア", "#1b5e20", "イタリアのメーカー"],
               ["ケーニッヒ", "koenig", "ドイツ", "#555555", "ドイツの水平対向エンジンのメーカー"], ["アエルマッキ", "aermacchi", "イタリア", "#555555", "イタリアのメーカー（ハーレーダビッドソン傘下）"],
               ["マッチレス", "matchless", "英国", "#333333", "英国のメーカー"], ["オッサ", "ossa", "スペイン", "#555555", "スペインのメーカー"],
               ["ヤマティ", "jamathi", "オランダ", "#555555", "オランダの50ccメーカー"], ["モンテサ", "montesa", "スペイン", "#555555", "スペインのメーカー"],
               ["ヤワ", "jawa", "チェコスロバキア", "#555555", "チェコのメーカー"], ["CZ", "cz", "チェコスロバキア", "#555555", "チェコのメーカー"]]

MAKER.update({"mondial": "モンディアル", "fb mondial": "モンディアル", "nsu": "NSU", "dkw": "DKW", "morini": "モト・モリーニ", "moto morini": "モト・モリーニ",
    "parilla": "パリラ", "bsa": "BSA", "excelsior": "エクセルシオール", "tohatsu": "トーハツ", "bridgestone": "ブリヂストン", "emc": "EMC", "rumi": "ルミ"})
NEW_MAKERS += [["モンディアル", "mondial", "イタリア", "#8b0000", "1949〜51年の125cc王者メーカー"], ["NSU", "nsu", "西ドイツ", "#444444", "1950年代の125cc・250ccで活躍"],
               ["DKW", "dkw", "西ドイツ", "#444444", "ドイツのメーカー"], ["モト・モリーニ", "moto-morini", "イタリア", "#555555", "イタリアのメーカー"],
               ["パリラ", "parilla", "イタリア", "#555555", "イタリアのメーカー"], ["BSA", "bsa", "英国", "#333333", "英国のメーカー"],
               ["エクセルシオール", "excelsior", "英国", "#555555", "英国のメーカー"], ["ブリヂストン", "bridgestone", "日本", "#1c1c1c", "1960年代に参戦した日本のメーカー"]]
