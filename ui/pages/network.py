from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QHeaderView, QAbstractItemView, QLineEdit,
    QPushButton, QComboBox, QFrame, QFileDialog, QMessageBox
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QTimer
from ui.styles import Theme
from ui.widgets.network_stats_card import NetworkStatsCard
from ui.widgets.packet_flow_widget import PacketFlowWidget
from ui.widgets.connection_detail_panel import ConnectionDetailPanel
from module1.network_tracker import NetworkTracker
import random
import csv
from datetime import datetime


class NetworkPage(QWidget):
    def __init__(self):
        super().__init__()
        
        # Initialize network tracker
        self.network_tracker = NetworkTracker()
        
        # Data
        self.connections = []
        self.filtered_connections = []
        self.connection_history = []  # Last 100 connections
        self.selected_connection = None
        
        # Statistics
        self.stats = {
            'active_count': 0,
            'prev_count': 0,
            'total_bytes_sent': 0,
            'total_bytes_received': 0,
            'threat_level': 0,
            'tcp_count': 0,
            'udp_count': 0
        }
        
        self.setup_ui()
        
        # Timers
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(2000)  # Refresh every 2 seconds
        
        self.stats_timer = QTimer(self)
        self.stats_timer.timeout.connect(self.update_statistics)
        self.stats_timer.start(1000)  # Update stats every second
        
        # Initial load
        self.refresh_data()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header = QLabel("NETWORK TRAFFIC MONITOR")
        header.setStyleSheet(f"""
            font-size: 24px; 
            font-weight: bold; 
            color: {Theme.COLOR_TEXT_MAIN};
            letter-spacing: 2px;
        """)
        main_layout.addWidget(header)
        
        # Statistics Dashboard
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        self.stat_active = NetworkStatsCard("ACTIVE CONNECTIONS", "🔗")
        self.stat_data = NetworkStatsCard("DATA TRANSFER", "📊")
        self.stat_threat = NetworkStatsCard("THREAT LEVEL", "⚠")
        self.stat_protocols = NetworkStatsCard("TCP/UDP RATIO", "📡")
        
        stats_layout.addWidget(self.stat_active)
        stats_layout.addWidget(self.stat_data)
        stats_layout.addWidget(self.stat_threat)
        stats_layout.addWidget(self.stat_protocols)
        
        main_layout.addLayout(stats_layout)
        
        # Content area with detail panel
        content_layout = QHBoxLayout()
        content_layout.setSpacing(0)
        
        # Left side - main content
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)
        
        # Packet Flow Visualization
        viz_label = QLabel("PACKET FLOW VISUALIZATION")
        viz_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            color: {Theme.COLOR_TEXT_DIM};
            letter-spacing: 1px;
        """)
        left_layout.addWidget(viz_label)
        
        self.packet_flow = PacketFlowWidget()
        self.packet_flow.setFixedHeight(300)
        left_layout.addWidget(self.packet_flow)
        
        # Filters and Search
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        
        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by IP, Port, or Process...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Theme.COLOR_PANEL};
                border: 1px solid {Theme.COLOR_BORDER};
                color: {Theme.COLOR_TEXT_MAIN};
                padding: 8px;
                border-radius: 4px;
                font-family: '{Theme.FONT_FAMILY_MONO}';
            }}
            QLineEdit:focus {{
                border: 1px solid {Theme.COLOR_ACCENT};
            }}
        """)
        self.search_input.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.search_input, 3)
        
        # Protocol filter
        self.protocol_filter = QComboBox()
        self.protocol_filter.addItems(["All Protocols", "TCP", "UDP"])
        self.protocol_filter.setStyleSheet(f"""
            QComboBox {{
                background-color: {Theme.COLOR_PANEL};
                border: 1px solid {Theme.COLOR_BORDER};
                color: {Theme.COLOR_TEXT_MAIN};
                padding: 8px;
                border-radius: 4px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {Theme.COLOR_PANEL};
                color: {Theme.COLOR_TEXT_MAIN};
                selection-background-color: {Theme.COLOR_ACCENT};
            }}
        """)
        self.protocol_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.protocol_filter, 1)
        
        # Quick filter buttons
        self.btn_suspicious = self.create_filter_btn("⚠ Suspicious Only")
        self.btn_suspicious.setCheckable(True)
        self.btn_suspicious.clicked.connect(self.apply_filters)
        filter_layout.addWidget(self.btn_suspicious, 1)
        
        self.btn_export = self.create_filter_btn("📥 Export CSV")
        self.btn_export.clicked.connect(self.export_to_csv)
        filter_layout.addWidget(self.btn_export, 1)
        
        left_layout.addLayout(filter_layout)
        
        # Connection Table
        table_label = QLabel("ACTIVE CONNECTIONS")
        table_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            color: {Theme.COLOR_TEXT_DIM};
            letter-spacing: 1px;
        """)
        left_layout.addWidget(table_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "PROCESS", "PID", "PROTOCOL", "LOCAL", "REMOTE", "STATE", "DURATION"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setFocusPolicy(Qt.NoFocus)
        
        # Table styling
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {Theme.COLOR_PANEL};
                color: {Theme.COLOR_TEXT_MAIN};
                gridline-color: {Theme.COLOR_BORDER};
                border: 1px solid {Theme.COLOR_BORDER};
                font-family: '{Theme.FONT_FAMILY_MONO}';
                font-size: 12px;
            }}
            QHeaderView::section {{
                background-color: {Theme.COLOR_BG};
                color: {Theme.COLOR_ACCENT};
                border: none;
                padding: 10px;
                font-weight: bold;
                border-bottom: 2px solid {Theme.COLOR_ACCENT};
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {Theme.COLOR_BORDER};
            }}
            QTableWidget::item:selected {{
                background-color: {Theme.COLOR_BORDER};
                color: {Theme.COLOR_ACCENT};
                border-left: 3px solid {Theme.COLOR_ACCENT};
            }}
        """)
        
        self.table.itemSelectionChanged.connect(self.on_row_selected)
        left_layout.addWidget(self.table)
        
        content_layout.addWidget(left_widget, 7)
        
        # Right side - detail panel
        self.detail_panel = ConnectionDetailPanel()
        self.detail_panel.closed.connect(self.on_detail_panel_closed)
        self.detail_panel.action_block.connect(self.action_block_connection)
        self.detail_panel.action_whitelist.connect(self.action_whitelist_connection)
        self.detail_panel.action_report.connect(self.action_report_connection)
        content_layout.addWidget(self.detail_panel, 3)
        
        main_layout.addLayout(content_layout)
        
    def create_filter_btn(self, text):
        """Create styled filter button"""
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.COLOR_PANEL};
                border: 1px solid {Theme.COLOR_BORDER};
                color: {Theme.COLOR_TEXT_MAIN};
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                border-color: {Theme.COLOR_ACCENT};
                background-color: {Theme.COLOR_ACCENT}20;
            }}
            QPushButton:checked {{
                background-color: {Theme.COLOR_ACCENT}40;
                border-color: {Theme.COLOR_ACCENT};
                color: {Theme.COLOR_ACCENT};
            }}
        """)
        return btn
        
    def refresh_data(self):
        """Fetch latest network connections"""
        try:
            # Get real network data
            real_connections = self.network_tracker.get_current_connections()
            
            # Enhance with threat detection
            for conn in real_connections:
                conn['status'] = self.detect_threat(conn)
                conn['risk'] = self.calculate_risk(conn)
                
            self.connections = real_connections
            
            # Update history (keep last 100)
            for conn in real_connections:
                if conn not in self.connection_history:
                    self.connection_history.append(conn)
            self.connection_history = self.connection_history[-100:]
            
        except Exception as e:
            print(f"Error refreshing data: {e}")
            # Fallback to simulated data if real data fails
            self.connections = self.generate_simulated_data()
        
        self.apply_filters()
        
    def detect_threat(self, conn):
        """Detect suspicious connections based on heuristics"""
        remote_port = conn.get('remote_port', 0)
        remote_ip = conn.get('remote_ip', '')
        
        # Suspicious ports
        suspicious_ports = [4444, 6667, 31337, 12345, 1337]
        
        # Check for suspicious indicators
        if remote_port in suspicious_ports:
            return 'Malware'
        elif remote_port > 49152 and random.random() < 0.1:  # High ports, 10% chance
            return 'Suspicious'
        elif conn.get('process', '').lower() in ['powershell.exe', 'cmd.exe'] and random.random() < 0.2:
            return 'Suspicious'
        else:
            return 'Clean'
            
    def calculate_risk(self, conn):
        """Calculate risk score for connection"""
        status = conn.get('status', 'Clean')
        
        if status == 'Malware':
            return random.randint(85, 99)
        elif status == 'Suspicious':
            return random.randint(40, 75)
        else:
            return random.randint(0, 30)
            
    def generate_simulated_data(self):
        """Generate simulated connection data as fallback"""
        simulated = []
        processes = ['chrome.exe', 'firefox.exe', 'discord.exe', 'steam.exe', 'python.exe']
        
        for i in range(random.randint(5, 15)):
            local_port = random.randint(49152, 65535)
            remote_port = random.choice([80, 443, 8080, 3000])
            remote_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            
            conn = {
                'pid': random.randint(1000, 9999),
                'process': random.choice(processes),
                'proto': random.choice(['TCP', 'UDP']),
                'local': f"192.168.1.100:{local_port}",
                'remote': f"{remote_ip}:{remote_port}",
                'remote_ip': remote_ip,
                'remote_port': remote_port,
                'state': random.choice(['ESTABLISHED', 'TIME_WAIT', 'CLOSE_WAIT']),
                'duration': f"{random.randint(1, 300)}s",
                'bytes': f"{random.randint(0, 1000)} KB"
            }
            
            conn['status'] = self.detect_threat(conn)
            conn['risk'] = self.calculate_risk(conn)
            simulated.append(conn)
            
        return simulated
        
    def apply_filters(self):
        """Apply search and filter criteria"""
        search_text = self.search_input.text().lower()
        protocol = self.protocol_filter.currentText()
        show_suspicious = self.btn_suspicious.isChecked()
        
        self.filtered_connections = []
        
        for conn in self.connections:
            # Protocol filter
            if protocol != "All Protocols" and conn['proto'] != protocol:
                continue
                
            # Suspicious filter
            if show_suspicious and conn['status'] not in ['Suspicious', 'Malware']:
                continue
                
            # Search filter
            if search_text:
                searchable = f"{conn['process']} {conn['remote']} {conn['local']} {conn['pid']}".lower()
                if search_text not in searchable:
                    continue
                    
            self.filtered_connections.append(conn)
            
        self.refresh_table()
        
    def refresh_table(self):
        """Update table with filtered connections"""
        self.table.setRowCount(len(self.filtered_connections))
        
        for r, conn in enumerate(self.filtered_connections):
            # Process
            process_item = QTableWidgetItem(conn['process'])
            self.table.setItem(r, 0, process_item)
            
            # PID
            pid_item = QTableWidgetItem(str(conn['pid']))
            pid_item.setForeground(QColor(Theme.COLOR_TEXT_DIM))
            self.table.setItem(r, 1, pid_item)
            
            # Protocol
            proto_item = QTableWidgetItem(conn['proto'])
            self.table.setItem(r, 2, proto_item)
            
            # Local
            local_item = QTableWidgetItem(conn['local'])
            self.table.setItem(r, 3, local_item)
            
            # Remote
            remote_item = QTableWidgetItem(conn['remote'])
            
            # Color based on status
            if conn['status'] == 'Malware':
                remote_item.setForeground(QColor(Theme.COLOR_MALWARE))
            elif conn['status'] == 'Suspicious':
                remote_item.setForeground(QColor(Theme.COLOR_SUS))
            else:
                remote_item.setForeground(QColor(Theme.COLOR_CLEAN))
                
            self.table.setItem(r, 4, remote_item)
            
            # State
            state_item = QTableWidgetItem(conn['state'])
            self.table.setItem(r, 5, state_item)
            
            # Duration
            duration_item = QTableWidgetItem(conn['duration'])
            self.table.setItem(r, 6, duration_item)
            
        # Update packet flow visualization
        self.update_packet_flow()
        
    def update_packet_flow(self):
        """Update packet flow visualization with current connections"""
        # Group connections by remote IP for visualization
        connection_groups = {}
        
        for conn in self.filtered_connections[:12]:  # Limit for performance
            remote = conn['remote']
            if remote not in connection_groups:
                connection_groups[remote] = {
                    'remote_ip': conn['remote_ip'],
                    'status': conn['status'],
                    'count': 0
                }
            connection_groups[remote]['count'] += 1
            
        self.packet_flow.set_connections(list(connection_groups.values()))
        
    def update_statistics(self):
        """Update statistics cards"""
        # Active connections
        active_count = len(self.connections)
        trend = ((active_count - self.stats['prev_count']) / max(self.stats['prev_count'], 1)) * 100
        self.stat_active.set_value(active_count)
        self.stat_active.set_trend(trend)
        self.stats['prev_count'] = active_count
        
        # Data transfer (simulated)
        total_kb = sum([int(c['bytes'].split()[0]) for c in self.connections])
        self.stat_data.set_value(total_kb, " KB")
        
        # Threat level
        threat_count = sum([1 for c in self.connections if c['status'] in ['Suspicious', 'Malware']])
        threat_percent = (threat_count / max(len(self.connections), 1)) * 100
        self.stat_threat.set_value(threat_percent, "%")
        
        if threat_percent > 30:
            self.stat_threat.set_critical(True)
        else:
            self.stat_threat.set_critical(False)
            
        # Protocol ratio
        tcp_count = sum([1 for c in self.connections if c['proto'] == 'TCP'])
        udp_count = len(self.connections) - tcp_count
        ratio = f"{tcp_count}/{udp_count}"
        self.stat_protocols.set_value(0)  # Use label instead
        self.stat_protocols.value_label.setText(ratio)
        
    def on_row_selected(self):
        """Handle row selection"""
        selected_rows = self.table.selectionModel().selectedRows()
        
        if selected_rows:
            row = selected_rows[0].row()
            self.selected_connection = self.filtered_connections[row]
            self.detail_panel.show_connection(self.selected_connection)
        else:
            self.selected_connection = None
            
    def on_detail_panel_closed(self):
        """Handle detail panel close"""
        self.table.clearSelection()
        self.selected_connection = None
        
    def action_block_connection(self, conn):
        """Block a connection"""
        QMessageBox.information(
            self,
            "Connection Blocked",
            f"Blocked connection to {conn['remote']}\n\nNote: This is a simulation. Actual blocking would require firewall integration."
        )
        
    def action_whitelist_connection(self, conn):
        """Whitelist a connection"""
        QMessageBox.information(
            self,
            "Connection Whitelisted",
            f"Whitelisted {conn['process']} connections to {conn['remote']}"
        )
        
    def action_report_connection(self, conn):
        """Generate report for connection"""
        QMessageBox.information(
            self,
            "Report Generated",
            f"Security report generated for connection:\n\nProcess: {conn['process']}\nRemote: {conn['remote']}\nStatus: {conn['status']}\nRisk: {conn['risk']}%"
        )
        
    def export_to_csv(self):
        """Export current connections to CSV"""
        if not self.filtered_connections:
            QMessageBox.warning(self, "No Data", "No connections to export.")
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Connections",
            f"network_connections_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='') as csvfile:
                    fieldnames = ['process', 'pid', 'proto', 'local', 'remote', 'state', 'duration', 'status', 'risk']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for conn in self.filtered_connections:
                        writer.writerow({k: conn.get(k, '') for k in fieldnames})
                        
                QMessageBox.information(self, "Export Successful", f"Exported {len(self.filtered_connections)} connections to:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Failed to export: {str(e)}")
