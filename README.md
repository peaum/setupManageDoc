# SKLL-ENGMATH

SKLL-ENGMATH is a documentation and build project for embedded systems datasheets, engineering reports, and technical references. Quarto renders source documents to Typst/PDF, HTML, and DOCX, while marked sections can be turned into spoken audio with a Python Piper TTS pipeline.

## Requirements

- Quarto 1.9 or newer
- Python 3.11 or newer
- Typst, bundled with current Quarto releases
- A Piper voice model, such as `en_US-lessac-medium.onnx`, in `data/raw/`

## Installation

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Install Quarto from [quarto.org/docs/get-started](https://quarto.org/docs/get-started/).

## Project Structure

```text
SKLL-ENGMATH/
├── .vscode/tasks.json
├── assets/{images,fonts}/
├── build/{pdf,html,docx,audio}/
├── content/{chapters,appendix,references}/
├── data/{raw,processed}/
├── scripts/{audio,build,utils}/
├── resources/{templates,brand,bibliography}/
├── src/{quarto,python,typst}/
├── _quarto.yml
├── .gitignore
├── README.md
├── pyproject.toml
└── requirements.txt
```

## Usage

Open a QMD file and run a VS Code task from **Terminal > Run Task**:

- `render:pdf` renders Typst and copies the PDF to `build/pdf/`.
- `render:html` renders HTML and copies it to `build/html/<stem>/index.html`.
- `render:docx` renders DOCX and copies it to `build/docx/`.
- `render:audio` synthesizes all audio chunks in the active QMD.
- `render:all` runs the four render tasks.
- `clean:staging` clears Quarto staging; `clean:all` clears every generated output.

To add a datasheet, copy `src/quarto/skeleton.qmd`, update its frontmatter and sections, and render it with the active file selected.

## Audio Workflow

Mark text with a Pandoc fenced div such as:

```markdown
::: {.audio-chunk #s1.1p1}
This paragraph becomes spoken audio.
:::
```

`build_audio.py from-qmd <path>` extracts these blocks, loads the configured Piper voice, and writes one MP3 per marker. `from-html` extracts the post-render text instead. `concat <stem>` combines the ordered MP3 chunks into `full.mp3`.

## Build Outputs

PDF files land in `build/pdf/`, HTML documents in `build/html/<stem>/`, DOCX files in `build/docx/`, and per-document audio in `build/audio/<stem>/`. Quarto’s intermediate files are staged in `build/_staging/`.

## Contributing

Keep source documents reproducible, use relative project paths, add or update focused examples when changing the pipeline, and run the relevant render or cleanup task before submitting changes.
