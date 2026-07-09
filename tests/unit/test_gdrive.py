"""Tests for Google Drive URL normalization (COI Content Intake M1)."""

from agent.media.gdrive import (
    build_direct_download_url,
    build_folder_url,
    normalize_media_url,
    parse_gdrive_file_id,
    parse_gdrive_folder_id,
)


def test_parse_file_id_view_link():
    url = "https://drive.google.com/file/d/1AbC-dEfGhIj/view?usp=sharing"
    assert parse_gdrive_file_id(url) == "1AbC-dEfGhIj"


def test_parse_file_id_open_link():
    url = "https://drive.google.com/open?id=xyz123ABC"
    assert parse_gdrive_file_id(url) == "xyz123ABC"


def test_parse_folder_id():
    url = "https://drive.google.com/drive/folders/FOLDER99/home"
    assert parse_gdrive_folder_id(url) == "FOLDER99"


def test_normalize_gdrive_to_direct():
    result = normalize_media_url(
        "https://drive.google.com/file/d/abc123/view"
    )
    assert result["ok"] is True
    assert result["media_source"] == "gdrive"
    assert result["gdrive_file_id"] == "abc123"
    assert result["media_url"] == build_direct_download_url("abc123")


def test_normalize_rejects_unknown():
    result = normalize_media_url("https://example.com/image.jpg")
    assert result["ok"] is False


def test_build_folder_url():
    assert "FOLDER99" in build_folder_url("FOLDER99")
