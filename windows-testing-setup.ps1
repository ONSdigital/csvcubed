$path = (Get-ItemProperty -Path 'Registry::HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\Environment' -Name PATH).path

$initialWorkingDir = $pwd

echo "=== Installing csvlint ==="

mkdir csvlint
cd csvlint

Invoke-WebRequest -Uri https://curl.se/windows/dl-7.86.0/curl-7.86.0-win64-mingw.zip -OutFile "curl.zip"
Expand-Archive -LiteralPath curl.zip -DestinationPath .
cp curl-7.86.0-win64-mingw\bin\libcurl-x64.dll curl-7.86.0-win64-mingw\bin\libcurl.dll 
cp curl-7.86.0-win64-mingw\bin\* C:\hostedtoolcache\windows\Ruby\2.4.10\x64\bin

gem install bundle
bundle init
bundle add i18n --version "~>1.12.0"
bundle add csvlint --git https://github.com/GSS-Cogs/csvlint.rb --ref v0.6.7

$gemDir = gem environment gemdir

bundle config set bin bin
bundle config set path "$gemDir"
bundle install

$csvLintInstallationFolder = (Get-Item bin | Resolve-Path).Path.Substring(38)

echo "@REM Forwarder script`n@echo off`necho Attempting to launch csvlint`nC:\hostedtoolcache\windows\Ruby\2.4.10\x64\bin\ruby $csvLintInstallationFolder\csvlint %*" > "$csvLintInstallationFolder\csvlint.bat"

$path = "$path;$csvLintInstallationFolder"

cd "$initialWorkingDir"

echo "=== Installing csv2rdf ==="

Invoke-WebRequest -Uri "https://github.com/Swirrl/csv2rdf/releases/download/0.4.7/csv2rdf-0.4.7-standalone.jar" -OutFile "csv2rdf.jar"
$csv2rdfPath = (Get-Item csv2rdf.jar | Resolve-Path).Path.Substring(38)
Set-Content -Path csv2rdf.bat -Value "@REM Forwarder script`n@echo off`necho Attempting to launch csv2rdf at $csv2rdfPath`njava -jar $csv2rdfPath %*" 

$csv2rdfLocation = (Get-Item csv2rdf.bat | Resolve-Path).Path.Substring(38)

$path = "$path;$pwd"

echo "=== Installing sparql-test-runner ==="

Invoke-WebRequest -Uri "https://github.com/GSS-Cogs/sparql-test-runner/releases/download/v0.0.1/sparql-test-runner-1.4.zip" -OutFile "sparql-test-runner.zip"
Expand-Archive -LiteralPath sparql-test-runner.zip -DestinationPath .

$sparqlTestRunnerBinDir = (Get-Item sparql-test-runner-1.4/bin | Resolve-Path).Path.Substring(38)
$path = "$path;$sparqlTestRunnerBinDir"

# sparql tests need to be available as well.
git clone --depth 1 https://github.com/GSS-Cogs/gdp-sparql-tests.git

echo "Setting path"
Set-ItemProperty -Path 'Registry::HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\Environment' -Name PATH -Value $path
echo $path