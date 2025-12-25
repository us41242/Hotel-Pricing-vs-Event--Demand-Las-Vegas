# Hotel Pricing vs. Event Demand (Las Vegas)

This project analyzes the relationship between hotel prices in Las Vegas and major local events (concerts, shows, sports). It consists of a data collection pipeline (scrapers) and an analysis script to identify price surges.

## Project Structure

- `booking_scraper.py`: Scrapes Booking.com for hotel prices for the upcoming weekend.
- `event_scraper.py`: Scrapes VisitLasVegas.com for upcoming events.
- `analyze_data.py`: Merges the collected datasets and calculates average hotel prices based on event presence.
- `data/`: Directory where all CSV data and analysis results are stored.

## Setup

1. **Install Dependencies**
   Ensure you have Python 3 installed. Install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```

2. **Requirements**
   - Google Chrome (installed on your system).
   - This project uses `selenium` and `webdriver-manager` to automatically handle the Chrome driver.

## Usage

### 1. Collect Data
Run the scrapers to gather fresh data.

**Scrape Hotel Prices:**
```bash
python booking_scraper.py --headless
```
*Note: The `--headless` flag runs the browser in the background.*

**Scrape Events:**
```bash
python event_scraper.py
```

### 2. Analyze Data
Run the analysis script to correlate prices with events.
```bash
python analyze_data.py
```

## Output
The analysis script will output a summary to the terminal and save a detailed report to `data/analysis_summary.csv`.

**Example Output:**
```text
--- Average Price by Event Count ---
   Events During Stay  Average Price
0                   0         $191.08
1                   3         $245.50
```
