import streamlit as st
from PIL import Image
from lib_image_models import ImageModels
import os, time, shutil
import subprocess

# ----------------------------------------
# ---- Dashboard Helper Functions
# ----------------------------------------

def insert_image( img_placeholder, image_path, status_placeholder ):
    try:
        if os.path.exists(image_path):
            image = Image.open(image_path)
            img_placeholder.image(image, caption="Updated Image", 
                            #width=350)
                            use_container_width=True)
        else:
            status_placeholder.success("No image found.")
            time.sleep(0.5)

    except Exception as e:
        print(e)

def insert_image_yolo_annotated( img_placeholder, image_path, status_placeholder ):
    valid_file_paths = []
    try:
        if os.path.exists(image_path):
            valid_file_paths += [image_path]
            try:
                img_models.yolo(image_path)
                l = img_models.get_annotated_image_paths()
                valid_file_paths = [p for p in l if os.path.exists(p)] # Replace original image with annotated.
            except Exception as e:
                pass
            annotated_image_path = valid_file_paths[-1]
            image = Image.open(annotated_image_path)
            img_placeholder.image(image, caption="Updated Image", 
                                    #width=350)
                                    use_container_width=True)
        else:
            status_placeholder.success("No image found.")
            time.sleep(0.5)

    except Exception as e:
        print(e)

def upload_image_picker(uploaded_file_placeholder, status_placeholder):
    uploaded_file = uploaded_file_placeholder.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        # Save the uploaded file with a timestamped filename and as current_image.jpg
        timestamp = int(time.time())
        timestamped_path = f'./tmp/image_{timestamp}.jpg'
        current_image_path = './tmp/current_image.jpg'    
        
        # Save the file
        with open(timestamped_path, 'wb') as f:
            f.write(uploaded_file.getvalue())
        shutil.copy(timestamped_path, current_image_path)

        status_placeholder.success(f"Uploaded image saved!")
        time.sleep(1)

def start_api(button_start_stop, status_placeholder):
    if 'process' not in st.session_state:
        st.session_state['process'] = None

    if st.session_state['process'] is None:
        if button_start_stop.button("Start API"):
            st.session_state['process'] = subprocess.Popen(['python', 'flask_api.py'])
            st.session_state['is_running'] = True
            status_placeholder.success("API started!", icon="✅")
            time.sleep(0.5)

    if st.session_state['process']:
        if button_start_stop.button("Stop API"):
            st.session_state['process'].terminate()
            st.session_state['process'] = None
            st.session_state['is_running'] = False
            status_placeholder.success("API stopped.", icon="✅")
            time.sleep(0.5)



# ----------------------------------------
# ---- Dashboard Layout
# ----------------------------------------
st.set_page_config(layout="wide")

# Title of the Streamlit app
st.title("Real-time Object Detection Monitor:")

# Loop control:
st.session_state['is_running'] = True

# Layout structure:
column_1, column_2, column_3 = st.columns([2,2,1])

with column_1:
    st.caption("_Show latest image_")
    img_placeholder1 = st.empty()

with column_2:
    st.caption("_Show latest annotated image_")
    img_placeholder2 = st.empty()

with column_3:
    button_start_stop = st.empty()
    uploaded_file_placeholder = st.empty()
    with st.expander("Show Ojbects Detected:", expanded=True):
        df_objs_placeholder = st.empty()
        st.caption("_Data frame of historical objects founds_")

# Below columns. (full length)
with st.expander("See Dashboard Parameters:"):
    latest_image_file = st.text_input("File path to .txt (JSON) data file:", "tmp/current_image.jpg")
    refresh_interval = st.slider("Time interval between data refresh (_seconds_):", 1, 60, 5)
    
status_placeholder = st.empty()



# ----------------------------------------
# ---- Dashboard Logic
# ----------------------------------------

img_models = ImageModels.run()
start_api(button_start_stop, status_placeholder)
upload_image_picker(uploaded_file_placeholder, status_placeholder)

if not latest_image_file:
    status_placeholder.error("Please provide a valid latest image file path.")
else:
    status_placeholder.success("Monitoring started!", icon="✅")
    time.sleep(1)

    while st.session_state['is_running']:

        # Image & Yolo annotated image:
        insert_image( img_placeholder1, latest_image_file, status_placeholder )
        insert_image_yolo_annotated(img_placeholder2, latest_image_file, status_placeholder)
        
        # Detected objects dataframe:
        df_objects = img_models.pd_dataframe()
        df_objs_placeholder.dataframe(df_objects.astype(str), use_container_width=True)
        
        time.sleep(refresh_interval)