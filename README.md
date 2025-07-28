# MSFileParserApp

**MSFileParserApp** is a Python Dash web application that parses targeted mass spectrometry experiment from **Skyline** and converts them into a **2D matrix format** for downstream statistical or bioinformatics analysis.

This tool is ideal for labs and analysts looking for a fast, browser-based interface to convert Skyline output into a pivoted matrix (samples × analytes).

---

## 🔍 What It Does

- Parses and decodes .TXT` Skyline data files
- Extracts quantification metrics like **Concentration**, **Response**, or **Area**
- Supports toggling of **internal standard inclusion**
- Transforms long-form MS data into a **pivoted matrix**: samples × analytes
- Allows direct **CSV download** of the processed matrix
- Provides a clean, responsive UI with `dash-mantine-components`

---

## 📁 Project Structure

```
MSFileParserApp/
├── app.py                   # Dash app (recommend renaming to massspec_dash_app.py)
├── scr/
│   └── conv.py              # Core logic for file decoding and data transformation
├── requirements.txt         # Python dependencies
├── README.md                # Project overview and usage
```

---

## 🛠️ Installation

```bash
# Clone the repo
git clone https://github.com/tkimhofer/MSFileParserApp.git
cd MSFileParserApp

# Set up a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Run the App

```bash
python app.py
```

Navigate to [http://127.0.0.1:8050](http://127.0.0.1:8050) in your browser.

---

## 📤 Output Format

- A **pivoted data matrix**: rows = samples, columns = analytes
- Index includes path and sample name
- Exported as `.csv` with dynamic naming:
  ```
  df_conc_[datetime].csv
  ```

---

## 🎯 Use Cases

- Preprocessing of Skyline output for statistical analysis
- Generating clean feature matrices for machine learning
- Quick QC of targeted LC-MS data via web interface

---

## 📦 Dependencies

- Dash
- Pandas
- Plotly
- dash-mantine-components

---

## 📖 License

MIT License

---

## 👩‍🔬 Acknowledgements

- Developed by [@tkimhofer](https://github.com/tkimhofer)
- Built with [Dash](https://dash.plotly.com/)
- UI powered by [dash-mantine-components](https://www.dash-mantine-components.com/)
