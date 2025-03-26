# Wildfire Resource Deployer & Predictor

A comprehensive application for analyzing wildfire data, tracking operational efficiency, visualizing key statistics, and predicting potential wildfire events through an interactive dashboard.

## Features

- 🔥 **Upload Wildfire Data**: Easily upload CSV files to analyze wildfire incidents and severity levels
- 📊 **Visualize Key Statistics**: View detailed charts on fires addressed, operational costs, and damage estimates
- 📍 **Predict Future Wildfires**: Get forecasts of wildfire risks based on weather and historical data

## Project Overview

This application consists of a Next.js frontend and Flask backend that work together to process, analyze, and visualize wildfire data. The system has two main components:

1. **Resource Deployer**: Analyzes historical wildfire data to optimize resource allocation and calculate efficiency metrics
2. **Wildfire Predictor**: Uses machine learning to predict future wildfire risks based on environmental data

## Prerequisites

- Node.js (v16+)
- Python (v3.8+)
- npm or yarn
- pip

## Installation

### Backend Setup

```bash
# Navigate to backend directory from the project root
cd backend

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Frontend Setup

```bash
# Navigate to frontend directory from the project root
cd frontend

# Install dependencies
npm install
# OR
yarn install
```

## Running the Application

### Start the Backend

```bash
# Make sure you're in the backend directory
cd backend

# Start the Flask server
python app.py
```

The Flask server will start on http://localhost:5000

### Start the Frontend

```bash
# Make sure you're in the frontend directory
cd frontend

# Start the Next.js development server
npm run dev
# OR
yarn dev
```

The Next.js application will start on http://localhost:3000

## Technical Architecture

### Backend System

#### Canadian Fire Weather Index (FWI) System

The backend implements the Canadian Fire Weather Index (FWI) System, a globally recognized methodology for assessing wildfire risk based on weather conditions. The system calculates several indices:

1. **Fine Fuel Moisture Code (FFMC)**: Represents moisture content of fine fuels and indicates ease of ignition
2. **Duff Moisture Code (DMC)**: Represents moisture content of loosely compacted organic layers
3. **Drought Code (DC)**: Represents deep soil moisture and seasonal drought effects
4. **Initial Spread Index (ISI)**: Combines wind and FFMC to estimate fire spread rate
5. **Buildup Index (BUI)**: Combines DMC and DC to estimate available fuel
6. **Fire Weather Index (FWI)**: Combines ISI and BUI to give overall fire intensity
7. **Daily Severity Rating (DSR)**: A transformed version of FWI used for daily fire danger

The implementation follows Van Wagner's 1987 equations with vectorized calculations for efficiency.

#### Feature Engineering

When the system processes environmental data:

1. Data is first sorted chronologically 
2. FWI components are calculated sequentially, as they depend on previous day values
3. Initial values are set (FFMC: 85.0, DMC: 6.0, DC: 15.0) as starting points
4. The system calculates all indices using temperature, humidity, wind speed, precipitation, and month
5. Additional features like vegetation indices and human activity are incorporated when available

#### Machine Learning Model

The system uses XGBoost classifier with the following characteristics:

- **Features**: Environmental data (temperature, humidity, wind speed, precipitation) and all FWI components
- **Training**: Uses chronological split (60% train, 40% test) to preserve temporal patterns and avoid data leaks
- **Class Imbalance Handling**: Uses `scale_pos_weight` parameter to account for rare wildfire events
- **Hyperparameters**: Tuned for wildfire prediction with learning rate of 0.001, 2000 trees, max depth of 6

#### Backend Workflow

1. **Data Preparation**: Environmental data is processed and enriched with FWI features
2. **Model Loading**: Pre-trained XGBoost model is loaded from the `/models` directory
3. **Prediction Generation**: Model produces probability scores for wildfire risk
4. **API Response**: Predictions are formatted with location, time, and risk factors

### Resource Deployment System

The Resource Deployer module handles wildfire event processing and resource allocation:

1. **Resource Pool**: Manages available firefighting resources (smoke jumpers, helicopters, etc.)
2. **Event Prioritization**: Sorts events by timestamp and severity to handle most urgent cases first
3. **Resource Assignment**: Allocates cheapest available resource to each fire event
4. **Cost Tracking**: Calculates operational costs for deployed resources and damage costs for missed responses
5. **Performance Analysis**: Generates statistics on response rates by severity level

## Project Structure

### Backend Components

- **Flask API** (`app.py`): Main entry point serving two routes:
  - `/api/p1/get_final_report`: Processes historical wildfire data and generates statistics
  - `/api/p2/get_predictions`: Generates wildfire predictions based on environmental data

- **Wildfire Response System** (`p1_system.py`):
  - Processes wildfire events
  - Manages resource allocation
  - Calculates efficiency metrics and damage costs

- **Machine Learning Model** (`p2_model.py`):
  - Uses XGBoost to predict wildfire occurrences
  - Features include temperature, humidity, wind speed, and Fire Weather Index components

- **Fire Weather Index Calculator** (`p2_fwi.py`):
  - Implements the Canadian Fire Weather Index system
  - Calculates indices used for fire danger predictions

- **Data Preparation** (`p2_data_prep.py`):
  - Creates features from environmental data
  - Integrates historical fire data for training

- **Prediction Export** (`p2_export.py`):
  - Formats predictions for API responses

### Frontend Components

- **Pages**:
  - Home (`page.tsx`): Landing page with features overview
  - Upload CSV (`upload-csv/page.tsx`): Interface for uploading data
  - Statistics (`statistics/page.tsx`): Visualizations of resource deployment analytics
  - Future Wildfires (`future-wildfires/page.tsx`): Map-based wildfire prediction viewer

- **Components**:
  - Charts (`BarChart.tsx`, `PieChart.tsx`, `StackedBarChart.tsx`): D3-based visualizations
  - Settings Panel (`SettingPanels.tsx`): Configuration interface for resource parameters
  - Navigation (`Navbar.tsx`): Application navigation

## Usage Workflow

1. **Upload Data**:
   - Navigate to the "Upload CSV" page
   - Upload historical wildfire data (for statistics) or environmental data (for predictions)
   - Configure operational resources and damage costs if needed

2. **View Statistics**:
   - Go to the "Resource Deployer" page to see analysis of uploaded historical data
   - Review charts showing fires addressed, cost analysis, and severity breakdowns

3. **Explore Predictions**:
   - Visit the "Wildfire Predictor" page to view predicted wildfire risks
   - Filter by date range and explore locations on the interactive map

## Data Requirements

### Statistics Data (CSV Format)
Required columns:
- `timestamp`: Date/time of the event
- `fire_start_time`: When the fire began
- `location`: Geographical coordinates
- `severity`: Fire severity level (low, medium, high)

### Predictions Data (CSV Format)
Required columns:
- `timestamp`: Date/time of the prediction
- `temperature`: Temperature in °C
- `humidity`: Relative humidity percentage
- `wind_speed`: Wind speed in km/h
- `precipitation`: Precipitation amount
- `vegetation_index`: Vegetation density indicator
- `human_activity_index`: Human activity level
- `latitude`: Location latitude
- `longitude`: Location longitude