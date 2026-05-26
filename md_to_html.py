#!/usr/bin/env python3
"""
md_to_html.py
=============
Convertit les fichiers markdown annotés du cours "Analyse quantitative en
sciences humaines" en pages HTML autonomes et stylisées, avec :
  - Panneau latéral de navigation (sections/sous-sections détectées auto.)
  - Blocs structurés colorés (définition, exemple, remarque, etc.)
  - Support des images (attribut image="..." dans les blocs figure)

Usage :
    python md_to_html.py [fichier.md ...]    # fichiers explicites
    python md_to_html.py                     # tous les *.md du dossier courant
                                             # ou dans chapitres/ si aucun trouvé

Convention des blocs :
    <!-- BLOC:type id="..." [titre="..."] [image="chemin.png"] -->
    contenu markdown
    <!-- /BLOC:type -->

Types reconnus : definition, exemple, remarque, theoreme, methode,
                 figure, tableau, resume

Prérequis : Python ≥ 3.10 (syntaxe `str | None` dans les annotations de type).
"""

import re
import sys
import glob
import os
import shlex
import html as html_mod

try:
    import markdown
    MD_AVAILABLE = True
except ImportError:
    MD_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────────
# Configuration des blocs
# ─────────────────────────────────────────────────────────────────────────────

BLOC_CONFIG = {
    "definition": {"label": "Définition",        "css": "bloc-definition", "icon": "📘"},
    "exemple":    {"label": "Exemple",            "css": "bloc-exemple",    "icon": "💡"},
    "remarque":   {"label": "Remarque",           "css": "bloc-remarque",   "icon": "⚠️"},
    "theoreme":   {"label": "Théorème",           "css": "bloc-theoreme",   "icon": "📐"},
    "methode":    {"label": "Méthode",             "css": "bloc-methode",    "icon": "🔧"},
    "figure":     {"label": "Figure",             "css": "bloc-figure",     "icon": "🖼"},
    "tableau":    {"label": "Tableau",            "css": "bloc-tableau",    "icon": "📊"},
    "resume":     {"label": "Résumé du chapitre", "css": "bloc-resume",     "icon": "📋"},
}

# ─────────────────────────────────────────────────────────────────────────────
# Chargement des ressources externes (CSS, JS, template)
# ─────────────────────────────────────────────────────────────────────────────

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def _load_resource(filename: str) -> str:
    path = os.path.join(_SCRIPT_DIR, filename)
    with open(path, encoding="utf-8") as f:
        return f.read()


def asset_href(filename: str) -> str:
    """Ajoute une version d'asset pour éviter les CSS/JS périmés en cache."""
    path = os.path.join(_SCRIPT_DIR, filename)
    version = int(os.path.getmtime(path))
    return f"{filename}?v={version}"

try:
    CSS  = _load_resource("style.css")
    JS   = _load_resource("script.js")
    HTML_TEMPLATE = _load_resource("template.html")
except FileNotFoundError as e:
    print(f"⚠  Fichier manquant : {e.filename}")
    print("    Assurez-vous que style.css, script.js et template.html sont")
    print("    dans le même dossier que md_to_html.py.")
    sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# Extraction du titre et de la table des matières
# ─────────────────────────────────────────────────────────────────────────────

HEADING_RE = re.compile(r'^(#{1,3})[ \t]+(.+?)(?:[ \t]+#+)?[ \t]*$', re.MULTILINE)


ROMAN_RE = re.compile(r'Chapitre\s+([IVXLCDM]+)')


def extract_chapter_num(title: str) -> str:
    m = ROMAN_RE.match(title)
    return m.group(1) if m else ''


def compute_section_numbers(headings: list[dict], chapter_num: str) -> list[dict]:
    """Ajoute un champ 'num' à chaque heading."""
    section_counter = 0
    subsection_counter = 0
    for h in headings:
        if h["text"] == "Résumé du chapitre":
            h["num"] = ""
            continue
        if h["level"] == 2:
            section_counter += 1
            subsection_counter = 0
            h["num"] = f"{chapter_num}.{section_counter}"
        elif h["level"] == 3:
            subsection_counter += 1
            h["num"] = f"{chapter_num}.{section_counter}.{subsection_counter}"
        else:
            h["num"] = ""
    return headings


def slugify(text: str) -> str:
    """Crée un identifiant HTML valide à partir d'un titre."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-') or 'section'


def normalize_heading_text(text: str) -> str:
    """Normalise un titre Markdown/HTML pour pouvoir le comparer."""
    text = re.sub(r'<[^>]+>', '', text)
    text = html_mod.unescape(text)
    text = re.sub(r'[*_`]+', '', text)
    return slugify(text)


def extract_headings(md_source: str) -> list[dict]:
    """Retourne la liste des titres avec leur niveau, texte et slug.
    Ignore les sous-titres (h3+) qui se trouvent entre "## Résumé du chapitre"
    et le prochain titre h2 (ou la fin du fichier).
    """
    headings = []
    seen: dict[str, int] = {}
    skip_until_h2 = 0  # > 0 → on saute les sous-titres jusqu'au prochain h2
    lines = md_source.splitlines()
    for line in lines:
        m = HEADING_RE.match(line)
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()

            # Détecter la fin de la section "Résumé du chapitre" au prochain h2
            if skip_until_h2:
                if level == 2:
                    skip_until_h2 = 0  # fin du skip, on garde ce titre
                else:
                    continue  # on saute les sous-titres du résumé

            # Détecter le début de la section "## Résumé du chapitre"
            if level == 2 and text == "Résumé du chapitre":
                skip_until_h2 = 1

            base_slug = slugify(text)
            count = seen.get(base_slug, 0)
            slug = base_slug if count == 0 else f"{base_slug}-{count}"
            seen[base_slug] = count + 1
            headings.append({"level": level, "text": text, "slug": slug})
    return headings


def extract_title(md_source: str) -> str:
    for line in md_source.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return "Analyse quantitative"


def build_toc_html(headings: list[dict]) -> str:
    """Génère le HTML de la table des matières latérale."""
    items = []
    for h in headings:
        if h["level"] == 1:
            continue  # le titre du chapitre est déjà visible
        cls = f"nav-item level-h{h['level']}"
        display = f"{h['num']} {h['text']}" if h.get('num') else h['text']
        text = html_mod.escape(display)
        items.append(
            f'<a class="{cls}" href="#{h["slug"]}" data-id="{h["slug"]}">{text}</a>'
        )
    return "\n".join(items)


# ─────────────────────────────────────────────────────────────────────────────
# Injection des id dans les titres HTML
# ─────────────────────────────────────────────────────────────────────────────

HEADING_HTML_RE = re.compile(r'<(h[1-3])>(.*?)</\1>', re.DOTALL)


def inject_heading_ids(body_html: str, headings: list[dict]) -> str:
    """Ajoute id="slug" aux balises <h1>–<h3> qui sont dans la table des matières."""
    idx = [0]  # compteur mutable dans la closure

    def replacer(m):
        tag = m.group(1)
        content = m.group(2)
        level_map = {"h1": 1, "h2": 2, "h3": 3}
        level = level_map.get(tag, 2)

        if idx[0] >= len(headings):
            return m.group(0)

        h = headings[idx[0]]
        if h["level"] != level:
            return m.group(0)

        if normalize_heading_text(content) != normalize_heading_text(h["text"]):
            return m.group(0)

        slug = h["slug"]
        num = h.get("num", "")
        display = f"{num} {content}" if num else content
        idx[0] += 1
        return f'<{tag} id="{slug}">{display}</{tag}>'

    return HEADING_HTML_RE.sub(replacer, body_html)


# ─────────────────────────────────────────────────────────────────────────────
# Traitement des blocs annotés
# ─────────────────────────────────────────────────────────────────────────────

BLOC_OPEN_RE  = re.compile(r'^\s*<!--\s*BLOC:(\w+)\s*(.*?)-->\s*$', re.IGNORECASE)
BLOC_CLOSE_RE = re.compile(r'^\s*<!--\s*/BLOC:(\w+)\s*-->\s*$', re.IGNORECASE)
ATTR_RE       = re.compile(r'(\w+)=["\']([^"\']*)["\']')


def parse_attrs(attr_str: str) -> dict:
    attrs = {}
    try:
        parts = shlex.split(attr_str)
    except ValueError:
        return dict(ATTR_RE.findall(attr_str))

    for part in parts:
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        if key:
            attrs[key] = value
    return attrs


def md_to_html_fragment(text: str) -> str:
    if MD_AVAILABLE:
        # ── Protéger le LaTeX avant le parsing Markdown ────────────────────────
        # Le parser markdown va manger les underscores, backslashes, etc.
        # On remplace temporairement le LaTeX par des placeholders.
        placeholders: dict[str, str] = {}
        counter = [0]

        def _protect_display(m):
            counter[0] += 1
            key = f"@@MJX_DISPLAY_{counter[0]}@@"
            placeholders[key] = m.group(0)
            return key

        def _protect_inline(m):
            counter[0] += 1
            key = f"@@MJX_INLINE_{counter[0]}@@"
            placeholders[key] = m.group(0)
            return key

        # Protéger d'abord les display $$...$$ et \[...\] (multi-lignes possible)
        text = re.sub(r'\$\$.+?\$\$', _protect_display, text, flags=re.DOTALL)
        text = re.sub(r'\\\[.+?\\\]', _protect_display, text, flags=re.DOTALL)
        # Ensuite les inline $...$ et \(...\) (sur une seule ligne)
        text = re.sub(r'\$[^\$\n]+?\$', _protect_inline, text)
        text = re.sub(r'\\\(.+?\\\)', _protect_inline, text)

        # Convertir **...** (encore non protégé) en <strong>...</strong>
        # pour que le bold fonctionne même dans les blocs HTML bruts (<div>...)
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

        # Conversion Markdown → HTML
        html = markdown.markdown(
            text,
            extensions=["tables", "fenced_code", "nl2br"],
        )

        # Restaurer le LaTeX (remettre les $, \, etc.)
        for key, original in placeholders.items():
            html = html.replace(key, original)

        return html
    # Fallback minimaliste
    result = []
    for line in text.split("\n"):
        line = line.rstrip()
        if line.startswith("# "):      result.append(f"<h1>{html_mod.escape(line[2:])}</h1>")
        elif line.startswith("## "):   result.append(f"<h2>{html_mod.escape(line[3:])}</h2>")
        elif line.startswith("### "): result.append(f"<h3>{html_mod.escape(line[4:])}</h3>")
        elif line.startswith("- ") or line.startswith("— "):
                                       result.append(f"<li>{html_mod.escape(line[2:])}</li>")
        elif line == "":               result.append("<br>")
        else:                          result.append(f"<p>{html_mod.escape(line)}</p>")
    return "\n".join(result)


def strip_single_paragraph(html: str) -> str:
    """Retire uniquement l'enveloppe <p>...</p> simple, sans casser les blocs riches."""
    match = re.fullmatch(r'\s*<p>(.*?)</p>\s*', html, flags=re.DOTALL)
    return match.group(1).strip() if match else html.strip()


def render_bloc(bloc_type: str, attrs: dict, content_md: str, md_file_dir: str, bloc_num: str = "", chapter_num: str = "") -> str:
    cfg = BLOC_CONFIG.get(bloc_type.lower(), {
        "label": bloc_type.capitalize(), "css": f"bloc-{bloc_type.lower()}", "icon": "📌"
    })

    bloc_id = attrs.get("id", "")
    titre   = attrs.get("titre", "")
    image   = attrs.get("image", "")

    # ── Pour les figures : extraire le titre depuis le contenu boldé ──────
    # (le titre n'est pas dans un attribut mais dans **Figure fig-X — Titre**)
    content = content_md.strip()
    if bloc_type.lower() == "figure":
        fig_title_m = re.match(r'\*\*\s*(?:Figure|Tableau)\s+[\w-]+\s*[—-]?\s*(.+?)\s*\*\*', content, re.DOTALL | re.IGNORECASE)
        if fig_title_m and not titre:
            titre = fig_title_m.group(1).strip()
            # Enlever le titre du contenu pour qu'il n'apparaisse pas dans le corps
            content = content[fig_title_m.end():].strip()

    # Header
    id_span = f'<span class="bloc-id">({html_mod.escape(bloc_id)})</span>' if bloc_id else ""
    # Pour le résumé : utiliser le numéro de chapitre au lieu du compteur séquentiel
    if bloc_type.lower() == "resume" and chapter_num:
        num_label = f'{cfg["label"]} {chapter_num}'
    elif bloc_type.lower() == "resume":
        num_label = cfg["label"]  # pas de numéro du tout
    else:
        num_label = f'{cfg["label"]} {bloc_num}' if bloc_num else cfg["label"]
    if titre:
        header_txt = f'{cfg["icon"]} {num_label} — {html_mod.escape(titre)} {id_span}'
    else:
        header_txt = f'{cfg["icon"]} {num_label} {id_span}'

    # ── Nettoyer le contenu : enlever la première ligne si c'est un
    #    en-tête en gras (**Type** ou **Type — Titre**) redondant avec
    #    l'en-tête généré automatiquement.
    # Détecter et enlever la première ligne si elle est de la forme
    # **Type** ou **Type — Titre**
    first_newline = content.find('\n')
    first_line = content[:first_newline] if first_newline >= 0 else content
    first_line_stripped = first_line.strip()
    # Pattern: ligne entièrement en gras (**...**) éventuellement suivie de ":"
    bold_match = re.match(r'^\*\*(.+?)\*\*\s*:?\s*$', first_line_stripped)
    if bold_match:
        bold_text = bold_match.group(1).strip().rstrip(':').strip()
        # Extraire le type et le titre du texte boldé
        # "Type — Titre" ou "Type" seulement
        bold_parts = re.split(r'\s*[—–]\s*', bold_text, maxsplit=1)
        bold_type = bold_parts[0].strip().lower()

        # Vérifier si cette ligne est redondante avec l'en-tête généré :
        #   - soit le type boldé correspond au label de config (insensible à la casse)
        #   - soit le type boldé est "propriété" et le label config est "théorème"
        #     (même mapping que convert_blocks.py)
        #   - soit un titre est présent et apparaît dans le texte boldé
        config_label_lower = cfg['label'].lower()
        is_same_type = (
            bold_type == config_label_lower
            # "Propriété" apparaît dans les blocs de type theoreme
            or (bold_type == 'propriété' and config_label_lower == 'théorème')
            or (bold_type == 'propriete' and config_label_lower == 'théorème')
        )
        titre_match = titre and titre.lower() in bold_text
        
        if is_same_type or (titre_match and bold_type in ['exemple', 'definition', 'remarque', 'theoreme', 'propriété', 'propriete', 'méthode', 'methode']):
            # Enlever la première ligne du contenu
            content = content[first_newline:].strip() if first_newline >= 0 else ''

    # Corps : figure avec image ?
    if bloc_type.lower() == "figure" and image:
        img_rel  = image
        # Le titre est deja dans l'en-tete du bloc (extrait plus haut)
        body_html = (
            f'<img src="{html_mod.escape(img_rel)}" alt="{html_mod.escape(cfg["label"])}">'
        )
    else:
        # Le contenu peut contenir du HTML pré-rendu (sous-blocs) mêlé à du markdown.
        # On utilise md_to_html_fragment qui laisse passer les blocs HTML intacts.
        body_html = md_to_html_fragment(content)

    bloc_id_attr = f' id="{html_mod.escape(bloc_id)}"' if bloc_id else ""
    header_html = f'  <div class="bloc-header">{header_txt}</div>\n' if header_txt else ""
    return (
        f'<div class="bloc {cfg["css"]}"{bloc_id_attr}>\n'
        f'{header_html}'
        f'  <div class="bloc-body">{body_html}</div>\n'
        f'</div>\n'
    )


_BLOC_COUNTERS = {}

def process_markdown(source: str, md_file_dir: str, chapter_title: str = "") -> str:
    """Parse le source markdown et retourne le HTML complet du corps.
    Reinitialise les compteurs de blocs automatiques."""
    global _BLOC_COUNTERS
    _BLOC_COUNTERS.clear()

    # ── Prétraitement des notes de bas de page ───────────────────────────
    # Les footnotes [^n]: ... sont dispersées dans le texte et parfois
    # dans des blocs différents de leurs références. On les extrait ici
    # pour les gérer manuellement.
    FOOTNOTE_DEF_RE = re.compile(r'^\[\^(\d+)\]\s*:\s*(.*?)(?=\n\[\^\d+\]\s*:|\n\s*\n|\Z)', re.MULTILINE | re.DOTALL)
    footnotes: dict[str, str] = {}
    footnote_refs: dict[str, list[str]] = {}

    def _extract_footnote(m):
        num = m.group(1)
        text = m.group(2).strip()
        footnotes[num] = text
        return ''  # remove definition line
    source = FOOTNOTE_DEF_RE.sub(_extract_footnote, source)

    # Remplacer les références [^n] par des ancres HTML
    def _replace_ref(m):
        num = m.group(1)
        refs = footnote_refs.setdefault(num, [])
        ref_id = f"fnref-{num}" if not refs else f"fnref-{num}-{len(refs) + 1}"
        refs.append(ref_id)
        return f'<sup id="{ref_id}"><a href="#fn-{num}" class="footnote-ref">{num}</a></sup>'
    source = re.sub(r'\[\^(\d+)\]', _replace_ref, source)

    lines = source.splitlines(keepends=True)
    segments: list = []
    # Pile pour gérer les blocs imbriqués.
    # Chaque entrée : [bloc_type, attrs, lignes_accumulées]
    stack: list = []

    def _next_bloc_num(bloc_type: str) -> int:
        key = bloc_type.lower()
        _BLOC_COUNTERS[key] = _BLOC_COUNTERS.get(key, 0) + 1
        return _BLOC_COUNTERS[key]

    def _chapter_num_for(bloc_type: str) -> str:
        if bloc_type.lower() != "resume" or not chapter_title:
            return ""
        return extract_chapter_num(chapter_title)

    def _append_rendered_bloc(bloc_type: str, attrs: dict, content: str):
        bloc_num = _next_bloc_num(bloc_type)
        chapter_num = _chapter_num_for(bloc_type)
        if stack:
            rendered = render_bloc(bloc_type, attrs, content, md_file_dir, str(bloc_num), chapter_num)
            stack[-1][2].append(rendered)
        else:
            segments.append(("bloc", (bloc_type, attrs, content, bloc_num, chapter_num)))

    for line in lines:
        open_m  = BLOC_OPEN_RE.match(line)
        close_m = BLOC_CLOSE_RE.match(line)

        if open_m:
            bt    = open_m.group(1)
            attrs = parse_attrs(open_m.group(2))
            stack.append([bt, attrs, []])

        elif close_m:
            close_type = close_m.group(1)
            if stack and stack[-1][0].lower() == close_type.lower():
                bt, attrs, bloc_lines = stack.pop()
                content = "".join(bloc_lines)
                _append_rendered_bloc(bt, attrs, content)
            elif stack:
                stack[-1][2].append(line)
            else:
                if segments and segments[-1][0] == "md":
                    segments[-1][1].append(line)
                else:
                    segments.append(("md", [line]))

        elif stack:
            stack[-1][2].append(line)

        else:
            if segments and segments[-1][0] == "md":
                segments[-1][1].append(line)
            else:
                segments.append(("md", [line]))

    # Fermer les blocs non fermés
    while stack:
        bt, attrs, bloc_lines = stack.pop()
        _append_rendered_bloc(bt, attrs, "".join(bloc_lines))

    parts = []
    for seg_type, seg_data in segments:
        if seg_type == "md":
            parts.append(md_to_html_fragment("".join(seg_data)))
        else:
            bloc_type, attrs, content = seg_data[:3]
            num = seg_data[3] if len(seg_data) > 3 else ""
            chapter_num = seg_data[4] if len(seg_data) > 4 else ""
            parts.append(render_bloc(bloc_type, attrs, content, md_file_dir, str(num), chapter_num))

    body = "\n".join(parts)

    # ── Ajouter les notes de bas de page à la fin ────────────────────────
    if footnotes:
        fn_items = []
        for num in sorted(footnotes.keys(), key=int):
            # Convertir le texte de la note (peut contenir du markdown)
            fn_text = strip_single_paragraph(md_to_html_fragment(footnotes[num]))
            backrefs = " ".join(
                f'<a href="#{ref_id}" class="footnote-backref">↩</a>'
                for ref_id in footnote_refs.get(num, [f"fnref-{num}"])
            )
            fn_items.append(
                f'<li id="fn-{num}">{fn_text} '
                f'{backrefs}</li>'
            )
        body += (
            '<hr class="footnotes-sep">\n'
            '<div class="footnotes">\n'
            '<ol>\n' +
            '\n'.join(fn_items) +
            '\n</ol>\n'
            '</div>\n'
        )

    return body


# ─────────────────────────────────────────────────────────────────────────────
# Génération des fichiers
# ─────────────────────────────────────────────────────────────────────────────

def build_chapter_links(all_md_files: list[str], current_file: str) -> str:
    links = []
    for f in sorted(all_md_files):
        basename = os.path.basename(f)
        html_name = basename.replace(".md", ".html")
        label = (
            basename
            .replace("chapitre_", "Chap. ")
            .replace(".md", "")
            .replace("_", " ")
        )
        if basename == os.path.basename(current_file):
            links.append(f'<span style="font-weight:700;color:var(--bleu)">{label}</span>')
        else:
            links.append(f'<a href="{html_name}">{label}</a>')
    return "\n".join(links)


def convert_file(md_path: str, all_md_files: list[str], output_dir: str | None = None) -> str:
    with open(md_path, encoding="utf-8") as f:
        source = f.read()

    md_file_dir = os.path.dirname(os.path.abspath(md_path))

    title    = extract_title(source)
    headings = extract_headings(source)
    chapter_num = extract_chapter_num(title)
    headings = compute_section_numbers(headings, chapter_num)
    toc_html = build_toc_html(headings)

    body_html = process_markdown(source, md_file_dir, title)
    body_html = inject_heading_ids(body_html, headings)

    chapter_links = build_chapter_links(all_md_files, md_path)

    page = HTML_TEMPLATE.format(
        title=html_mod.escape(title),
        style_href=asset_href("style.css"),
        script_href=asset_href("script.js"),
        chapter_links=chapter_links,
        toc_html=toc_html,
        body=body_html,
    )

    if output_dir is None:
        output_dir = os.path.dirname(md_path) or "."

    html_name = os.path.basename(md_path).replace(".md", ".html")
    out_path  = os.path.join(output_dir, html_name)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)

    print(f"✓  {md_path}  →  {out_path}")
    return out_path


def build_index(all_md_files: list[str], output_dir: str, intro_md: str | None = None):
    items = []
    for f in sorted(all_md_files):
        basename  = os.path.basename(f)
        html_name = basename.replace(".md", ".html")
        with open(f, encoding="utf-8") as fh:
            title = extract_title(fh.read())
        items.append(f'<li><a href="{html_name}">{html_mod.escape(title)}</a></li>')

    if intro_md:
        intro_html = process_markdown(intro_md, output_dir)
        # Extraire le titre s'il y en a un
        intro_title_m = re.search(r'<h1[^>]*>(.*?)</h1>', intro_html)
        if intro_title_m:
            page_title = html_mod.escape(intro_title_m.group(1))
            body = intro_html
        else:
            page_title = "Analyse quantitative"
            body = intro_html
        body += f'\n<hr>\n<h2>Table des chapitres</h2>\n<ul>\n' + "\n".join(items) + "\n</ul>\n"
    else:
        page_title = "Analyse quantitative — Table des matières"
        body = (
            "<h1>Analyse quantitative en sciences humaines</h1>\n"
            "<p>Balthazar Charles, 2026</p>\n"
            "<hr>\n"
            "<h2>Table des chapitres</h2>\n"
            "<ul>\n" + "\n".join(items) + "\n</ul>\n"
        )

    page = HTML_TEMPLATE.format(
        title=page_title,
        style_href=asset_href("style.css"),
        script_href=asset_href("script.js"),
        chapter_links="",
        toc_html="",
        body=body,
    )

    out_path = os.path.join(output_dir, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"✓  index.html  →  {out_path}")


# ─────────────────────────────────────────────────────────────────────────────
# Point d'entrée
# ─────────────────────────────────────────────────────────────────────────────

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    if len(sys.argv) > 1:
        md_files = [f for f in sys.argv[1:] if f.endswith(".md")]
    else:
        # Par défaut : tous les .md dans chapitres/
        md_dir = os.path.join(script_dir, "chapitres")
        md_files = sorted(glob.glob(os.path.join(md_dir, "*.md")))
        # Exclure les fichiers de review
        md_files = [f for f in md_files if "review_" not in os.path.basename(f)]

    if not md_files:
        print("Aucun fichier .md trouvé. Usage :")
        print("  python md_to_html.py chapitre_01.md chapitre_02.md ...")
        print("  (ou placez les .md dans chapitres/)")
        sys.exit(1)

    if not MD_AVAILABLE:
        print("Module 'markdown' manquant. Lancez :")
        print(f"  {sys.executable} -m pip install markdown")
        sys.exit(1)

    # Les fichiers HTML sont générés dans le dossier du script (cours_website/)
    output_dir = script_dir
    all_abs    = [os.path.abspath(f) for f in md_files]

    print(f"\nConversion de {len(md_files)} fichier(s) vers {output_dir}/...\n")
    for f in md_files:
        convert_file(f, all_abs, output_dir)

    # Chercher un éventuel intro.md pour personnaliser l'index
    intro_path = os.path.join(script_dir, "intro.md")
    intro_content = None
    if os.path.exists(intro_path):
        with open(intro_path, encoding="utf-8") as f:
            intro_content = f.read()
        print(f"ℹ️  intro.md trouvé — personnalisation de l'index.")

    build_index(all_abs, output_dir, intro_content)
    print(f"\n✅  Terminé ! Ouvrez {output_dir}/index.html dans votre navigateur.")


if __name__ == "__main__":
    main()
