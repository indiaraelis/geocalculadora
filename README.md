# 🌍 GeoCalculator Brazil

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![pyproj](https://img.shields.io/badge/pyproj-007ACC?style=for-the-badge&logo=python&logoColor=white)](https://pyproj4.github.io/pyproj/stable/)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML/HTML5)

## 📝 About the Project

The **GeoCalculator Brazil** is a web-based geodetic calculation application designed to perform various geospatial computations. Built with **Flask** for the backend logic and **Pyproj** for precise geodetic transformations, it offers a user-friendly interface to calculate distances, areas, azimuths, convert coordinates (geographic to UTM, decimal to DMS, DMS to decimal), and determine new coordinates based on a starting point, distance, and azimuth.

This project supports multiple geodetic datums, including those commonly used in Brazil, ensuring accuracy for diverse applications.

## ✨ Features

The GeoCalculator provides a range of functionalities for geospatial professionals and enthusiasts:

* **Geodesic Distance Calculation:** Compute the precise distance between two geographic points (latitude/longitude), along with forward and inverse azimuths.
* **Polygon Area Calculation:** Determine the area and perimeter of a polygon defined by at least three points.
* **Azimuth Calculation:** Find the direct and inverse azimuth between two geographic points.
* **Geographic to UTM Conversion:** Transform geographic coordinates (latitude/longitude) to Universal Transverse Mercator (UTM) coordinates, including zone and hemisphere determination.
* **New Coordinates Calculation:** Compute the geographic coordinates of a new point given a starting point, a distance, and an azimuth.
* **Unit Conversion:** Convert values between various common measurement units (e.g., kilometers to miles, meters to feet, nautical miles).
* **Decimal to DMS Conversion:** Convert decimal degrees to Degrees, Minutes, and Seconds (DMS) format.
* **DMS to Decimal Conversion:** Convert coordinates from DMS format back to decimal degrees.

## 🌎 Supported Geodetic Datums

The application supports the following geodetic datums, allowing for accurate calculations tailored to specific regional or global requirements:

* **WGS84** (World Geodetic System 1984) - EPSG: 4326
* **SIRGAS2000** (Sistema de Referência Geocêntrico para as Américas 2000) - EPSG: 4674
* **SAD69** (South American Datum 1969) - EPSG: 4618
* **CORREGO_ALEGRE** (Córrego Alegre 1970-72) - EPSG: 4225

## 💻 Technologies Used

* **Python:** The core programming language for the backend.
* **Flask:** A micro-web framework for Python, handling API routes and serving the frontend.
* **Pyproj:** A Python library for performing conversions between coordinate systems and geodetic calculations.
* **Flask-CORS:** Enables Cross-Origin Resource Sharing for the Flask API.
* **python-dotenv:** For managing environment variables (though currently not used for sensitive keys, it's good practice for deployment).
* **HTML5, CSS3, JavaScript:** For building the interactive and responsive frontend user interface.

## 🚀 Getting Started

Follow these steps to get a copy of the project up and running on your local machine.

### Prerequisites

Ensure you have Python installed. It's highly recommended to use a virtual environment.

* [Python 3.x](https://www.python.org/downloads/)
* `pip` (Python package installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/indiaraelis/geocalculadora.git](https://github.com/indiaraelis/geocalculadora.git)
    cd geocalculadora
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install Flask pyproj Flask-Cors python-dotenv
    ```

    *Note: The `pyproj` library might require PROJ data. The `app.py` includes `datadir.set_data_dir("/usr/share/proj")`, which is common for Linux environments. On Windows, `pyproj` usually handles PROJ data automatically upon installation. If you encounter issues related to PROJ data, refer to the [pyproj documentation](https://pyproj4.github.io/pyproj/stable/api/datadir.html).*

### Running the Application

1.  **Ensure Frontend Files:** This repository expects an `index.html` file (and potentially associated CSS) in a `templates` folder or directly in the root if Flask's `render_template` is configured differently. The provided JavaScript indicates the frontend logic that interacts with the Flask API.

2.  **Run the Flask application:**
    ```bash
    python app.py
    ```

3.  Open your web browser and navigate to `http://127.0.0.1:5000/` (or the port specified in your `app.py` or environment variables, e.g., `5001` or `5000` based on the code).

The application will be accessible through your browser, providing the interactive calculator interface.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/indiaraelis/geocalculadora/blob/main/LICENSE) file for details.

## 👩‍💻 Author

Made with 💚 by **Indiara Elis**

Geotechnology specialist passionate about transforming data into decisions.
