import base64
import binascii
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from PIL import Image, UnidentifiedImageError
from pypdf import PdfReader
from docx import Document


class AttachmentProcessor:
    """
    Validates supported attachments and extracts their content
    without coupling file handling to the LLM provider.
    """

    MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024
    MAX_PASTED_TEXT_BYTES = 1 * 1024 * 1024

    SUPPORTED_TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".json"}
    SUPPORTED_DOCUMENT_EXTENSIONS = {".pdf", ".docx"}
    SUPPORTED_IMAGE_EXTENSIONS = {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".gif",
    }

    IMAGE_FORMATS = {
        ".png": "PNG",
        ".jpg": "JPEG",
        ".jpeg": "JPEG",
        ".webp": "WEBP",
        ".gif": "GIF",
    }

    def process_file(self, file_path: str | Path) -> dict[str, Any]:
        path = Path(file_path)

        if not path.is_file():
            raise FileNotFoundError("Attachment file was not found.")

        if path.stat().st_size > self.MAX_ATTACHMENT_BYTES:
            raise ValueError("Attachment exceeds the 10 MiB file-size limit.")

        extension = path.suffix.lower()

        if extension in self.SUPPORTED_TEXT_EXTENSIONS:
            return self._process_text_file(path)

        if extension == ".pdf":
            return self._process_pdf(path)

        if extension == ".docx":
            return self._process_docx(path)

        if extension in self.SUPPORTED_IMAGE_EXTENSIONS:
            return self._process_image(path)

        return {
            "type": "file",
            "name": path.name,
            "extension": extension,
            "content": None,
            "status": "unsupported",
        }

    def _process_text_file(self, path: Path) -> dict[str, Any]:
        content = path.read_text(encoding="utf-8")

        return {
            "type": "text_file",
            "name": path.name,
            "extension": path.suffix.lower(),
            "content": content,
            "status": "processed",
        }

    def _process_pdf(self, path: Path) -> dict[str, Any]:
        with path.open("rb") as file:
            if file.read(5) != b"%PDF-":
                raise ValueError("The uploaded file is not a valid PDF.")

        reader = PdfReader(str(path), strict=True)

        if reader.is_encrypted:
            raise ValueError("Encrypted PDF files are not supported.")

        pages = []

        for page in reader.pages:
            text = page.extract_text() or ""

            if text.strip():
                pages.append(text)

        return {
            "type": "pdf",
            "name": path.name,
            "extension": ".pdf",
            "content": "\n\n".join(pages),
            "page_count": len(reader.pages),
            "status": "processed",
        }

    def _process_docx(self, path: Path) -> dict[str, Any]:
        if not zipfile.is_zipfile(path):
            raise ValueError("The uploaded file is not a valid DOCX document.")

        try:
            with zipfile.ZipFile(path) as archive:
                names = set(archive.namelist())

                if (
                    "[Content_Types].xml" not in names
                    or "word/document.xml" not in names
                ):
                    raise ValueError(
                        "The uploaded file is not a valid DOCX document."
                    )
        except zipfile.BadZipFile as exc:
            raise ValueError("The DOCX document is malformed.") from exc

        document = Document(str(path))

        paragraphs = [
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        return {
            "type": "docx",
            "name": path.name,
            "extension": ".docx",
            "content": "\n".join(paragraphs),
            "status": "processed",
        }

    def _process_image(self, path: Path) -> dict[str, Any]:
        expected_format = self.IMAGE_FORMATS[path.suffix.lower()]

        try:
            with Image.open(path) as image:
                actual_format = image.format

                if actual_format != expected_format:
                    raise ValueError(
                        "The image content does not match its file extension."
                    )

                image.verify()

            with Image.open(path) as image:
                return {
                    "type": "image",
                    "name": path.name,
                    "extension": path.suffix.lower(),
                    "content": None,
                    "mime_type": Image.MIME.get(image.format),
                    "width": image.width,
                    "height": image.height,
                    "format": image.format,
                    "status": "processed",
                }

        except (UnidentifiedImageError, OSError) as exc:
            raise ValueError("The uploaded image is invalid or corrupted.") from exc

    def process_text(self, text: str) -> dict[str, Any]:
        if not isinstance(text, str):
            raise ValueError("Pasted content must be text.")

        if len(text.encode("utf-8")) > self.MAX_PASTED_TEXT_BYTES:
            raise ValueError("Pasted text exceeds the 1 MiB size limit.")

        return {
            "type": "pasted_text",
            "name": None,
            "extension": None,
            "content": text,
            "status": "processed",
        }

    def process_attachment(
        self,
        attachment: dict[str, Any],
    ) -> dict[str, Any]:

        if not isinstance(attachment, dict):
            raise ValueError("Invalid attachment.")

        attachment_type = attachment.get("type")

        # Validate pasted text.
        if attachment_type == "pasted_text":
            return self.process_text(attachment.get("content", ""))

        # Process uploaded files.
        if attachment_type == "file_upload":
            name = attachment.get("name")

            if not isinstance(name, str) or not name.strip():
                raise ValueError("Uploaded attachment must have a filename.")

            # Reject directory paths and filenames with no actual filename.
            safe_name = Path(name.replace("\\", "/")).name

            if safe_name in {"", ".", ".."}:
                raise ValueError("Invalid attachment filename.")

            data = attachment.get("data")

            if not isinstance(data, str) or not data:
                raise ValueError("No valid file data was received.")

            # Accept raw Base64 or a data URL.
            if data.startswith("data:"):
                header, separator, encoded_data = data.partition(",")

                if not separator or ";base64" not in header.lower():
                    raise ValueError("Invalid file data URL.")

                data = encoded_data

            max_encoded_length = 4 * (
                (self.MAX_ATTACHMENT_BYTES + 2) // 3
            )

            if len(data) > max_encoded_length:
                raise ValueError(
                    "Attachment exceeds the 10 MiB file-size limit."
                )

            try:
                file_bytes = base64.b64decode(data, validate=True)
            except (binascii.Error, ValueError) as exc:
                raise ValueError("Invalid encoded file data.") from exc

            if not file_bytes:
                raise ValueError("The uploaded file is empty.")

            if len(file_bytes) > self.MAX_ATTACHMENT_BYTES:
                raise ValueError(
                    "Attachment exceeds the 10 MiB file-size limit."
                )

            with tempfile.TemporaryDirectory() as temp_dir:
                path = Path(temp_dir) / safe_name
                path.write_bytes(file_bytes)
                processed = self.process_file(path)

            # Use the verified MIME type for images rather than trusting
            # a MIME type supplied by the frontend.
            if processed.get("type") != "image":
                processed.pop("mime_type", None)

            return processed

        # Do not trust preprocessed attachment dictionaries.
        # These may contain client-supplied content or fabricated metadata.
        if attachment_type in {"text_file", "pdf", "docx", "image"}:
            raise ValueError(
                "Preprocessed attachments are not accepted from clients."
            )

        return {
            "type": "file",
            "name": None,
            "content": None,
            "status": "unsupported",
        }