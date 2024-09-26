from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle form submissions for adding new devices
@app.route('/add-device', methods=['GET', 'POST'])
def add_device():
    if request.method == 'POST':
        # Get form data
        device_name = request.form['device_name']
        vendor = request.form['vendor']
        wan_ip = request.form['wan_ip']
        routing_protocol = request.form['routing_protocol']
        j2_template = request.form['j2_template']

        # Process the data (e.g., store in database, generate config, etc.)
        # You could call an automation script here to add the device to the network

        # Redirect to home page or success page
        return redirect(url_for('index'))

    return render_template('add_device.html')

if __name__ == '__main__':
    app.run(debug=True)

