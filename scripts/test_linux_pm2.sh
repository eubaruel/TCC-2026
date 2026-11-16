#!/usr/bin/env bash
set -Eeuo pipefail
PROJECT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ "${1:-}" == --child ]]; then
    source "$PROJECT/LINUX_INICIAR_PM2"
    TCC_ROOT="$TCC_TEST_ROOT"
    uname() { if [[ "$1" == -s ]]; then echo Linux; else echo x86_64; fi; }
    ldd() { echo 'ldd (GNU libc) 2.39'; }
    tcc_system_dependencies() { echo system >> "$TCC_TEST_LOG"; }
    tcc_python() { TCC_PYTHON=tcc_fake_python; }
    tcc_node() { echo node >> "$TCC_TEST_LOG"; }
    tcc_pm2() { echo pm2-ready >> "$TCC_TEST_LOG"; }
    tcc_fake_python() {
        printf 'prepare %s\n' "$*" >> "$TCC_TEST_LOG"
        [[ "$TCC_TEST_SCENARIO" != failure ]]
    }
    pm2() {
        printf 'pm2 %s\n' "$*" >> "$TCC_TEST_LOG"
        if [[ "$1" == jlist ]]; then
            if [[ "$TCC_TEST_SCENARIO" == first ]]; then echo '[]';
            elif [[ "$TCC_TEST_SCENARIO" == invalid-json ]]; then echo 'invalid';
            else echo '[{"name":"frontend"},{"name":"sistema-correcao"},{"name":"api-principal"},{"name":"unrelated"}]'; fi
        fi
    }
    # Top-level call: preserva errexit para testar falhas reais de preparacao.
    tcc_start --reinstalar
    exit 0
fi

TEST_TEMP="$(mktemp -d)"
trap 'rm -rf -- "$TEST_TEMP"' EXIT
export TCC_TEST_ROOT="$TEST_TEMP/project with spaces"
mkdir -p "$TCC_TEST_ROOT/backend/.venv-leitor/bin"
printf 'URI_BD=mongodb://example.invalid\n' > "$TCC_TEST_ROOT/backend/.env"
printf '#!/usr/bin/env bash\necho smoke >> "$TCC_TEST_LOG"\n' > "$TCC_TEST_ROOT/backend/.venv-leitor/bin/python"
chmod +x "$TCC_TEST_ROOT/backend/.venv-leitor/bin/python"
for scenario in existing first failure invalid-json; do
    export TCC_TEST_SCENARIO="$scenario" TCC_TEST_LOG="$TEST_TEMP/$scenario.log"
    set +e
    bash "$0" --child > "$TEST_TEMP/$scenario.out" 2>&1
    result=$?
    set -e
    if [[ "$scenario" == failure || "$scenario" == invalid-json ]]; then
        [[ "$result" != 0 ]]
        ! grep -q '^pm2 delete\|^pm2 start' "$TCC_TEST_LOG"
    else
        [[ "$result" == 0 ]] || { cat "$TEST_TEMP/$scenario.out"; exit 1; }
        grep -q '^prepare .*--preparar --reinstalar$' "$TCC_TEST_LOG"
        grep -q '^smoke$' "$TCC_TEST_LOG"
        grep -q '^pm2 start .*/ecosystem.config.js$' "$TCC_TEST_LOG"
        if [[ "$scenario" == existing ]]; then
            [[ "$(grep -c '^pm2 delete' "$TCC_TEST_LOG")" == 3 ]]
            ! grep -q '^pm2 delete unrelated' "$TCC_TEST_LOG"
        else
            ! grep -q '^pm2 delete' "$TCC_TEST_LOG"
        fi
    fi
    printf 'PASS: %s\n' "$scenario"
done
