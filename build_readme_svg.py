# -*- coding: utf-8 -*-
"""Gera margod-readme.svg, a peca unica do README deste perfil.

A CENA
------
As duas esferas sao os "O" que ladeiam a palavra, paradas nas pontas. O nome
cresce do centro para fora, em pares simetricos:

    O          O   ->   O  R G  O   ->   O A R G O O   ->   O M A R G O D O

Isso acontece duas vezes. Na segunda, nome e subtitulo congelam acesos, as
esferas se apagam e sobra so o nome -- que dai em diante recebe uma varredura de
luz percorrendo as letras da esquerda para a direita, em loop.

OS ATIVOS
---------
Os pixels do wordmark e das esferas sao EXTRAIDOS de margod-banner.svg, que por
isso precisa continuar no repositorio -- este script nao redesenha o pixel art,
so o recompoe com um novo tempo e um novo layout.

COMO EDITAR
-----------
Mexa em TECH / WORK abaixo e rode:

    python build_readme_svg.py

SAIDA
-----
SVG estatico: sem webfont, sem script, sem nenhuma referencia de rede -- o proxy
Camo do GitHub bloqueia recurso externo. Toda animacao e SMIL, e o arquivo foi
escrito para funcionar tambem SEM ela: os elementos nascem com opacity="1", entao
se o Camo descartar o SMIL o nome aparece do mesmo jeito.
"""
import re

SRC = "margod-banner.svg"
OUT = "margod-readme.svg"

BG, INK, T4, T3, T2, T1 = "#0a0a0a", "#f1efe8", "#b4b2a9", "#888780", "#5f5e5a", "#3a3a3a"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, &#39;Courier New&#39;, monospace"
W = 680

# ------------------------------------------------------------------ extrair ativos
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

# cada letra: camada de contorno (#0a0a0a) sob o glifo (#f1efe8), coordenadas originais
letters = []
for g in letter_groups:
    layers = [(fill, re.sub(r">\s+<", "><", inner).strip())
              for fill, inner in re.findall(r'<g fill="(#[0-9a-f]{6})"[^>]*>(.*?)</g>', g, re.S)]
    xs = [int(x) for x in re.findall(r'x="(-?\d+)"', g)]
    letters.append((min(xs) + (max(xs) + 8 - min(xs)) / 2.0, layers))
letters.sort(key=lambda p: p[0])            # M A R G O D, da esquerda para a direita

# esferas: camadas base sempre visiveis + 7 quadros que se alternam sozinhos
spheres = []
for track in sphere_tracks:
    kids = top_groups(track, track.index(">") + 1)
    spheres.append("".join(re.sub(r">\s+<", "><", k).strip()
                           .replace('begin="-1.55s"', 'begin="0s"') for k in kids))

# ----------------------------------------------------------------------- conteudo
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

# ------------------------------------------------------------------------- layout
RULE1, RULE2 = 236, 344
ROWS_Y = (262, 292, 322)
HEAD_Y = 382
ITEM0, PITCH, DESC_DY = 412, 40, 15
FOOT_Y = 622
H = 652
MX = 40                      # margem horizontal do conteudo
GRID = 85                    # celula da grade de fundo (680 = 8 colunas exatas)
RX = 14                      # raio do canto do cartao

# As esferas ficam paradas nas pontas, como os "O" que ladeiam a palavra.
# O wordmark ocupa x=200..480; cada esfera fica a 10px de folga dele.
SPHERE_X = (126, 546)        # origem do translate; o centro do sprite e origem+4
SPHERE_Y = 100

# ------------------------------------------------------------------------- tempos
LOOP = 5.0                           # duracao de uma escrita
CYCLES = 2
TOTAL = LOOP * CYCLES                # depois disso o nome congela aceso
PAIRS = ((2, 3), (1, 4), (0, 5))     # R,G -> A,O -> M,D : do centro para fora
PAIR_T = (0.90, 1.40, 1.90)          # quando cada par acende
GROW = 0.30                          # tempo de subida
SUB_T = PAIR_T[-1] + 0.40            # subtitulo logo apos o ultimo par
OUT_A, OUT_B = 4.20, 4.55            # apagada entre um ciclo e o outro

BALL_DUR = TOTAL + 1.0               # as esferas somem depois da segunda escrita
BALL_OUT_A, BALL_OUT_B = TOTAL, TOTAL + 0.8

SHINE = 7.0                          # periodo da varredura de brilho
SHINE_BEGIN = BALL_OUT_B             # so comeca quando sobra apenas o nome
LEAD, STEP, PEAK, BACK = 0.10, 0.16, 0.35, 0.85
GLOW = {INK: "#ffffff", BG: T1}      # tom base -> pico do brilho


def keytimes(ts, span):
    return ";".join("%.4f" % (t / span) for t in ts)


def reveal(t):
    """Acende em t, apaga entre os ciclos, reacende no 2o e CONGELA acesa.

    Um unico <animate> cobre os dois ciclos, entao o valor congelado e sempre 1 --
    nao depende de prioridade entre animacoes concorrentes.
    """
    ts = [0.0, t, t + GROW, OUT_A, OUT_B, LOOP + t, LOOP + t + GROW, TOTAL]
    assert ts[2] < ts[3] and ts[4] < ts[5], "os ciclos se sobrepoem"
    return ('<animate attributeName="opacity" dur="%gs" repeatCount="1" fill="freeze" '
            'calcMode="linear" keyTimes="%s" values="0;0;1;1;0;0;1;1"/>'
            % (TOTAL, keytimes(ts, TOTAL)))


def ball_opacity():
    """As esferas entram, acompanham as duas escritas e se apagam no fim."""
    ts = [0.0, 0.15, 0.55, OUT_A, OUT_B, LOOP + 0.15, LOOP + 0.55,
          BALL_OUT_A, BALL_OUT_B, BALL_DUR]
    return ('<animate attributeName="opacity" dur="%gs" repeatCount="1" fill="freeze" '
            'calcMode="linear" keyTimes="%s" values="0;0;1;1;0;0;1;1;0;0"/>'
            % (BALL_DUR, keytimes(ts, BALL_DUR)))


def shine(i, base, peak):
    """Onda de luz percorrendo as letras da esquerda para a direita, em loop.

    Como anima `fill`, o estado sem SMIL continua sendo o tom base: e acrescimo puro.
    """
    t0 = LEAD + i * STEP
    ts = [0.0, t0, t0 + PEAK, t0 + BACK, SHINE]
    return ('<animate attributeName="fill" begin="%gs" dur="%gs" repeatCount="indefinite" '
            'calcMode="linear" keyTimes="%s" values="%s;%s;%s;%s;%s"/>'
            % (SHINE_BEGIN, SHINE, keytimes(ts, SHINE), base, base, peak, base, base))


def txt(x, y, s, size, fill, ls=0, op=1.0, anchor="start"):
    return ('<text x="%s" y="%s" font-family="%s" font-size="%s" fill="%s" '
            'letter-spacing="%s" opacity="%s" text-anchor="%s" '
            'xml:space="preserve">%s</text>') % (x, y, MONO, size, fill, ls, op, anchor, s)


# ---------------------------------------------------------- cabecalho: O + nome + O
sphere_svg = "".join(
    '<g transform="translate(%d %d)" opacity="1">%s%s</g>'
    % (x, SPHERE_Y, body, ball_opacity())
    for x, body in zip(SPHERE_X, spheres))

when = [None] * 6                    # em que instante cada letra acende
for (a, b), t in zip(PAIRS, PAIR_T):
    when[a] = when[b] = t

letters_svg = "".join(
    '<g opacity="1">%s%s</g>' % (
        "".join('<g fill="%s">%s%s</g>' % (fill, inner, shine(i, fill, GLOW[fill]))
                for fill, inner in layers),
        reveal(when[i]))
    for i, (cx, layers) in enumerate(letters))

subtitle_svg = '<g opacity="1">%s%s</g>' % (
    txt(W / 2, 192, SUB, 10, T3, 2.6, 1.0, "middle"), reveal(SUB_T))

# ----------------------------------------------------------------- marquee da stack
CH = 7.55                            # largura aproximada de um caractere a 12.5px


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

# --------------------------------------------------------------------- trabalhos
work_svg = [txt(MX, HEAD_Y, "LATEST WORK &amp; PROJECTS", 11.5, INK, 2.4, 0.95)]
for i, (year, title, desc) in enumerate(WORK):
    y = ITEM0 + i * PITCH
    work_svg.append(txt(MX, y, "-", 11, T2, 0))
    work_svg.append(txt(MX + 16, y, "[%s] %s" % (year, title), 11, INK, 1.2, 0.92))
    work_svg.append(txt(MX + 16, y + DESC_DY, desc, 9, T2, 0.5, 1.0))
work_svg.append(txt(MX, FOOT_Y, FOOTER, 8.5, T2, 1.6, 1.0))
work_svg = "".join(work_svg)

# ------------------------------------------------------- grade de fundo e moldura
grid = ('<path d="%s" stroke="%s" stroke-width="1" fill="none" opacity="0.05"/>'
        % ("".join("M%d 0V%d" % (x, H) for x in range(GRID, W, GRID))
           + "".join("M0 %dH%d" % (y, W) for y in range(GRID, H, GRID)), INK))

defs = ('<clipPath id="card"><rect x="0" y="0" width="%d" height="%d" rx="%d"/></clipPath>'
        '<linearGradient id="fade" gradientUnits="userSpaceOnUse" x1="%d" x2="%d" y1="0" y2="0">'
        '<stop offset="0" stop-color="#000"/><stop offset="0.10" stop-color="#fff"/>'
        '<stop offset="0.90" stop-color="#fff"/><stop offset="1" stop-color="#000"/>'
        '</linearGradient>'
        '<mask id="edges" maskUnits="userSpaceOnUse" x="%d" y="%d" width="%d" height="%d">'
        '<rect x="%d" y="%d" width="%d" height="%d" fill="url(#fade)"/></mask>'
        % (W, H, RX, MX, W - MX,
           MX, RULE1, W - 2 * MX, RULE2 - RULE1,
           MX, RULE1, W - 2 * MX, RULE2 - RULE1))

svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" shape-rendering="crispEdges" role="img" aria-label="MARGOD — Marcus Vinicius, Software Engineer at Softsafe (Medsafe) and CS student at iCEV. Stack: {stack}. Latest work: {worklist}.">
  <title>MARGOD — Marcus Vinicius</title>
  <defs>{defs}</defs>
  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="{BG}"/>
    {grid}
    {spheres}
    {letters}
    {subtitle}
    <rect x="{MX}" y="{RULE1}" width="{cw}" height="1" fill="{T1}" opacity="0.8"/>
    <g mask="url(#edges)" shape-rendering="auto">{marquee}</g>
    <rect x="{MX}" y="{RULE2}" width="{cw}" height="1" fill="{T1}" opacity="0.8"/>
    <g shape-rendering="auto">{work}</g>
  </g>
  <rect x="0.5" y="0.5" width="{fw}" height="{fh}" rx="{RX}" fill="none" stroke="{T1}" stroke-width="1" opacity="0.55"/>
</svg>
""".format(W=W, H=H, BG=BG, T1=T1, MX=MX, RX=RX, cw=W - 2 * MX, fw=W - 1, fh=H - 1,
           RULE1=RULE1, RULE2=RULE2, defs=defs, grid=grid, spheres=sphere_svg,
           letters=letters_svg, subtitle=subtitle_svg, marquee=marquee, work=work_svg,
           stack=", ".join(t.title() for t in TECH),
           worklist="; ".join("%s (%s)" % (t.title(), y) for y, t, _ in WORK))

open(OUT, "w", encoding="utf-8", newline="\n").write(svg)

print("%s: %d bytes  %dx%d" % (OUT, len(svg.encode("utf-8")), W, H))
for t in (0.0,) + PAIR_T:
    print("   %.2fs   O%sO" % (
        t, "".join(c if (when[i] is not None and when[i] <= t) else " "
                   for i, c in enumerate("MARGOD"))))
print("subtitulo em %.2fs · esferas somem em %.1f-%.1fs · brilho a partir de %.1fs"
      % (SUB_T, BALL_OUT_A, BALL_OUT_B, SHINE_BEGIN))
