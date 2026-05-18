from locust import HttpUser, task, between
import uuid


class ReservationUser(HttpUser):

    wait_time = between(0.1, 0.5)

    @task
    def reserve(self):

        self.client.post(
            "/reservations/",
            json={
                "cart_id": 1,
                "product_id": 1,
                "quantity": 1,
                "idempotency_key": str(uuid.uuid4())
            },
            headers={
                "X-API-KEY": "your_api_key"
            }
        )