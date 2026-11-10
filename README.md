# Harvest Moon SNES Power Berry Checker

Ferramenta em Python para ler um save SRAM (`.srm`) de **Harvest Moon para SNES** e exibir marcadores de eventos associados às Power Berries. Também verifica o estado do diamante azul, que permite inferir se a cena da flor de inverno já foi acionada quando se sabe que o item foi obtido anteriormente.

O estudo foi feito com base no projeto de decompilação [HarvestMoonSNES](https://github.com/dzik87/HarvestMoonSNES), inspeções no Memory Viewer do Mesen, comparações de SRAM e leitura de dados no ImHex. As conclusões são inferências sobre a versão e os saves analisados; não são garantias universais para todas as revisões do jogo ou todas as condições de save.

## Requisitos

- Python 3.10 ou superior
- Um arquivo `.srm` de 8 KiB com os slots de save do jogo

Não há dependências externas.

## Uso

```sh
python3 tools/check_power_berry_events.py "/caminho/para/Harvest Moon.srm"
```

Por padrão, o programa valida os checksums e seleciona o slot marcado como o mais recente. Para escolher explicitamente um slot:

```sh
python3 tools/check_power_berry_events.py "/caminho/para/Harvest Moon.srm" --slot 0
python3 tools/check_power_berry_events.py "/caminho/para/Harvest Moon.srm" --slot 1
```

O resultado classifica os marcadores persistentes conhecidos como presentes/ausentes e informa os campos relevantes do diamante azul. Nenhum save é alterado.

## Interpretando a flor de inverno

Não foi encontrado um bit persistente dedicado à cena. A inferência usa o inventário: o diamante azul aparece em um dos slots de ferramenta ou no depósito antes de ser usado; a rotina que inicia a cena o consome. Assim, se há certeza de que o save já teve o diamante, sua ausência indica que ele foi usado nessa cena.

Um `.srm` isolado não consegue distinguir “consumido” de “nunca obtido”. Cheats que restauram itens também mudam a interpretação. O verificador explicita essa limitação.

## Documentação do estudo

- [Histórico, método, resultados e limitações](docs/estudo.md)
- [Mapa dos campos do SRAM usados pelo programa](docs/layout-sram.md)

## Base de engenharia reversa

Este programa não é uma ferramenta oficial do jogo. A análise toma como referência o disassembly e os dados mantidos no projeto [dzik87/HarvestMoonSNES](https://github.com/dzik87/HarvestMoonSNES). Ver [docs/estudo.md](docs/estudo.md) para os caminhos de código consultados, as observações no Mesen/ImHex e os resultados experimentais.
