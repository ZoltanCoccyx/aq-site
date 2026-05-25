# Guide de style — Markdown du cours « Analyse quantitative »

Ce guide explique comment rédiger le contenu du cours dans les fichiers `.md` pour qu'il soit correctement converti en HTML par le script `md_to_html.py`.

---

## 1. Structure générale

Chaque fichier `.md` correspond à un chapitre. Le fichier commence par un titre de niveau 1 :

```markdown
# Chapitre III — Concepts fondamentaux
```

Le numéro de chapitre (`III`) est déduit automatiquement du titre pour numéroter les sections.  
Utilisez la convention : `# Chapitre [chiffre romain] — [titre]`

---

## 2. Sections et sous-sections

Utilisez `##` pour les sections et `###` pour les sous-sections.  
**Ne mettez PAS de numéro manuel** — le script les génère automatiquement.

```markdown
## Population et échantillon

Ceci est un paragraphe de la section III.1.

### Population et échantillon

Sous-section III.1.1.

### Paramètres et statistiques

Sous-section III.1.2.
```

✅ Résultat : `III.1 Population et échantillon`, `III.1.1 Population et échantillon`, `III.1.2 Paramètres et statistiques`.

Le script ignore les numéros déjà présents dans le texte (ex: `III.3.1`) et les regénère.

---

## 3. Blocs structurés (définitions, exemples, etc.)

Les blocs sont délimités par des commentaires HTML.  
**Syntaxe générale :**

```markdown
<!-- BLOC:type id="identifiant" [titre="Titre facultatif"] -->

Contenu markdown ici...

<!-- /BLOC:type -->
```

### 3.1 Types de blocs reconnus

| Type | Comment utiliser | Icône |
|---|---|---|
| `definition` | Définition d'un concept | 📘 |
| `exemple` | Exemple illustratif | 💡 |
| `remarque` | Remarque, note importante | ⚠️ |
| `theoreme` | Théorème, proposition | 📐 |
| `methode` | Méthode, propriété, procédure | 🔧 |
| `figure` | Image / figure | 🖼 |
| `tableau` | Tableau structuré | 📊 |
| `resume` | Résumé de fin de chapitre | 📋 |

### 3.2 Identifiants

Chaque bloc doit avoir un `id` unique. Convention :

| Type | Préfixe | Exemple |
|---|---|---|
| Définition | `definition-` | `definition-5` |
| Exemple | `exemple-` | `exemple-23` |
| Remarque | `remarque-` | `remarque-2` |
| Théorème | `theoreme-` | `theoreme-6` |
| Méthode | `methode-` | `methode-3` |
| Figure | `fig-` | `fig-13` |
| Tableau | `tab-` | `tab-14` |
| Résumé | `resume-` | `resume-1` |

Les identifiants servent d'ancres pour les liens.  
Pour créer un lien vers un bloc : `[Voir Figure](#fig-13)`.

### 3.3 Titre dans l'attribut (optionnel mais recommandé)

```markdown
<!-- BLOC:definition id="definition-5" titre="Population" -->
```

Si le titre est fourni, il apparaît dans l'en-tête du bloc.  
S'il n'est pas fourni, le script peut parfois l'extraire du contenu (pour les figures notamment).

### 3.4 Contenu du bloc

Le contenu est du Markdown standard. La première ligne en gras (`**Définition — Titre**`) est automatiquement supprimée si elle est redondante avec l'en-tête généré.

```markdown
<!-- BLOC:definition id="definition-5" titre="Population" -->
**Définition — Population**

La **population** (ou univers) est l'ensemble complet de tous les éléments qui font l'objet d'une étude statistique.

**Notation :** $N$
<!-- /BLOC:definition -->
```

✅ Résultat : l'en-tête du bloc sera `📘 Définition 1 — Population` (le `**Définition — Population**` en première ligne est automatiquement retiré).

---

## 4. Figures

```markdown
<!-- BLOC:figure id="fig-13" image="../figures/histogramme_age_frequence-1.png" -->

**Figure 13 — Distribution de la population du Québec par groupe d'âge (2021, en pourcentage)**

<!-- /BLOC:figure -->
```

Règles :
- L'attribut `image` doit pointer vers le fichier PNG (chemin relatif depuis `chapitres/` vers `figures/`).
- Les images doivent être en PNG avec fond transparent (RGBA), suffixe `-1` (ex: `histogramme_age_frequence-1.png`).
- Le titre se met en **gras** sur la première ligne du contenu. Il existe deux formats acceptables :

  ```markdown
  **Figure fig-13 — Titre de la figure**
  **Figure 13 — Titre de la figure**
  ```
- La légende n'est PAS dupliquée — elle apparaît uniquement dans l'en-tête du bloc.

---

## 5. Tableaux

### 5.1 Tableaux simples (Markdown standard)

```markdown
<!-- BLOC:tableau id="tab-14" titre="Nombre de classes suggéré selon la règle de Sturges" -->

| $n$ | $k$ |
|---|---|
| Moins de 23 | 5 |
| De 23 à 45 | 6 |

<!-- /BLOC:tableau -->
```

Le titre peut être :
- Dans l'attribut `titre="..."` de la balise d'ouverture
- OU sur une ligne en **gras** juste avant la balise (converti automatiquement en attribut)

### 5.2 Tableaux complexes (avec cellules fusionnées)

Pour les tableaux avec `rowspan` / `colspan` (provenant du LaTeX `\SetCell`), utilisez du HTML directement :

```html
<!-- BLOC:tableau id="tab-6" -->
<table style="border-collapse:collapse;width:100%;">
<thead>
<tr>
  <th rowspan="2">Genre</th>
  <th colspan="2">Résultat</th>
  <th rowspan="2">Total</th>
</tr>
<tr>
  <th>Pile</th>
  <th>Face</th>
</tr>
</thead>
<tbody>
<tr>
  <td>Homme</td>
  <td>31</td>
  <td>19</td>
  <td>50</td>
</tr>
</tbody>
</table>
<!-- /BLOC:tableau -->
```

**Important :** N'utilisez pas de couleurs codées en dur dans les styles (`background:#1e3a8a`). Le script les remplace automatiquement par des variables CSS (`var(--table-hdr)`) qui s'adaptent au mode clair/sombre.

Utilisez plutôt les classes et styles suivants comme base :
- `<th>` pour les en-têtes (couleur gérée par CSS)
- `rowspan`/`colspan` pour les cellules fusionnées
- Pas de `background` ni `color` en dur dans les `style=""` des `<td>`/`<th>`

---

## 6. Équations LaTeX

Les équations sont écrites en LaTeX et rendues par **MathJax**.

| Type | Syntaxe |
|---|---|
| Inline | `$\mu = \frac{1}{n}\sum x_i$` |
| Display | `$$\bar{x} \sim \mathcal{N}\left(\mu, \frac{\sigma}{\sqrt{n}}\right)$$` |
| Display (alternative) | `\[...\]` (aussi supporté) |

Attention :
- Ne pas utiliser de `|` (pipe) nu dans les mathématiques inline — à l'intérieur d'un tableau Markdown, le pipe sert de séparateur. Utilisez plutôt `\lvert` et `\rvert` pour les valeurs absolues.
- Évitez les `%` seuls dans les équations (commentaire en LaTeX). Utilisez `\%` si nécessaire.
- Les exposants : `$x^2$` fonctionne, mais `3\textsuperscript{e}` doit être converti en `$3^e$` pour MathJax.

---

## 7. Notes de bas de page

```markdown
Une phrase avec une note[^3].

[^3]: Texte de la note ici. Le lien est ajouté automatiquement.
```

- La définition `[^n]:` peut être placée **n'importe où** dans le fichier (pas besoin de les regrouper à la fin).
- Le script les collecte automatiquement et les place en bas de page.
- Les notes de bas de page sont numérotées automatiquement dans l'ordre d'apparition.

---

## 8. Texte centré

Pour centrer du texte, utilisez :

```html
<div style="text-align:center;">
**Texte en gras centré**
</div>
```

Le `**` est correctement converti en `<strong>` même à l'intérieur du `<div>`.

Pour centrer une équation, utilisez le display math `$$...$$` seul — il est centré par défaut.

---

## 9. Le résumé de fin de chapitre

```markdown
## Résumé du chapitre
```

Le résumé commence par `## Résumé du chapitre`. Tout ce qui suit (jusqu'au prochain `##`) est considéré comme faisant partie du résumé. Les sous-titres (`###`) dans le résumé sont **automatiquement masqués** de la table des matières latérale.

---

## 10. Texte en gras (`**...**`)

Le gras standard `**texte**` fonctionne partout, y compris à l'intérieur des `<div>` HTML. Il est automatiquement converti en `<strong>` avant le rendu Markdown.

---

## 11. Ce qui est géré automatiquement (vous n'avez pas à le faire)

- **Numérotation des sections** (I.1, I.2, II.1.1, etc.) → générée à partir de la hiérarchie des titres
- **Numérotation des blocs** (Définition 1, Exemple 1, Figure 1…) → comptage automatique par type
- **Numérotation des notes de bas de page** → ordre d'apparition
- **Mode sombre** → les couleurs s'adaptent automatiquement à la préférence du navigateur
- **Table des matières latérale** → générée à partir des titres `##` et `###` (sauf dans le résumé)
- **Centrage** → Les `\begin{center}` et `\end{center}` du LaTeX sont déjà convertis

---

## 12. Exemple complet

```markdown
# Chapitre IV — Statistiques descriptives

## Tendances centrales

### Mode

<!-- BLOC:definition id="definition-20" titre="Mode" -->
**Définition — Mode**

Le **mode** (ou valeur modale) est la valeur la plus fréquente dans un ensemble de données.
<!-- /BLOC:definition -->

<!-- BLOC:exemple id="exemple-61" -->
**Exemple**

Pour les notes d'un examen : 65, 73, 68, 85, 70, 78.
La moyenne est $\bar{x} = \frac{65 + 73 + \dots}{6} = 73,2$.
<!-- /BLOC:exemple -->

### Médiane

<!-- BLOC:theoreme id="theoreme-6" titre="Propriétés de la médiane" -->
**Théorème — Propriétés de la médiane**

- Robuste face aux valeurs extrêmes
- Applicable aux variables ordinales et quantitatives
<!-- /BLOC:theoreme -->

<!-- BLOC:figure id="fig-42" image="../figures/mediane_exemple-1.png" -->
**Figure 42 — Distribution des salaires avec médiane indiquée**
<!-- /BLOC:figure -->

## Résumé du chapitre

<!-- BLOC:resume id="resume-2" -->
### Mots-clés

- **Mode** : valeur la plus fréquente
- **Médiane** : valeur centrale
- **Moyenne** : somme / effectif
<!-- /BLOC:resume -->
```

---

## 13. Commandes de génération

```bash
# Générer la version HTML du site
cd cours_website/chapitres
python3 ../md_to_html.py chapitre_01.md chapitre_02.md ...
# Ou pour tous les fichiers
python3 ../md_to_html.py
```

Le site généré se trouve dans `cours_website/chapitres/`. Ouvrez `index.html` dans un navigateur.
