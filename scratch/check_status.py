import paramiko

def check_status():
    host = "140.238.153.123"
    user = "ubuntu"
    pw = "Klon0012"
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=pw)
        print("--- Docker PS ---")
        stdin, stdout, stderr = client.exec_command("sudo docker ps")
        print(stdout.read().decode())
        
        print("--- App Logs (last 20 lines) ---")
        stdin, stdout, stderr = client.exec_command("cd calendar-booking && sudo docker compose logs --tail=20 app")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_status()
