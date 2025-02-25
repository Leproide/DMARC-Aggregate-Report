#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
#    https://muninn.ovh
#    leprechaun@muninn.ovh
#    https://github.com/Leproide
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects

def parse_dmarc_report(file_path):
    """
    Legge un file XML di DMARC Aggregate Report e restituisce un dizionario
    con i principali dettagli e tutti i record.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    report_metadata = root.find('report_metadata')
    policy_published = root.find('policy_published')
    if not report_metadata or not policy_published:
        return None

    org_name = report_metadata.findtext('org_name', default='N/D')
    email = report_metadata.findtext('email', default='N/D')
    report_id = report_metadata.findtext('report_id', default='N/D')
    begin_epoch = report_metadata.find('date_range').findtext('begin', default='0')
    end_epoch = report_metadata.find('date_range').findtext('end', default='0')
    try:
        begin_date = datetime.utcfromtimestamp(int(begin_epoch)).strftime('%Y-%m-%d %H:%M:%S')
        end_date = datetime.utcfromtimestamp(int(end_epoch)).strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        begin_date, end_date = begin_epoch, end_epoch

    published_domain = policy_published.findtext('domain', default='N/D')
    adkim = policy_published.findtext('adkim', default='N/D')
    aspf = policy_published.findtext('aspf', default='N/D')
    p = policy_published.findtext('p', default='N/D')
    sp = policy_published.findtext('sp', default='N/D')
    pct = policy_published.findtext('pct', default='N/D')

    records = []
    for record in root.findall('record'):
        row = record.find('row')
        if row is not None:
            source_ip = row.findtext('source_ip', default='N/D')
            count = row.findtext('count', default='0')
            disposition = row.find('policy_evaluated').findtext('disposition', default='N/D')
            dkim_eval = row.find('policy_evaluated').findtext('dkim', default='N/D')
            spf_eval = row.find('policy_evaluated').findtext('spf', default='N/D')

            identifiers = record.find('identifiers')
            header_from = identifiers.findtext('header_from', default='N/D') if identifiers is not None else 'N/D'

            auth_results = record.find('auth_results')
            if auth_results is not None:
                dkim_node = auth_results.find('dkim')
                spf_node = auth_results.find('spf')
                dkim_domain = dkim_node.findtext('domain', default='N/D') if dkim_node is not None else 'N/D'
                dkim_result = dkim_node.findtext('result', default='N/D') if dkim_node is not None else 'N/D'
                dkim_selector = dkim_node.findtext('selector', default='N/D') if dkim_node is not None else 'N/D'
                spf_domain = spf_node.findtext('domain', default='N/D') if spf_node is not None else 'N/D'
                spf_result = spf_node.findtext('result', default='N/D') if spf_node is not None else 'N/D'
            else:
                dkim_domain, dkim_result, dkim_selector = 'N/D', 'N/D', 'N/D'
                spf_domain, spf_result = 'N/D', 'N/D'

            records.append({
                'source_ip': source_ip,
                'count': count,
                'disposition': disposition,
                'dkim_eval': dkim_eval,
                'spf_eval': spf_eval,
                'header_from': header_from,
                'dkim_domain': dkim_domain,
                'dkim_result': dkim_result,
                'dkim_selector': dkim_selector,
                'spf_domain': spf_domain,
                'spf_result': spf_result
            })

    return {
        'org_name': org_name,
        'email': email,
        'report_id': report_id,
        'begin_date': begin_date,
        'end_date': end_date,
        'published_domain': published_domain,
        'adkim': adkim,
        'aspf': aspf,
        'p': p,
        'sp': sp,
        'pct': pct,
        'records': records
    }

def genera_grafico_pass_fail(records, output_file="dmarc_chart.png"):
    """
    Crea un grafico a torta (pie chart) che mostra la percentuale
    di record "Pass" e "Fail".

    Consideriamo "Pass" i record in cui sia DKIM che SPF siano "pass".
    Il conteggio è basato sul valore del tag <count>.
    """
    plt.rcParams.update({'font.size': 14})
    pass_count = 0
    fail_count = 0
    for r in records:
        try:
            cnt = int(r['count'])
        except:
            cnt = 1
        if r['dkim_eval'].lower() == "pass" and r['spf_eval'].lower() == "pass":
            pass_count += cnt
        else:
            fail_count += cnt

    total = pass_count + fail_count
    if total == 0:
        print("Nessun record valido per generare il grafico a torta.")
        fig, ax = plt.subplots(figsize=(6,6))
        ax.text(0.5, 0.5, "Nessun dato", horizontalalignment='center',
                verticalalignment='center', transform=ax.transAxes, fontsize=20)
        plt.axis('off')
        plt.savefig(output_file, transparent=True)
        plt.close()
        return

    labels = ['Pass', 'Fail']
    sizes = [pass_count, fail_count]
    colors = ['#50fa7b', '#ff5555']

    fig, ax = plt.subplots(figsize=(6,6))
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                      colors=colors, startangle=90)

    outline_effect = [path_effects.withStroke(linewidth=2, foreground='white')]

    for text in texts:
        text.set_fontsize(16)
        text.set_fontweight('bold')
        text.set_color('#000000')
        text.set_path_effects(outline_effect)

    for autotext in autotexts:
        autotext.set_fontsize(18)
        autotext.set_fontweight('bold')
        autotext.set_color('#000')

    title = ax.set_title('DMARC: Pass vs Fail', color='#000000', fontsize=25, fontweight='bold')
    title.set_path_effects([path_effects.Stroke(linewidth=2, foreground='white'), path_effects.Normal()])
    plt.axis('equal')
    plt.savefig(output_file, transparent=True)
    plt.close()
    print(f"Grafico salvato in: {output_file}")

def genera_report_html_interattivo(dmarc_reports, output_html='report_dmarc_interattivo.html', chart_image='dmarc_chart.png', client_name=""):
    """
    Genera un report HTML interattivo che include:
      - Il titolo (che include il nome cliente)
      - Il grafico generato
      - Le tabelle per i record Pass e per i record Fail
      - In fondo alla pagina, una sezione collassabile che elenca (uno per riga)
        i Report ID dei report; ogni Report ID è a sua volta collassabile per mostrare i dettagli.
    """
    # Il template HTML utilizza placeholder per i dati dinamici.
    # NOTA: tutte le parentesi graffe letterali sono state raddoppiate ({{ e }}) per evitare errori con .format()
    html_content = """<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<title>Aggregate DMARC report - {client_name}</title>
<style>
  body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #282a36; color: #f8f8f2; }}
  .header {{ background-color: #44475a; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.5); margin-bottom: 20px; position: relative; }}
  .header h1 {{ margin: 0; color: #f8f8f2; }}
  body.print-mode .header h1 {{ color: #000000; }}
  .toggle-button {{ position: absolute; top: 20px; padding: 10px 15px; border-radius: 5px; cursor: pointer; font-weight: bold; border: none; }}
  #toggleAll {{ right: 20px; background-color: #bd93f9; color: #282a36; }}
  #toggleMode {{ right: 150px; background-color: #bd93f9; color: #282a36; }}
  .chart-container {{ text-align: center; margin-bottom: 20px; }}
  .details-section {{ background-color: #44475a; border-radius: 8px; padding: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.5); margin-bottom: 20px; }}
  details {{ margin-bottom: 10px; border: 1px solid #6272a4; border-radius: 5px; padding: 5px; }}
  summary {{ cursor: pointer; font-weight: bold; font-size: 1.2em; padding: 10px; background-color: #6272a4; border-radius: 5px; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
  th, td {{ padding: 8px; border: 1px solid #6272a4; text-align: left; }}
  th {{ background-color: #bd93f9; color: #282a36; }}
  hr {{ border: none; border-top: 1px solid #6272a4; margin: 20px 0; }}
  .report-ids-section details {{ margin-bottom: 5px; border: 1px solid #6272a4; border-radius: 3px; padding: 5px; }}
  .report-ids-section summary {{ font-size: 1em; background-color: #6272a4; padding: 5px; border-radius: 3px; color: #282a36; }}
  .report-ids-section p {{ margin: 5px 10px; font-size: 0.9em; }}
  body.print-mode {{ background-color: #ffffff; color: #000000; }}
  body.print-mode .header {{ background-color: #f0f0f0; color: #000000; }}
  body.print-mode .toggle-button {{ background-color: #dddddd; color: #000000; }}
  body.print-mode .details-section {{ background-color: #ffffff; }}
  body.print-mode details {{ border: 1px solid #ccc; background-color: #f7f7f7; }}
  body.print-mode summary {{ background-color: #eeeeee; color: #000000; }}
  body.print-mode th {{ background-color: #dddddd; color: #000000; }}
  body.print-mode td, body.print-mode th {{ border: 1px solid #ccc; }}
</style>
</head>
<body>
<div class="header">
  <h1>Aggregate DMARC report - {client_name}</h1>
  <button id="toggleAll" class="toggle-button">Expand all</button>
  <button id="toggleMode" class="toggle-button">Printable Mode</button>
</div>
<div class="chart-container">
  <img src="{chart_image}" alt="DMARC Chart" style="max-width:400px;">
</div>
<div class="details-section">
  <details open>
    <summary>Record Pass</summary>
    <table>
      <tr>
        <th>Source IP</th>
        <th>Count</th>
        <th>Disposition</th>
        <th>DKIM Eval</th>
        <th>SPF Eval</th>
        <th>Header From</th>
      </tr>
      {pass_rows}
    </table>
  </details>
  <details>
    <summary>Record Fail</summary>
    <table>
      <tr>
        <th>Source IP</th>
        <th>Count</th>
        <th>Disposition</th>
        <th>DKIM Eval</th>
        <th>SPF Eval</th>
        <th>Header From</th>
      </tr>
      {fail_rows}
    </table>
  </details>
</div>
<div class="details-section report-ids-section">
  <details>
    <summary>Report IDs</summary>
    {report_ids}
  </details>
</div>
<script>
document.getElementById('toggleAll').addEventListener('click', function() {{
    var details = document.querySelectorAll('details');
    var allOpen = true;
    details.forEach(function(detail) {{
        if (!detail.open) {{
            allOpen = false;
        }}
    }});
    if (!allOpen) {{
        details.forEach(function(detail) {{
            detail.open = true;
        }});
        this.textContent = "Collapse all";
    }} else {{
        details.forEach(function(detail) {{
            detail.open = false;
        }});
        this.textContent = "Expand all";
    }}
}});
document.getElementById('toggleMode').addEventListener('click', function() {{
    document.body.classList.toggle('print-mode');
    if(document.body.classList.contains('print-mode')) {{
         this.textContent = "Dark Mode";
    }} else {{
         this.textContent = "Printable Mode";
    }}
}});
</script>
</body>
</html>
"""

    # Costruiamo le righe per i record Pass e Fail e la sezione dei Report IDs
    pass_rows = ""
    fail_rows = ""
    for report in dmarc_reports:
        for r in report['records']:
            if r['dkim_eval'].lower() == 'pass' and r['spf_eval'].lower() == 'pass':
                pass_rows += f"""
      <tr>
        <td>{r['source_ip']}</td>
        <td>{r['count']}</td>
        <td>{r['disposition']}</td>
        <td>{r['dkim_eval']}</td>
        <td>{r['spf_eval']}</td>
        <td>{r['header_from']}</td>
      </tr>
"""
            else:
                fail_rows += f"""
      <tr>
        <td>{r['source_ip']}</td>
        <td>{r['count']}</td>
        <td>{r['disposition']}</td>
        <td>{r['dkim_eval']}</td>
        <td>{r['spf_eval']}</td>
        <td>{r['header_from']}</td>
      </tr>
"""
    report_ids = ""
    for report in dmarc_reports:
        report_ids += f"""
    <details>
      <summary>Report ID: {report['report_id']}</summary>
      <p><strong>Organization (org_name):</strong> {report['org_name']}</p>
      <p><strong>Contact E-Mail:</strong> {report['email']}</p>
      <p><strong>Published Domain:</strong> {report['published_domain']}</p>
      <p><strong>Range date:</strong> {report['begin_date']} - {report['end_date']}</p>
      <p><strong>Policy DMARC:</strong> p={report['p']}, sp={report['sp']}, pct={report['pct']}</p>
      <p><strong>Alignment:</strong> ADKIM={report['adkim']}, ASPF={report['aspf']}</p>
      <hr>
    </details>
"""
    html_content = html_content.format(chart_image=chart_image,
                                       client_name=client_name,
                                       pass_rows=pass_rows,
                                       fail_rows=fail_rows,
                                       report_ids=report_ids)
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"HTML report generated: {output_html}")

if __name__ == "__main__":
    # Se il nome del cliente viene passato come parametro, usalo, altrimenti chiedilo in input
    if len(sys.argv) > 1:
        client_name = sys.argv[1]
    else:
        client_name = input("Insert customer name: ")

    folder_reports = "dmarc_reports"
    all_reports = []

    # Ricerca ricorsiva dei file XML (anche nelle sottocartelle)
    for root_dir, dirs, files in os.walk(folder_reports):
        for filename in files:
            if filename.lower().endswith(".xml"):
                filepath = os.path.join(root_dir, filename)
                print(f"Parsing {filepath}...")
                try:
                    report_data = parse_dmarc_report(filepath)
                    if report_data:
                        all_reports.append(report_data)
                except Exception as e:
                    with open("error.log", "a", encoding="utf-8") as log:
                        log.write(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - Error, cant read file {filepath}: {e}\n")

    # Aggrega tutti i record per il grafico
    all_records = []
    for report in all_reports:
        all_records.extend(report['records'])
    
    # Crea la cartella di output con il nome REPORT_dd-mm-yyyy
    now = datetime.now()
    today_str = now.strftime("%d-%m-%Y")
    timestamp_str = now.strftime("%d-%m-%Y_%H-%M-%S")
    output_folder = f"REPORT_{today_str}"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    chart_file = os.path.join(output_folder, f"DMARC_{timestamp_str}.png")
    html_report_file = os.path.join(output_folder, f"DMARC_{timestamp_str}.html")
    
    genera_grafico_pass_fail(all_records, output_file=chart_file)
    genera_report_html_interattivo(all_reports, output_html=html_report_file, chart_image=os.path.basename(chart_file), client_name=client_name)
