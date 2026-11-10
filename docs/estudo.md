# Estudo dos eventos de Power Berry

[English version](estudo.en.md)

[Versión en español](estudio.es.md)

## Objetivo

Identificar, a partir de um save SRAM de Harvest Moon para SNES, quais eventos associados às dez Power Berries parecem já ter ocorrido. O objetivo prático é apontar eventos ainda não acionados, inclusive quando o jogo não mantém uma flag explícita para a cena.

O estudo combina o projeto de decompilação [HarvestMoonSNES](https://github.com/dzik87/HarvestMoonSNES), inspeção da WRAM pelo Memory Viewer do Mesen, leitura de bytes no ImHex e comparação de arquivos `.srm` de antes/depois. O disassembly serviu como guia para localizar rotinas, endereços e campos e para formular interpretações do código. Os saves experimentais vieram de uma ROM comum do jogo, disponível publicamente há anos, não de uma build do projeto de decompilação. Portanto, o verificador analisa saves SRAM normais do jogo; eles não precisam ter sido produzidos por uma ROM compilada a partir desse projeto. As conclusões abaixo são inferências e podem depender da revisão do jogo.

## 1. Primeira hipótese: localizar flags persistentes

A primeira etapa foi mapear os campos de energia e as flags do jogo. As variáveis relevantes encontradas no disassembly incluem:

| WRAM | Offset Mesen | Uso identificado |
|---|---:|---|
| `$7E:0917` | `$00917` | Stamina máxima atual. A rotina de consumo de Power Berry soma `$0A`. |
| `$7F:1F36` | `$11F36` | `nPowerBerryEaten`, contador de berries consumidas. |
| `$7F:1F5A`–`$7F:1F63` | `$11F5A`–`$11F63` | Flags diárias; são estado temporário, não um registro persistente por evento. |
| `$7F:1F64`–`$7F:1F73` | `$11F64`–`$11F73` | `event1`–`event8`, flags permanentes gravadas no save. |

Ao consumir uma Power Berry, o jogo incrementa o contador, aumenta a stamina máxima em 10 e aumenta a felicidade. Isso informa que uma berry foi comida, mas não identifica qual evento a forneceu. A berry também pode ser obtida sem consumo automático.

### Correção de uma hipótese antiga

O arquivo de notas inicial sugeria que `daily1` bit `$0080` poderia estar ligado à flor de inverno. Essa interpretação não foi confirmada e deve ser considerada incorreta para fins deste verificador: flags diárias não constituem prova persistente de que o evento da flor ocorreu. Também não se deve usar um bit diário isolado como histórico após salvar/recarregar ou avançar a noite.

## 2. Marcadores persistentes encontrados

O save tem oito palavras de eventos em `slot+0x60` a `slot+0x76`. As máscaras abaixo foram relacionadas a rotinas/eventos no código-fonte e usadas pelo programa:

| Evento / ramo | Campo SRAM | Máscara | O que o marcador sustenta | Limite da interpretação |
|---|---:|---:|---|---|
| Estátua da galinha | `slot+0x60` (`event1`) | `0x0200` | Ramo associado ao script da Power Berry. | O bit registra o ramo/script descrito no código, não necessariamente consumo do item. |
| Achado raro com enxada 1 | `slot+0x60` (`event1`) | `0x0800` | Primeiro marcador de achado raro com enxada. | Não é um contador universal de berries. |
| Achado raro com enxada 2 | `slot+0x60` (`event1`) | `0x1000` | Segundo marcador de achado raro com enxada. | Mesma ressalva. |
| Achado associado ao machado | `slot+0x60` (`event1`) | `0x0400` | Marcador associado ao achado com machado. | O vínculo é interpretado a partir do código de ferramenta. |
| Oferta do mercador no outono | `slot+0x62` (`event2`) | `0x4000` | A oferta foi iniciada. | Não prova que a troca foi aceita. |
| Peixe devolvido / espírito da água | `slot+0x62` (`event2`) | `0x2000` | Evento de soltar o peixe; o script associado faz aparecer uma berry. | Não prova que a berry foi consumida. |
| Cena dos duendes na caverna | `slot+0x64` (`event3`) | `0x2000` | Cena associada à entrega da foice. | A ligação com a recompensa é inferida pelo fluxo de AI. |
| Caça aos ovos | `slot+0x70` (`event5`) | `0x3C00` | Algum dos ramos A–D de prêmio foi registrado. | Os bits não identificam isoladamente qual berry ou prêmio foi obtido. |
| Festival da colheita | `slot+0x70` (`event5`) | `0x8000` | Ramo do festival que incrementa o contador geral de berries. | Não prova consumo posterior. |

Esses nove marcadores cobrem eventos/ramificações úteis para a análise. Algumas máscaras representam ramos de evento e não uma contagem simples de “berry coletada”. O programa preserva essa distinção no texto do resultado.

## 3. Flor de inverno e diamante azul

### O que o código mostra

No projeto de decompilação, `fToolUsedAction0x17_BlueDiamond` em [`src/code/bank_82/tools.asm`](https://github.com/dzik87/HarvestMoonSNES/blob/master/src/code/bank_82/tools.asm) valida o horário, a área da montanha de inverno e o objeto à frente. Ao encontrar o objeto esperado (`$F6`), inicia o script AI `$12` e zera `toolEquipped`.

O script [`src/ai/us/scripts/script_12.asm`](https://github.com/dzik87/HarvestMoonSNES/blob/master/src/ai/us/scripts/script_12.asm) executa a cena. Não foi encontrado nesse fluxo um bit dedicado de `event1`–`event8` que registre permanentemente “flor de inverno concluída”. A rotina de restauração da área de topo de montanha no inverno também é vazia em [`src/code/bank_81/items_misc.asm`](https://github.com/dzik87/HarvestMoonSNES/blob/master/src/code/bank_81/items_misc.asm).

Inicialmente, `STZ toolEquipped` parecia poder significar apenas desequipar. A inspeção do fluxo de armazenamento e o experimento do jogador esclareceram a interpretação: o diamante é retirado do inventário ao ser usado nessa cena; restaurá-lo com Action Replay permitiu repetir o evento e obter novamente a Power Berry. Essa evidência empírica sustenta que o consumo é o mecanismo que impede a repetição normal.

### Como o inventário fica representado no save

O formato de save documentado em `src/code/bank_83/game_engine.asm` grava:

- ferramenta equipada em `slot+0x0F`;
- segunda ferramenta em `slot+0x1A`;
- depósito (shed) nos bytes `slot+0x84`–`slot+0x87`.

A tabela `nShedToolPlacementTable`, em [`assets/tables/data/tile_scripts.csv`](https://github.com/dzik87/HarvestMoonSNES/blob/master/assets/tables/data/tile_scripts.csv), associa o diamante azul (`EITEM_BLUEDIAMOND`, ID `$17`) ao byte da terceira linha do depósito (`slot+0x86`) e à máscara `$40`. O item é considerado disponível se estiver equipado, no segundo espaço ou no depósito.

Logo, a ausência do diamante pode servir como **marcador indireto da cena**, sob a premissa de que o save já teve o item. Um arquivo isolado sem o item não distingue “foi consumido” de “nunca foi obtido”; por isso o programa qualifica o resultado como inferência e documenta a condição.

## 4. Comparação experimental dos saves

Foram comparados `BEFORE.srm` e `AFTER.srm`, fornecidos pelo jogador e criados ao jogar uma ROM comum do jogo, disponível publicamente há anos (não uma build do projeto de decompilação). Ambos têm 8192 bytes; o slot 0 é o slot selecionado na análise. Os arquivos não são distribuídos neste repositório.

O jogador informou que os saves correspondem a 02/Winter e 03/Winter, depois de avançar um dia e realizar o evento/consumo. Valores observados no slot 0:

| Campo | Antes | Depois | Interpretação |
|---|---:|---:|---|
| `slot+0x17`, berries consumidas | `0x08` | `0x09` | Aumentou de 8 para 9. |
| `slot+0x0E`, stamina máxima | `0xB4` (180) | `0xBE` (190) | Aumento de 10 compatível com consumo de uma berry. |
| `slot+0x86`, terceira linha do depósito | `0x5E` | `0x1F` | O bit `$40` do diamante azul estava ligado e depois desligado. |
| `slot+0x1A`, segunda ferramenta | `0x0E` | `0x0E` | Sem mudança. |
| palavras `event1`–`event8` | sem mudança nos campos relevantes | sem mudança nos campos relevantes | Nenhuma flag permanente nova identificou a flor. |

O checksum validado é o do slot 0. O slot 1 foi ignorado por checksum inválido. A combinação “bit do diamante removido + contador de berries +1 + stamina máxima +10”, junto da confirmação do jogador de que a Power Berry do inverno foi consumida nesse intervalo, é evidência forte de que o item foi usado e a berry foi comida. Como o período também incluiu avanço de dia e outros dados mudaram, não se atribui cada byte alterado exclusivamente à cena.

## 5. Método e limites

1. Consultar no disassembly os writers/readers das variáveis de energia, flags de evento, ferramentas e dados de save.
2. Inspecionar endereços candidatos no Memory Viewer do Mesen durante o jogo.
3. Comparar valores de WRAM com os bytes do `.srm` usando o layout de slots e endianness little-endian.
4. Validar checksum e marcador do slot antes de interpretar os dados.
5. Comparar saves controlados antes/depois e cruzar os deltas com uma sequência de jogo conhecida.

Limitações conhecidas:

- O resultado é uma análise de engenharia reversa, não uma especificação oficial da Nintendo.
- O disassembly pode ter lacunas ou nomes de rotina provisórios; uma associação de bit com evento pode ser revisada.
- Flags de ramo não garantem que o item foi efetivamente coletado, mantido ou consumido.
- A ausência do diamante, em um único save, não prova histórico de posse. Cheats, edição de save ou outra perda externa quebram a inferência.
- O incremento de `nPowerBerryEaten` não informa a origem da berry.
- Resultados podem variar entre revisões regionais/ROMs, hacks, patches e comportamentos específicos de emulador.
- A análise deve ser repetida com saves da revisão que se pretende suportar.

## Referências de código

- Projeto de decompilação: [dzik87/HarvestMoonSNES](https://github.com/dzik87/HarvestMoonSNES)
- Fluxo do diamante azul: [`tools.asm`](https://github.com/dzik87/HarvestMoonSNES/blob/master/src/code/bank_82/tools.asm)
- Cena AI da flor: [`script_12.asm`](https://github.com/dzik87/HarvestMoonSNES/blob/master/src/ai/us/scripts/script_12.asm)
- Leitura/gravação do save: [`game_engine.asm`](https://github.com/dzik87/HarvestMoonSNES/blob/master/src/code/bank_83/game_engine.asm)
- Bits do depósito: [`tile_scripts.csv`](https://github.com/dzik87/HarvestMoonSNES/blob/master/assets/tables/data/tile_scripts.csv)
