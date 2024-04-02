import requests
import json
import os

# 设置您的API密钥
api_key = os.environ['Map_Key']

# 谷歌地图Geocoding API的端点
geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"

class google_map():
    def __init__(self):
        pass

    def get_geocode(self, place):
        # 配置Geocoding API请求参数
        geocode_params = {
            'address': place,
            'key': api_key
            }
        # 发送GET请求获取地点的经纬度信息
        geocode_response = requests.get(geocode_url, params=geocode_params)
        geocode_result = json.loads(geocode_response.text)

        # 先检查是否有结果
        if geocode_result['status'] == 'OK':
            # 提取地点的经纬度
            location = geocode_result['results'][0]['geometry']['location']
            lat, lng = location['lat'], location['lng']
            return lat, lng
        else:
            print("Geocoding API did not find the location.")
            return None


    def place_info(self, place, type):
        # 获取经纬度
        lat, lng = self.get_geocode(place)

        # 设置搜索半径(单位为米)
        radius = '2000'  # 2公里内

        # 谷歌地图Places API的附近搜索端点
        places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

        # 配置Places API请求参数

        places_params = {
            'location': f"{lat},{lng}",
            'radius': radius,
            'type': type,
            'key': api_key
        }

        # 发送GET请求获取附近的餐馆信息
        places_response = requests.get(places_url, params=places_params)
        places_result = json.loads(places_response.text)

        if places_result['status'] == 'OK':
            places = places_result['results']
            # print(places[0])
            return places

        else:
            print("No places found or an error occurred.")

        # # 检查是否有结果
        # if places_result['status'] == 'OK':
        #     # 遍历并打印所有地点信息
        #     for place in places_result['results']:
        #         print(f"Name: {place['name']}")
        #         print(f"Address: {place.get('vicinity', 'No address found')}")
        #         print('-' * 40)
        # else:
        #     print("No places found or an error occurred.")


    def get_location_map(self, place):
        lat, lng = self.get_geocode(place)

        static_maps_url = "https://maps.googleapis.com/maps/api/staticmap"
        zoom = '15'
        size = '600x300'
        maptype ='roadmap'
        map_url = f"{static_maps_url}?center={lat},{lng}&zoom={zoom}&size={size}&maptype={maptype}&key={api_key}"
        # print(map_url)

        return map_url


    def get_location_photo(self, place):
        lat, lng = self.get_geocode(place)

        street_view_url = "https://maps.googleapis.com/maps/api/streetview"
        size = '600x300'
        result_url = f"{street_view_url}?size={size}&location={lat},{lng}&key={api_key}"
        # print(result_url)

        return result_url # 返回图片的链接


if __name__ == '__main__':
    demo_test = google_map()

    type_list = ['tourist_attraction', 'restaurant', 'park', 'shopping_mall',
                 'bakery', 'cafe', 'clothing_store', 'drugstore', 'university']

    type = type_list[0]  # 设置为可以选择的逻辑

    place = '香港西九龙' #可以给用户填写

    demo_test.place_info(place,type)
    # demo_test.get_location_map(place)
    # demo_test.get_location_photo(place)