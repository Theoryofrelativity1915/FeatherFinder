import os
import csv
import shutil
import json

train_path = os.path.join("data", "train")
val_path = os.path.join("data", "val")
test_path = os.path.join("data", "test", "public_test")

# replace this with whichever directory you're cleaning


def clean():
    for subdir, dirs, files in os.walk(val_path):
        animal_type_array = subdir.split('/')[2:]
        if len(animal_type_array) == 0:
            continue
        else:
            animal_directory_array = animal_type_array[0].split('_')
            domain = animal_directory_array[1]
            print(animal_directory_array)
            kingdom = animal_directory_array[2]
            phylum = animal_directory_array[3]
            species = animal_directory_array[-2:]
            if (domain != "Animalia" or
                    len(domain) < 2 or
                    phylum != "Aves"):  # Don't care about anything but birds
                shutil.rmtree(subdir)
                continue


def read_json_and_create_csv():
    with open(os.path.join("data", "test", "labels.json")) as file:
        data = json.load(file)
        # This returns a massive array of individual dictionaries...
        arr = []
        for category_dict in data.get("categories"):
            if "Birds" in category_dict.values():
                # print(category_dict.values())
                arr.append(category_dict)
        with open(os.path.join("data", "test", "labels.csv"), "w", newline='') as csvfile:
            fieldnames = list(arr[0].keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(arr)
            # shutil.copy2(os.path.join("data", "test", "public_test", "test.txt"), os.path.join("data", "test"))


def get_ids_from_csv():
    ids = []
    with open(os.path.join("data", "test", "labels.csv")) as file:
        csvFile = csv.DictReader(file)
        for line in csvFile:
            id = line['id']
            print(id)
            # if id[0] == "0":
            #     print("stripping 0")
            #     id = id[1:]
            # ids.append(line['id'])
    return ids


def clean_img_files():
    ids = get_ids_from_csv()
    for subdir, dirs, files in os.walk(test_path):
        for file in files:
            # print(file.split('.')[0] in ids)
            pass


# clean_folders()
# read_json_and_create_csv()
clean_img_files()
