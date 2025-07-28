import csv
import os

class DataWriter():
    def __init__(self,directory=r"C:\Santec Data",file_name="default.csv"):
        self.directory = directory
        self.file_name = file_name
        self.filepath = os.path.join(self.directory,self.file_name)
        self._file = None
        self._writer = None
        self.file_flag = False
    
    def update_file_name(self,file_name):
        self.file_name = file_name
        self.file_flag = False
    
    def update_file_path(self,file_path):
        self.file_path = file_path
        self.file_flag = False

    def _initialize_file(self):
        os.makedirs(self.directory,exist_ok=True) #create directory if it does not exist

        #open and create file for appending
        file_exists = os.path.exists(self.filepath)
        self._file = open(self.filepath,'a',newline='')
        self._writer = csv.writer(self._file)

        self.file_flag = True #set file flag to true indicating that a file has been created and open

    def get_file_path(self):
        return self.file_path
    
    def write_data_row_csv(self,data_row):
        #writes a csv formatted data row to the file. 
        if not self.file_flag:
            self._initialize_file()
        self._writer.writerow(data_row)

    def write_data_txt(self,txt):
        #writes text to a file (typically a .txt file).
        if not self.file_flag:
            self._initialize_file()
        self._writer.write


