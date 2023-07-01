import re
from typing import Sequence

from ai import complete
from config import LIMIT_CHANGES_PER_CHANGESET
from um_poi import UmPoi


def ai_name_convert(pois: Sequence[UmPoi]) -> Sequence[UmPoi]:
    batch_size = 20
    task = []
    result = []

    for p in pois:
        if p.name:
            task.append(p)
        else:
            result.append(p)

    for i in range(0, len(task), batch_size):
        if len(result) >= 1.5 * LIMIT_CHANGES_PER_CHANGESET:
            break

        batch = task[i:i + batch_size]
        names = tuple(p.name for p in batch)
        query = '\n'.join(f'{j},{name}' for j, name in enumerate(names, 1))

        print(f'🤖 [{i + batch_size}/{len(task)}] Querying AI...')
        answer = complete(
            ('You are provided with a list of restaurant names, which are sometimes descriptive. '
             'These names originate from a Polish data source. '
             'Your task is to extract an own name for each restaurant. '
             'The output will be in CSV format, just like the input.'),

            ('1,lokal gastronomiczny Sao Do Asia Food\n'
             '2,"BoQ"\n'
             '3,Restauracja Garden w hotelu Double Tree by Hilton\n'
             '4,Klub Sosnowy\n'
             '5,Spiewajaca Lipka\n'
             '6,Bar Alchemy w hotelu\n'
             '7,w klubie tenisowym Wilga\n'
             '8,bar w Hotelu "Boss"\n'
             '9,ruchomy punkt gastronomiczny (room service, mini bar, VIP Lounge)\n'
             '10,na terenie tymczasowego targowiska "Kawiarnia Olkuska"'),

            ('1,Sao Do Asia Food\n'
             '2,BoQ\n'
             '3,Garden\n'
             '4,Klub Sosnowy\n'
             '5,Śpiewająca Lipka\n'
             '6,Alchemy\n'
             '7,Wilga\n'
             '8,Boss\n'
             '9,Ruchomy punkt gastronomiczny\n'
             '10,Kawiarnia Olkuska'),

            query)

        answer_lines = answer.splitlines()
        assert len(answer_lines) == len(batch), 'Unexpected answer'

        for j, (p, line) in enumerate(zip(batch, answer_lines), 1):
            parts = line.split(',', maxsplit=1)
            assert len(parts) == 2, f'Unexpected answer line: {line!r}'
            assert int(parts[0]) == j, f'Unexpected answer line: {line!r}'

            new_name = parts[1].strip()
            print(f'💡 {p.name!r} -> {new_name!r}')
            result.append(p._replace(name=new_name))

    # reverse to put unnamed POIs at the end
    result.reverse()

    return tuple(result)
