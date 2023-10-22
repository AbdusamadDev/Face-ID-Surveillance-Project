from flask import Flask, send_from_directory, abort, request, jsonify
import os
import glob

app = Flask(__name__, static_folder="../screenshots", static_url_path="/screenshots")


@app.route("/media/<username>")
def serve_image(username):
    if not username.isalnum():
        abort(400, description="Invalid username")

    # Construct the path for the image
    image_path = os.path.join("../media", username, "main.jpg")
    print(image_path)
    # Check if the file exists and serve it
    if os.path.exists(image_path):
        return send_from_directory(os.path.join("../media", username), "main.jpg")

    else:
        abort(404, description="Image not found!")


@app.route("/criminals/<username>/")
def criminal_faces(username):
    # Extract query parameters
    year = request.args.get("year")
    month = request.args.get("month")
    day = request.args.get("day")

    if not all([year, month, day]):
        abort(400, description="All query parameters (year, month, day) are required")

    path = f"../screenshots/{username}/{year}/{month}/{day}"

    # Check if path exists
    if not os.path.exists(path):
        abort(404, description="Path does not exist")

    # Get all jpg images from the path
    images = glob.glob(os.path.join(path, "*.jpg"))

    # Check if there are images in the folder
    if not images:
        abort(404, description="No images found for the specified date")

    # Generate the URLs for the images
    base_url = request.url_root + "screenshots/"
    image_links = [
        base_url + os.path.relpath(img, start="../screenshots/") for img in images
    ]

    return jsonify({"images": image_links})


@app.route("/screenshots/<path:path>")
def serve_screenshots(path):
    return send_from_directory("../screenshots", path)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=12345)
