# LearnEd - AI Powered Study Buddy

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An intelligent Streamlit web application that leverages the Google Gemini API to transform your study materials into dynamic learning tools. Upload your notes, and let the AI summarize key concepts, simplify complex topics, generate interactive quizzes, and create a structured study plan.

## Features

-   **Multi-format File Upload**: Ingests study notes from `.pdf`, `.docx`, and `.txt` files, or directly from pasted text.
-   **AI-Powered Summarization**: Condenses long documents into concise summaries. Choose from multiple styles: short, detailed, or bullet points.
-   **Concept Simplification**: Explains complex topics in easy-to-understand language, with modes for both beginners and college-level learners.
-   **Automatic Quiz Generation**: Creates multiple-choice questions and flashcards from your study material to test your knowledge.
-   **Custom Study Plans**: Generates a structured study session plan, breaking down topics into manageable blocks of study, revision, and breaks.
-   **Text-to-Speech Accessibility**: Reads generated summaries and explanations aloud with the click of a button, enhancing accessibility and allowing for auditory learning.
-   **Downloadable Content**: Save generated summaries, explanations, and flashcards (as `.csv`) for offline use.

## Getting Started

Follow these instructions to get a local copy of the project up and running on your machine.

### Prerequisites

-   Python 3.8+
-   An active Google Gemini API Key.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/manolina-13/AI-powered--Study-Buddy.git
    cd AI-powered--Study-Buddy
    ```

2.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up your Gemini API Key:**
    Create an environment variable to store your API key.

    *On Windows (PowerShell):*
    ```powershell
    $env:GEMINI_API_KEY="YOUR_API_KEY_HERE"
    ```

    *On macOS/Linux:*
    ```bash
    export GEMINI_API_KEY="YOUR_API_KEY_HERE"
    ```
    ***Note**: For a permanent solution, add this line to your `.bashrc`, `.zshrc`, or shell configuration file.*

### Running the Application

Once the setup is complete, launch the Streamlit application:

```bash
streamlit run app.py
```

Navigate to the local URL provided by Streamlit in your web browser to start using the AI Study Buddy.

## How to Use

1.  **Provide Input**: Use the sidebar to either upload a document (`.pdf`, `.docx`, `.txt`) or paste your text directly into the text area.
2.  **Configure Options**: Adjust the settings for summarization, simplification, quizzes, and study plans in the sidebar.
3.  **Select an Action**: Click one of the main action buttons:
    -   `🔍 Summarize`
    -   `🧑‍🏫 Simplify / Explain`
    -   `📝 Generate Quiz`
    -   `🗓️ Plan Session`
4. **Interact with the Output**: The generated content will appear in the main panel. For summaries and explanations, click the 🔊 Read Aloud button to listen to the text. Use the download buttons to save any    materials you need.
5.  **View and Download**: The generated content will appear in the main panel. Use the download buttons to save the materials you need.

## Code Overview

The application is structured to separate concerns, making it easy to maintain and extend.

-   **`app.py`**: The main Streamlit application file. It handles the user interface, state management, and orchestrates calls to the backend logic.
-   **`utils/file_reader.py`**: Contains functions for reading and extracting text from various file formats.
-   **`utils/prompts.py`**: Defines the prompt engineering logic, creating structured prompts for the Gemini API for each feature.
-   **`utils/gemini_client.py`**: A wrapper for the Google Gemini API, handling the communication and response retrieval.
-   **`utils/quiz_parser.py`**: Safely parses the JSON output from the API to extract quiz and flashcard data, with robust error handling.

## License

This project is distributed under the MIT License. See `LICENSE` for more information.

## Contact

Manolina Das - [GitHub Profile](https://github.com/manolina-13)

Project Link: [https://github.com/manolina-13/AI-powered--Study-Buddy](https://github.com/manolina-13/AI-powered--Study-Buddy)
