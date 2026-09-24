"""公式リザルトPDF（text化済み）の決勝結果を解析"""
import re
NATIONS = ("ITA SPA ESP JPN FRA GER USA GBR CZE AUS HUN RSM SMR NED SWI SUI BRA ARG FIN SWE COL CHN MAL THA AUT SVK SLO POR "
           "INA CAN BEL DEN NOR RSA ZAF NZL MEX VEN POL CRO IRL RUS UKR EST LAT LTU IND AND ISR KOR PHI QAT TUR TPE HKG SIN "
           "UAE YUG RHO GDR FRG URS TCH CHI PER URU ECU CUB MON LUX GRE BUL ROM ROU EGY MAR ALG KEN IRI KSA BHR SRB MNE BIH "
           "MKD CYP MLT ISL LIE KAZ UZB GEO ARM AZE PAN CRC GUA DOM PUR TRI JAM BAH BAR NCA HON ESA BOL PAR VIE CAM MYA PAK "
           "SRI BAN NEP MGL PRK LBN SYR JOR IRQ KUW OMA YEM TUN LBA SUD ETH NGR GHA CIV SEN CMR ZIM ZAM MOZ NAM BOT ANG").split()
NAT_RE = "|".join(NATIONS)
LINE = re.compile(r"^\s*(?:(\d+)\s+)?(?:(\d+(?:\.\d)?)\s+)?(\d+)\s+(\S.*?)\s+(" + NAT_RE + r")\s+(\S.*?)\s{2,}([A-Z][A-Za-z0-9 \-\.&/']*?[A-Za-z0-9])(?:\s{2,}|\s*$)")
SECTIONS = [("not classified", "DNF"), ("not finished first lap", "DNF"), ("not starting", "DNS"),
            ("not started", "DNS"), ("excluded", "EXC"), ("disqualified", "DSQ"), ("did not start", "DNS")]

def parse(text):
    rows, status, started = [], "FIN", False
    for ln in text.splitlines():
        low = ln.strip().lower()
        if low.startswith("pos") and "rider" in low:
            started = True; continue
        if not started: continue
        for k, v in SECTIONS:
            if low.startswith(k):
                status = v; break
        else:
            if low.startswith("the results are provisional") or low.startswith("fastest lap") or low.startswith("most laps"):
                break
            m = LINE.match(ln)
            if not m: continue
            pos, pts, num, name, nat, team, moto = m.groups()
            if status == "FIN" and not pos: continue
            rows.append(dict(pos=int(pos) if (pos and status == "FIN") else None,
                             points=float(pts) if (pts and status == "FIN") else 0.0,
                             number=int(num), name=name.strip(), nation=nat, team=team.strip(),
                             moto=moto.strip(), status=status))
    return rows
