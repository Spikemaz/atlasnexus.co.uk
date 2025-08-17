#!/usr/bin/env python3
"""
AtlasNexus Security Tracking System
Monitors failed login attempts and sends notifications
"""

import json
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import hashlib

class SecurityTracker:
    def __init__(self, db_path='security_incidents.db'):
        self.db_path = db_path
        self.init_database()
        
        # Email configuration - you'll need to set these
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.smtp_username = os.environ.get('SMTP_USERNAME', '')
        self.smtp_password = os.environ.get('SMTP_PASSWORD', '')
        self.alert_email = 'marcus@atlasnexus.co.uk'
        
    def init_database(self):
        """Initialize the security incidents database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table for tracking failed attempts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT NOT NULL,
                attempted_passwords TEXT,
                attempt_count INTEGER,
                user_agent TEXT,
                referrer TEXT,
                country TEXT,
                city TEXT,
                isp TEXT,
                incident_type TEXT,
                lockout_triggered BOOLEAN DEFAULT 0,
                email_sent BOOLEAN DEFAULT 0,
                resolved BOOLEAN DEFAULT 0,
                notes TEXT
            )
        ''')
        
        # Table for temporary login attempts (cleared on success)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS temp_login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT NOT NULL,
                attempted_password TEXT,
                user_agent TEXT,
                session_id TEXT
            )
        ''')
        
        # Table for IP reputation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ip_reputation (
                ip_address TEXT PRIMARY KEY,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_attempts INTEGER DEFAULT 0,
                blocked_count INTEGER DEFAULT 0,
                risk_score INTEGER DEFAULT 0,
                is_whitelisted BOOLEAN DEFAULT 0,
                is_blacklisted BOOLEAN DEFAULT 0,
                notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def log_failed_attempt(self, ip_address: str, password: str, user_agent: str, 
                          session_id: str = None) -> Dict:
        """Log a failed password attempt"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Hash the password for security (we don't store actual passwords)
        password_hash = hashlib.sha256(password.encode()).hexdigest()[:8]
        
        # Add to temporary attempts
        cursor.execute('''
            INSERT INTO temp_login_attempts (ip_address, attempted_password, user_agent, session_id)
            VALUES (?, ?, ?, ?)
        ''', (ip_address, password_hash, user_agent, session_id))
        
        # Count attempts from this IP in last hour
        one_hour_ago = datetime.now() - timedelta(hours=1)
        cursor.execute('''
            SELECT COUNT(*) FROM temp_login_attempts 
            WHERE ip_address = ? AND timestamp > ?
        ''', (ip_address, one_hour_ago))
        
        attempt_count = cursor.fetchone()[0]
        
        # Update IP reputation
        cursor.execute('''
            INSERT INTO ip_reputation (ip_address, total_attempts, last_seen)
            VALUES (?, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(ip_address) DO UPDATE SET
                total_attempts = total_attempts + 1,
                last_seen = CURRENT_TIMESTAMP,
                risk_score = CASE 
                    WHEN total_attempts > 10 THEN 100
                    WHEN total_attempts > 5 THEN 75
                    WHEN total_attempts > 3 THEN 50
                    ELSE 25
                END
        ''', (ip_address,))
        
        conn.commit()
        
        # Check if this triggers a security incident (4+ attempts)
        incident_data = None
        if attempt_count >= 4:
            incident_data = self.create_security_incident(ip_address, cursor)
            
        conn.close()
        
        return {
            'attempt_count': attempt_count,
            'incident_triggered': incident_data is not None,
            'incident_data': incident_data
        }
        
    def create_security_incident(self, ip_address: str, cursor) -> Dict:
        """Create a security incident record and trigger notifications"""
        
        # Get all attempts from this IP in the last hour
        one_hour_ago = datetime.now() - timedelta(hours=1)
        cursor.execute('''
            SELECT attempted_password, user_agent 
            FROM temp_login_attempts 
            WHERE ip_address = ? AND timestamp > ?
            ORDER BY timestamp DESC
        ''', (ip_address, one_hour_ago))
        
        attempts = cursor.fetchall()
        passwords = [a[0] for a in attempts]
        user_agent = attempts[0][1] if attempts else 'Unknown'
        
        # Get IP location info (you'd integrate with an IP geolocation API)
        location_info = self.get_ip_location(ip_address)
        
        # Create incident record
        cursor.execute('''
            INSERT INTO security_incidents 
            (ip_address, attempted_passwords, attempt_count, user_agent, 
             country, city, isp, incident_type, lockout_triggered, email_sent)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ip_address,
            json.dumps(passwords),
            len(attempts),
            user_agent,
            location_info.get('country', 'Unknown'),
            location_info.get('city', 'Unknown'),
            location_info.get('isp', 'Unknown'),
            '45min_lockout' if len(attempts) == 4 else 'permanent_lockout',
            1,
            0
        ))
        
        incident_id = cursor.lastrowid
        
        # Prepare incident data
        incident_data = {
            'id': incident_id,
            'ip_address': ip_address,
            'attempt_count': len(attempts),
            'passwords_tried': passwords,
            'user_agent': user_agent,
            'location': location_info,
            'timestamp': datetime.now().isoformat()
        }
        
        # Send email notification
        self.send_security_alert(incident_data)
        
        # Mark email as sent
        cursor.execute('''
            UPDATE security_incidents SET email_sent = 1 WHERE id = ?
        ''', (incident_id,))
        
        return incident_data
        
    def send_security_alert(self, incident_data: Dict):
        """Send email alert for security incident"""
        if not self.smtp_username or not self.smtp_password:
            print("Email credentials not configured - skipping notification")
            return
            
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🚨 AtlasNexus Security Alert - IP {incident_data['ip_address']}"
            msg['From'] = self.smtp_username
            msg['To'] = self.alert_email
            
            # Create HTML email body
            html = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .alert-box {{ 
                        background: #fff3cd; 
                        border: 2px solid #ffc107; 
                        padding: 20px; 
                        border-radius: 8px;
                        margin: 20px 0;
                    }}
                    .critical {{ 
                        background: #f8d7da; 
                        border-color: #dc3545; 
                    }}
                    .info-grid {{
                        display: grid;
                        grid-template-columns: 150px 1fr;
                        gap: 10px;
                        margin: 15px 0;
                    }}
                    .label {{ font-weight: bold; color: #333; }}
                    .value {{ color: #666; }}
                    .passwords {{ 
                        background: #f0f0f0; 
                        padding: 10px; 
                        border-radius: 4px;
                        font-family: monospace;
                    }}
                </style>
            </head>
            <body>
                <h2>⚠️ Security Incident Detected</h2>
                
                <div class="alert-box {'critical' if incident_data['attempt_count'] >= 5 else ''}">
                    <h3>Potential Breach Attempt</h3>
                    <p>An IP address has triggered the security lockout after multiple failed attempts.</p>
                </div>
                
                <div class="info-grid">
                    <div class="label">Incident ID:</div>
                    <div class="value">#{incident_data['id']}</div>
                    
                    <div class="label">IP Address:</div>
                    <div class="value">{incident_data['ip_address']}</div>
                    
                    <div class="label">Failed Attempts:</div>
                    <div class="value">{incident_data['attempt_count']}</div>
                    
                    <div class="label">Timestamp:</div>
                    <div class="value">{incident_data['timestamp']}</div>
                    
                    <div class="label">Location:</div>
                    <div class="value">
                        {incident_data['location'].get('city', 'Unknown')}, 
                        {incident_data['location'].get('country', 'Unknown')}
                    </div>
                    
                    <div class="label">ISP:</div>
                    <div class="value">{incident_data['location'].get('isp', 'Unknown')}</div>
                    
                    <div class="label">User Agent:</div>
                    <div class="value" style="font-size: 12px;">{incident_data['user_agent']}</div>
                </div>
                
                <h3>Password Hashes Attempted:</h3>
                <div class="passwords">
                    {', '.join(incident_data['passwords_tried'])}
                </div>
                
                <div style="margin-top: 30px; padding: 15px; background: #e7f3ff; border-radius: 4px;">
                    <h4>Recommended Actions:</h4>
                    <ul>
                        <li>Review if this IP belongs to a known user or partner</li>
                        <li>Check if passwords match any known leaked credentials</li>
                        <li>Consider blocking this IP permanently if suspicious</li>
                        <li>Investigate potential credential leak if passwords are valid</li>
                    </ul>
                </div>
                
                <p style="margin-top: 30px; color: #666; font-size: 12px;">
                    This is an automated security alert from AtlasNexus Security System.<br>
                    Access your admin panel to view more details and manage this incident.
                </p>
            </body>
            </html>
            """
            
            part = MIMEText(html, 'html')
            msg.attach(part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                
            print(f"Security alert sent to {self.alert_email}")
            
        except Exception as e:
            print(f"Failed to send security alert: {e}")
            
    def get_ip_location(self, ip_address: str) -> Dict:
        """Get location information for an IP address"""
        # You would integrate with an IP geolocation service here
        # For now, returning placeholder data
        # Consider using services like ipapi.co, ipgeolocation.io, or ipinfo.io
        
        # Example integration (requires API key):
        # import requests
        # response = requests.get(f'https://ipapi.co/{ip_address}/json/')
        # return response.json()
        
        return {
            'country': 'Unknown',
            'city': 'Unknown',
            'isp': 'Unknown',
            'latitude': 0,
            'longitude': 0
        }
        
    def clear_successful_login(self, ip_address: str):
        """Clear temporary attempts after successful login"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete temporary attempts for this IP
        cursor.execute('''
            DELETE FROM temp_login_attempts WHERE ip_address = ?
        ''', (ip_address,))
        
        conn.commit()
        conn.close()
        
    def get_recent_incidents(self, limit: int = 50) -> List[Dict]:
        """Get recent security incidents for admin dashboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM security_incidents 
            ORDER BY incident_time DESC 
            LIMIT ?
        ''', (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        incidents = []
        
        for row in cursor.fetchall():
            incident = dict(zip(columns, row))
            incident['attempted_passwords'] = json.loads(incident['attempted_passwords'])
            incidents.append(incident)
            
        conn.close()
        return incidents
        
    def get_ip_reputation_report(self) -> List[Dict]:
        """Get IP reputation report for admin dashboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM ip_reputation 
            WHERE risk_score > 0
            ORDER BY risk_score DESC, last_seen DESC 
            LIMIT 100
        ''')
        
        columns = [desc[0] for desc in cursor.description]
        report = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return report

# Singleton instance
security_tracker = SecurityTracker()