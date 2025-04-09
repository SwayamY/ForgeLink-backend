from locust import HttpUser , task, between
class DDoSSimulationUser(HttpUser):
    wait_time  = between(1,2)

    @task
    def simulate_attack(self):
        self.client.get("/simulate_ddos/test123")