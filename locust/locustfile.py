from locust import HttpUser, task, between
import os

class DDoSUser(HttpUser):
    wait_time = between(0.1, 0.3)  # Simulate aggressive user behavior

    @property
    def protection(self):
        return os.getenv("LOCUST_PROTECTION_MODE", "").strip()

    @task
    def attack_redirect(self):
        short_url = os.getenv("SHORT_URL","str")  
        headers = {}

        query = ""
        if self.protection:
            query = f"?protection={self.protection}"
            if "captcha" in self.protection:
                headers["x-Captcha-Token"] = "valid"

        #print(f"Attacking /redirect/{short_url} with protection={self.protection}")
        self.client.get(f"/redirect/{short_url}{query}", headers=headers,allow_redirects=False)
