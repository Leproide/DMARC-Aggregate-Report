# DMARC Aggregate Report
Python script for generating human-readable HTML summaries with a chart for aggregated DMARC reports.

### Dependencies
```bash
pip install matplotlib
```
### Instructions

- Place all the XML reports (or zip/gz archive) in a folder named `dmarc_reports`.
- Run `report.bat`.

The Python script will create a folder with today's date and generate a report with all the data found in the provided XML files.

When the report is generated, all files in the working folder `dmarc_reports` will be automatically deleted. 

You can easily automate the creation of reports upon receiving a DMARC email by scripting it within an email client (eg, Thunderbird with FiltaQuilla addon).

The HTML report has two modes:
1. The first mode uses the classic Dracula theme.
2. The second mode is print-friendly with a white background to save toner/ink.

The script is configurable to add a name to the title. For example:
```bash
python.exe REPORT_Full.py "Test S.r.l"
```


## Screenshots
![immagine](https://github.com/user-attachments/assets/e730f4d7-c841-4510-b275-f123840463b5)

![immagine](https://github.com/user-attachments/assets/ffe2e3f3-9d8b-4255-875c-f87563c29e16)

