import websocket # NOTE: pip install websocket-client
import uuid
import json
import urllib.request
import urllib.parse

server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())

def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break #Execution is done
        else:
            continue #previews are binary data

    history = get_history(prompt_id)[prompt_id]
    for o in history['outputs']:
        for node_id in history['outputs']:
            node_output = history['outputs'][node_id]
            if 'images' in node_output:
                images_output = []
                for image in node_output['images']:
                    image_data = get_image(image['filename'], image['subfolder'], image['type'])
                    images_output.append(image_data)
                output_images[node_id] = images_output

    return output_images

# Example Workflow (You need to replace this with your actual exported API JSON from ComfyUI)
# To get this:
# 1. Open ComfyUI (http://localhost:8188)
# 2. Load your desired workflow (e.g., Flux Dev or SDXL)
# 3. Enable "Enable Dev mode Options" in settings (gear icon)
# 4. Click "Save (API Format)" button
prompt_workflow = {
    "3": {
        "inputs": {
            "seed": 156680208700286,
            "steps": 20,
            "cfg": 8,
            "sampler_name": "euler",
            "scheduler": "normal",
            "denoise": 1,
            "model": ["4", 0],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "latent_image": ["5", 0]
        },
        "class_type": "KSampler",
        "_meta": {
            "title": "KSampler"
        }
    },
    "4": {
        "inputs": {
            "ckpt_name": "v1-5-pruned-emaonly.ckpt"
        },
        "class_type": "CheckpointLoaderSimple",
        "_meta": {
            "title": "Load Checkpoint"
        }
    },
    "5": {
        "inputs": {
            "width": 512,
            "height": 512,
            "batch_size": 1
        },
        "class_type": "EmptyLatentImage",
        "_meta": {
            "title": "Empty Latent Image"
        }
    },
    "6": {
        "inputs": {
            "text": "beautiful scenery nature glass bottle landscape, , purple galaxy bottle,",
            "clip": ["4", 1]
        },
        "class_type": "CLIPTextEncode",
        "_meta": {
            "title": "CLIP Text Encode (Prompt)"
        }
    },
    "7": {
        "inputs": {
            "text": "text, watermark",
            "clip": ["4", 1]
        },
        "class_type": "CLIPTextEncode",
        "_meta": {
            "title": "CLIP Text Encode (Prompt)"
        }
    },
    "8": {
        "inputs": {
            "samples": ["3", 0],
            "vae": ["4", 2]
        },
        "class_type": "VAEDecode",
        "_meta": {
            "title": "VAE Decode"
        }
    },
    "9": {
        "inputs": {
            "filename_prefix": "ComfyUI",
            "images": ["8", 0]
        },
        "class_type": "SaveImage",
        "_meta": {
            "title": "Save Image"
        }
    }
}

if __name__ == "__main__":
    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_images(ws, prompt_workflow)
    
    # Save images
    for node_id in images:
        for i, image_data in enumerate(images[node_id]):
            with open(f"output_{node_id}_{i}.png", "wb") as f:
                f.write(image_data)
    print("Done!")
