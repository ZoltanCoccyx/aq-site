# Progress

## Status
In Progress

## Tasks
- ✅ ch01: Remove manual numbering from ## and ### headings
- ✅ ch01: Remove trailing periods from ### subheadings
- ✅ ch01: Convert #### to ###
- ✅ ch01: Remove trailing period from Figure 1 title
- ✅ ch01: Move ## Résumé du chapitre and --- before BLOC:resume
- ✅ ch01: Convert XIX^e to $XIX^e$ (MathJax)
- ✅ ch01: Add titre attribute to tab-1, tab-2, tab-3

## ch02 — Done
- ✅ Remove manual numbering from all ## and ### headings (14 occurrences)
- ✅ Convert #### Validité, #### Fidélité, #### Outils de collecte to ###
- ✅ Un-nest nested blocks: exemple-18, exemple-19, exemple-22, resume-1
- ✅ Move --- and ## Résumé du chapitre before BLOC:resume
- ✅ Move footnote definitions outside BLOC:resume
- ✅ Fix URL in footnote 7 (add https://)
- ✅ Add titre="..." to 18 exemple blocks missing it

## ch03 — Done
- ✅ Remove manual numbering (III.1, III.1.1, etc.) from all 16 ## and ### headings
- ✅ Convert 7 #### headings to ###
- ✅ Fix BLOC:resume positioning (close before ## Résumé du chapitre, reopen after)
- ✅ Remove empty line between all BLOC openings and bold text (~60 blocks)
- ✅ Add titre="..." to 13 blocks (definition, remarque, tableau) missing it

## ch04 — Done
- ✅ Remove manual numbering (IV.1, IV.1.1, etc.) from all ## and ### headings
- ✅ Add titre="..." to definition-3 (Moyenne), definition-4 (Asymétrie)
- ✅ Add titre="..." to theoreme-4 (Moyenne pondérée), theoreme-6 (Variance pondérée)
- ✅ Add titre="..." to methode-3 (Calcul du rang quantile), methode-4 (Lecture des quantiles et rangs sur une ogive)
- ✅ Add titre="..." to 14 examples missing it
- ✅ Add titre="..." to 10 tableaux missing it

## ch05 — Done
- ✅ Remove manual numbering from all ## and ### headings (14)
- ✅ Convert #### to ### (2 headings)
- ✅ Fix incomplete equations — remove trailing = (2 equations)
- ✅ Fix resume block placement: move ## Résumé du chapitre before BLOC:resume
- ✅ Add titre="..." to theoreme-1, theoreme-3, theoreme-5, theoreme-7, theoreme-8
- ✅ Add titre="..." to definition-5 (Marge d'erreur)
- ✅ Add titre="..." to remarque-1 (Valeur de 1,96)

## Files Changed
- chapitres/chapitre_01.md
- chapitres/chapitre_03.md
- chapitres/chapitre_04.md
- chapitres/chapitre_05.md

## Notes
ch04: Internal links (#fig-9→#fig-1, #fig-8→#fig-4, #fig-12→#fig-2, #exemple-65→#exemple-10) were already correct in the file. Images without -1 suffix left unchanged per instructions.
ch05: % in LaTeX math was already escaped with \%. Image filenames without -1 suffix left unchanged per instructions. fig-9 already had bold title. Figure number mismatches (fig-5→Figure 36, fig-6→Figure 37, fig-7→Figure 5) left as-is — content not to be modified per rules.
