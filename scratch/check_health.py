import paramiko

def check_health_local():
    host = "140.238.153.123"
    user = "ubuntu"
    pw = "Klon0012"
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=pw)
        stdin, stdout, stderr = client.exec_command("curl -s http://localhost:8000/health")
        print(f"Health check: {stdout.read().decode()}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_health_local()
