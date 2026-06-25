import psutil
from plyer import notification

def execute(command_text):
    print("[Doctor Protocol] Running system hardware diagnostics...")
    
    # interval=0.5 ensures we get a somewhat active reading without blocking for too long
    cpu_usage = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    ram_percent = ram.percent
    ram_free_gb = round(ram.available / (1024 ** 3), 1)
    
    disk = psutil.disk_usage('/')
    disk_free_gb = round(disk.free / (1024 ** 3), 1)
    
    diagnostic_report = []
    
    # Analyze CPU
    if cpu_usage > 85:
        diagnostic_report.append(f"Your CPU is currently under heavy load at {cpu_usage} percent.")
        notification.notify(title="R.O.O.T. Warning", message=f"High CPU Load: {cpu_usage}%", app_name="R.O.O.T.", timeout=10)
    else:
        diagnostic_report.append(f"Your CPU is running smoothly at {cpu_usage} percent.")
        
    # Analyze RAM
    if ram_percent > 85:
        diagnostic_report.append(f"Warning: Your memory is almost full. You are using {ram_percent} percent of your RAM, with only {ram_free_gb} gigabytes free.")
        notification.notify(title="R.O.O.T. Warning", message=f"Memory Critical: {ram_free_gb}GB Free", app_name="R.O.O.T.", timeout=10)
    else:
        diagnostic_report.append(f"Memory levels are optimal. You have {ram_free_gb} gigabytes of free RAM.")
        
    # Analyze Disk
    if disk.percent > 90:
        diagnostic_report.append(f"Critical Warning: Your primary hard drive is critically full. You only have {disk_free_gb} gigabytes of free space remaining.")
        notification.notify(title="R.O.O.T. Warning", message=f"Storage Critical: {disk_free_gb}GB Free", app_name="R.O.O.T.", timeout=10)
        
    return " ".join(diagnostic_report)
