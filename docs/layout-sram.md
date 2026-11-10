# Campos SRAM usados pelo verificador

[English version](layout-sram.en.md)

[Versión en español](layout-sram.es.md)

O `.srm` examinado tem dois slots de `0x1000` bytes, nas bases `0x0000` e `0x1000`. Os offsets abaixo são relativos ao início do slot selecionado.

## Validação do slot

| Offset | Tamanho | Campo |
|---:|---:|---|
| `+0x2E` | 1 byte | Marcador do slot mais recente (`01` no slot escolhido). |
| `+0x2F` | 2 bytes | Checksum little-endian. O cálculo soma palavras de 16 bits e ignora o marcador e o próprio checksum. |
| `+0x3C` | 4 bytes | Assinatura ASCII `FARM`. |

O programa ignora slots incompletos, sem assinatura ou com checksum incompatível.

## Contador e ferramentas

| Offset | Tamanho | Interpretação |
|---:|---:|---|
| `+0x0E` | 1 byte | Stamina máxima. |
| `+0x0F` | 1 byte | ID da ferramenta equipada. Diamante azul: `$17`. |
| `+0x17` | 1 byte | `nPowerBerryEaten`, contador de berries consumidas. |
| `+0x1A` | 1 byte | ID da segunda ferramenta. Diamante azul: `$17`. |
| `+0x84`–`+0x87` | 4 bytes | Quatro linhas de bits dos itens no depósito. |
| `+0x86` bit `$40` | 1 bit | Diamante azul armazenado no depósito. |

O diamante é considerado ainda disponível se qualquer um destes estados estiver presente: equipado igual a `$17`, segunda ferramenta igual a `$17`, ou `slot+0x86 & 0x40 != 0`.

## Flags de eventos

As flags são palavras little-endian em `+0x60`, `+0x62`, `+0x64`, `+0x66`, `+0x70`, `+0x72`, `+0x74` e `+0x76`, que correspondem a `event1`–`event8`. O verificador usa somente as máscaras listadas em `docs/estudo.md`; elas são marcadores de ramos específicos, não uma lista universal de berries obtidas.

## WRAM e offset de SRAM não são a mesma coisa

Endereços como `$7F:1F64` são endereços de WRAM observados no Mesen. O save serializa esses estados em campos próprios do slot. Para eventos, a relação usada pelo programa vem da rotina de load/save do jogo; portanto o offset de arquivo indicado aqui é `slot+...`, e não o endereço WRAM convertido mecanicamente.
