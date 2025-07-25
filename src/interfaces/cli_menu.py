"""OCR-PYMUPDF System CLI.

Features:
1. List PDFs
2. Convert to Markdown
3. Configuration
4. Exit
"""

import sys
from pathlib import Path
from loguru import logger
from domain.use_cases import convert_pdf_to_md
from interfaces.config_menu import ConfigMenu
from config.llm_config import LLMConfig

# ───────────────────────── Helpers ──────────────────────────
def _show_llm_status() -> None:
    """Display current LLM configuration status."""
    provider = LLMConfig.get_current_provider()
    status = "Disabled" if provider is None else f"Enabled ({provider})"
    print(f"\nLLM Processing: {status}")
    
def _convert_pdf(pdf_path: Path) -> None:
    """Convert PDF to Markdown using current configuration."""
    logger.info(f"Converting to Markdown: {pdf_path}")
    try:
        md_path = convert_pdf_to_md(pdf_path)
        print(f"[OK] Markdown generated: {md_path}")
    except Exception as e:
        logger.exception("Error in PDF conversion")
        print(f"[ERROR] Failed to convert PDF: {e}")

# ───────────────────────── PDF Management ──────────────────────────
PDF_DIR = Path("pdfs")

def list_pdfs() -> list[str]:
    """List available PDFs in the pdfs directory."""
    return [p.name for p in sorted(PDF_DIR.glob("*.pdf"))]

def select_pdf() -> str | None:
    """Show PDF selection menu."""
    files = list_pdfs()
    if not files:
        print("[INFO] No PDFs found in ./pdfs directory")
        return None
        
    print("\nAvailable PDFs:")
    for i, pdf in enumerate(files, 1):
        print(f"{i}. {pdf}")
    
    try:
        sel = input("\nSelect number: ").strip()
        if sel.isdigit() and 1 <= int(sel) <= len(files):
            return files[int(sel) - 1]
        print("[ERROR] Invalid selection")
        return None
    except (ValueError, IndexError):
        print("[ERROR] Invalid selection")
        return None

# ───────────────────────── Main Menu ──────────────────────────
def main_loop() -> None:
    """Main menu loop with integrated LLM configuration."""
    while True:
        print("\n=== OCR-PYMUPDF ===")
        _show_llm_status()
        print("\nAvailable options:")
        print("1. List PDFs")
        print("2. Convert PDF to Markdown")
        print("3. Configuration")
        print("4. Exit")

        match input("\nSelect option (1-4): ").strip():
            case "1":
                files = list_pdfs()
                if files:
                    print("\nFound PDFs:")
                    for pdf in files:
                        print(f" - {pdf}")
                else:
                    print("[INFO] No PDFs found in ./pdfs directory")
            case "2":
                if pdf := select_pdf():
                    _convert_pdf(PDF_DIR / pdf)
            case "3":
                ConfigMenu.show_provider_menu()
            case "4":
                print("\nGoodbye!")
                sys.exit(0)
            case _:
                print("[ERROR] Invalid option")