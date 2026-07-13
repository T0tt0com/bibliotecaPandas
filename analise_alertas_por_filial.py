"""Gera a análise de alertas por filial com pandas.

O objetivo é reproduzir a visão do exemplo compartilhado: para cada filial,
contar a quantidade de alertas e calcular o percentual de alertas sobre a
base de carros multiplicada por um fator (padrão: 4). Informações de infrações
podem existir na base, mas não são necessárias para esta análise.

Exemplo:
    python analise_alertas_por_filial.py --alertas alertas.xlsx --frota frota.xlsx --saida resultado.xlsx

A base de alertas deve conter, no mínimo, a coluna "Filial". A base de frota
pode conter as colunas "Filial" e "QTD de carros". Se a frota não for enviada,
o relatório trará apenas "Filial" e "QTD alertas".
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import pandas as pd


COLUNA_FILIAL = "Filial"
COLUNA_QTD_CARROS = "QTD de carros"
COLUNA_QTD_ALERTAS = "QTD alertas"
COLUNA_CARROS_MULTIPLICADOR = "CarrosXmultiplicador"
COLUNA_PERCENTUAL_ALERTAS = "% alertas"


def _normalizar_colunas(colunas: Iterable[object]) -> list[str]:
    """Remove espaços extras dos nomes de colunas, preservando os textos."""
    return [str(coluna).strip() for coluna in colunas]


def ler_base(caminho: str | Path) -> pd.DataFrame:
    """Lê arquivos CSV, XLS ou XLSX e normaliza os nomes das colunas."""
    caminho = Path(caminho)
    extensao = caminho.suffix.lower()

    if extensao in {".xlsx", ".xls"}:
        base = pd.read_excel(caminho)
    elif extensao == ".csv":
        base = pd.read_csv(caminho)
    else:
        raise ValueError(f"Formato não suportado: {caminho.suffix}. Use CSV, XLS ou XLSX.")

    base.columns = _normalizar_colunas(base.columns)
    return base


def contar_alertas_por_filial(alertas: pd.DataFrame) -> pd.DataFrame:
    """Conta somente os registros de alertas por filial."""
    if COLUNA_FILIAL not in alertas.columns:
        raise KeyError(f'A base de alertas precisa conter a coluna "{COLUNA_FILIAL}".')

    alertas_validos = alertas.dropna(subset=[COLUNA_FILIAL]).copy()
    alertas_validos[COLUNA_FILIAL] = alertas_validos[COLUNA_FILIAL].astype(str).str.strip()

    return (
        alertas_validos.groupby(COLUNA_FILIAL, as_index=False)
        .size()
        .rename(columns={"size": COLUNA_QTD_ALERTAS})
        .sort_values(COLUNA_FILIAL)
    )


def montar_analise_alertas(
    alertas: pd.DataFrame,
    frota: pd.DataFrame | None = None,
    multiplicador: int = 4,
) -> pd.DataFrame:
    """Monta a visão de QTD alertas e % alertas por filial.

    Quando a frota é informada, o percentual segue a regra do material:
    QTD alertas / (QTD de carros * multiplicador). Filiais sem alertas ficam
    com zero para facilitar a leitura do relatório final.
    """
    resultado = contar_alertas_por_filial(alertas)

    if frota is None:
        return resultado

    colunas_obrigatorias = {COLUNA_FILIAL, COLUNA_QTD_CARROS}
    ausentes = colunas_obrigatorias.difference(frota.columns)
    if ausentes:
        raise KeyError(f"A base de frota precisa conter as colunas: {sorted(ausentes)}.")

    frota_base = frota[[COLUNA_FILIAL, COLUNA_QTD_CARROS]].copy()
    frota_base[COLUNA_FILIAL] = frota_base[COLUNA_FILIAL].astype(str).str.strip()
    frota_base[COLUNA_QTD_CARROS] = pd.to_numeric(frota_base[COLUNA_QTD_CARROS], errors="coerce").fillna(0)
    frota_base = frota_base.groupby(COLUNA_FILIAL, as_index=False)[COLUNA_QTD_CARROS].sum()

    resultado = frota_base.merge(resultado, on=COLUNA_FILIAL, how="left")
    resultado[COLUNA_QTD_ALERTAS] = resultado[COLUNA_QTD_ALERTAS].fillna(0).astype(int)
    resultado[COLUNA_CARROS_MULTIPLICADOR] = resultado[COLUNA_QTD_CARROS] * multiplicador
    divisor = resultado[COLUNA_CARROS_MULTIPLICADOR].where(resultado[COLUNA_CARROS_MULTIPLICADOR] != 0)
    resultado[COLUNA_PERCENTUAL_ALERTAS] = (resultado[COLUNA_QTD_ALERTAS] / divisor).fillna(0).round(2)

    return resultado[
        [
            COLUNA_FILIAL,
            COLUNA_QTD_CARROS,
            COLUNA_CARROS_MULTIPLICADOR,
            COLUNA_QTD_ALERTAS,
            COLUNA_PERCENTUAL_ALERTAS,
        ]
    ].sort_values(COLUNA_FILIAL)


def salvar_resultado(resultado: pd.DataFrame, caminho_saida: str | Path) -> None:
    """Salva o relatório em CSV ou Excel."""
    caminho_saida = Path(caminho_saida)
    if caminho_saida.suffix.lower() in {".xlsx", ".xls"}:
        resultado.to_excel(caminho_saida, index=False)
    elif caminho_saida.suffix.lower() == ".csv":
        resultado.to_csv(caminho_saida, index=False)
    else:
        raise ValueError("A saída precisa terminar com .csv, .xls ou .xlsx.")


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Gera análise de alertas por filial.")
    parser.add_argument("--alertas", required=True, help="Caminho da base de alertas em CSV, XLS ou XLSX.")
    parser.add_argument("--frota", help='Caminho da base com "Filial" e "QTD de carros".')
    parser.add_argument("--multiplicador", type=int, default=4, help="Multiplicador da base de carros. Padrão: 4.")
    parser.add_argument("--saida", default="analise_alertas_por_filial.xlsx", help="Arquivo de saída CSV/XLS/XLSX.")
    return parser


def main() -> None:
    args = criar_parser().parse_args()
    alertas = ler_base(args.alertas)
    frota = ler_base(args.frota) if args.frota else None
    resultado = montar_analise_alertas(alertas=alertas, frota=frota, multiplicador=args.multiplicador)
    salvar_resultado(resultado, args.saida)
    print(resultado.to_string(index=False))


if __name__ == "__main__":
    main()
