"""
RentSmart - Sistema de Orçamento de Locação da R.M Imóveis
Disciplina: Algorithmic Thinking & Introduction to Object-Oriented Programming

O programa solicita as características da locação, aplica as regras comerciais
da imobiliária, exibe um orçamento detalhado e gera um CSV com a projeção
dos 12 primeiros meses de contrato.
"""

import csv
from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP

# ---------------------------------------------------------------------------
# CONSTANTES DE NEGÓCIO (todas as regras comerciais em um único lugar)
# ---------------------------------------------------------------------------
TAXA_CONTRATUAL = Decimal("2000.00")
MAX_PARCELAS_TAXA = 5
MESES_PROJECAO = 12

ADICIONAL_GARAGEM = Decimal("300.00")          # casas e apartamentos
ADICIONAL_QUARTO_APARTAMENTO = Decimal("200.00")
ADICIONAL_QUARTO_CASA = Decimal("250.00")

PACOTE_ESTUDIO = Decimal("250.00")             # inclui 2 vagas
VAGAS_PACOTE_ESTUDIO = 2
VAGA_EXTRA_ESTUDIO = Decimal("60.00")

DESCONTO_SEM_CRIANCAS = Decimal("0.05")        # somente apartamentos


def arredondar(valor):
    """Arredonda para centavos (2 casas decimais)."""
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def moeda(valor):
    """Formata um Decimal como moeda brasileira: R$ 1.234,56."""
    texto = f"{arredondar(valor):,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


# ---------------------------------------------------------------------------
# CLASSES DE IMÓVEL (herança + polimorfismo)
# ---------------------------------------------------------------------------
class Imovel(ABC):
    """Classe base: define o contrato que todo tipo de imóvel deve cumprir."""

    def __init__(self, nome, aluguel_base):
        self.nome = nome
        self.aluguel_base = aluguel_base

    @abstractmethod
    def itens_aluguel(self):
        """Retorna lista de tuplas (descrição, valor) que compõem o aluguel."""

    def calcular_aluguel(self):
        """Soma todos os itens (adicionais positivos e descontos negativos)."""
        return arredondar(sum((valor for _, valor in self.itens_aluguel()),
                              Decimal("0")))

    def descricao(self):
        return self.nome


class Apartamento(Imovel):
    def __init__(self, quartos, tem_garagem, tem_criancas):
        super().__init__(f"Apartamento de {quartos} quarto(s)", Decimal("700.00"))
        self.quartos = quartos
        self.tem_garagem = tem_garagem
        self.tem_criancas = tem_criancas

    def itens_aluguel(self):
        itens = [("Aluguel-base do apartamento", self.aluguel_base)]
        if self.quartos == 2:
            itens.append(("Adicional de 2º quarto", ADICIONAL_QUARTO_APARTAMENTO))
        if self.tem_garagem:
            itens.append(("Vaga de garagem", ADICIONAL_GARAGEM))
        if not self.tem_criancas:
            # o desconto incide sobre o valor já com os adicionais
            subtotal = sum((v for _, v in itens), Decimal("0"))
            desconto = arredondar(subtotal * DESCONTO_SEM_CRIANCAS)
            itens.append(("Desconto de 5% (sem crianças)", -desconto))
        return itens


class Casa(Imovel):
    def __init__(self, quartos, tem_garagem):
        super().__init__(f"Casa de {quartos} quarto(s)", Decimal("900.00"))
        self.quartos = quartos
        self.tem_garagem = tem_garagem

    def itens_aluguel(self):
        itens = [("Aluguel-base da casa", self.aluguel_base)]
        if self.quartos == 2:
            itens.append(("Adicional de 2º quarto", ADICIONAL_QUARTO_CASA))
        if self.tem_garagem:
            itens.append(("Vaga de garagem", ADICIONAL_GARAGEM))
        return itens


class Estudio(Imovel):
    def __init__(self, vagas):
        super().__init__("Estúdio", Decimal("1200.00"))
        self.vagas = vagas  # 0 = sem estacionamento; mínimo 2 se contratar

    def itens_aluguel(self):
        itens = [("Aluguel-base do estúdio", self.aluguel_base)]
        if self.vagas > 0:
            itens.append((f"Pacote de estacionamento ({VAGAS_PACOTE_ESTUDIO} vagas)",
                          PACOTE_ESTUDIO))
            extras = self.vagas - VAGAS_PACOTE_ESTUDIO
            if extras > 0:
                itens.append((f"{extras} vaga(s) adicional(is) x {moeda(VAGA_EXTRA_ESTUDIO)}",
                              VAGA_EXTRA_ESTUDIO * extras))
        return itens

    def descricao(self):
        return f"Estúdio ({self.vagas} vaga(s))" if self.vagas else "Estúdio (sem vaga)"


# ---------------------------------------------------------------------------
# TAXA CONTRATUAL (custo separado do aluguel)
# ---------------------------------------------------------------------------
class TaxaContratual:
    def __init__(self, parcelas):
        self.valor_total = TAXA_CONTRATUAL
        self.parcelas = parcelas

    def valor_parcelas(self):
        """
        Retorna a lista com o valor de cada parcela. A última parcela absorve
        a diferença de centavos, garantindo que a soma seja exatamente R$ 2.000.
        """
        base = arredondar(self.valor_total / self.parcelas)
        lista = [base] * self.parcelas
        lista[-1] = self.valor_total - base * (self.parcelas - 1)
        return lista


# ---------------------------------------------------------------------------
# ORÇAMENTO (junta imóvel + taxa; gera resumo e projeção)
# ---------------------------------------------------------------------------
class Orcamento:
    def __init__(self, cliente, imovel, taxa):
        self.cliente = cliente
        self.imovel = imovel
        self.taxa = taxa

    def projecao_12_meses(self):
        """Lista de dicts com a previsão de pagamento de cada mês."""
        aluguel = self.imovel.calcular_aluguel()
        parcelas = self.taxa.valor_parcelas()
        linhas, acumulado = [], Decimal("0")
        for mes in range(1, MESES_PROJECAO + 1):
            parcela = parcelas[mes - 1] if mes <= len(parcelas) else Decimal("0.00")
            total = aluguel + parcela
            acumulado += total
            linhas.append({
                "mes": mes,
                "aluguel": aluguel,
                "parcela_taxa": parcela,
                "total_mes": total,
                "acumulado": acumulado,
            })
        return linhas

    def exibir_resumo(self):
        largura = 58
        print("\n" + "=" * largura)
        print("ORÇAMENTO DE LOCAÇÃO - R.M IMÓVEIS".center(largura))
        print("=" * largura)
        print(f"Cliente: {self.cliente}")
        print(f"Imóvel : {self.imovel.descricao()}")
        print("-" * largura)
        print("COMPOSIÇÃO DO ALUGUEL MENSAL")
        for descricao, valor in self.imovel.itens_aluguel():
            texto = ("-" if valor < 0 else "") + moeda(abs(valor))
            print(f"  {descricao:<38} {texto:>16}")
        print("-" * largura)
        print(f"  {'VALOR MENSAL DO ALUGUEL':<38} {moeda(self.imovel.calcular_aluguel()):>16}")
        print("-" * largura)
        print("TAXA CONTRATUAL (cobrada à parte do aluguel)")
        print(f"  Valor total: {moeda(self.taxa.valor_total)}")
        parcelas = self.taxa.valor_parcelas()
        print(f"  Parcelamento: {len(parcelas)}x")
        for i, valor in enumerate(parcelas, start=1):
            print(f"    Parcela {i}/{len(parcelas)} (mês {i}): {moeda(valor)}")
        print("-" * largura)
        projecao = self.projecao_12_meses()
        print(f"  {'TOTAL PREVISTO NOS 12 PRIMEIROS MESES':<38} {moeda(projecao[-1]['acumulado']):>16}")
        print("=" * largura)

    def exportar_csv(self, caminho="projecao_12_meses.csv"):
        campos = ["mes", "aluguel", "parcela_taxa", "total_mes", "acumulado"]
        # utf-8-sig e ';' para abrir corretamente no Excel em português
        with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=campos, delimiter=";")
            escritor.writeheader()
            for linha in self.projecao_12_meses():
                escritor.writerow({
                    k: (str(arredondar(v)).replace(".", ",") if k != "mes" else v)
                    for k, v in linha.items()
                })
        return caminho


# ---------------------------------------------------------------------------
# ENTRADA DE DADOS COM VALIDAÇÃO
# ---------------------------------------------------------------------------
def ler_texto(mensagem):
    while True:
        texto = input(mensagem).strip()
        if texto:
            return texto
        print("  ! Este campo não pode ficar vazio.")


def ler_opcao(mensagem, opcoes_validas):
    """Repete a pergunta até que o usuário digite uma das opções válidas."""
    while True:
        resposta = input(mensagem).strip().lower()
        if resposta in opcoes_validas:
            return resposta
        print(f"  ! Opção inválida. Escolha entre: {', '.join(opcoes_validas)}")


def ler_inteiro(mensagem, minimo, maximo):
    while True:
        try:
            valor = int(input(mensagem).strip())
        except ValueError:
            print("  ! Digite um número inteiro.")
            continue
        if minimo <= valor <= maximo:
            return valor
        print(f"  ! Digite um valor entre {minimo} e {maximo}.")


def ler_sim_nao(mensagem):
    return ler_opcao(mensagem + " (s/n): ", ["s", "n"]) == "s"


def montar_imovel():
    """Pergunta ao usuário e devolve o objeto de imóvel correspondente."""
    print("\nTipo de imóvel:")
    print("  1 - Apartamento")
    print("  2 - Casa")
    print("  3 - Estúdio")
    tipo = ler_opcao("Escolha (1-3): ", ["1", "2", "3"])

    if tipo == "1":
        quartos = ler_inteiro("Quantidade de quartos (1 ou 2): ", 1, 2)
        garagem = ler_sim_nao("Deseja vaga de garagem?")
        criancas = ler_sim_nao("Possui crianças?")
        return Apartamento(quartos, garagem, criancas)

    if tipo == "2":
        quartos = ler_inteiro("Quantidade de quartos (1 ou 2): ", 1, 2)
        garagem = ler_sim_nao("Deseja vaga de garagem?")
        return Casa(quartos, garagem)

    vagas = 0
    if ler_sim_nao(f"Deseja estacionamento? (pacote inicial de "
                   f"{VAGAS_PACOTE_ESTUDIO} vagas por {moeda(PACOTE_ESTUDIO)})"):
        vagas = ler_inteiro(f"Total de vagas desejadas (mínimo {VAGAS_PACOTE_ESTUDIO}, "
                            f"máximo 10): ", VAGAS_PACOTE_ESTUDIO, 10)
    return Estudio(vagas)


def main():
    print("=" * 58)
    print("RentSmart - Orçamento de Locação | R.M Imóveis".center(58))
    print("=" * 58)

    cliente = ler_texto("Nome do cliente: ")
    imovel = montar_imovel()
    parcelas = ler_inteiro(
        f"Taxa contratual de {moeda(TAXA_CONTRATUAL)} - "
        f"parcelar em quantas vezes? (1 a {MAX_PARCELAS_TAXA}): ",
        1, MAX_PARCELAS_TAXA)

    orcamento = Orcamento(cliente, imovel, TaxaContratual(parcelas))
    orcamento.exibir_resumo()

    caminho = orcamento.exportar_csv()
    print(f"\nProjeção dos 12 meses salva em: {caminho}")


if __name__ == "__main__":
    main()
