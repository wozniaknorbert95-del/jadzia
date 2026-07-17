"""Unit tests for agent.publishers.calendar_publish routing."""

from unittest.mock import patch

from agent.publishers.calendar_publish import publish_calendar_content


def test_routes_text():
    with patch("agent.publishers.calendar_publish.publish_post") as mock_post:
        mock_post.return_value = {"status": "success", "post_id": "t1"}
        result = publish_calendar_content({"content_type": "text", "body_nl": "Hello"})
    assert result["post_id"] == "t1"
    mock_post.assert_called_once_with("Hello")


def test_routes_image():
    row = {
        "content_type": "image",
        "body_nl": "Pic",
        "media_url": "https://drive.google.com/uc?export=download&id=x",
    }
    with patch("agent.publishers.calendar_publish.publish_photo") as mock_photo:
        mock_photo.return_value = {"status": "success", "post_id": "p1"}
        result = publish_calendar_content(row)
    assert result["post_id"] == "p1"
    mock_photo.assert_called_once_with("Pic", row["media_url"])


def test_routes_video():
    row = {
        "content_type": "video",
        "body_nl": "Vid",
        "media_url": "https://drive.google.com/uc?export=download&id=v",
    }
    with patch("agent.publishers.calendar_publish.publish_video") as mock_video:
        mock_video.return_value = {"status": "success", "post_id": "v1"}
        result = publish_calendar_content(row)
    assert result["post_id"] == "v1"
    mock_video.assert_called_once_with("Vid", row["media_url"])


def test_video_missing_media_url():
    result = publish_calendar_content({"content_type": "video", "body_nl": "No url"})
    assert result["status"] == "error"
    assert "media_url" in result["error"]
