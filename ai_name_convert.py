from collections.abc import Sequence

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

        batch = task[i : i + batch_size]
        names = tuple(p.name for p in batch)
        query = '\n'.join(f'{j},{name}' for j, name in enumerate(names, 1))

        print(f'🤖 [{i + batch_size}/{len(task)}] Querying AI...')
        answer = complete(
            (
                'You are provided with a list of restaurant names, which are sometimes descriptive. '
                'These names originate from a Polish data source. '
                "Your task is to extract an own name for each restaurant - if there isn't one, you output nothing. "
                'The output will be in CSV format, just like the input.'
            ),
            (
                '1,mała gastronomia\n'
                '2,lokal gastronomiczny Sao Do Asia Food\n'
                '3,"BoQ"\n'
                '4,Restauracja Garden w hotelu Double Tree by Hilton\n'
                '5,Klub Sosnowy\n'
                '6,Barek z Wygrodzonym Ogródkiem\n'
                '7,Spiewajaca Lipka\n'
                '8,Bar Alchemy w hotelu "Lisbon"\n'
                '9,w klubie tenisowym Wilga\n'
                '10,bar w Hotelu "Boss"\n'
                '11,bufet dla publiczności w Kasynie\n'
                '12,ruchomy punkt gastronomiczny (room service, mini bar, VIP Lounge)\n'
                '13,restauracja Indyjska\n'
                '14,restauracja\n'
            ),
            (
                '1,\n'
                '2,Sao Do Asia Food\n'
                '3,BoQ\n'
                '4,Garden\n'
                '5,Klub Sosnowy\n'
                '6,\n'
                '7,Śpiewająca Lipka\n'
                '8,Alchemy\n'
                '9,Wilga\n'
                '10,Boss\n'
                '11,\n'
                '12,\n'
                '13,\n'
                '14,\n'
            ),
            query,
        )

        answer_lines = answer.splitlines()
        if len(answer_lines) != len(batch):
            raise RuntimeError('Unexpected answer')

        for j, (p, line) in enumerate(zip(batch, answer_lines, strict=True), 1):
            parts = line.split(',', maxsplit=1)

            if len(parts) != 2 or int(parts[0]) != j:
                raise RuntimeError(f'Unexpected answer line: {line!r}')

            new_name = parts[1].strip()
            print(f'💡 {p.name!r} -> {new_name!r}')
            result.append(p._replace(name=new_name))

    # reverse to put unnamed POIs at the end
    result.reverse()

    return tuple(result)
