from flask import Flask, request, jsonify

app = Flask(__name__)

# Define the allowed IP address
ALLOWED_IP = "91.227.144.54"


# Define a route to listen for incoming webhook requests
@app.route("/webhook", methods=["POST"])
def webhook_listener():
    # Get the JSON data from the incoming request
    data = request.get_json()

    # Get the IP address of the sender
    sender_ip = request.remote_addr

    # Verify if the sender's IP matches the allowed IP
    if sender_ip == ALLOWED_IP:
        # Process the webhook data
        # You can add your custom logic here to handle the webhook payload
        # For this example, we'll just print it
        print("Received webhook data from allowed IP:")
        print(data)

        # Respond with a 200 OK status code
        return jsonify({"message": "Webhook received successfully"}), 200

    # If the sender's IP doesn't match the allowed IP, return a 403 Forbidden status
    return jsonify({"error": "Access forbidden"}), 403


if __name__ == "__main__":
    # Start the Flask web server
    app.run(host="0.0.0.0", port=5000)
