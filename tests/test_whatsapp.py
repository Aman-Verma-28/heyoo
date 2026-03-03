"""
Comprehensive tests for the heyoo WhatsApp Cloud API wrapper.
"""

import unittest
from unittest.mock import patch, MagicMock
from heyoo import WhatsApp


class TestWhatsAppConstructor(unittest.TestCase):
    """Tests for WhatsApp class initialization."""

    def test_init_with_token_and_phone_number_id(self):
        messenger = WhatsApp(token="test_token", phone_number_id="123456")
        self.assertEqual(messenger.token, "test_token")
        self.assertEqual(
            messenger.url,
            "https://graph.facebook.com/v13.0/123456/messages",
        )
        self.assertEqual(messenger.headers["Content-Type"], "application/json")
        self.assertEqual(
            messenger.headers["Authorization"], "Bearer test_token"
        )

    def test_init_with_none_defaults(self):
        messenger = WhatsApp()
        self.assertIsNone(messenger.token)
        self.assertEqual(
            messenger.url,
            "https://graph.facebook.com/v13.0/None/messages",
        )
        self.assertEqual(
            messenger.headers["Authorization"], "Bearer None"
        )

    def test_init_with_only_token(self):
        messenger = WhatsApp(token="my_token")
        self.assertEqual(messenger.token, "my_token")
        self.assertIn("None", messenger.url)

    def test_init_with_only_phone_number_id(self):
        messenger = WhatsApp(phone_number_id="999")
        self.assertIsNone(messenger.token)
        self.assertIn("999", messenger.url)


class TestSendMessage(unittest.TestCase):
    """Tests for send_message method."""

    def setUp(self):
        self.messenger = WhatsApp(token="test_token", phone_number_id="123456")

    @patch("heyoo.requests.post")
    def test_send_message_basic(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"messages": [{"id": "msg_id_1"}]}
        mock_post.return_value = mock_response

        result = self.messenger.send_message("Hello", "1234567890")

        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs["json"] if "json" in call_kwargs.kwargs else call_kwargs[1]["json"]
        self.assertEqual(payload["messaging_product"], "whatsapp")
        self.assertEqual(payload["to"], "1234567890")
        self.assertEqual(payload["type"], "text")
        self.assertEqual(payload["text"]["body"], "Hello")
        self.assertTrue(payload["text"]["preview_url"])
        self.assertEqual(payload["recipient_type"], "individual")
        self.assertEqual(result, {"messages": [{"id": "msg_id_1"}]})

    @patch("heyoo.requests.post")
    def test_send_message_with_preview_url_false(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"messages": [{"id": "msg_id_2"}]}
        mock_post.return_value = mock_response

        self.messenger.send_message("Hello", "1234567890", preview_url=False)

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs["json"] if "json" in call_kwargs.kwargs else call_kwargs[1]["json"]
        self.assertFalse(payload["text"]["preview_url"])

    @patch("heyoo.requests.post")
    def test_send_message_with_recipient_type(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        self.messenger.send_message(
            "Hello", "1234567890", recipient_type="group"
        )

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs["json"] if "json" in call_kwargs.kwargs else call_kwargs[1]["json"]
        self.assertEqual(payload["recipient_type"], "group")

    @patch("heyoo.requests.post")
    def test_send_message_uses_correct_url_and_headers(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        self.messenger.send_message("test", "1234567890")

        call_args = mock_post.call_args
        self.assertEqual(
            call_args.args[0] if call_args.args else call_args[0][0],
            "https://graph.facebook.com/v13.0/123456/messages",
        )
        headers = call_args.kwargs.get("headers") or call_args[1].get("headers")
        self.assertEqual(headers["Authorization"], "Bearer test_token")


class TestSendTemplate(unittest.TestCase):
    """Tests for send_template method."""

    def setUp(self):
        self.messenger = WhatsApp(token="test_token", phone_number_id="123456")

    @patch("heyoo.requests.post")
    def test_send_template_default_language(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"messages": [{"id": "tmpl_1"}]}
        mock_post.return_value = mock_response

        result = self.messenger.send_template("hello_world", "1234567890")

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs["json"] if "json" in call_kwargs.kwargs else call_kwargs[1]["json"]
        self.assertEqual(payload["messaging_product"], "whatsapp")
        self.assertEqual(payload["to"], "1234567890")
        self.assertEqual(payload["type"], "template")
        self.assertEqual(payload["template"]["name"], "hello_world")
        self.assertEqual(payload["template"]["language"]["code"], "en_US")
        self.assertEqual(result, {"messages": [{"id": "tmpl_1"}]})

    @patch("heyoo.requests.post")
    def test_send_template_custom_language(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        self.messenger.send_template("greeting", "1234567890", lang="es_ES")

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs["json"] if "json" in call_kwargs.kwargs else call_kwargs[1]["json"]
        self.assertEqual(payload["template"]["language"]["code"], "es_ES")


class TestSendLocation(unittest.TestCase):
    """Tests for send_location method."""

    def setUp(self):
        self.messenger = WhatsApp(token="test_token", phone_number_id="123456")

    @patch("heyoo.requests.post")
    def test_send_location(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"messages": [{"id": "loc_1"}]}
        mock_post.return_value = mock_response

        result = self.messenger.send_location(
            lat="-6.7924",
            long="39.2083",
            name="Dar es Salaam",
            address="Tanzania",
            recipient_id="1234567890",
        )

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs["json"] if "json" in call_kwargs.kwargs else call_kwargs[1]["json"]
        self.assertEqual(payload["messaging_product"], "whatsapp")
        self.assertEqual(payload["to"], "1234567890")
        self.assertEqual(payload["type"], "location")
        self.assertEqual(payload["location"]["latitude"], "-6.7924")
        self.assertEqual(payload["location"]["longitude"], "39.2083")
        self.assertEqual(payload["location"]["name"], "Dar es Salaam")
        self.assertEqual(payload["location"]["address"], "Tanzania")
        self.assertEqual(result, {"messages": [{"id": "loc_1"}]})


class TestSendImage(unittest.TestCase):
    """Tests for send_image method."""

    def setUp(self):
        self.messenger = WhatsApp(token="test_token", phone_number_id="123456")

    @patch("heyoo.requests.post")
    def test_send_image_with_link(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"messages": [{"id": "img_1"}]}
        mock_post.return_value = mock_response

        result = self.messenger.send_image(
            image="https://example.com/image.jpg",
            recipient_id="1234567890",
            caption="Test image",
            link=True,
        )

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs["json"] if "json" in call_kwargs.kwargs else call_kwargs[1]["json"]
        self.assertEqual(payload["type"], "image")
        self.assertEqual(payload["image"]["link"], "https://example.com/image.jpg")
        self.assertEqual(payload["image"]["caption"], "Test image")
        self.assertNotIn("id", payload["image"])
        self.assertEqual(result, {"messages": [{"id": "img_1"}]})

    @patch("heyoo.requests.post")
    def test_send_image_with_media_id(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        self.messenger.send_image(
            image="media_id_123",
            recipient_id="1234567890",
            caption="Uploaded image",
            link=False,
        )

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs["json"] if "json" in call_kwargs.kwargs else call_kwargs[1]["json"]
        self.assertEqual(payload["image"]["id"], "media_id_123")
        self.assertEqual(payload["image"]["caption"], "Uploaded image")
        self.assertNotIn("link", payload["image"])

    @patch("heyoo.requests.post")
    def test_send_image_default_link_true(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        self.messenger.send_image(
            image="https://example.com/photo.png",
            recipient_id="1234567890",
        )

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs["json"] if "json" in call_kwargs.kwargs else call_kwargs[1]["json"]
        self.assertIn("link", payload["image"])
        self.assertIsNone(payload["image"]["caption"])

    @patch("heyoo.requests.post")
    def test_send_image_recipient_type(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        self.messenger.send_image(
            image="https://example.com/photo.png",
            recipient_id="1234567890",
            recipient_type="group",
        )

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs["json"] if "json" in call_kwargs.kwargs else call_kwargs[1]["json"]
        self.assertEqual(payload["recipient_type"], "group")


class TestSendAudio(unittest.TestCase):
    """Tests for send_audio method."""

    def setUp(self):
        self.messenger = WhatsApp(token="test_token", phone_number_id="123456")

    @patch("heyoo.requests.post")
    def test_send_audio_with_link(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"messages": [{"id": "audio_1"}]}
        mock_post.return_value = mock_response

        result = self.messenger.send_audio(
            audio="https://example.com/audio.mp3",
            recipient_id="1234567890",
            link=True,
        )

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs["json"] if "json" in call_kwargs.kwargs else call_kwargs[1]["json"]
        self.assertEqual(payload["type"], "audio")
        self.assertEqual(payload["audio"]["link"], "https://example.com/audio.mp3")
        self.assertNotIn("id", payload["audio"])
        self.assertEqual(result, {"messages": [{"id": "audio_1"}]})

    @patch("heyoo.requests.post")
    def test_send_audio_with_media_id(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        self.messenger.send_audio(
            audio="audio_media_id_456",
            recipient_id="1234567890",
            link=False,
        )

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs["json"] if "json" in call_kwargs.kwargs else call_kwargs[1]["json"]
        self.assertEqual(payload["audio"]["id"], "audio_media_id_456")
        self.assertNotIn("link", payload["audio"])


class TestSendVideo(unittest.TestCase):
    """Tests for send_video method."""

    def setUp(self):
        self.messenger = WhatsApp(token="test_token", phone_number_id="123456")

    @patch("heyoo.requests.post")
    def test_send_video_with_link(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"messages": [{"id": "video_1"}]}
        mock_post.return_value = mock_response

        result = self.messenger.send_video(
            video="https://example.com/video.mp4",
            recipient_id="1234567890",
            caption="My video",
            link=True,
        )

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs["json"] if "json" in call_kwargs.kwargs else call_kwargs[1]["json"]
        self.assertEqual(payload["type"], "video")
        self.assertEqual(payload["video"]["link"], "https://example.com/video.mp4")
        self.assertEqual(payload["video"]["caption"], "My video")
        self.assertNotIn("id", payload["video"])
        self.assertEqual(result, {"messages": [{"id": "video_1"}]})

    @patch("heyoo.requests.post")
    def test_send_video_with_media_id(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        self.messenger.send_video(
            video="video_media_id_789",
            recipient_id="1234567890",
            caption="Uploaded video",
            link=False,
        )

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs["json"] if "json" in call_kwargs.kwargs else call_kwargs[1]["json"]
        self.assertEqual(payload["video"]["id"], "video_media_id_789")
        self.assertEqual(payload["video"]["caption"], "Uploaded video")
        self.assertNotIn("link", payload["video"])

    @patch("heyoo.requests.post")
    def test_send_video_no_caption(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        self.messenger.send_video(
            video="https://example.com/video.mp4",
            recipient_id="1234567890",
        )

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs["json"] if "json" in call_kwargs.kwargs else call_kwargs[1]["json"]
        self.assertIsNone(payload["video"]["caption"])


class TestSendDocument(unittest.TestCase):
    """Tests for send_document method."""

    def setUp(self):
        self.messenger = WhatsApp(token="test_token", phone_number_id="123456")

    @patch("heyoo.requests.post")
    def test_send_document_with_link(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"messages": [{"id": "doc_1"}]}
        mock_post.return_value = mock_response

        result = self.messenger.send_document(
            document="https://example.com/doc.pdf",
            recipient_id="1234567890",
            caption="My document",
            link=True,
        )

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs["json"] if "json" in call_kwargs.kwargs else call_kwargs[1]["json"]
        self.assertEqual(payload["type"], "document")
        self.assertEqual(payload["document"]["link"], "https://example.com/doc.pdf")
        self.assertEqual(payload["document"]["caption"], "My document")
        self.assertNotIn("id", payload["document"])
        self.assertEqual(result, {"messages": [{"id": "doc_1"}]})

    @patch("heyoo.requests.post")
    def test_send_document_with_media_id(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        self.messenger.send_document(
            document="doc_media_id_321",
            recipient_id="1234567890",
            caption="Uploaded doc",
            link=False,
        )

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs["json"] if "json" in call_kwargs.kwargs else call_kwargs[1]["json"]
        self.assertEqual(payload["document"]["id"], "doc_media_id_321")
        self.assertEqual(payload["document"]["caption"], "Uploaded doc")
        self.assertNotIn("link", payload["document"])

    @patch("heyoo.requests.post")
    def test_send_document_no_caption(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        self.messenger.send_document(
            document="https://example.com/doc.pdf",
            recipient_id="1234567890",
        )

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs["json"] if "json" in call_kwargs.kwargs else call_kwargs[1]["json"]
        self.assertIsNone(payload["document"]["caption"])


class TestCreateButton(unittest.TestCase):
    """Tests for create_button method."""

    def setUp(self):
        self.messenger = WhatsApp(token="test_token", phone_number_id="123456")

    def test_create_button(self):
        button_data = {
            "header": "Menu Header",
            "body": "Choose an option",
            "footer": "Tap to select",
            "action": {
                "button": "Options",
                "sections": [
                    {
                        "title": "Section 1",
                        "rows": [
                            {"id": "1", "title": "Option 1", "description": "First"},
                            {"id": "2", "title": "Option 2", "description": "Second"},
                        ],
                    }
                ],
            },
        }
        result = self.messenger.create_button(button_data)

        self.assertEqual(result["type"], "list")
        self.assertEqual(result["header"]["type"], "text")
        self.assertEqual(result["header"]["text"], "Menu Header")
        self.assertEqual(result["body"]["text"], "Choose an option")
        self.assertEqual(result["footer"]["text"], "Tap to select")
        self.assertEqual(result["action"], button_data["action"])

    def test_create_button_missing_keys(self):
        button_data = {}
        result = self.messenger.create_button(button_data)
        self.assertEqual(result["type"], "list")
        self.assertIsNone(result["header"]["text"])
        self.assertIsNone(result["body"]["text"])
        self.assertIsNone(result["footer"]["text"])
        self.assertIsNone(result["action"])


class TestSendButton(unittest.TestCase):
    """Tests for send_button method."""

    def setUp(self):
        self.messenger = WhatsApp(token="test_token", phone_number_id="123456")

    @patch("heyoo.requests.post")
    def test_send_button(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"messages": [{"id": "btn_1"}]}
        mock_post.return_value = mock_response

        button = {
            "header": "Header",
            "body": "Body text",
            "footer": "Footer",
            "action": {"button": "Menu", "sections": []},
        }
        result = self.messenger.send_button(button, "1234567890")

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs["json"] if "json" in call_kwargs.kwargs else call_kwargs[1]["json"]
        self.assertEqual(payload["messaging_product"], "whatsapp")
        self.assertEqual(payload["to"], "1234567890")
        self.assertEqual(payload["type"], "interactive")
        self.assertEqual(payload["interactive"]["type"], "list")
        self.assertEqual(result, {"messages": [{"id": "btn_1"}]})


class TestSendReplyButton(unittest.TestCase):
    """Tests for send_reply_button method."""

    def setUp(self):
        self.messenger = WhatsApp(token="test_token", phone_number_id="123456")

    @patch("heyoo.requests.post")
    def test_send_reply_button(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"messages": [{"id": "rbtn_1"}]}
        mock_post.return_value = mock_response

        reply_button = {
            "type": "button",
            "body": {"text": "Choose one"},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "yes", "title": "Yes"}},
                    {"type": "reply", "reply": {"id": "no", "title": "No"}},
                ]
            },
        }
        result = self.messenger.send_reply_button(reply_button, "1234567890")

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs["json"] if "json" in call_kwargs.kwargs else call_kwargs[1]["json"]
        self.assertEqual(payload["messaging_product"], "whatsapp")
        self.assertEqual(payload["recipient_type"], "individual")
        self.assertEqual(payload["to"], "1234567890")
        self.assertEqual(payload["type"], "interactive")
        self.assertEqual(payload["interactive"], reply_button)
        self.assertEqual(result, {"messages": [{"id": "rbtn_1"}]})


class TestPreprocess(unittest.TestCase):
    """Tests for preprocess method."""

    def setUp(self):
        self.messenger = WhatsApp(token="test_token", phone_number_id="123456")

    def test_preprocess_extracts_value(self):
        data = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {"messaging_product": "whatsapp", "metadata": {}},
                            "field": "messages",
                        }
                    ]
                }
            ]
        }
        result = self.messenger.preprocess(data)
        self.assertEqual(result, {"messaging_product": "whatsapp", "metadata": {}})


class TestChangedField(unittest.TestCase):
    """Tests for changed_field method."""

    def setUp(self):
        self.messenger = WhatsApp(token="test_token", phone_number_id="123456")

    def test_changed_field_messages(self):
        data = {
            "entry": [{"changes": [{"value": {}, "field": "messages"}]}]
        }
        self.assertEqual(self.messenger.changed_field(data), "messages")

    def test_changed_field_other(self):
        data = {
            "entry": [{"changes": [{"value": {}, "field": "account_update"}]}]
        }
        self.assertEqual(self.messenger.changed_field(data), "account_update")


class TestGetMobile(unittest.TestCase):
    """Tests for get_mobile method."""

    def setUp(self):
        self.messenger = WhatsApp(token="test_token", phone_number_id="123456")

    def test_get_mobile_with_contacts(self):
        data = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "contacts": [{"wa_id": "1234567890", "profile": {"name": "John"}}],
                                "messages": [{"from": "1234567890", "type": "text", "text": {"body": "Hi"}}],
                            },
                            "field": "messages",
                        }
                    ]
                }
            ]
        }
        self.assertEqual(self.messenger.get_mobile(data), "1234567890")

    def test_get_mobile_without_contacts(self):
        data = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "statuses": [{"status": "delivered"}],
                            },
                            "field": "messages",
                        }
                    ]
                }
            ]
        }
        self.assertIsNone(self.messenger.get_mobile(data))


class TestGetName(unittest.TestCase):
    """Tests for get_name method."""

    def setUp(self):
        self.messenger = WhatsApp(token="test_token", phone_number_id="123456")

    def test_get_name(self):
        data = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "contacts": [{"wa_id": "1234567890", "profile": {"name": "Alice"}}],
                                "messages": [{"from": "1234567890", "type": "text", "text": {"body": "Hi"}}],
                            },
                            "field": "messages",
                        }
                    ]
                }
            ]
        }
        self.assertEqual(self.messenger.get_name(data), "Alice")


class TestGetMessage(unittest.TestCase):
    """Tests for get_message method."""

    def setUp(self):
        self.messenger = WhatsApp(token="test_token", phone_number_id="123456")

    def test_get_message_text(self):
        data = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "from": "1234567890",
                                        "id": "msg_001",
                                        "type": "text",
                                        "text": {"body": "Hello World"},
                                        "timestamp": "1234567890",
                                    }
                                ]
                            },
                            "field": "messages",
                        }
                    ]
                }
            ]
        }
        self.assertEqual(self.messenger.get_message(data), "Hello World")

    def test_get_message_no_messages(self):
        data = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {"statuses": [{"status": "read"}]},
                            "field": "messages",
                        }
                    ]
                }
            ]
        }
        self.assertIsNone(self.messenger.get_message(data))


class TestGetMessageId(unittest.TestCase):
    """Tests for get_message_id method."""

    def setUp(self):
        self.messenger = WhatsApp(token="test_token", phone_number_id="123456")

    def test_get_message_id(self):
        data = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "from": "1234567890",
                                        "id": "wamid.abc123",
                                        "type": "text",
                                        "text": {"body": "test"},
                                        "timestamp": "1234567890",
                                    }
                                ]
                            },
                            "field": "messages",
                        }
                    ]
                }
            ]
        }
        self.assertEqual(self.messenger.get_message_id(data), "wamid.abc123")

    def test_get_message_id_no_messages(self):
        data = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {"statuses": [{"status": "sent"}]},
                            "field": "messages",
                        }
                    ]
                }
            ]
        }
        self.assertIsNone(self.messenger.get_message_id(data))


class TestGetMessageTimestamp(unittest.TestCase):
    """Tests for get_message_timestamp method."""

    def setUp(self):
        self.messenger = WhatsApp(token="test_token", phone_number_id="123456")

    def test_get_message_timestamp(self):
        data = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "from": "1234567890",
                                        "id": "msg_ts",
                                        "type": "text",
                                        "text": {"body": "test"},
                                        "timestamp": "1672531200",
                                    }
                                ]
                            },
                            "field": "messages",
                        }
                    ]
                }
            ]
        }
        self.assertEqual(self.messenger.get_message_timestamp(data), "1672531200")

    def test_get_message_timestamp_no_messages(self):
        data = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {"statuses": [{"status": "delivered"}]},
                            "field": "messages",
                        }
                    ]
                }
            ]
        }
        self.assertIsNone(self.messenger.get_message_timestamp(data))


class TestGetMessageType(unittest.TestCase):
    """Tests for get_message_type method."""

    def setUp(self):
        self.messenger = WhatsApp(token="test_token", phone_number_id="123456")

    def test_get_message_type_text(self):
        data = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {"from": "1234567890", "type": "text", "text": {"body": "Hi"}}
                                ]
                            },
                            "field": "messages",
                        }
                    ]
                }
            ]
        }
        self.assertEqual(self.messenger.get_message_type(data), "text")

    def test_get_message_type_image(self):
        data = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {"from": "1234567890", "type": "image", "image": {"id": "img_id"}}
                                ]
                            },
                            "field": "messages",
                        }
                    ]
                }
            ]
        }
        self.assertEqual(self.messenger.get_message_type(data), "image")

    def test_get_message_type_interactive(self):
        data = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "from": "1234567890",
                                        "type": "interactive",
                                        "interactive": {"type": "list_reply", "list_reply": {"id": "1"}},
                                    }
                                ]
                            },
                            "field": "messages",
                        }
                    ]
                }
            ]
        }
        self.assertEqual(self.messenger.get_message_type(data), "interactive")

    def test_get_message_type_no_messages(self):
        data = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {"statuses": [{"status": "read"}]},
                            "field": "messages",
                        }
                    ]
                }
            ]
        }
        self.assertIsNone(self.messenger.get_message_type(data))


class TestGetInteractiveResponse(unittest.TestCase):
    """Tests for get_interactive_response method."""

    def setUp(self):
        self.messenger = WhatsApp(token="test_token", phone_number_id="123456")

    def test_get_interactive_response(self):
        data = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "from": "1234567890",
                                        "type": "interactive",
                                        "interactive": {
                                            "type": "list_reply",
                                            "list_reply": {"id": "option_1", "title": "Option 1"},
                                        },
                                    }
                                ]
                            },
                            "field": "messages",
                        }
                    ]
                }
            ]
        }
        result = self.messenger.get_interactive_response(data)
        self.assertEqual(result, {"id": "option_1", "title": "Option 1"})

    def test_get_interactive_response_no_messages(self):
        data = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {"statuses": [{"status": "read"}]},
                            "field": "messages",
                        }
                    ]
                }
            ]
        }
        self.assertIsNone(self.messenger.get_interactive_response(data))


class TestGetDelivery(unittest.TestCase):
    """Tests for get_delivery method."""

    def setUp(self):
        self.messenger = WhatsApp(token="test_token", phone_number_id="123456")

    def test_get_delivery_sent(self):
        data = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "statuses": [
                                    {
                                        "id": "wamid.xyz",
                                        "status": "sent",
                                        "timestamp": "1234567890",
                                        "recipient_id": "1234567890",
                                    }
                                ]
                            },
                            "field": "messages",
                        }
                    ]
                }
            ]
        }
        self.assertEqual(self.messenger.get_delivery(data), "sent")

    def test_get_delivery_delivered(self):
        data = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "statuses": [
                                    {
                                        "id": "wamid.xyz",
                                        "status": "delivered",
                                        "timestamp": "1234567890",
                                        "recipient_id": "1234567890",
                                    }
                                ]
                            },
                            "field": "messages",
                        }
                    ]
                }
            ]
        }
        self.assertEqual(self.messenger.get_delivery(data), "delivered")

    def test_get_delivery_read(self):
        data = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "statuses": [
                                    {
                                        "id": "wamid.xyz",
                                        "status": "read",
                                        "timestamp": "1234567890",
                                        "recipient_id": "1234567890",
                                    }
                                ]
                            },
                            "field": "messages",
                        }
                    ]
                }
            ]
        }
        self.assertEqual(self.messenger.get_delivery(data), "read")

    def test_get_delivery_no_statuses(self):
        data = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {"from": "1234567890", "type": "text", "text": {"body": "Hi"}}
                                ]
                            },
                            "field": "messages",
                        }
                    ]
                }
            ]
        }
        self.assertIsNone(self.messenger.get_delivery(data))


class TestWebhookIntegration(unittest.TestCase):
    """Integration-style tests simulating full webhook data flows."""

    def setUp(self):
        self.messenger = WhatsApp(token="test_token", phone_number_id="123456")

    def test_full_text_message_webhook(self):
        """Simulate a full incoming text message webhook payload."""
        webhook_data = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "BUSINESS_ACCOUNT_ID",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {
                                    "display_phone_number": "15551234567",
                                    "phone_number_id": "123456",
                                },
                                "contacts": [
                                    {
                                        "profile": {"name": "Test User"},
                                        "wa_id": "15559876543",
                                    }
                                ],
                                "messages": [
                                    {
                                        "from": "15559876543",
                                        "id": "wamid.HBgLMTU1NTk4NzY1NDMVAgARGBI5QTNDQ",
                                        "timestamp": "1677000000",
                                        "text": {"body": "Hello from webhook!"},
                                        "type": "text",
                                    }
                                ],
                            },
                            "field": "messages",
                        }
                    ],
                }
            ],
        }

        self.assertEqual(self.messenger.changed_field(webhook_data), "messages")
        self.assertEqual(self.messenger.get_mobile(webhook_data), "15559876543")
        self.assertEqual(self.messenger.get_name(webhook_data), "Test User")
        self.assertEqual(self.messenger.get_message(webhook_data), "Hello from webhook!")
        self.assertEqual(
            self.messenger.get_message_id(webhook_data),
            "wamid.HBgLMTU1NTk4NzY1NDMVAgARGBI5QTNDQ",
        )
        self.assertEqual(self.messenger.get_message_timestamp(webhook_data), "1677000000")
        self.assertEqual(self.messenger.get_message_type(webhook_data), "text")

    def test_full_delivery_status_webhook(self):
        """Simulate a full delivery status webhook payload."""
        webhook_data = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "BUSINESS_ACCOUNT_ID",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {
                                    "display_phone_number": "15551234567",
                                    "phone_number_id": "123456",
                                },
                                "statuses": [
                                    {
                                        "id": "wamid.HBgLMTU1NTk4NzY1NDMVAgARGBI5QTNDQ",
                                        "status": "delivered",
                                        "timestamp": "1677000100",
                                        "recipient_id": "15559876543",
                                    }
                                ],
                            },
                            "field": "messages",
                        }
                    ],
                }
            ],
        }

        self.assertEqual(self.messenger.changed_field(webhook_data), "messages")
        self.assertEqual(self.messenger.get_delivery(webhook_data), "delivered")
        self.assertIsNone(self.messenger.get_mobile(webhook_data))
        self.assertIsNone(self.messenger.get_message(webhook_data))

    def test_full_interactive_message_webhook(self):
        """Simulate a full incoming interactive list reply webhook payload."""
        webhook_data = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "BUSINESS_ACCOUNT_ID",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {
                                    "display_phone_number": "15551234567",
                                    "phone_number_id": "123456",
                                },
                                "contacts": [
                                    {
                                        "profile": {"name": "Interactive User"},
                                        "wa_id": "15550001111",
                                    }
                                ],
                                "messages": [
                                    {
                                        "from": "15550001111",
                                        "id": "wamid.INTERACTIVE_MSG",
                                        "timestamp": "1677000200",
                                        "type": "interactive",
                                        "interactive": {
                                            "type": "list_reply",
                                            "list_reply": {
                                                "id": "row_1",
                                                "title": "First Option",
                                                "description": "The first option",
                                            },
                                        },
                                    }
                                ],
                            },
                            "field": "messages",
                        }
                    ],
                }
            ],
        }

        self.assertEqual(self.messenger.get_message_type(webhook_data), "interactive")
        response = self.messenger.get_interactive_response(webhook_data)
        self.assertEqual(response["id"], "row_1")
        self.assertEqual(response["title"], "First Option")


if __name__ == "__main__":
    unittest.main()
