# Script para remover comentários de HTML, CSS e JavaScript
# Preserva todo o código funcional

function Remove-Comments {
    param(
        [string]$Content,
        [string]$FileType
    )
    
    $result = $Content
    
    if ($FileType -eq 'html') {
        # Remove comentários HTML <!-- -->
        $result = $result -replace '<!--[\s\S]*?-->', ''
        
        # Remove comentários JavaScript // (apenas linhas completas ou finais de linha)
        $result = $result -replace '(?m)^\s*//.*$', ''
        $result = $result -replace '(?m)\s+//[^"\n]*$', ''
        
        # Remove comentários JavaScript /* */
        $result = $result -replace '/\*[\s\S]*?\*/', ''
    }
    elseif ($FileType -eq 'css') {
        # Remove comentários CSS /* */
        $result = $result -replace '/\*[\s\S]*?\*/', ''
    }
    elseif ($FileType -eq 'js') {
        # Remove comentários JavaScript // (apenas linhas completas ou finais de linha)
        $result = $result -replace '(?m)^\s*//.*$', ''
        $result = $result -replace '(?m)\s+//[^"\n]*$', ''
        
        # Remove comentários JavaScript /* */
        $result = $result -replace '/\*[\s\S]*?\*/', ''
    }
    
    # Remove linhas vazias excessivas (mais de 2 seguidas)
    $result = $result -replace '(?m)^\s*$\n(?:\s*$\n)+', "`n`n"
    
    return $result
}

function Process-Files {
    param(
        [string]$Path,
        [string]$Filter,
        [string]$FileType
    )
    
    $files = Get-ChildItem -Path $Path -Filter $Filter -Recurse -ErrorAction SilentlyContinue
    $count = 0
    
    foreach ($file in $files) {
        try {
            $content = Get-Content $file.FullName -Raw -Encoding UTF8 -ErrorAction Stop
            
            if ($content) {
                $newContent = Remove-Comments -Content $content -FileType $FileType
                
                # Só escreve se houve mudanças
                if ($newContent -ne $content) {
                    Set-Content -Path $file.FullName -Value $newContent -Encoding UTF8 -NoNewline
                    $count++
                    Write-Host "✓ Processado: $($file.Name)" -ForegroundColor Green
                }
            }
        }
        catch {
            Write-Host "✗ Erro ao processar: $($file.Name) - $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    return $count
}

Write-Host "`n=== Removendo Comentários ===" -ForegroundColor Cyan
Write-Host "Iniciando processo...`n" -ForegroundColor Yellow

# Processar ficheiros HTML
Write-Host "Processando ficheiros HTML..." -ForegroundColor Cyan
$htmlCount = Process-Files -Path "templates" -Filter "*.html" -FileType "html"
Write-Host "Total HTML processados: $htmlCount`n" -ForegroundColor Yellow

# Processar ficheiros CSS
Write-Host "Processando ficheiros CSS..." -ForegroundColor Cyan
$cssCount = Process-Files -Path "static/css" -Filter "*.css" -FileType "css"
Write-Host "Total CSS processados: $cssCount`n" -ForegroundColor Yellow

# Processar ficheiros JS
Write-Host "Processando ficheiros JS..." -ForegroundColor Cyan
$jsCount = Process-Files -Path "static/js" -Filter "*.js" -FileType "js"
Write-Host "Total JS processados: $jsCount`n" -ForegroundColor Yellow

Write-Host "=== Processo Concluído ===" -ForegroundColor Green
Write-Host "Total de ficheiros modificados: $($htmlCount + $cssCount + $jsCount)" -ForegroundColor Green
