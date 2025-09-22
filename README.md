# Georgian Corner (ქართული კუთხე)

**Georgian Corner** is a specialized desktop application designed to generate high-quality Georgian (ქართული) advertisements using AI technology. Built specifically for Georgian businesses, marketers, and content creators who need professional, culturally-appropriate advertising content in the Georgian language.

## What It Does

This application transforms your product information into compelling Georgian advertisements through an intuitive spreadsheet-style interface. Simply input your product names and descriptions, select your desired tone, and let AI generate professional marketing copy that resonates with Georgian-speaking audiences.

### Key Capabilities

* **AI-Powered Georgian Content**: Generates authentic, grammatically correct Georgian advertisements using OpenAI's GPT models
* **Cultural Sensitivity**: Designed specifically for Georgian market nuances and language patterns
* **Multiple Advertising Tones**: Choose from professional, friendly, urgent, luxury, or casual tones to match your brand voice
* **Batch Processing**: Generate multiple advertisements simultaneously with intelligent rate limiting
* **CSV Integration**: Import existing product data and export generated content for easy integration with your workflow
* **Privacy-First**: Your OpenAI API key stays on your device - no data is stored remotely

## Who It's Created For

* **Georgian E-commerce Businesses**: Online retailers selling to Georgian-speaking customers
* **Local Georgian Businesses**: Restaurants, shops, and services needing professional marketing materials
* **Georgian Marketing Agencies**: Content creators and marketers serving Georgian clients
* **Georgian Freelancers**: Copywriters and marketers working with Georgian brands
* **International Companies**: Businesses expanding into the Georgian market who need culturally appropriate content

## Features

* Spreadsheet UI with three columns: Product Name, Description, Generated Ad
* Choose advertising tone (professional, friendly, urgent, luxury, casual)
* Import / export CSV files
* Batch ad generation with rate limiting and progress status
* Users supply their own OpenAI API key — no key is stored remotely

## Tech-Stack

| Layer     | Technology |
|-----------|------------|
| Language  | Python 3.9+ |
| GUI       | [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) |
| AI        | OpenAI `gpt-3.5-turbo` via [openai-python](https://github.com/openai/openai-python) |
| Prompts   | LangGraph (placeholder) |
| Data I/O  | pandas |

## Installation

```bash
# Clone repository
$ git clone https://github.com/yourname/TakoADsGenerator.git
$ cd TakoADsGenerator

# Create virtual environment (optional)
$ python -m venv .venv
$ source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
$ pip install -r requirements.txt
```

Create a `.env` file or use the GUI to enter your key:

```
OPENAI_API_KEY=sk-...
```

## Usage

```bash
# Optional but recommended on macOS to suppress deprecated system Tk warning
export TK_SILENCE_DEPRECATION=1
python main.py
```

1. Click **Enter API Key** and paste your OpenAI key.
2. Import an existing CSV *or* start typing product names and descriptions.
3. Pick a tone from the drop-down.
4. Press **Generate Ads**.
5. Export your finished CSV when ready.

## CSV Format

Column order:

| A | B | C |
|---|---|---|
| Product Name | Product Description | Generated Advertisement |

Headers are optional.

## Design Tokens

* Primary: **#FA8148** (buttons)
* Background: **#FFF5B2**
* Success: **#03CEA4**

## Roadmap / TODO

* Integrate LangGraph workflows for richer prompt chains
* Advanced caching to skip already-generated ads
* Undo / Redo support in spreadsheet widget
* Unit testing suite

---
© 2025 Giga Inc. All rights reserved.
