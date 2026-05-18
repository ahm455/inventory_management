from locust import HttpUser, task, between, events
import uuid
import random
import json
from inventory_management.settings.base import API_KEY

# -----------------------------
# GLOBAL DEBUG LOGGING
# -----------------------------
@events.request.add_listener
def log_request(request_type, name, response_time, response_length, response, context, exception, **kwargs):
    if exception:
        print(f"\n❌ REQUEST FAILED")
        print(f"Type: {request_type}")
        print(f"Name: {name}")
        print(f"Exception: {exception}")

    elif response is not None and response.status_code >= 400:
        print(f"\n⚠️ HTTP ERROR")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")


class ReservationUser(HttpUser):

    # Think time between requests (simulates real users)
    wait_time = between(0.5, 2)

    # Change this in UI OR here
    host = "http://localhost:8000"

    @task
    def create_reservation(self):

        payload = {
            "cart_id": random.randint(1, 10),
            "product_id": random.randint(1, 50),
            "quantity": random.randint(1, 3),
            "idempotency_key": str(uuid.uuid4())
        }

        headers = {
            "X-API-KEY": "dev-9f3c2a7b1d5e4c8f",
            "Content-Type": "application/json"
        }

        with self.client.post(
            "/reservations/",
            data=json.dumps(payload),
            headers=headers,
            catch_response=True,
            name="POST /reservations"
        ) as response:

            # -----------------------------
            # SUCCESS CHECK
            # -----------------------------
            if response.status_code == 200 or response.status_code == 201:
                try:
                    data = response.json()
                    print(f"✅ Success: {data}")
                except:
                    print("✅ Success but non-JSON response")

            # -----------------------------
            # FAILURE HANDLING
            # -----------------------------
            else:
                response.failure(
                    f"Failed with status {response.status_code}: {response.text}"
                )

                print("\n🚨 REQUEST DEBUG INFO")
                print("Payload sent:")
                print(json.dumps(payload, indent=2))
                print("Response received:")
                print(response.text)