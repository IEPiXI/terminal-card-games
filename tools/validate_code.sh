#!/usr/bin/env bash
set -euo pipefail

# navigate to repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

# run ruff lint and format checks
ruff check "$@"
ruff format --check "$@"

# check that comments start with a lowercase letter
python3 -c "
import glob, re, sys
bad = [f'{p}:{i}: {line.strip()}' for p in glob.glob('**/*.py', recursive=True)
       if not p.startswith('.git')
       for i, line in enumerate(open(p), 1)
       if (m := re.search(r'#\s*([A-Za-z])', line)) and m.group(1).isupper()
       and not any(line.split('#', 1)[1].strip().startswith(x) for x in ('noqa', 'type:', 'pylint:', 'pragma:'))]
if bad:
    print('comments starting with capital letter found:\n' + '\n'.join(bad))
    sys.exit(1)
"
