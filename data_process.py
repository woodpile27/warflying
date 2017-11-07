import json


def spliter(file):
    with open("data.json", "r") as f:
        items = f.readlines()
        for data in items:
            data = json.loads(data)
            essid = data.get('essid')
            bssid = data.get('bssid')
            locates = data.get("locates")
            valid_locates = []
            for locate in locates:
                if locate[0] != '0':
                    valid_locates.append(locate)
            if len(valid_locates) == 0:
                pass
            else:
                max_locate = valid_locates[0]
                max_power = int(valid_locates[0][-3:])
                for info in valid_locates:
                    if int(info[-3:]) > max_power:
                        max_locate = info
                        max_power = int(info[-3:])
            douhao = max_locate.find(',')
            lat = float(max_locate[0:douhao])
            lng = float(max_locate[douhao+1:-4])
            final_data = {'lat':lat, 'lng':lng, 'infobox':essid}
            file.write(str(final_data) + '\n')


if __name__ == '__main__':
    with open("out.json", "w") as f2:
        spliter(f2)

