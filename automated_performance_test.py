import os
import subprocess
import time
from datetime import datetime

SHORT_URL = "string"
DURATION = "2m"  # Each test duration
USER_COUNTS = [100, 200, 500, 1000]
PROTECTION_MODES = [
    "none",
    "rate_limit",
    "ip_block",
    "captcha",
    "rate_limit+ip_block",
    "rate_limit+captcha",
    "ip_block+captcha",
    "ip_block+rate_limit+captcha"
]

RESOURCE_MODES = {
    "high": "docker-compose.override.high.yml",
    "low": "docker-compose.override.low.yml"
}

def run_locust(protection, users, resource_mode):
    env = os.environ.copy()
    env["LOCUST_PROTECTION_MODE"] = protection
    env["SHORT_URL"] = SHORT_URL

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_id = f"{resource_mode}_{protection}_{users}_{timestamp}"
    report_html = f"results/{file_id}.html"
    csv_prefix = f"results/{file_id}"

    command = [
        "docker", "exec", "locust",
        "locust", "-f", "locustfile.py",
        "--host", "http://api:8000",
        "--headless",
        "-u", str(users),
        "-r", str(int(users / 20)),
        "--run-time", DURATION,
        "--csv", csv_prefix,
        "--html", report_html
    ]

    print(f"\n🚀 Running: Users={users}, Protection={protection}, Mode={resource_mode}")
    subprocess.run(command, env=env)

def main():
    os.makedirs("results", exist_ok=True)

    for mode, override_file in RESOURCE_MODES.items():
        print(f"\n🔁 Restarting Docker in {mode.upper()} resource mode...")

        # Step 1: Shut everything down
        subprocess.run(["docker-compose", "down"])

        # Step 2: Start with correct override (NO --build)
        subprocess.run([
            "docker-compose",
            "-f", "docker-compose.yml",
            "-f", override_file,
            "up", "-d"
        ])

        time.sleep(10)  # Let services become healthy

        for protection in PROTECTION_MODES:
            for users in USER_COUNTS:
                run_locust(protection, users, mode)
                print("⏳ Waiting 10s before next test...\n")
                time.sleep(10)

    print("\n✅ All tests completed. Reports are in the 'results/' directory.")

if __name__ == "__main__":
    main()
