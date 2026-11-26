"""Offline family maker missions. Standard library only."""
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


def plan(materials, minutes, space, adult=False):
    """Maximize activity minutes without exceeding the budget; deterministic ties."""
    if isinstance(minutes, bool) or not isinstance(minutes, int) or minutes < 1:
        raise ValueError('minutes must be a positive integer')
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
        if q['minutes'] > minutes:
            reasons.append('needs at least ' + str(q['minutes']) + ' minutes')
        if reasons:
            excluded.append(dict(id=q['id'], reasons=reasons))
        else:
            eligible.append(q)
    best, used = (), 0
    # Exhaustive selection is intentional for this small, curated catalog.
    for size in range(1, len(eligible) + 1):
        for selection in itertools.combinations(eligible, size):
            total = sum(q['minutes'] for q in selection)
            if used < total <= minutes:
                best, used = selection, total
    selected_ids = {q['id'] for q in best}
    excluded.extend(dict(id=q['id'], reasons=['not selected within the shared time budget'])
                    for q in eligible if q['id'] not in selected_ids)
    return dict(minutes=used, remaining=minutes-used, quests=list(best), excluded=excluded)


def markdown(result):
    lines = ['# Backyard Quest Lab', '',
             f"Activity time: {result['minutes']} minutes; unused budget: {result['remaining']} minutes.",
             'Allow extra time for setup and cleanup. An adult should choose activities suited to the participants.', '']
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--materials', nargs='+', choices=MATERIALS, required=True)
    parser.add_argument('--minutes', type=int, required=True)
    parser.add_argument('--space', choices=['table', 'floor', 'both'], required=True)
    parser.add_argument('--adult', action='store_true', help='An adult will participate in activities that require it')
    parser.add_argument('--json', action='store_true', help='Output structured plan instead of printable Markdown')
    args = parser.parse_args()
    try:
        result = plan(args.materials, args.minutes, args.space, args.adult)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2) if args.json else markdown(result), end='\n' if args.json else '')


if __name__ == '__main__':
    main()
