# Matar processos vim
Get-Process | Where-Object {$_.ProcessName -match "vim|vi"} | Stop-Process -Force -ErrorAction SilentlyContinue

# Remover ficheiros swap
Remove-Item ".git/.COMMIT_EDITMSG.swp" -Force -ErrorAction SilentlyContinue
Remove-Item ".git/COMMIT_EDITMSG" -Force -ErrorAction SilentlyContinue
Remove-Item ".git/MERGE_MSG" -Force -ErrorAction SilentlyContinue

# Configurar editor para notepad
git config --global core.editor "notepad"

# Verificar estado
Write-Host "Estado do Git:" -ForegroundColor Green
git status

# Fazer push forçado
Write-Host "`nFazendo push..." -ForegroundColor Yellow
git push origin master --force

Write-Host "`nConcluído!" -ForegroundColor Green
