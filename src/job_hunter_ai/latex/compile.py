import subprocess
import os

def compile_pdf(tex_path: str, output_dir: str):
    """Compile LaTeX using pdflatex (simpler than latexmk for Windows)."""
    
    cmd = [
        "pdflatex",
        "-interaction=nonstopmode",
        "-output-directory", output_dir,
        tex_path
    ]

    print("Running:", " ".join(cmd))
    proc = subprocess.run(cmd, capture_output=True, text=True)

    if proc.returncode != 0:
        print("STDERR:", proc.stderr)
        raise RuntimeError("pdflatex failed. See errors above.")

    # PDF name = same as tex but .pdf
    pdf_name = os.path.basename(tex_path).replace(".tex", ".pdf")
    return os.path.join(output_dir, pdf_name)
