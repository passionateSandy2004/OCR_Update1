import os
import tableM as t
import json 

def Instance(path):
    print("Before Table")
    t.Table(path)

def TableOcr(pathT):
    Instance(pathT)
TableOcr(r"D:\OCR Models\Own model\working\invoice 2.jpeg")