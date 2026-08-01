import pymupdf
import fitz
from pathlib import Path

def parse_pdf(file_path: str) -> str:
    path = Path(file_path)

    #guards for nonexistent files and wrong file formats
    if not path.exists():
        raise FileNotFoundError(f"{file_path} cannot be found")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"{file_path} is in the wrong format")
    with open(path, "rb") as f:
        if f.read(5) != b"%PDF-":
            raise ValueError(f"{file_path} is not a PDF file")
    try:
        doc = pymupdf.open(path)

        if doc.is_encrypted:
            doc.close()
            raise PermissionError(
                f"{file_path} is encrypted and cannot be opened"
            )

        extract_text = []
        for page in doc:
            extract_text.append(page.get_text())
        doc.close()
        return "\n".join(extract_text)
    
    except PermissionError as e:
        raise PermissionError(
            f"{file_path} is encrypted and cannot be opened"
        ) from e
    except fitz.FileDataError as e:
        raise ValueError(
            f"{file_path} is corrupted or invalid"
        ) from e
    except OSError as e:
        raise OSError(
            f"Failed to read file '{file_path}': {e}"
        ) from e
    
file_path = "sampleresume.pdf"

if __name__ == "__main__":
    result = parse_pdf(file_path)
    print(result)


#maybe need to add guardrails for invalid fonts or symbols??