import os
import pytest
from app.services.input_processors.audio_processor import AudioProcessor, TranscribedAudio
from app.services.input_processors.pdf_processor import PDFProcessor, ExtractedDocument
from app.services.input_processors.image_processor import ImageProcessor, ImageSet


class TestAudioProcessor:
    def test_instantiation(self):
        p = AudioProcessor()
        assert p is not None

    @pytest.mark.asyncio
    async def test_missing_file_raises(self):
        p = AudioProcessor()
        with pytest.raises(FileNotFoundError):
            await p.transcribe("/nonexistent/audio.mp3")

    def test_transcribed_audio_dataclass(self):
        ta = TranscribedAudio(text="hello", language="en", duration=5.0, segments=[])
        assert ta.text == "hello"
        assert ta.duration == 5.0


class TestPDFProcessor:
    def test_instantiation(self):
        p = PDFProcessor()
        assert p is not None

    @pytest.mark.asyncio
    async def test_missing_file_raises(self):
        p = PDFProcessor()
        with pytest.raises(FileNotFoundError):
            await p.extract("/nonexistent/doc.pdf")

    def test_extracted_document_dataclass(self):
        doc = ExtractedDocument(text="content", title="Title", pages=3, images=[])
        assert doc.pages == 3


class TestImageProcessor:
    def test_instantiation(self):
        p = ImageProcessor()
        assert p is not None

    def test_collect_no_images(self):
        p = ImageProcessor()
        result = p.collect_images(paths=[])
        assert result.count == 0

    def test_collect_with_paths(self, tmp_path):
        # Create fake images
        img1 = tmp_path / "photo1.jpg"
        img2 = tmp_path / "photo2.png"
        txt = tmp_path / "readme.txt"
        img1.write_bytes(b"fake jpg")
        img2.write_bytes(b"fake png")
        txt.write_text("not an image")

        p = ImageProcessor()
        result = p.collect_images(paths=[str(img1), str(img2), str(txt)])
        assert result.count == 2  # Only jpg and png

    def test_collect_from_directory(self, tmp_path):
        (tmp_path / "a.jpg").write_bytes(b"fake")
        (tmp_path / "b.png").write_bytes(b"fake")
        (tmp_path / "c.txt").write_text("nope")

        p = ImageProcessor()
        result = p.collect_images(directory=str(tmp_path))
        assert result.count == 2

    @pytest.mark.asyncio
    async def test_prepare_video_params(self, tmp_path):
        img = tmp_path / "slide.jpg"
        img.write_bytes(b"fake")

        p = ImageProcessor()
        params = await p.prepare_video_params([str(img)], title="My Slides")
        assert params["video_subject"] == "My Slides"
        assert params["video_source"] == "local"
        assert len(params["video_materials"]) == 1

    @pytest.mark.asyncio
    async def test_empty_images_raises(self):
        p = ImageProcessor()
        with pytest.raises(ValueError):
            await p.prepare_video_params([], title="Empty")
