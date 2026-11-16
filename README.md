# RentSmart - Sistema de Orçamento de Locação (R.M Imóveis)

Aplicação em Python, com Programação Orientada a Objetos, que calcula o orçamento
de locação de casas, apartamentos e estúdios, exibe um resumo detalhado e gera um
arquivo CSV com a projeção dos 12 primeiros meses de contrato.

## Como executar

Requisitos: **Python 3.8 ou superior**. Não há bibliotecas externas para instalar.

```bash
python main.py
```

O programa pergunta nome do cliente, tipo de imóvel, características e parcelamento
da taxa. Ao final, mostra o orçamento na tela e cria o arquivo `projecao_12_meses.csv`
na mesma pasta. O arquivo `exemplo_projecao_12_meses.csv` é um exemplo já gerado.

## Regras de negócio implementadas

| Item | Regra |
|---|---|
| Aluguel-base | Apartamento: R$ 700 · Casa: R$ 900 · Estúdio: R$ 1.200 |
| 2º quarto | Apartamento: +R$ 200 · Casa: +R$ 250 |
| Garagem (casa/apto) | +R$ 300 por mês |
| Estúdio | Pacote de 2 vagas: R$ 250 · Vaga adicional: +R$ 60 cada |
| Desconto | Apartamento sem crianças: 5% sobre o aluguel já com os adicionais |
| Taxa contratual | R$ 2.000, parcelável em até 5x, exibida separada do aluguel |

### Decisões de interpretação
- O desconto de 5% incide sobre o aluguel-base **mais** os adicionais (2º quarto e garagem).
- A taxa contratual **não** compõe o aluguel mensal. No CSV ela aparece em coluna própria,
  distribuída nos primeiros meses conforme o número de parcelas.
- Se a divisão da taxa gerar centavos (ex.: 3x), a última parcela absorve a diferença,
  de modo que a soma seja sempre exatamente R$ 2.000,00.
- No estúdio, o estacionamento é opcional; se contratado, o mínimo é o pacote de 2 vagas.
- Os cálculos usam `Decimal` para evitar erros de arredondamento com dinheiro.

## Estrutura de classes

| Classe | Responsabilidade |
|---|---|
| `Imovel` (abstrata) | Contrato comum: `itens_aluguel()`, `calcular_aluguel()`, `descricao()` |
| `Apartamento`, `Casa`, `Estudio` | Herdam de `Imovel`; cada uma aplica suas próprias regras (polimorfismo) |
| `TaxaContratual` | Guarda o valor da taxa e calcula as parcelas |
| `Orcamento` | Reúne imóvel + taxa; gera resumo na tela, projeção de 12 meses e CSV |

Funções auxiliares (`ler_opcao`, `ler_inteiro`, `ler_sim_nao`, `ler_texto`) validam
as entradas e repetem a pergunta até receber uma resposta válida.

## Formato do CSV

Separador `;` e codificação UTF-8 com BOM (abre direto no Excel em português).

| Coluna | Descrição |
|---|---|
| `mes` | Número do mês (1 a 12) |
| `aluguel` | Aluguel mensal |
| `parcela_taxa` | Parcela da taxa contratual naquele mês |
| `total_mes` | Aluguel + parcela da taxa |
| `acumulado` | Total acumulado até o mês |

## Exemplo

Apartamento de 2 quartos, com garagem, sem crianças, taxa em 3x:
(700 + 200 + 300) - 5% = **R$ 1.140,00/mês** + parcelas de R$ 666,67 / 666,67 / 666,66.
