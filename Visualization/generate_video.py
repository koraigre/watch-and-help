# Generate video for a program. Make sure you have the executable open
import sys
import re
import pickle
import cv2
import os

sys.path.append('../simulation')
from unity_simulator.comm_unity import UnityCommunication

pik_path = "logs_agent_95_setup_table_0.pik"
action_length = 10
output_folders = 'simulation/unity_simulator/output/'
image_folders = ['0','1']

with open(pik_path, 'rb') as file:
    data = pickle.load(file)

print('Starting Unity...')
comm = UnityCommunication()

print('Starting scene...')
comm.reset(data["env_id"])
s, g = comm.environment_graph()
comm.add_character('Chars/Female1', initial_room='kitchen')
comm.add_character('Chars/Male2', initial_room='kitchen')

data_0 = data["action"][0]
data_1 = data["action"][1]

script = []
pattern = r'<([^>]+)>'

for i in range(len(data_0)):        
    action_0 = data_0[i]
    action_1 = data_1[i]
    s, g = comm.environment_graph()

    if i > 0:
        if action_0 == data_0[i-1]:
            action_0 = None
        if action_1 == data_1[i-1]:
            action_1 = None
    
    if action_0:
        things = re.findall(pattern, action_0)
        for index, thing in enumerate(things):
            matching_nodes = [node['id'] for node in g['nodes'] if node['class_name'] == thing]
            if matching_nodes:
                id = matching_nodes[0]
                action_0 = re.sub(rf'<{thing}> \(\d+\)', rf'<{thing}> ({id})', action_0, count=1)
    if action_1:
        things = re.findall(pattern, action_1)
        for index, thing in enumerate(things):
            matching_nodes = [node['id'] for node in g['nodes'] if node['class_name'] == thing]
            if matching_nodes:
                id = matching_nodes[0]
                action_1 = re.sub(rf'<{thing}> \(\d+\)', rf'<{thing}> ({id})', action_1, count=1)

    action_string = ''
    if action_0:
        action_string = '<char0> ' + action_0
        if action_1:
            action_string += ' | <char1> ' + action_1
    elif action_1:
        action_string = '<char1> ' + action_1
    else:
        continue
    script.append(action_string.replace('walktowards', 'walk'))

script = script[:action_length]
#print(script)

print('Generating snaps...')
#comm.render_script(script, recording=True, find_solution=True)
comm.render_script(script, frame_rate=15, recording=True, camera_mode=["AUTO"])

print('Generating videos...')
for image_folder in image_folders:
    output_video = output_folders + image_folder + '.mp4'
    images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
    images.sort()

    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, 30.0, (width, height))

    for image in images:
        img_path = os.path.join(image_folder, image)
        frame = cv2.imread(img_path)
        out.write(frame)

    out.release()
    cv2.destroyAllWindows()

print('Generated!')
