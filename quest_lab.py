"""Offline family maker missions. Standard library only."""
from html import escape
import argparse
import itertools
import json

QUESTS = [
    dict(id='paper-bridge', title='Paper Bridge Engineers', minutes=15, space='table', adult=False,
         materials=['paper', 'blocks'],
         challenge='Bridge a gap between two blocks using one sheet of paper.',
         predict='Which fold will hold a third block: flat, accordion, or a tube?',
         steps=['Set two blocks a hand-width apart on a low table.', 'Span the gap with paper. Add one block gently at the center.', 'Try a different fold with the same gap and load.'],
         measure='Record which folds held the same block for five seconds.',
         reflect='What changed when you folded the paper? What stayed the same?',
         care='Keep blocks on the table; do not build a bridge for people to stand on.'),
    dict(id='rolling-goal', title='Slow-Roll Goal Lab', minutes=20, space='floor', adult=True,
         materials=['cardboard', 'tape', 'ball'],
         challenge='Make a wide cardboard goal and guide a ball into it with a gentle hand roll.',
         predict='Will a wider entrance or side rails make the goal easier to reach?',
         steps=['An adult folds cardboard into a freestanding goal; tape the folds.', 'Choose one starting spot on a clear floor.', 'Roll five times, change one feature, then repeat from the same spot.'],
         measure='Count goals out of five before and after the change.',
         reflect='Did your design help, or did your rolling technique change?',
         care='Use a soft ball and gentle rolls, away from stairs, pets, and breakable items. No cutting is required.'),
    dict(id='robot-route', title='Human Robot Rescue', minutes=10, space='floor', adult=True,
         materials=['paper'],
         challenge='Write commands that guide a walking partner to a paper rescue station.',
         predict='How many small steps and quarter-turns will the route need?',
         steps=['Clear a short walking route and put a paper station at its end.', 'Write a sequence of step and turn commands.', 'A partner follows the commands slowly with eyes open. Change one command and retry.'],
         measure='Count commands and note where the first mismatch happened.',
         reflect='Which instruction needed more detail? How could you make it repeatable?',
         care='An adult checks the route. Walk only, keep eyes open, and avoid stairs. A seated version can move a finger across paper.'),
    dict(id='shadow-stadium', title='Shadow Stadium', minutes=15, space='table', adult=False,
         materials=['paper', 'blocks'],
         challenge='Use room light to make a block cast a shadow onto a paper field.',
         predict='How will the shadow change when the block moves closer to the paper?',
         steps=['Lay paper on a table near an existing room light.', 'Place a block on the paper and observe its shadow.', 'Move the block to three positions while leaving the light alone.'],
         measure='Compare shadow lengths using the edge of another sheet of paper.',
         reflect='Which movement changed the shadow most? What else might affect it?',
         care='Use existing room lighting. Do not touch lamps, climb, or look at the sun.'),
]
MATERIALS = sorted({m for q in QUESTS for m in q['materials']})


def plan(materials, minutes, space, adult=False, buffer=0):
    """Maximize activity minutes without exceeding the budget; deterministic ties."""
    if isinstance(minutes, bool) or not isinstance(minutes, int) or minutes < 1:
        raise ValueError('minutes must be a positive integer')
    if isinstance(buffer, bool) or not isinstance(buffer, int) or buffer < 0:
        raise ValueError('buffer must be a nonnegative integer')
    if space not in ('table', 'floor', 'both'):
        raise ValueError('space must be table, floor, or both')
    supplied = set(materials)
    unknown = supplied - set(MATERIALS)
    if unknown:
        raise ValueError('unknown materials: ' + ', '.join(sorted(unknown)))
    eligible, excluded = [], []
    for q in QUESTS:
        reasons = []
        missing = sorted(set(q['materials']) - supplied)
        if missing:
            reasons.append('missing materials: ' + ', '.join(missing))
        if space != 'both' and q['space'] != space:
            reasons.append('needs ' + q['space'] + ' space')
        if q['adult'] and not adult:
            reasons.append('needs adult participation')
        if q['minutes'] + buffer > minutes:
            reasons.append('needs at least ' + str(q['minutes'] + buffer) + ' minutes including buffer')
        if reasons:
            excluded.append(dict(id=q['id'], reasons=reasons))
        else:
            eligible.append(q)
    best, used = (), 0
    # Exhaustive selection is intentional for this small, curated catalog.
    for size in range(1, len(eligible) + 1):
        for selection in itertools.combinations(eligible, size):
            total = sum(q['minutes'] for q in selection)
            if used < total and total + size * buffer <= minutes:
                best, used = selection, total
    selected_ids = {q['id'] for q in best}
    excluded.extend(dict(id=q['id'], reasons=['not selected within the shared time budget'])
                    for q in eligible if q['id'] not in selected_ids)
    return dict(minutes=used, buffer_per_mission=buffer, buffer_minutes=len(best)*buffer,
                total_minutes=used+len(best)*buffer, remaining=minutes-used-len(best)*buffer,
                quests=list(best), excluded=excluded)


def markdown(result):
    lines = ['# Backyard Quest Lab', '',
             f"Activity time: {result['minutes']} minutes; setup/cleanup allowance: {result['buffer_minutes']} minutes; total: {result['total_minutes']} minutes; unused budget: {result['remaining']} minutes.",
             'Setup/cleanup allowance is an estimate; adjust it for your family. An adult should choose activities suited to the participants.', '']
    if not result['quests']:
        lines += ['No missions match these constraints. See the reasons below.', '']
    for q in result['quests']:
        lines += [f"## {q['title']} ({q['minutes']} min)", '', q['challenge'], '',
                  'Materials: ' + ', '.join(q['materials']), '', '**Predict:** ' + q['predict'], '']
        lines += [f'{i}. {step}' for i, step in enumerate(q['steps'], 1)]
        lines += ['', '**Measure:** ' + q['measure'], '', '**Reflect:** ' + q['reflect'], '',
                  '**Care:** ' + q['care'], '', 'Our prediction: ____________________',
                  'What happened: ____________________', 'Next change: ____________________', '']
    if result['excluded']:
        lines += ['## Not included', '']
        lines += ['- ' + x['id'] + ': ' + '; '.join(x['reasons']) for x in result['excluded']]
    return '\n'.join(lines) + '\n'


def html_cards(result):
    """Render a portable, script-free worksheet; escape all activity text."""
    e = lambda value: escape(str(value), quote=True)
    parts = ["<!doctype html><html lang='en'><meta charset='utf-8'>",
             "<meta name='viewport' content='width=device-width,initial-scale=1'>",
             "<title>Backyard Quest Lab — Mission cards</title>",
             """<style>
body{font:17px/1.55 system-ui,sans-serif;color:#19382e;background:#f5f3e9;margin:0}
main{max-width:850px;margin:auto;padding:32px 20px}h1{font-size:2.5rem;line-height:1.1}
h2{line-height:1.2}article{background:white;border:1px solid #bccbbf;border-radius:14px;padding:28px;margin:24px 0}
.tag{font-weight:700;color:#386446}.care{border-left:4px solid #a97518;padding-left:16px}
.write{display:block;border-bottom:1px solid #8e9f94;min-height:44px;margin-top:12px}
li{margin:8px 0}.note{color:#476354}footer{font-size:.9rem}
@media(max-width:500px){main{padding:20px 12px}article{padding:18px}h1{font-size:2rem}}
@media print{@page{margin:15mm}body{background:white;font-size:11pt}main{max-width:none;padding:0}article{break-before:page;border:0;border-radius:0;padding:0;margin:0}h2,h3{break-after:avoid}li,.care,.write{break-inside:avoid}.screen{display:none}}
</style><main><header><p class='tag'>MAKE · TRY · DISCOVER</p><h1>Backyard Quest Lab</h1>""",
             f"<p>Activity time: {e(result['minutes'])} minutes · Setup/cleanup: {e(result['buffer_minutes'])} minutes · Total: {e(result['total_minutes'])} minutes · Unused budget: {e(result['remaining'])} minutes</p>",
             "<p>Setup/cleanup allowance is an estimate; adjust it for your family. An adult should choose activities suited to the participants.</p>",
             "<p class='screen note'>Use your browser’s Print command. Each mission starts on a new printed page.</p></header>"]
    if not result['quests']:
        parts.append('<p>No missions match these constraints. See the reasons below.</p>')
    for q in result['quests']:
        parts.extend([f"<article><p class='tag'>{e(q['minutes'])} MIN · {e(q['space']).upper()}</p><h2>{e(q['title'])}</h2>",
                      f"<p>{e(q['challenge'])}</p><p><strong>Materials:</strong> {e(', '.join(q['materials']))}</p>",
                      f"<h3>Predict</h3><p>{e(q['predict'])}</p><h3>Build and test</h3><ol>"])
        parts.extend('<li>' + e(step) + '</li>' for step in q['steps'])
        parts.extend([f"</ol><h3>Measure</h3><p>{e(q['measure'])}</p><h3>Reflect</h3><p>{e(q['reflect'])}</p>",
                      f"<p class='care'><strong>Care:</strong> {e(q['care'])}</p>",
                      "<div class='write'>Our prediction:</div><div class='write'>What happened:</div><div class='write'>Next change:</div></article>"])
    if result['excluded']:
        parts.append('<section><h2>Not included</h2><ul>')
        parts.extend('<li>' + e(x['id']) + ': ' + e('; '.join(x['reasons'])) + '</li>' for x in result['excluded'])
        parts.append('</ul></section>')
    parts.append('<footer>Original family maker missions · No accounts or network access needed.</footer></main></html>')
    return '\n'.join(parts) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--materials', nargs='+', choices=MATERIALS, required=True)
    parser.add_argument('--minutes', type=int, required=True)
    parser.add_argument('--space', choices=['table', 'floor', 'both'], required=True)
    parser.add_argument('--buffer', type=int, default=0, help='Setup/cleanup minutes reserved per selected mission (default: 0)')
    parser.add_argument('--adult', action='store_true', help='An adult will participate in activities that require it')
    output = parser.add_mutually_exclusive_group()
    output.add_argument('--html', action='store_true', help='Output standalone printable HTML cards')
    output.add_argument('--json', action='store_true', help='Output structured plan instead of printable Markdown')
    args = parser.parse_args()
    try:
        result = plan(args.materials, args.minutes, args.space, args.adult, args.buffer)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2) if args.json else html_cards(result) if args.html else markdown(result), end='\n' if args.json else '')


if __name__ == '__main__':
    main()
