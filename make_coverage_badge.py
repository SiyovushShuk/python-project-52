import json
import sys

import coverage


def main() -> int:
    cov = coverage.Coverage()
    try:
        cov.load()
    except coverage.CoverageException:
        print('No coverage data found — run coverage run first', file=sys.stderr)
        return 1

    total = int(round(cov.report(show_missing=False, skip_covered=False, ignore_errors=True)))

    if total >= 90:
        color = 'brightgreen'
    elif total >= 80:
        color = 'green'
    elif total >= 70:
        color = 'yellowgreen'
    elif total >= 50:
        color = 'orange'
    else:
        color = 'red'

    payload = {
        'schemaVersion': 1,
        'label': 'coverage',
        'message': f'{total}%',
        'color': color,
    }
    with open('coverage-badge.json', 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False)
    print(f'Wrote coverage-badge.json: {total}% ({color})')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
