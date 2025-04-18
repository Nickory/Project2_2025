# SoilMoistureMonitor.py
# Ziheng Wang - Automated Plant Watering Alert System
import RPi.GPIO as GPIO
import time
import smtplib
from email.message import EmailMessage
from datetime import datetime

# Email Configuration
SMTP_SERVER = 'smtp.qq.com'
SMTP_PORT = 465
SENDER_EMAIL = "3119349688@qq.com"
SENDER_PASSWORD = "okhhgidjogtndfid"  # QQ email authorization code
RECIPIENT_EMAIL = "2563373919@qq.com"

# GPIO Setup
MOISTURE_SENSOR_PIN = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOISTURE_SENSOR_PIN, GPIO.IN)

# Notification Schedule (24-hour format)
DAILY_CHECK_TIMES = ["07:00", "10:00", "13:00", "16:00"]

def check_moisture():
    """Read soil moisture sensor and return status in English"""
    if GPIO.input(MOISTURE_SENSOR_PIN):
        return "Soil is DRY - Water NEEDED"
    return "Soil is WET - No water needed"

def send_alert_email(status):
    """Send email notification with proper English formatting"""
    try:
        email = EmailMessage()
        email['From'] = SENDER_EMAIL
        email['To'] = RECIPIENT_EMAIL
        email['Subject'] = "🌱 Plant Watering Alert"
        
        email_content = f"""
        PLANT STATUS UPDATE:
        - Condition: {status}
        - Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        ACTION REQUIRED:
        { 'Water your plant immediately!' if 'NEEDED' in status else 'No action required at this time.' }
        """
        email.set_content(email_content.strip())

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(email)
            print(f"✅ Alert email sent: {status}")

    except Exception as e:
        print(f"")

def should_check_now():
    """Check if current time matches any scheduled check time"""
    current_time = datetime.now().strftime("%H:%M")
    return current_time in DAILY_CHECK_TIMES

def run_diagnostic_test():
    """Run comprehensive system test"""
    print("\n=== SYSTEM DIAGNOSTIC ===")
    
    # Test sensor reading
    test_result = check_moisture()
    print(f"Sensor Test: {test_result}")
    
    # Test email functionality
    print("Testing email system...")
    send_alert_email("[TEST] This is a system diagnostic email")
    
    print("=== DIAGNOSTIC COMPLETE ===\n")

def main_monitoring_loop():
    """Main monitoring loop with scheduled checks"""
    last_check_time = None
    
    try:
        print("🌿 Plant Monitoring System Active")
        print(f"Scheduled checks at: {', '.join(DAILY_CHECK_TIMES)}")
        print("Press Ctrl+C to exit or type 'test' for diagnostic\n")
        
        while True:
            current_time = datetime.now().strftime("%H:%M")
            
            # Perform scheduled check
            if should_check_now() and current_time != last_check_time:
                status = check_moisture()
                print(f"{current_time} - {status}")
                send_alert_email(status)
                last_check_time = current_time
            
            # Check for user input (non-blocking)
            try:
                if input() == 'test':
                    run_diagnostic_test()
            except:
                pass
                
            time.sleep(30)  # Check every 30 seconds

    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    finally:
        GPIO.cleanup()
        print("GPIO resources cleaned up")

if __name__ == "__main__":
    main_monitoring_loop()
