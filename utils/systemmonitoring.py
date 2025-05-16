import os
import psutil
import json
import subprocess
import time


def get_kernel_info():
    return {
        "kernel_version": os.uname().release,
        "system_name": os.uname().sysname,
        "node_name": os.uname().nodename,
        "machine": os.uname().machine,
        "pid": os.getpid(),
    }


def get_memory_info():
    return {
        "virtual_memory [GB]": psutil.virtual_memory().total / (1024.0**3),
        "available_virtual_memory [GB]": psutil.virtual_memory().available
        / (1024.0**3),
        "used_virtual_memory [GB]": psutil.virtual_memory().used / (1024.0**3),
        "memory_percentage": psutil.virtual_memory().percent,
    }


def get_cpu_info():
    return {
        "physical_cores": psutil.cpu_count(logical=False),
        "total_cores": psutil.cpu_count(logical=True),
        "processor_speed": psutil.cpu_freq().current,
        "cpu_usage_per_core": dict(
            enumerate(psutil.cpu_percent(percpu=True, interval=1))
        ),
        "total_cpu_usage": psutil.cpu_percent(interval=1),
    }


def get_disk_info():
    partitions = psutil.disk_partitions()
    disk_info = {}
    for partition in partitions:
        partition_usage = psutil.disk_usage(partition.mountpoint)
        disk_info[partition.mountpoint] = {
            "total_space": partition_usage.total / (1024.0**3),
            "used_space": partition_usage.used / (1024.0**3),
            "free_space": partition_usage.free / (1024.0**3),
            "usage_percentage": partition_usage.percent,
        }
    return disk_info


def get_network_info():
    net_io_counters = psutil.net_io_counters()
    return {
        "bytes_sent": net_io_counters.bytes_sent,
        "bytes_recv": net_io_counters.bytes_recv,
    }


def get_process_info():
    process_info = []
    for process in psutil.process_iter(
        ["pid", "name", "memory_percent", "cpu_percent"]
    ):
        try:
            process_info.append(
                {
                    "pid": process.info["pid"],
                    "name": process.info["name"],
                    "memory_percent": process.info["memory_percent"],
                    "cpu_percent": process.info["cpu_percent"],
                }
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return process_info


def get_load_average():
    load_avg_1, load_avg_5, load_avg_15 = psutil.getloadavg()
    return {
        "load_average_1": load_avg_1,
        "load_average_5": load_avg_5,
        "load_average_15": load_avg_15,
    }


def get_disk_io_counters():
    io_counters = psutil.disk_io_counters()
    return {
        "read_count": io_counters.read_count,
        "write_count": io_counters.write_count,
        "read_bytes": io_counters.read_bytes,
        "write_bytes": io_counters.write_bytes,
        "read_time": io_counters.read_time,
        "write_time": io_counters.write_time,
    }


def get_net_io_counters():
    io_counters = psutil.net_io_counters()
    return {
        "bytes_sent": io_counters.bytes_sent,
        "bytes_recv": io_counters.bytes_recv,
        "packets_sent": io_counters.packets_sent,
        "packets_recv": io_counters.packets_recv,
        "errin": io_counters.errin,
        "errout": io_counters.errout,
        "dropin": io_counters.dropin,
        "dropout": io_counters.dropout,
    }


def get_system_uptime():
    boot_time_timestamp = psutil.boot_time()
    current_time_timestamp = time.time()
    uptime_seconds = current_time_timestamp - boot_time_timestamp
    uptime_minutes = uptime_seconds // 60
    uptime_hours = uptime_minutes // 60
    uptime_days = uptime_hours // 24
    uptime_str = f"{int(uptime_days)} days, {int(uptime_hours % 24)} hours, {int(uptime_minutes % 60)} minutes, {int(uptime_seconds % 60)} seconds"
    return {"uptime": uptime_str}


def get_hardware_info():
    return {
        "kernel_info": get_kernel_info(),
        "memory_info": get_memory_info(),
        "cpu_info": get_cpu_info(),
        "network_info": get_network_info(),
        "system_uptime": get_system_uptime(),
        "load_average": get_load_average(),
        "disk_io_counters": get_disk_io_counters(),
        "net_io_counters": get_net_io_counters(),
    }


if __name__ == "__main__":
    data = get_hardware_info()
    print("=" * 40)
    print("System Monitoring")
    print("=" * 40)
    print(json.dumps(data, indent=4))
