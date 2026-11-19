"""CLI para uso local / pipelines batch.

    rfp-analyzer analyze caminho/rfp.pdf --out saida/
    rfp-analyzer analyze caminho/rfp.txt --offline      # sem LLM, custo zero
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from . import __version__
from .config import get_settings
from .ingestion.loaders import load_path
from .observability import setup_logging, setup_tracing
from .pipeline.orchestrator import analyze_text
from .reporting import export_excel, render_markdown

app = typer.Typer(help="RFP Requirements Analyzer — análise estratégica de RFPs com IA (Groq).",
                  no_args_is_help=True)


@app.command()
def analyze(
    document: Annotated[Path, typer.Argument(exists=True, readable=True, help="Arquivo da RFP")],
    out: Annotated[Path, typer.Option("--out", "-o", help="Diretório de saída")] = Path("output"),
    offline: Annotated[bool, typer.Option("--offline", help="Não chama LLM (modo determinístico)")] = False,
) -> None:
    """Analisa uma RFP e gera analysis.json, relatorio.md e matriz_requisitos.xlsx."""
    settings = get_settings()
    setup_logging("WARNING")
    setup_tracing(settings)
    result = analyze_text(load_path(document), document.name, settings=settings, use_llm=not offline)

    out.mkdir(parents=True, exist_ok=True)
    (out / "analysis.json").write_text(result.model_dump_json(indent=2), encoding="utf-8")
    (out / "relatorio.md").write_text(render_markdown(result), encoding="utf-8")
    export_excel(result, out / "matriz_requisitos.xlsx")

    k, u = result.kpis, result.usage
    typer.echo(f"\n✔ {k['total_requisitos']} requisitos · {k['lacunas']} lacunas · {k['riscos_cruzados']} riscos "
               f"cruzados · clareza {k['indice_clareza']}/100")
    typer.echo(f"  Sinal indicativo de bid: {result.summary.bid_signal} (fonte: {result.summary.source})")
    mode = "DETERMINÍSTICO (sem LLM)" if u.degraded_mode and not u.calls else ", ".join(u.models_used)
    typer.echo(f"  IA: {mode} · {u.calls} chamadas · {u.total_tokens} tokens · cache {u.cached_calls}")
    typer.echo(f"  Saídas em: {out.resolve()}\n")


@app.command()
def version() -> None:
    typer.echo(__version__)


if __name__ == "__main__":
    app()
