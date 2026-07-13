# bibliotecaPandas

## Análise de alertas por filial

Este repositório agora inclui um script para montar a visão de **alertas por filial**, ignorando as informações de infrações. A lógica foi pensada para chegar no número de `QTD alertas` por filial e, quando houver uma base de frota, calcular também o `% alertas` usando o multiplicador informado.

### Colunas esperadas

Base de alertas:

- `Filial` — coluna obrigatória usada para agrupar os alertas.
- As demais colunas, como `Veículo`, `Ofensa`, `Velocidade (Km/h)`, `Tempo em Excesso de Velocidade`, `Data e Hora`, `Endereço` e `Tipo`, podem permanecer na planilha, mas não entram no cálculo do total por filial.

Base de frota, opcional:

- `Filial`
- `QTD de carros`

### Regra de cálculo

Com base de frota:

```text
CarrosXmultiplicador = QTD de carros * multiplicador
% alertas = QTD alertas / CarrosXmultiplicador
```

O multiplicador padrão é `4`, conforme o modelo compartilhado.

### Como executar

Gerando Excel com alertas e frota:

```bash
python analise_alertas_por_filial.py --alertas alertas.xlsx --frota frota.xlsx --saida resultado_alertas.xlsx
```

Gerando CSV somente com a contagem de alertas por filial:

```bash
python analise_alertas_por_filial.py --alertas alertas.csv --saida resultado_alertas.csv
```

Alterando o multiplicador:

```bash
python analise_alertas_por_filial.py --alertas alertas.xlsx --frota frota.xlsx --multiplicador 5 --saida resultado_alertas.xlsx
```

### Saída esperada

Quando a base de frota é informada, a saída contém:

- `Filial`
- `QTD de carros`
- `CarrosXmultiplicador`
- `QTD alertas`
- `% alertas`

Sem a base de frota, a saída contém apenas:

- `Filial`
- `QTD alertas`
