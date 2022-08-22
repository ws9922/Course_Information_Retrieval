import json
import os

class CourseSearcher:
    def __init__(self) -> None:
        self._dependencies = self._init_dependencies()
    
    def _init_dependencies(self):
        output = dict()

        return output
    
    def get_course(self, course_code):
        dirs = os.listdir("./data/course")
        if course_code + ".json" not in dirs:
            raise KeyError("Course Code not found")
        with open("./data/course/" + course_code + ".json") as f:
            data = json.load(f)
        return data

    def get_prof(self, prof):
        dirs = os.listdir("./data/prof")
        for prof_initial in prof:
            if prof_initial + ".json" not in dirs:
                continue
            with open("./data/prof/" + prof_initial + ".json") as f:
                data = json.load(f)
            print("./data/course/" + prof_initial + ".json")
            return data
    
    def get_dependency(self, course_code):
        return self._dependencies[course_code]