import requests
import json
import base64
import time

BASE_URL = "http://127.0.0.1:8001"

def test_endpoints():
    print("Testing Endpoints...")
    
    # 1. Load Sample Input
    try:
        with open("input.txt", "r") as f:
            payload = json.load(f)
    except FileNotFoundError:
        print("input.txt not found, using default payload.")
        payload = {
          "plot": {"length": 40, "width": 30, "unit": "ft", "shape": "rectangle", "facing": "east"},
          "building": {"floors": "G+1", "building_type": "independent_house"},
          "rooms": {"bedrooms": 3, "bathrooms": 2, "kitchen": True, "living_room": True, "dining_area": True, "pooja_room": True, "parking": True},
          "vastu_level": "high",
          "design": {"style": "modern", "layout_type": "open-plan", "natural_lighting": "high", "visualization": "2D"}
        }

    # 2. Test /generate-prompt
    print("\n--- Testing /generate-prompt ---")
    try:
        start = time.time()
        response = requests.post(f"{BASE_URL}/generate-prompt", json=payload)
        duration = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success ({duration:.2f}s)!")
            print(f"Vastu Score: {data.get('vastu_score')}")
            print(f"Prompt Preview: {data.get('optimized_prompt')[:100]}...")
        else:
            print(f"Failed! Status: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Is it running? (uvicorn app.main:app --reload)")
        return

    # 3. Test /generate-design
    print("\n--- Testing /generate-design ---")
    try:
        start = time.time()
        response = requests.post(f"{BASE_URL}/generate-design", json=payload)
        duration = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            try:
                if "images" in data and data["images"]:
                     for i, img_b64 in enumerate(data["images"]):
                        image_data = base64.b64decode(img_b64)
                        filename = f"output_option_{i+1}.png"
                        with open(filename, "wb") as f:
                            f.write(image_data)
                        print(f"Option {i+1} saved to '{filename}'")
                
                if "reports" in data and data["reports"]:
                     for i, pdf_b64 in enumerate(data["reports"]):
                        pdf_data = base64.b64decode(pdf_b64)
                        filename = f"output_report_{i+1}.pdf"
                        with open(filename, "wb") as f:
                            f.write(pdf_data)
                        print(f"Report {i+1} saved to '{filename}'")

                elif "image_base64" in data and data["image_base64"]:
                    # Fallback
                    image_data = base64.b64decode(data["image_base64"])
                    with open("output_design.png", "wb") as f:
                        f.write(image_data)
                    print(f"Image saved to 'output_design.png'")
                else:
                    print("No image data found in response.")
                    print(f"Message: {data.get('prompt')}") # Added this line to maintain original behavior
            except Exception as e:
                print(f"Error saving image: {e}")
        else:
            print(f"Failed! Status: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_endpoints()
