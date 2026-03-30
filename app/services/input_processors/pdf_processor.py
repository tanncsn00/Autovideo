"""PDF/Slides to Video — extract text from documents and generate video"""

import os
from dataclasses import dataclass
from loguru import logger


@dataclass
class ExtractedDocument:
    text: str
    title: str
    pages: int
    images: list[str]


class PDFProcessor:
    """Extract content from PDF files for video generation"""

    async def extract(self, pdf_path: str) -> ExtractedDocument:
        """Extract text and metadata from PDF"""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            return await self._extract_with_pymupdf(pdf_path)
        except ImportError:
            try:
                return await self._extract_with_pypdf(pdf_path)
            except ImportError:
                raise ImportError(
                    "PDF processing requires PyMuPDF or pypdf. "
                    "Install: pip install pymupdf  OR  pip install pypdf"
                )

    async def _extract_with_pymupdf(self, pdf_path: str) -> ExtractedDocument:
        """Extract using PyMuPDF (best quality)"""
        import fitz  # PyMuPDF

        doc = fitz.open(pdf_path)
        pages_text = []
        images = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            pages_text.append(page.get_text())

            # Extract images from first few pages
            if page_num < 5:
                for img_idx, img in enumerate(page.get_images(full=True)):
                    if img_idx < 3:  # Max 3 images per page
                        xref = img[0]
                        img_data = doc.extract_image(xref)
                        if img_data:
                            img_path = os.path.join(
                                os.path.dirname(pdf_path),
                                f"pdf_img_{page_num}_{img_idx}.{img_data['ext']}"
                            )
                            with open(img_path, "wb") as f:
                                f.write(img_data["image"])
                            images.append(img_path)

        title = doc.metadata.get("title", "") or os.path.basename(pdf_path).replace(".pdf", "")
        text = "\n\n".join(pages_text)
        doc.close()

        return ExtractedDocument(text=text[:5000], title=title, pages=len(pages_text), images=images)

    async def _extract_with_pypdf(self, pdf_path: str) -> ExtractedDocument:
        """Extract using pypdf (fallback)"""
        from pypdf import PdfReader

        reader = PdfReader(pdf_path)
        pages_text = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)

        title = reader.metadata.title if reader.metadata else os.path.basename(pdf_path).replace(".pdf", "")
        text = "\n\n".join(pages_text)

        return ExtractedDocument(text=text[:5000], title=title or "", pages=len(pages_text), images=[])

    async def prepare_video_params(self, pdf_path: str, template_id: str = None) -> dict:
        """Extract PDF content and prepare VideoParams"""
        doc = await self.extract(pdf_path)

        params = {
            "video_subject": doc.title,
            "video_script": doc.text[:3000],
            "video_language": "en",
        }

        if template_id:
            from app.services.template import TemplateManager
            mgr = TemplateManager()
            try:
                template_params = mgr.apply_template(template_id)
                template_params.update(params)
                params = template_params
            except ValueError:
                pass

        return params


pdf_processor = PDFProcessor()
