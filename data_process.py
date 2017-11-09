import json


def spliter(file):
    with open("data.json", "r") as f:
        items = f.readlines()
        for data in items:
            data = json.loads(data)
            essid, bssid, locates = data.get('essid'), data.get('bssid'), data.get('locates')
            valid_locates = []
            for locate in locates:
                if locate[0] != '0':
                    valid_locates.append(locate)
            if len(valid_locates) == 0:
                pass
            else:
                max_locate = sorted(valid_locates, key=lambda x: x[-2:])[0]
            lat, lng, _ = [float(i) for i in max_locate.split(',')] 
            final_data = {'lat':lat, 'lng':lng, 'infobox':essid}
            file.write(str(final_data) + '\n')


if __name__ == '__main__':
    with open("out.json", "w") as f2:
        spliter(f2)

