# -*- coding: utf-8 -*-
"""Gera margod-readme.svg, a peca unica do README deste perfil.

As esferas atravessam a faixa acendendo as letras de MARGOD conforme passam por
cima delas; o subtitulo entra logo depois e nome + subtitulo congelam acesos,
enquanto as esferas seguem orbitando e as faixas de stack rolando.

Os pixels do wordmark e das esferas sao EXTRAIDOS de margod-banner.svg, que por
isso precisa continuar no repositorio -- este script nao redesenha o pixel art,
so o recompoe com um novo tempo e um novo layout.

Para editar a stack ou a lista de trabalhos, mexa em TECH / WORK abaixo e rode:

    python build_readme_svg.py

Saida: SVG estatico, sem webfont, sem script e sem nenhuma referencia de rede --
o proxy Camo do GitHub bloqueia recurso externo. Toda animacao e SMIL, e o SVG
foi escrito para funcionar tambem SEM ela: os elementos nascem com opacity="1",
entao se o Camo descartar o SMIL o nome aparece mesmo assim.
"""
import re

SRC = "margod-banner.svg"
OUT = "margod-readme.svg"

BG, INK, T4, T3, T2, T1 = "#0a0a0a", "#f1efe8", "#b4b2a9", "#888780", "#5f5e5a", "#3a3a3a"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, &#39;Courier New&#39;, monospace"
W = 680
LOOP = 5.0          # duracao do trajeto das esferas (igual ao banner atual)
FRAMES = LOOP * 7   # ciclo de quadros do sprite (igual ao banner atual)

# ---------------------------------------------------------------- extrair ativos
src = open(SRC, encoding="utf-8").read()


def top_groups(s, start_at=0):
    depth, out, start = 0, [], None
    for m in re.finditer(r"<(/?)g\b", s[start_at:]):
        if m.group(1) == "":
            if depth == 0:
                start = m.start() + start_at
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                out.append(s[start:m.end() + start_at + 1])
    return out


tops = top_groups(src)
letter_groups = [t for t in tops if "<animateTransform" not in t]
sphere_tracks = [t for t in tops if "<animateTransform" in t]
assert len(letter_groups) == 6 and len(sphere_tracks) == 2

# cada letra: camada de contorno (#0a0a0a) + glifo (#f1efe8), coordenadas originais
letters = []
for g in letter_groups:
    layers = [(fill, re.sub(r">\s+<", "><", inner).strip())
              for fill, inner in re.findall(r'<g fill="(#[0-9a-f]{6})"[^>]*>(.*?)</g>', g, re.S)]
    xs = [int(x) for x in re.findall(r'x="(-?\d+)"', g)]
    letters.append((min(xs) + (max(xs) + 8 - min(xs)) / 2.0, layers))
letters.sort(key=lambda p: p[0])

# esferas: camadas base + 7 quadros, cada quadro com seu animate discreto
spheres = []
for track in sphere_tracks:
    at = re.search(r'<animateTransform[^>]*values="([^"]+)"', track)
    kids = top_groups(track, track.index(">") + 1)
    parts = []
    for k in kids:
        k = re.sub(r'dur="35s"', 'dur="%gs"' % FRAMES, k)
        k = re.sub(r'begin="-1\.55s"', 'begin="0s"', k)
        parts.append(re.sub(r">\s+<", "><", k).strip())
    spheres.append((at.group(1), "".join(parts)))

# ------------------------------------------------------------------- conteudo
SUB = "SOFTWARE ENGINEER @ SOFTSAFE (MEDSAFE)  ·  CS STUDENT @ iCEV"
TECH = ["AI ENGINEERING", "LLM ORCHESTRATION", "RAG", "VECTOR DATABASES",
        "PROMPT ENGINEERING", "ANTHROPIC CLAUDE", "OPENAI", "DEEPSEEK", "OLLAMA",
        "SPEECH-TO-TEXT", "TEXT-TO-SPEECH",
        "PYTHON", "FASTAPI", "TYPESCRIPT", "REACT", "NEXT.JS",
        "JAVA", "SPRING", "ANGULAR", "SUPABASE", "POSTGRESQL", "DOCKER", "GIT"]
WORK = [
    ("2026", "SHOGUN",
     "Personal JARVIS-style voice assistant built from scratch, desktop and mobile app"),
    ("2026", "MEDSAFE / PACIENTE INTEGRADO",
     "AI transcription &amp; structured-field pipeline for clinical software"),
    ("2026", "SAFEBRAIN",
     "Company AI assistant, deployed to a VPS with PM2 + Nginx"),
    ("2026", "QA PIPELINE (iCEV)",
     "Test automation in Python: API testing with Requests, Web E2E with Selenium/Pytest, Page Objects"),
    ("2026", "PETMATCH",
     "React Native pet-matching app built with Expo, NestJS and Supabase"),
]
FOOTER = "(C) 2026 MARCUS VINICIUS  ·  TERESINA, PIAUI  ·  BRAZIL"

# --------------------------------------------------------------------- layout
HEADER_END = 212
RULE1, RULE2 = 236, 344
ROWS_Y = (262, 292, 322)
HEAD_Y = 382
ITEM0, PITCH, DESC_DY = 412, 40, 15
FOOT_Y = 622
H = 652
MX = 40                      # margem horizontal do conteudo


def txt(x, y, s, size, fill, ls=0, op=1.0, anchor="start", weight=None):
    w = ' font-weight="%s"' % weight if weight else ""
    return ('<text x="%s" y="%s" font-family="%s" font-size="%s" fill="%s" '
            'letter-spacing="%s" opacity="%s" text-anchor="%s"%s '
            'xml:space="preserve">%s</text>') % (
        x, y, MONO, size, fill, ls, op, anchor, w, s)


# ------------------------------------------------------- esferas + nome escrito
# instante em que o centro de cada esfera cruza cada letra
def cross_time(values, cx):
    a, b = [float(v.split()[0]) for v in values.split(";")]
    # centro do sprite = origem + 4 (bbox local -56..64)
    t = (cx - 4 - a) / (b - a) * LOOP
    return t


order = []
for idx, (cx, _) in enumerate(letters):
    best = min((abs(cross_time(v, cx)), cross_time(v, cx)) for v, _ in spheres)
    order.append(best[1])
REVEAL_END = max(order)
SUB_T = REVEAL_END + 0.3

sphere_svg = "".join(
    '<g transform="translate(%s)">%s'
    '<animateTransform attributeName="transform" type="translate" dur="%gs" '
    'repeatCount="indefinite" calcMode="linear" values="%s"/></g>'
    % (v.split(";")[0], body, LOOP, v)
    for v, body in spheres)


CYCLES = 2                    # quantas vezes as esferas escrevem o nome
TOTAL = LOOP * CYCLES
# Na virada do ciclo as duas esferas ficam fora de quadro ao mesmo tempo (~4,74s
# a ~5,26s). Se o nome apagasse ali, o cabecalho ficaria completamente vazio.
# Apagar so depois disso mantem sempre alguma coisa em cena.
OUT_A, OUT_B = 5.30, 5.60     # apagada entre um ciclo e o outro


def reveal(t, dur=0.35):
    """Acende em t, apaga no fim do 1o ciclo, reacende no 2o e CONGELA acesa.

    Um unico <animate> cobre os dois ciclos, entao o valor congelado e sempre 1 --
    nao depende de ordem de prioridade entre animacoes concorrentes.
    """
    k = [0.0, t / TOTAL, (t + dur) / TOTAL, OUT_A / TOTAL, OUT_B / TOTAL,
         (LOOP + t) / TOTAL, (LOOP + t + dur) / TOTAL, 1.0]
    assert k[2] < k[3] and k[4] < k[5], "ciclos se sobrepoem"
    return ('<animate attributeName="opacity" dur="%gs" repeatCount="1" fill="freeze" '
            'calcMode="linear" keyTimes="%s" values="0;0;1;1;0;0;1;1"/>'
            % (TOTAL, ";".join("%.4f" % v for v in k)))


SHINE = 7.0        # periodo da varredura de brilho
LEAD = 0.10        # respiro antes da primeira letra (keyTimes tem de ser crescente)
STEP = 0.16        # atraso de uma letra para a proxima
PEAK = 0.35        # subida ate o pico
BACK = 0.85        # volta ao tom base


def shine(i, base, peak):
    """Onda de luz percorrendo as letras da esquerda para a direita, em loop.

    So comeca depois que o nome assenta (begin=TOTAL). Como anima `fill`, o estado
    sem SMIL continua sendo o tom base -- o brilho e puro acrescimo.
    """
    t0 = LEAD + i * STEP
    k = [0.0, t0 / SHINE, (t0 + PEAK) / SHINE, (t0 + BACK) / SHINE, 1.0]
    return ('<animate attributeName="fill" begin="%gs" dur="%gs" repeatCount="indefinite" '
            'calcMode="linear" keyTimes="%s" values="%s;%s;%s;%s;%s"/>'
            % (TOTAL, SHINE, ";".join("%.4f" % v for v in k),
               base, base, peak, base, base))


# O glifo ja esta no tom mais claro da paleta, entao o unico "acima" e o branco
# puro -- um ganho pequeno. Quem faz o brilho ler e o contorno escuro clareando
# ate #3a3a3a, que vira um halo de 8px em volta de cada letra.
GLOW = {INK: "#ffffff", BG: "#3a3a3a"}      # tom base -> pico do brilho

letters_svg = "".join(
    '<g opacity="1">%s%s</g>' % (
        "".join('<g fill="%s">%s%s</g>' % (fill, inner, shine(i, fill, GLOW[fill]))
                for fill, inner in layers),
        reveal(t))
    for i, ((cx, layers), t) in enumerate(zip(letters, order)))

subtitle_svg = '<g opacity="1">%s%s</g>' % (
    txt(W / 2, 192, SUB, 10, T3, 2.6, 1.0, "middle"), reveal(SUB_T, 0.6))

# ------------------------------------------------------------- marquee da stack
CH = 7.55  # largura aproximada de um caractere monoespacado a 12.5px


def row(items, y, size, op, speed, reverse, fill):
    """speed em px/s; a duracao sai da largura, entao mexer na lista TECH nao
    altera a velocidade de rolagem."""
    run = "  —  ".join(items) + "  —  "
    width = int(len(run) * CH * size / 12.5)
    copies = "".join(
        '<text x="%d" y="%d" textLength="%d" lengthAdjust="spacing" font-family="%s" '
        'font-size="%s" fill="%s" letter-spacing="0" xml:space="preserve">%s</text>'
        % (MX + i * width, y, width, MONO, size, fill, run) for i in range(3))
    dur = width / float(speed)
    frm, to = ("%d 0" % -width, "0 0") if reverse else ("0 0", "%d 0" % -width)
    return ('<g opacity="%s">%s<animateTransform attributeName="transform" '
            'type="translate" dur="%gs" repeatCount="indefinite" calcMode="linear" '
            'values="%s;%s"/></g>') % (op, copies, dur, frm, to)


rot = lambda n: TECH[n:] + TECH[:n]
marquee = "".join([
    row(rot(0),  ROWS_Y[0], 12.5, 0.92, 47, False, INK),
    row(rot(8),  ROWS_Y[1], 12.5, 0.70, 39, True,  T4),
    row(rot(16), ROWS_Y[2], 12.5, 0.52, 43, False, T3),
])

# ----------------------------------------------------------------- trabalhos
work_svg = [txt(MX, HEAD_Y, "LATEST WORK &amp; PROJECTS", 11.5, INK, 2.4, 0.95)]
for i, (year, title, desc) in enumerate(WORK):
    y = ITEM0 + i * PITCH
    work_svg.append(txt(MX, y, "-", 11, T2, 0))
    work_svg.append(txt(MX + 16, y, "[%s] %s" % (year, title), 11, INK, 1.2, 0.92))
    work_svg.append(txt(MX + 16, y + DESC_DY, desc, 9, T2, 0.5, 1.0))
work_svg.append(txt(MX, FOOT_Y, FOOTER, 8.5, T2, 1.6, 1.0))
work_svg = "".join(work_svg)

# --------------------------------------------------------------------- montagem
mask = ('<linearGradient id="fade" gradientUnits="userSpaceOnUse" '
        'x1="%d" x2="%d" y1="0" y2="0">'
        '<stop offset="0" stop-color="#000"/><stop offset="0.10" stop-color="#fff"/>'
        '<stop offset="0.90" stop-color="#fff"/><stop offset="1" stop-color="#000"/>'
        '</linearGradient>'
        '<mask id="edges" maskUnits="userSpaceOnUse" x="%d" y="%d" width="%d" height="%d">'
        '<rect x="%d" y="%d" width="%d" height="%d" fill="url(#fade)"/></mask>'
        % (MX, W - MX, MX, RULE1, W - 2 * MX, RULE2 - RULE1,
           MX, RULE1, W - 2 * MX, RULE2 - RULE1))

svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" shape-rendering="crispEdges" role="img" aria-label="MARGOD — Marcus Vinicius, Software Engineer at Softsafe (Medsafe) and CS student at iCEV. Stack: {stack}. Latest work: {worklist}.">
  <title>MARGOD — Marcus Vinicius</title>
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <rect x="8.5" y="8.5" width="{fw}" height="{fh}" fill="none" stroke="{T1}" stroke-width="1" opacity="0.55"/>
  <defs>{mask}</defs>
  {spheres}
  {letters}
  {subtitle}
  <rect x="{MX}" y="{RULE1}" width="{cw}" height="1" fill="{T1}" opacity="0.8"/>
  <g mask="url(#edges)" shape-rendering="auto">{marquee}</g>
  <rect x="{MX}" y="{RULE2}" width="{cw}" height="1" fill="{T1}" opacity="0.8"/>
  <g shape-rendering="auto">{work}</g>
</svg>
""".format(W=W, H=H, BG=BG, T1=T1, MX=MX, cw=W - 2 * MX, fw=W - 17, fh=H - 17,
           RULE1=RULE1, RULE2=RULE2, mask=mask, spheres=sphere_svg,
           letters=letters_svg, subtitle=subtitle_svg, marquee=marquee, work=work_svg,
           stack=", ".join(t.title() for t in TECH),
           worklist="; ".join("%s (%s)" % (t.title(), y) for y, t, _ in WORK))

open(OUT, "w", encoding="utf-8", newline="\n").write(svg)
print("%s: %d bytes  %dx%d" % (OUT, len(svg.encode("utf-8")), W, H))
print("letras acendem em: %s" % ", ".join("%.2fs" % t for t in order))
print("subtitulo em %.2fs  ·  %d ciclos de escrita, congela aceso em %.0fs, brilho a cada %.0fs" % (SUB_T, CYCLES, TOTAL, SHINE))
