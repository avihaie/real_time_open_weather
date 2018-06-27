"""
User can retrieve a selected city weather report with relevant current weather
attributes as temperature ,humidity, wind , pressure & clouds statistics

Weather Data Library using data from https://openweathermap.org.

Access current weather data for any location on Earth including over 200,000
cities!

Current weather is frequently updated based on global models and data from more
than 40,000 weather stations
"""
import argparse
import urllib.request
import xml.dom.minidom

SERVER_NAME = "http://api.openweathermap.org"
DATA_PATH = "/data/2.5/weather?q="
CITY_FILE_NAME = "weather.xml"

city_weather_dict = {}
unit_conversion_dict = {
    "fahrenheit": "imperial", "celsius": "metric", "kelvin": ""
}


class WeatherException(Exception):
    pass


class CityWeather:
    """
    Class the represents real time city weather

    Args:
    """
    def __init__(self, city_name="paris", units="celsius", api_key=None):
        self.__city_name = city_name
        self.__units = units
        self.__api_key = api_key
        self.mode = 'xml'

    @property
    def city_name(self):
        return self.__city_name

    @city_name.setter
    def city_name(self, val):
        if type(val) is not str:
            raise WeatherException(
                "city name inserted is not of string type, please enter only"
                " a string and if the city name is more than one word "
                "separated by space"
            )

        self.__city_name = val

    @property
    def units(self):
        return self.__units

    @units.setter
    def units(self, val):
        for k in unit_conversion_dict:
            if val != k:
                raise WeatherException(
                    "Wrong value is set for temperature units, enter only %s"
                    % unit_conversion_dict.keys()
                )
        self.__units = val

    @property
    def api_key(self):
        return self.__api_key

    @api_key.setter
    def api_key(self, val):
        if val:
            self.api_key = val
        else:
            raise WeatherException(
                "No value was entered to api_key.\nPlease enter a valid key "
                "after signing up the openweathermap site, see help at:\n"
                "https://openweathermap.org/appid"
            )

    def create_city_weather_data_file(self):
        """
        Retrieve weather info from openweathermap site and a create a file with
        retrieved info
        """
        api_units = unit_conversion_dict[self.units]
        urlh = urllib.request.urlopen(
            SERVER_NAME + DATA_PATH + self.city_name + "&appid=" + self.api_key
            + "&mode=" + self.mode + "&units=" + api_units
        )
        xml_data = urlh.read()

        try:
            with open(CITY_FILE_NAME, mode='wb') as file:
                file.write(xml_data)
        except WeatherException as e:
            print("File operations failed with error: %s" % e)

    def update_city_weather_dict(self):
        """
        Update city_weather dictionary with relevant parse weather attributes
        taken from the xml data file retrieved from the
        """
        self.create_city_weather_data_file()
        try:
            document = xml.dom.minidom.parse(CITY_FILE_NAME)
        except WeatherException as e:
            print(
                "Parsing data file %s failed with error: %s" % (
                    CITY_FILE_NAME, e
                )
            )

        node_current = document.getElementsByTagName("current")[0]
        node_temp = node_current.getElementsByTagName("temperature")
        node_wind = node_current.getElementsByTagName("wind")
        node_humidity = node_current.getElementsByTagName("humidity")
        node_pressure = node_current.getElementsByTagName("pressure")
        node_clouds = node_current.getElementsByTagName("clouds")
        temperature_val = node_temp[0].getAttribute("value")
        api_temp_unit = node_temp[0].getAttribute("unit")
        if api_temp_unit == "metric":
            temp_unit = [k for k, v in unit_conversion_dict.items() if
                         v == api_temp_unit][0]
        else:
            temp_unit = api_temp_unit
        humidity_val = node_humidity[0].getAttribute("value")
        humidity_unit = node_humidity[0].getAttribute("unit")
        wind_val = node_wind[0].getElementsByTagName("speed")[0].getAttribute(
            "value"
        )
        wind_desc = node_wind[0].getElementsByTagName("speed")[0].getAttribute(
            "name"
        )
        clouds_val = node_clouds[0].getAttribute("value")
        clouds_desc = node_clouds[0].getAttribute("name")
        pressure_val = node_pressure[0].getAttribute("value")
        pressure_unit = node_pressure[0].getAttribute("unit")

        city_weather_dict[self.city_name] = {
            'temperature': {
                'temperature_val': temperature_val, 'temp_unit': temp_unit
            },
            'humidity': {
                'humidity_val': humidity_val, 'humidity_unit': humidity_unit
            },
            'wind': {'wind_val': wind_val, 'wind_desc': wind_desc},
            'pressure': {
                'pressure_val': pressure_val, 'pressure_unit': pressure_unit
            },
            'clouds': {'clouds_val': clouds_val, 'clouds_desc': clouds_desc},
        }

    def print_city_weather_report(self):
        """
        Print current city weather report with relevant weather attributes as
        Temperature ,humidity, wind , pressure & clouds statsistics
        """
        city_name = self.city_name
        print(
            "Weather report for %s:\n"
            "Temperature is at %s %s\n"
            "Humidity is %s%s\n"
            "Wind is at %s speed meaning %s\n"
            "Air pressure is %s %s\n"
            "Clouds coverage is %s%% meaning %s\n" % (
                city_name,
                city_weather_dict[city_name]['temperature']['temperature_val'],
                city_weather_dict[city_name]['temperature']['temp_unit'],
                city_weather_dict[city_name]['humidity']['humidity_val'],
                city_weather_dict[city_name]['humidity']['humidity_unit'],
                city_weather_dict[city_name]['wind']['wind_val'],
                city_weather_dict[city_name]['wind']['wind_desc'].lower(),
                city_weather_dict[city_name]['pressure']['pressure_val'],
                city_weather_dict[city_name]['pressure']['pressure_unit'],
                city_weather_dict[city_name]['clouds']['clouds_val'],
                city_weather_dict[city_name]['clouds']['clouds_desc'].lower(),
            )
        )


def run(city_name, units, api_key):
    """
    Create weather object and provide current city weather report object
    This function should be used when imported from another module
    For running locally use the main function
    """
    weather_obj = CityWeather(
        city_name=city_name, units=units, api_key=api_key
    )
    weather_obj.update_city_weather_dict()
    weather_obj.print_city_weather_report()


def main():
    """
    Create weather current city weather report - running script directly
    This function should be used for running the script directly(not imported)

    Example:
    python3 /path/to/script/current_city_weather.py
    "tel aviv" celsius 0e0ab2271488dc844f64ead7184b53fc
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "city_name", help="city name in small letters", default="tel aviv"
    )
    parser.add_argument(
        "temp_units",
        help="temperature units kelvin or celsius or fahrenheit",
        default="tel aviv", choices=["kelvin", "celsius", "fahrenheit"]
    )
    parser.add_argument(
        "api_key", help="api_key you get when signing in to the openweathermap"
                        " site"
    )

    args = parser.parse_args()
    city_name, temp_units, api_key = args.city_name, args.temp_units, args.api_key

    ob = CityWeather(city_name=city_name, units=temp_units, api_key=api_key)
    ob.update_city_weather_dict()
    ob.print_city_weather_report()

if __name__ == '__main__':
    main()
