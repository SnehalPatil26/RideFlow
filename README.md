# 🚕 RideFlow – Smart Ride Data Engineering & Analytics Platform

RideFlow is an end-to-end Data Engineering and Analytics project designed to process, clean, validate, transform, store, and analyze large-scale ride-booking data.

The project demonstrates a complete data pipeline starting from raw CSV data and ending with an interactive analytics dashboard.

---

## 📌 Project Overview

RideFlow processes real-world ride-booking data containing more than 100,000 records.

The system performs:

- Data Ingestion
- Data Cleaning
- Data Validation
- Data Transformation
- Data Storage
- SQL-based Analytics
- Dashboard Visualization
- Pipeline Monitoring

The final processed data is stored in a SQLite database and exposed through a Flask API for dashboard visualization.

---

## 🎯 Objectives

The main objectives of RideFlow are:

1. Build an end-to-end Data Engineering pipeline.
2. Clean and prepare raw ride-booking data.
3. Validate data quality and identify invalid records.
4. Transform raw data into analytics-ready information.
5. Store processed data in a SQL database.
6. Generate useful ride and business analytics.
7. Provide an interactive dashboard for data visualization.
8. Demonstrate pipeline execution and monitoring.

---

## 🔄 Data Engineering Pipeline

```text
                 RAW DATA
                    │
                    ▼
              Bookings.csv
                    │
                    ▼
            ┌─────────────────┐
            │ Data Ingestion  │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Data Cleaning   │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Data Validation │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Transformation  │
            └────────┬────────┘
                     │
                     ▼
              Clean CSV Data
                     │
                     ▼
            ┌─────────────────┐
            │ SQLite Database │
            └────────┬────────┘
                     │
                     ▼
              Flask REST API
                     │
                     ▼
          Interactive Dashboard