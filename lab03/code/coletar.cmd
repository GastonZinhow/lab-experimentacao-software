@echo off
rem Roda a coleta completa e a conferencia, gravando o log em .cache\pipeline.log.
rem Se for interrompida (reinicio, queda de rede), basta rodar de novo: o cache retoma.
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
echo ==== inicio %date% %time% >> .cache\pipeline.log
python -u -m pipeline --config config.yaml >> .cache\pipeline.log 2>&1
python -u conferencia.py --config config.yaml >> .cache\pipeline.log 2>&1
echo ==== fim %date% %time% (conferencia: %errorlevel%) >> .cache\pipeline.log
