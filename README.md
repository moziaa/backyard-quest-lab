# Backyard Quest Lab

An offline family maker planner inspired by robotics coaching, soccer practice, and learning through play. Turn materials you already have into a short **predict → build → test → reflect** session.

## Try it

Python 3.9 or newer; no packages, accounts, network access, or purchases required.

```sh
python quest_lab.py --materials paper blocks cardboard tape ball --minutes 25 --space both --adult
python quest_lab.py --materials paper blocks --minutes 30 --space table > mission-cards.md
python quest_lab.py --materials paper --minutes 10 --space floor --adult --json
python -m unittest -v
```

Open the generated Markdown in a Markdown viewer to print the mission cards. Output goes to stdout; shell redirection may overwrite an existing file. This release is a CLI with standalone HTML output, not an interactive website or PDF generator.

## How it chooses

Four original mission cards: Paper Bridge Engineers, Slow-Roll Goal Lab, Human Robot Rescue, and Shadow Stadium. Filter by available materials, table/floor space, and whether an adult participates. The planner finds the combination that uses the most activity minutes without exceeding the **shared** budget. Ties use catalog order and fewer missions. Every omitted activity has an explanation, including eligible activities left out by the shared budget. Time estimates exclude setup and cleanup.

`--adult` enables activities requiring active adult participation. Without it, an adult should still choose activities appropriate to the participants. No age suitability or safety certification is claimed. Cards include practical care notes and an eyes-open, walking-only robot activity with a seated adaptation. No real child data is collected.

## Scope and next steps

The small curated catalog intentionally uses exhaustive subset selection for transparent, deterministic results. It is not intended for thousands of activities. Next: a visual material picker, more seated adaptations, and user-authored local missions. No AI-generated activity service or child profiles.

Original code and activity wording, MIT licensed. Familiar experiments are not claimed as novel inventions.

## Browser-printable cards

```sh
python quest_lab.py --materials paper blocks --minutes 30 --space table --html > mission-cards.html
```

Open the HTML file in a browser and use Print. The cover summarizes time; each mission starts on a new printed page with prompts and writing space. Pagination depends on paper size and browser settings. Cards work offline with no scripts or external assets. `--html` and `--json` are mutually exclusive. Shell redirection may overwrite an existing file.
