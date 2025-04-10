from unittest.mock import patch, MagicMock
from prompts import generate_letter_prompt
from services.client_openai import generate_cover_letter


@patch("services.client_openai.client")
def test_generate_letter(mock_client):
    mock_response = MagicMock()
    mock_response.output_text = "Test"

    mock_client.responses.create.return_value = mock_response

    cv = "CV text"
    job = "Job description"
    letter = generate_cover_letter(cv, job)
    assert letter == 'Test'

    mock_client.responses.create.assert_called_once_with(
        model="gpt-4o",
        instructions=generate_letter_prompt,
        input=f"<cv> {cv} </cv> <job> {job} </job>"
    )
