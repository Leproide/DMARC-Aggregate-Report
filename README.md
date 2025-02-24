# DMARC Aggregate Report
Python script for generating human-readable HTML summaries with a chart for aggregated DMARC reports.

### Dependencies
```bash
pip install matplotlib
```
### Instructions

- Place all the XML reports in a folder named `dmarc_reports`.
- Run `report.bat`.

The Python script will create a folder with today's date and generate a report with all the data found in the provided XML files.

The HTML report has two modes:
1. The first mode uses the classic Dracula theme.
2. The second mode is print-friendly with a white background to save toner/ink.

The script is configurable to add a name to the title. For example:
```bash
python.exe REPORT_Full.py "Test S.r.l"
```


## Screenshots
![immagine](https://github.com/user-attachments/assets/da896732-3600-44db-a2c8-9430506e61a6)

![immagine](https://github.com/user-attachments/assets/adf2744d-fd61-4144-b974-772e769ead9b)
