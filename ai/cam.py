import nmap


def scan_cameras(ip_range):
    scanner = nmap.PortScanner()
    scanner.scan(
        hosts=ip_range, arguments="-p80,554,8000"
    )  # Scans for HTTP, RTSP, and custom camera ports
    cameras = []

    for ip in scanner.all_hosts():
        if scanner[ip].state() == "up":
            print(f"Host : {ip} is up")
            for proto in scanner[ip].all_protocols():
                for port in scanner[ip][proto].keys():
                    if scanner[ip][proto][port]["state"] == "open":
                        print(f"Port : {port} is open")
                        cameras.append(ip)

    return cameras


def scan_multiple_subnets(ip_ranges):
    all_camera_ips = []
    for ip_range in ip_ranges:
        camera_ips = scan_cameras(ip_range)
        all_camera_ips.extend(camera_ips)
    return all_camera_ips


if __name__ == "__main__":
    ip_ranges = [
        "192.168.0.0/24",
    ]  # Replace with your local network ranges
    all_camera_ips = scan_multiple_subnets(ip_ranges)
    print("Camera IPs found:", all_camera_ips)
