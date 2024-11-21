from ultralytics import YOLO
import os
os.environ['YOLO_VERBOSE'] = 'False'
from collections import Counter
import threading
import pandas as pd

class ImageModels:    
    def __init__(self, models:list, 
                 _tags:Counter=None, 
                 annotated_image_path_prefix = "tmp/tmp_image_annotate_",
                 confidence_threshold=0.25
                 ):
        self.__tags = Counter() if not _tags else _tags
        self.tags_lock = threading.Lock()
        self.models = models
        os.makedirs('tmp', exist_ok=True)
        self.yolo_annotated_image_path_prefix = annotated_image_path_prefix
        self.yolo_annotated_image_path_suffix = ".jpg"
        self._confidence_threshold = confidence_threshold
    """
    ------ Model Predict Functions:
    """    
    def yolo(self, path_to_local_image):
        for idx,model in enumerate(self.models):
            self._update_tags(model, path_to_local_image, output_path=f"{self.yolo_annotated_image_path_prefix}{idx}{self.yolo_annotated_image_path_suffix}")
      
    def _update_tags(self, model, image_path, output_path):
        try:
            results = []
            results = model.predict(image_path, stream=False, verbose=False)
            for result in results:
                new_tags = [result.names[int(c)] for c,conf in zip(result.boxes.cls, result.boxes.conf) if conf>self._confidence_threshold]
                self.__update_counter_threadsafe( new_tags ) #float(conf)
                result.save(output_path)
        except ConnectionError as e:
            pass
        except Exception as e:
            print(e)
    
    """
    ------ Get Prediction Data:
    """
    def get_annotated_image_paths(self) -> list:
        r = []
        for idx,_ in enumerate(self.models):
            r += [f"{self.yolo_annotated_image_path_prefix}{idx}{self.yolo_annotated_image_path_suffix}"]
        return r
    
    def pd_dataframe(self):
        t = self.__get_counter_threadsafe()
        _df = pd.DataFrame.from_records([t]).T
        if 0 in _df.columns:
            _df = _df.sort_values(by=[0], ascending=False)
        return _df
    """
    ------ Thread Safe Functions:
    """
    def __update_counter_threadsafe(self, new_tags:list):
        with self.tags_lock:
            self.__tags.update( new_tags )

    def __get_counter_threadsafe(self):
        with self.tags_lock:
            return dict(self.__tags) # return copy.
        
    @staticmethod
    def run():
        # model_yolov8n_coco = YOLO("yolov8n.pt")
        model_yolov8n_oiv7 = YOLO('yolov8n-oiv7.pt')
        return ImageModels( models=[ model_yolov8n_oiv7 ] )
