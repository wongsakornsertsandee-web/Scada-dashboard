# Mini SCADA Web Dashboard
## You can see our website and Dashboard in this link !! https://scada-dashboard.onrender.com/ !!
Real-time Smart Building / HVAC Monitoring Dashboard using Flask, SQLite, and Open-Meteo API.
---
## Features
- Realtime Weather Monitoring
- Historical Data Logging
- Automation Logic
- Alarm / Event System
- Historical Trend Graph
- API vs Database Verification
- SQLite Database Storage
- Responsive Web Dashboard
---
## Dashboard Preview
### Main Dashboard
- Temperature
- Humidity
- Wind Speed
- Precipitation
- Heater Status
- Ventilation Status
- Weather Alarm
### Historical Data
- Historical Trend Graph
- Scrollable Historical Table
- SQLite Data Logging
### Data Verification
- Compare Open-Meteo API data with SQLite database
- Real-time validation system
---
## System Architecture
Open-Meteo API →Python Flask Backend → SQLite Database → Web Dashboard
      //You can customize it in app.py
Temperature < 18°C → Heater ON // --Humidity > 70% → Ventilation ON // --Wind Speed > 15 km/h OR Rain > 5 mm → Weather Alarm ON.
| Technology          | Purpose             |
| ------------------- | ------------------- |
| Python              | Backend Logic       |
| Flask               | Web Framework       |
| SQLite              | Historical Database |
| Chart.js            | Realtime Graph      |
| Open-Meteo API      | Weather Data Source |
| HTML/CSS/JavaScript | Frontend UI         |
| Gunicorn            | Production Server   |
| Render              | Cloud Deployment    |


#Sources 
#Flask Full Course https://www.youtube.com/watch?v=Z1RJmh_OqeA
#Documentation     https://flask.palletsprojects.com/en/stable/?utm_source=chatgpt.com
#SQLite Database   https://www.youtube.com/watch?v=pd-0G0MigUA
#Getting Started With Chart.js https://www.youtube.com/watch?v=sE08f4iuOhA !!
