# Cardiac Monitoring System

A web-based cardiac monitoring system built with Flask that provides real-time ECG visualization and arrhythmia detection.

## Features

- Real-time ECG monitoring with realistic waveform generation
- Multiple cardiac rhythm simulations:
  - Normal Sinus Rhythm
  - Sinus Tachycardia
  - Sinus Bradycardia
  - Atrial Fibrillation
  - Ventricular Tachycardia
  - Ventricular Fibrillation
  - 2nd Degree Heart Block
  - 3rd Degree Heart Block
  - Premature Ventricular Contractions (PVC)
- AI-based rhythm analysis
- Vital signs monitoring (Heart Rate, Blood Pressure, O2 Saturation, Temperature)
- Patient information display

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cardiac-monitoring.git
cd cardiac-monitoring
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Technologies Used

- Python
- Flask
- HTML/CSS
- JavaScript
- Plotly.js for real-time plotting
- Bootstrap for UI components

## Project Structure

```
cardiac-monitoring/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   └── monitor.html     # ECG monitoring interface
├── static/              # Static files (CSS, JS)
└── README.md           # Project documentation
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This system is for educational and demonstration purposes only. It should not be used as a primary medical device for patient care without proper medical certification and validation. 