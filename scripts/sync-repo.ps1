$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$gitArgs = @('-c', "safe.directory=$repoRoot", '-C', $repoRoot)

function Invoke-Git {
    param([string[]]$Args)
    & git @gitArgs @Args
}

try {
    $status = Invoke-Git @('status', '--porcelain')
    if ($status) {
        Write-Warning 'Repositorio com alteracoes locais. Auto-sync ignorado para nao sobrescrever trabalho em andamento.'
        exit 0
    }

    Invoke-Git @('fetch', 'origin', '--prune') | Out-Null
    $counts = (Invoke-Git @('rev-list', '--left-right', '--count', 'origin/main...HEAD')).Trim() -split "`t| "
    $behind = [int]$counts[0]
    $ahead = [int]$counts[1]

    if ($behind -gt 0 -and $ahead -eq 0) {
        Write-Host "Atualizando repositorio local via fast-forward ($behind commit(s))..."
        Invoke-Git @('pull', '--ff-only', 'origin', 'main')
        exit 0
    }

    if ($behind -gt 0 -and $ahead -gt 0) {
        Write-Warning 'Repositorio divergiu do origin/main. Auto-sync ignorado; faça merge/rebase manualmente.'
        exit 0
    }

    Write-Host 'Repositorio local ja esta sincronizado com origin/main.'
    exit 0
}
catch {
    Write-Warning ("Falha no auto-sync: " + $_.Exception.Message)
    exit 0
}
