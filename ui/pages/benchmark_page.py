from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QTextEdit, QFrame, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer
from ui.styles import Theme
from ui.widgets.network_stats_card import NetworkStatsCard
from module4.process_state_manager import calculate_risk
import json
import os
import csv
from datetime import datetime
from collections import Counter


class BenchmarkPage(QWidget):
    def __init__(self):
        super().__init__()
        
        # State
        self.selected_file = None
        self.analysis_results = None
        
        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with export buttons
        header_layout = QHBoxLayout()
        
        header = QLabel("BENCHMARK ANALYSIS")
        header.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {Theme.COLOR_TEXT_MAIN};
            letter-spacing: 2px;
        """)
        header_layout.addWidget(header)
        header_layout.addStretch()
        
        # Export buttons (initially hidden)
        self.btn_export_pdf = self.create_export_btn("📄 PDF")
        self.btn_export_json = self.create_export_btn("📋 JSON")
        self.btn_export_csv = self.create_export_btn("📊 CSV")
        
        self.btn_export_pdf.clicked.connect(lambda: self.export_report("pdf"))
        self.btn_export_json.clicked.connect(lambda: self.export_report("json"))
        self.btn_export_csv.clicked.connect(lambda: self.export_report("csv"))
        
        self.btn_export_pdf.hide()
        self.btn_export_json.hide()
        self.btn_export_csv.hide()
        
        header_layout.addWidget(self.btn_export_pdf)
        header_layout.addWidget(self.btn_export_json)
        header_layout.addWidget(self.btn_export_csv)
        
        main_layout.addLayout(header_layout)
        
        # File Selection Section
        file_section = self.create_file_selection_section()
        main_layout.addWidget(file_section)
        
        # Scan Button
        self.btn_scan = QPushButton("🔍 SCAN FILE")
        self.btn_scan.setEnabled(False)
        self.btn_scan.setCursor(Qt.PointingHandCursor)
        self.btn_scan.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.COLOR_ACCENT};
                color: #000000;
                font-weight: bold;
                font-size: 16px;
                padding: 12px 24px;
                border: none;
                border-radius: 4px;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background-color: #00d4e6;
            }}
            QPushButton:disabled {{
                background-color: {Theme.COLOR_TEXT_DIM};
                color: #333333;
            }}
        """)
        self.btn_scan.clicked.connect(self.scan_file)
        main_layout.addWidget(self.btn_scan, alignment=Qt.AlignLeft)
        
        # Progress Bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {Theme.COLOR_BORDER};
                border-radius: 4px;
                text-align: center;
                background-color: {Theme.COLOR_PANEL};
                color: {Theme.COLOR_TEXT_MAIN};
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background-color: {Theme.COLOR_ACCENT};
                border-radius: 3px;
            }}
        """)
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)
        
        # Statistics Cards (initially hidden)
        self.stats_container = QWidget()
        stats_layout = QHBoxLayout(self.stats_container)
        stats_layout.setSpacing(15)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        
        self.stat_events = NetworkStatsCard("TOTAL EVENTS", "📊")
        self.stat_processes = NetworkStatsCard("PROCESSES", "⚙️")
        self.stat_threats = NetworkStatsCard("THREATS FOUND", "⚠️")
        self.stat_duration = NetworkStatsCard("DURATION", "⏱️")
        
        stats_layout.addWidget(self.stat_events)
        stats_layout.addWidget(self.stat_processes)
        stats_layout.addWidget(self.stat_threats)
        stats_layout.addWidget(self.stat_duration)
        
        self.stats_container.hide()
        main_layout.addWidget(self.stats_container)
        
        # Results Section
        results_label = QLabel("DETAILED ANALYSIS")
        results_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {Theme.COLOR_TEXT_DIM};
            letter-spacing: 1px;
            margin-top: 10px;
        """)
        main_layout.addWidget(results_label)
        
        # Results Display
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Theme.COLOR_PANEL};
                border: 1px solid {Theme.COLOR_BORDER};
                border-radius: 4px;
                color: {Theme.COLOR_TEXT_MAIN};
                font-family: '{Theme.FONT_FAMILY_MONO}';
                font-size: 13px;
                padding: 15px;
            }}
        """)
        self.results_display.setPlaceholderText("No analysis performed yet. Select a file and click SCAN FILE.")
        main_layout.addWidget(self.results_display, stretch=1)
        
    def create_export_btn(self, text):
        """Create styled export button"""
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {Theme.COLOR_ACCENT};
                color: {Theme.COLOR_ACCENT};
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {Theme.COLOR_ACCENT}30;
            }}
        """)
        return btn
        
    def create_file_selection_section(self):
        """Create the file selection UI section"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.COLOR_PANEL};
                border: 1px solid {Theme.COLOR_BORDER};
                border-radius: 4px;
                padding: 15px;
            }}
        """)
        
        layout = QHBoxLayout(frame)
        
        # Label
        label = QLabel("Select Data File:")
        label.setStyleSheet(f"color: {Theme.COLOR_TEXT_MAIN}; font-weight: bold;")
        layout.addWidget(label)
        
        # File path display
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setStyleSheet(f"""
            color: {Theme.COLOR_TEXT_DIM};
            padding: 5px 10px;
            background-color: rgba(0,0,0,0.3);
            border-radius: 3px;
        """)
        layout.addWidget(self.file_path_label, stretch=1)
        
        # Browse button
        btn_browse = QPushButton("📁 BROWSE...")
        btn_browse.setCursor(Qt.PointingHandCursor)
        btn_browse.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {Theme.COLOR_ACCENT};
                color: {Theme.COLOR_ACCENT};
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(0, 240, 255, 20);
            }}
        """)
        btn_browse.clicked.connect(self.browse_file)
        layout.addWidget(btn_browse)
        
        return frame
    
    def browse_file(self):
        """Open file dialog to select a JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Data File",
            "s:\\ORBIT\\module1\\output",
            "JSON Files (*.json);;All Files (*.*)"
        )
        
        if file_path:
            self.selected_file = file_path
            # Display just the filename
            filename = os.path.basename(file_path)
            self.file_path_label.setText(filename)
            self.file_path_label.setStyleSheet(f"""
                color: {Theme.COLOR_ACCENT};
                padding: 5px 10px;
                background-color: rgba(0, 240, 255, 10);
                border-radius: 3px;
            """)
            self.btn_scan.setEnabled(True)
    
    def scan_file(self):
        """Analyze the selected file and display results"""
        if not self.selected_file:
            return
        
        # Show progress bar
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        
        try:
            # Read the file
            self.progress_bar.setValue(20)
            with open(self.selected_file, 'r') as f:
                events = json.load(f)
            
            if not isinstance(events, list):
                self.show_error("Invalid file format. Expected a JSON array of events.")
                self.progress_bar.hide()
                return
            
            self.progress_bar.setValue(40)
            
            # Perform analysis
            results = self.analyze_events(events)
            self.analysis_results = results
            
            self.progress_bar.setValue(80)
            
            # Display results
            self.display_results(results)
            
            self.progress_bar.setValue(100)
            
            # Hide progress bar after a short delay
            QTimer.singleShot(500, self.progress_bar.hide)
            
            # Show export buttons
            self.btn_export_pdf.show()
            self.btn_export_json.show()
            self.btn_export_csv.show()
            
        except json.JSONDecodeError:
            self.show_error("Failed to parse JSON file. Please check the file format.")
            self.progress_bar.hide()
        except FileNotFoundError:
            self.show_error("File not found. Please select a valid file.")
            self.progress_bar.hide()
        except Exception as e:
            self.show_error(f"Error analyzing file: {str(e)}")
            self.progress_bar.hide()
    
    def analyze_events(self, events):
        """Analyze the event data and return metrics"""
        if not events:
            return {
                "total_events": 0,
                "unique_processes": 0,
                "threat_distribution": {"Malware": 0, "Suspicious": 0, "Clean": 0},
                "timeline": {"start": "N/A", "end": "N/A", "duration": "N/A", "duration_seconds": 0},
                "file_size": 0,
                "process_details": [],
                "event_types": {},
                "top_threats": []
            }
        
        # Calculate metrics
        total_events = len(events)
        unique_pids = set()
        process_risks = {}
        process_details = []
        event_types = Counter()
        process_event_counts = Counter()
        
        for event in events:
            pid = event.get("pid")
            process_name = event.get("process", "unknown")
            event_type = event.get("event", "unknown")
            
            # Count event types
            event_types[event_type] += 1
            
            if pid:
                unique_pids.add(pid)
                process_event_counts[f"{process_name}_{pid}"] += 1
                
                # Calculate risk for this process
                if pid not in process_risks:
                    risk, status = calculate_risk(process_name)
                    process_risks[pid] = status
                    process_details.append({
                        "pid": pid,
                        "name": process_name,
                        "status": status,
                        "risk": risk,
                        "event_count": 0
                    })
        
        # Update event counts for processes
        for proc in process_details:
            key = f"{proc['name']}_{proc['pid']}"
            proc["event_count"] = process_event_counts.get(key, 0)
        
        # Threat distribution
        threat_dist = {"Malware": 0, "Suspicious": 0, "Clean": 0}
        for status in process_risks.values():
            if status in threat_dist:
                threat_dist[status] += 1
        
        # Get top 5 threats
        threat_processes = [p for p in process_details if p["status"] in ["Malware", "Suspicious"]]
        top_threats = sorted(threat_processes, key=lambda x: x["risk"], reverse=True)[:5]
        
        # Timeline with duration calculation
        timestamps = [e.get("timestamp") for e in events if e.get("timestamp")]
        timeline = {
            "start": timestamps[0] if timestamps else "N/A",
            "end": timestamps[-1] if timestamps else "N/A",
            "duration": "N/A",
            "duration_seconds": 0
        }
        
        # Calculate duration if we have timestamps
        if len(timestamps) >= 2:
            try:
                # Try to parse timestamps and calculate duration
                start_time = datetime.strptime(timestamps[0], "%H:%M:%S")
                end_time = datetime.strptime(timestamps[-1], "%H:%M:%S")
                duration_seconds = (end_time - start_time).total_seconds()
                
                # Format duration
                hours = int(duration_seconds // 3600)
                minutes = int((duration_seconds % 3600) // 60)
                seconds = int(duration_seconds % 60)
                
                if hours > 0:
                    timeline["duration"] = f"{hours}h {minutes}m {seconds}s"
                elif minutes > 0:
                    timeline["duration"] = f"{minutes}m {seconds}s"
                else:
                    timeline["duration"] = f"{seconds}s"
                    
                timeline["duration_seconds"] = duration_seconds
            except:
                # If parsing fails, just count events
                timeline["duration"] = f"~{len(timestamps)} events"
        
        # File size
        file_size = os.path.getsize(self.selected_file)
        
        return {
            "total_events": total_events,
            "unique_processes": len(unique_pids),
            "threat_distribution": threat_dist,
            "timeline": timeline,
            "file_size": file_size,
            "filename": os.path.basename(self.selected_file),
            "process_details": process_details,
            "event_types": dict(event_types.most_common()),
            "top_threats": top_threats
        }
    
    def display_results(self, results):
        """Format and display analysis results"""
        # Show statistics cards
        self.stats_container.show()
        
        # Update statistics cards
        self.stat_events.set_value(results["total_events"])
        self.stat_processes.set_value(results["unique_processes"])
        
        threat_count = results["threat_distribution"]["Malware"] + results["threat_distribution"]["Suspicious"]
        self.stat_threats.set_value(threat_count)
        
        if threat_count > 0:
            self.stat_threats.set_critical(True)
        else:
            self.stat_threats.set_critical(False)
        
        # Duration
        duration_text = results["timeline"]["duration"]
        self.stat_duration.set_value(0)  # Use custom text
        self.stat_duration.value_label.setText(duration_text)
        
        # Format detailed results
        size_mb = results["file_size"] / (1024 * 1024)
        size_str = f"{size_mb:.2f} MB" if size_mb >= 1 else f"{results['file_size'] / 1024:.2f} KB"
        
        # Calculate percentages
        total_procs = results["unique_processes"]
        threat_dist = results["threat_distribution"]
        
        malware_pct = (threat_dist["Malware"] / total_procs * 100) if total_procs > 0 else 0
        sus_pct = (threat_dist["Suspicious"] / total_procs * 100) if total_procs > 0 else 0
        clean_pct = (threat_dist["Clean"] / total_procs * 100) if total_procs > 0 else 0
        
        # Build results text with enhanced formatting
        output = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                    BENCHMARK ANALYSIS REPORT                         ║
╚══════════════════════════════════════════════════════════════════════╝

📁 FILE INFORMATION
──────────────────────────────────────────────────────────────────────
  Filename:         {results['filename']}
  File Size:        {size_str}
  Total Events:     {results['total_events']:,}
  Unique Processes: {results['unique_processes']:,}

⏱️  TIMELINE
──────────────────────────────────────────────────────────────────────
  Start Time:       {results['timeline']['start']}
  End Time:         {results['timeline']['end']}
  Duration:         {results['timeline']['duration']}

🔍 THREAT ANALYSIS
──────────────────────────────────────────────────────────────────────
  🔴 Malware:       {threat_dist['Malware']:,} processes ({malware_pct:.1f}%)
  🟡 Suspicious:    {threat_dist['Suspicious']:,} processes ({sus_pct:.1f}%)
  🟢 Clean:         {threat_dist['Clean']:,} processes ({clean_pct:.1f}%)

"""
        
        # Add top threats section if any exist
        if results["top_threats"]:
            output += "🎯 TOP THREAT PROCESSES\n"
            output += "──────────────────────────────────────────────────────────────────────\n"
            for i, proc in enumerate(results["top_threats"], 1):
                icon = "🔴" if proc["status"] == "Malware" else "🟡"
                output += f"  {i}. {icon} {proc['name']} (PID: {proc['pid']})\n"
                output += f"     Risk Score: {proc['risk']}% | Events: {proc['event_count']}\n"
            output += "\n"
        
        # Add event type breakdown
        if results["event_types"]:
            output += "📊 EVENT TYPE BREAKDOWN\n"
            output += "──────────────────────────────────────────────────────────────────────\n"
            for event_type, count in list(results["event_types"].items())[:10]:  # Top 10
                pct = (count / results['total_events'] * 100) if results['total_events'] > 0 else 0
                output += f"  • {event_type:20s} {count:6,} ({pct:5.1f}%)\n"
            output += "\n"
        
        # Add process details if threats found
        if threat_dist["Malware"] > 0 or threat_dist["Suspicious"] > 0:
            output += "⚠️  ALL THREAT DETAILS\n"
            output += "──────────────────────────────────────────────────────────────────────\n"
            
            for proc in results["process_details"]:
                if proc["status"] in ["Malware", "Suspicious"]:
                    icon = "🔴" if proc["status"] == "Malware" else "🟡"
                    output += f"  {icon} {proc['name']} (PID: {proc['pid']}) - Risk: {proc['risk']}%\n"
            output += "\n"
        
        # Summary
        output += "📋 SUMMARY\n"
        output += "──────────────────────────────────────────────────────────────────────\n"
        
        if threat_dist["Malware"] > 0:
            output += f"  ⚠️  CRITICAL: {threat_dist['Malware']} malware process(es) detected!\n"
            output += "  ⚡ Immediate investigation and remediation required.\n"
        elif threat_dist["Suspicious"] > 0:
            output += f"  ⚠️  WARNING: {threat_dist['Suspicious']} suspicious process(es) detected.\n"
            output += "  📌 Review and monitoring recommended.\n"
        else:
            output += "  ✅ No threats detected. All processes appear clean.\n"
            output += "  🛡️  System baseline appears normal.\n"
        
        output += "\n" + "═" * 70 + "\n"
        output += f"Analysis completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        self.results_display.setPlainText(output)
    
    def export_report(self, format_type):
        """Export analysis results in specified format"""
        if not self.analysis_results:
            QMessageBox.warning(self, "No Data", "Please run an analysis before exporting.")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_name = f"benchmark_report_{timestamp}"
        
        if format_type == "pdf":
            self.export_pdf(default_name)
        elif format_type == "json":
            self.export_json(default_name)
        elif format_type == "csv":
            self.export_csv(default_name)
    
    def export_pdf(self, default_name):
        """Export report as PDF (text-based)"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export as PDF",
            f"{default_name}.txt",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.results_display.toPlainText())
                QMessageBox.information(self, "Export Successful", f"Report exported to:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Failed to export: {str(e)}")
    
    def export_json(self, default_name):
        """Export analysis results as JSON"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export as JSON",
            f"{default_name}.json",
            "JSON Files (*.json);;All Files (*.*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.analysis_results, f, indent=2)
                QMessageBox.information(self, "Export Successful", f"Analysis data exported to:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Failed to export: {str(e)}")
    
    def export_csv(self, default_name):
        """Export process details as CSV"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export as CSV",
            f"{default_name}.csv",
            "CSV Files (*.csv);;All Files (*.*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Header
                    writer.writerow(['Process Name', 'PID', 'Status', 'Risk Score', 'Event Count'])
                    
                    # Process details
                    for proc in self.analysis_results.get("process_details", []):
                        writer.writerow([
                            proc['name'],
                            proc['pid'],
                            proc['status'],
                            f"{proc['risk']}%",
                            proc.get('event_count', 0)
                        ])
                    
                    # Summary
                    writer.writerow([])
                    writer.writerow(['Summary'])
                    writer.writerow(['Total Events', self.analysis_results['total_events']])
                    writer.writerow(['Unique Processes', self.analysis_results['unique_processes']])
                    
                    threat_dist = self.analysis_results['threat_distribution']
                    writer.writerow(['Malware Count', threat_dist['Malware']])
                    writer.writerow(['Suspicious Count', threat_dist['Suspicious']])
                    writer.writerow(['Clean Count', threat_dist['Clean']])
                    
                QMessageBox.information(self, "Export Successful", f"Process data exported to:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Failed to export: {str(e)}")
    
    def show_error(self, message):
        """Display error message in results area"""
        error_text = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                              ERROR                                   ║
╚══════════════════════════════════════════════════════════════════════╝

❌ {message}

Please select a valid JSON file containing process event data.
"""
        self.results_display.setPlainText(error_text)
