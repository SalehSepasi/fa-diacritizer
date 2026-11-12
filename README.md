# Persian Text Diacritization

### ✨ Give Persian text its correct pronunciation!

An AI-powered tool that automatically adds Persian diacritical marks (Harakat) to text using a pretrained deep learning model.

Built with **Python**, **PyTorch**, and **Hugging Face Transformers**, this project makes Persian text easier to read and more useful for applications such as Text-to-Speech (TTS) and Natural Language Processing (NLP).

---

## 📌 Overview

Persian is usually written without diacritical marks. While native speakers can often figure out the correct pronunciation from context, computers don't always have that ability.

That's where this project comes in!

**Persian Text Diacritization** automatically predicts and adds the appropriate diacritical marks to Persian text, making it easier for machines to understand and process.

🧠 **Powered by:** [PedramR/canine-fa-diacritizer](https://huggingface.co/PedramR/canine-fa-diacritizer)

- **Model author:** Pedram Rostami
- **Model license:** MIT
- **Base model:** [google/canine-s](https://huggingface.co/google/canine-s)
- **Base model license:** Apache-2.0

⚙️ **Architecture:** CANINE (Character-Level Neural Network)

---

## 🚀 Features

- ✍️ **Automatic Diacritization** — Add Persian diacritical marks to unvowelled text.
- 🧠 **AI-Powered Prediction** — Use a pretrained neural network to predict the appropriate marks.
- 🧹 **Text Cleaning** — Remove existing diacritical marks before processing.
- 📄 **Multi-Sentence Support** — Process multiple sentences and paragraphs.
- 🖥️ **Web Interface** — Interact with the application through Streamlit.
- 🔒 **Local Inference** — Run the model locally without sending every request to an external API.
- ⚡ **CPU Support** — Run inference with PyTorch without requiring a dedicated GPU.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| 🐍 Python 3.12 | Main programming language |
| 🔥 PyTorch | Running the neural network |
| 🤗 Hugging Face Transformers | Loading and using the model |
| 📦 Hugging Face Hub | Downloading the pretrained model |
| 🌐 Streamlit | Building the web interface |
| ⚡ uv | Managing dependencies and the Python environment |

---

### 📥 Loading the Model

```python
from transformers import CanineTokenizer, CanineForTokenClassification

MODEL_ID = "PedramR/canine-fa-diacritizer"

tokenizer = CanineTokenizer.from_pretrained(
    MODEL_ID,
    local_files_only=True
)

model = CanineForTokenClassification.from_pretrained(
    MODEL_ID,
    local_files_only=True
).eval()
```

> **Note:** The model must be downloaded before running the application. Since `local_files_only=True` is enabled, Transformers loads the model from the local Hugging Face cache instead of downloading it automatically.

---

## 📂 Project Structure

```text
fa-diacritizer/
├── .venv/
├── src/
|   |── main.py
│   └── fa_diacritizer/
│       ├── __init__.py
│       ├── model.py
│       └── pre_processor.py
├── .python-version
├── .gitignore
├── LICENSE
├── pyproject.toml
├── README.md
└── uv.lock
```

## 💻 Installation

Get started in just a few steps!

### 1️⃣ Prerequisites

Make sure you have installed:

- Python 3.12
- [uv](https://docs.astral.sh/uv/)

### 2️⃣ Clone the Repository

```bash
git clone https://github.com/SalehSepasi/fa-diacritizer.git
cd fa-diacritizer
```

### 3️⃣ Install Dependencies

```bash
uv sync
```

This command creates or synchronizes the virtual environment and installs all required dependencies.

### 4️⃣ Download the Pretrained Model

```bash
uv run hf download PedramR/canine-fa-diacritizer
```

The model files will be stored in the Hugging Face cache directory.

Once the download is complete, you're ready to run the application!

---

## 🎯 Usage

The project separates text preprocessing from model inference, allowing each component to be used independently.

**The pipeline:**

```text
       Persian Text
             │
             ▼
    🧹 Text Preprocessing
             │
             ▼
      🧠 Model Inference
             │
             ▼
     ✨ Diacritized Text
```

---

## 🌐 Running the Application

The project also includes a web-based interface built with Streamlit.

Launch it using:

```bash
uv run streamlit run src/main.py
```

---

## ⚙️ Hardware & Inference

The current development environment uses CPU-based PyTorch for model inference.

| Component | Configuration |
|---|---|
| Python | 3.12 |
| PyTorch | 2.15.0+cpu |
| CUDA | Not enabled |
| Transformers | 5.22.2 |
| Streamlit | 1.67.0 |

📌 **Input Length:** The model is configured with a maximum input length of 2048 tokens/characters, according to its tokenizer configuration and inference code.

For longer documents, consider splitting the input into smaller sections to avoid truncation.

---

## 🎯 Project Scope

This project has one main goal:

**Persian Text Diacritization.**

It focuses on converting unvowelled Persian text into text with predicted diacritical marks.

Text-to-Speech (TTS) functionality is outside the scope of this repository. Instead, the generated text can be passed to a separate TTS component.

The core diacritization functionality is designed to work independently, making it easy to integrate into other applications and NLP pipelines.

---

## 🙏 Acknowledgements

Special thanks to **[PedramR](https://huggingface.co/PedramR)** for developing and sharing the pretrained model:

🤗 [CANINE Persian Diacritizer](https://huggingface.co/PedramR/canine-fa-diacritizer)

This project builds upon their publicly available model and implementation.

---

## 📄 License

Before redistributing this project or using it commercially, make sure to review the licensing terms of both this repository and the pretrained model.

---