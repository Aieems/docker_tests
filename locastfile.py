from faker import Faker
from locust import HttpUser, SequentialTaskSet, TaskSet, constant_throughput, task
import random

fake = Faker("ru_RU")

class BrowseTests(TaskSet):

    def on_start(self):
        response = self.client.post("/api/auth/login", json={
            "username": "admin",
            "password": "Admin123!",
        })
        token = response.json()["accessToken"]
        self.headers = {"Authorization": "Bearer " + token}

    @task(5)
    def list_projects(self):
        self.client.get("/api/projects", headers=self.headers, params={
            "page": 1,
            "size": 10,
        })

    @task(5)
    def list_partners(self):
        self.client.get("/api/partners", headers=self.headers, params={
            "page": random.randint(1, 2),
            "size": 10,
        })

    @task(5)
    def list_categories(self):
        self.client.get("/api/categories", headers=self.headers)

    @task(5)
    def open_project(self):
        project_id = random.choice([1, 2])
        self.client.get(f"/api/projects/{project_id}", headers=self.headers)

    @task(1)
    def add_partner(self):
        self.client.post("/api/partners", headers=self.headers, json={
            "lastName": fake.last_name(),
            "firstName": fake.first_name(),
            "country": fake.country(),
            "birthYear": random.randint(1950, 2005),
        })


class CoordinatorFlow(SequentialTaskSet):

    def on_start(self):
        response = self.client.post("/api/auth/login", json={
            "username": "admin",
            "password": "Admin123!",
        })
        token = response.json()["accessToken"]
        self.headers = {"Authorization": "Bearer " + token}

    @task(5)
    def list_volunteers(self):
        self.client.get("/api/volunteers", headers=self.headers)

    @task(5)
    def admin_stats(self):
        self.client.get("/api/admin/stats", headers=self.headers)

    @task(5)
    def list_users(self):
        self.client.get("/api/admin/users", headers=self.headers)

    @task(1)
    def add_category(self):
        self.client.post("/api/categories", headers=self.headers, json={
            "name": fake.word().capitalize() + " " + str(random.randint(1, 999999)),
        })

    @task(1)
    def add_volunteer(self):
        number = random.randint(1000, 9999)
        self.client.post("/api/volunteers", headers=self.headers, json={
            "firstName": fake.first_name(),
            "lastName": fake.last_name(),
            "email": f"vol{number}{random.randint(1, 999999)}@fund.ru",
            "card": {
                "cardNumber": f"V-{number}",
                "issuedAt": "2024-01-15",
                "expiresAt": "2026-01-15",
            },
        })


class WebsiteUser(HttpUser):
    wait_time = constant_throughput(2)
    tasks = [BrowseTests, CoordinatorFlow]