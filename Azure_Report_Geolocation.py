import os
import csv
import json
import requests
from requests.exceptions import HTTPError
from tkinter import filedialog as fd

USER_AGENT = {'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0"}
API_URL = "http://api.ipstack.com/"
API_ACCESS_KEY_EXTRAS = "?access_key="
try:
    API_KEY = os.getenv("IPSTACK_KEY")
except:
    print("You must add an environment variable with your API access key with name IPSTACK_KEY")
    print("Please refer to your OS documentation on adding the environment variable")


def get_file():
    filename = fd.askopenfilename()
    if not filename.lower().endswith('.csv'):
        filename = fd.askopenfilename()
    return filename


def get_ipstack_geolocation(IP_Address):

    full_url = API_URL + IP_Address + API_ACCESS_KEY_EXTRAS + API_KEY

    response = requests.get(full_url, headers=USER_AGENT)
    response.raise_for_status()
    json_response = response.json()
    continent = json_response["continent_name"]
    country = json_response["country_name"]
    city = json_response["city"]
    region = json_response["region_name"]
    return {"continent_name": continent, "country" : country, "region": region, "city": city}


def write_new_file(array_of_lines):
    fields = ['CreationTime', 'UserId', 'Operation', 'IP_Address', "continent_name", "country", "region", "city"]
    with open('audit_report_with_geolocation.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames = fields)
        writer.writeheader()
        writer.writerows(array_of_lines)


def main():
    filename = get_file()

    #used for debugging purposes
    count = 0
    geostore_access = 0
    ipstack_access = 0

    geolocation_store = {} #empty dictionary, will store the IP's that have been looked up for reference later'
    array_of_lines = [] #hold the

    with open(filename, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:

            row_dict = json.loads(row['AuditData'])

            Creation_Time = row_dict['CreationTime']
            User_Id = row_dict['UserId']
            operation = row_dict['Operation']
            IP_Address = row_dict['ClientIP']

            #create a new dictionary for each line to be written to a file later
            line_dict = {'CreationTime': Creation_Time, 'UserId': User_Id, 'Operation': operation, 'IP_Address': IP_Address}

            if IP_Address in geolocation_store:
                location = geolocation_store[IP_Address] #retreive geolocation from memory
                geostore_access += 1
            else:
                location = get_ipstack_geolocation(IP_Address) #retreive geolocation from IPStack.com
                geolocation_store[IP_Address] = location #add geolocation to memory
                ipstack_access += 1

            line_dict.update(location)
            array_of_lines.append(line_dict)
            count += 1

           #if (count >= 400):  #used for limiting the number of rows for testing
            #    break

    print(f"There were {ipstack_access} calls to IP Stack")
    print(f"There were {geostore_access} calls to the local geolocation_store")
    print(f"The total between the is {geostore_access + ipstack_access}, which should match the total: {count}")

    write_new_file(array_of_lines)

if __name__ == "__main__":
    main()
