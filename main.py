from datetime import datetime, timedelta

from data_manager import DataManager
from flight_search import FlightSearch
from notification_manager import NotificationManager

data_manager = DataManager()
sheet_data = data_manager.get_destination_data()
flight_search = FlightSearch()
notification_manager = NotificationManager()

ORIGIN_CITY_IATA = "LON"

print(sheet_data)

if sheet_data[0]["iataCode"] == "":
    for row in sheet_data:
        row["iataCode"] = flight_search.get_destination_code(row["city"])
    data_manager.destination_data = sheet_data
    data_manager.update_destination_codes()

tomorrow = datetime.now() + timedelta(days=1)
six_month_from_today = datetime.now() + timedelta(days=(6 * 30))

for destination in sheet_data:
    flight = flight_search.check_flights(
        ORIGIN_CITY_IATA,
        destination["iataCode"],
        from_time=tomorrow,
        to_time=six_month_from_today,
        max_stopovers=0
    )
    try:
        if flight.price < destination["lowestPrice"]:
            link_text = f"https://www.google.co.uk/flights?hl=en#flt={ORIGIN_CITY_IATA}.{flight.destination_city}.{flight.out_date}*{flight.destination_city}.{ORIGIN_CITY_IATA}.{flight.return_date}"
            if flight.stop_overs > 0:
                message_text =  f"Low price alert! Only £{flight.price} to fly from {flight.origin_city}-{flight.origin_airport} to {flight.destination_city}-{flight.destination_airport}, from {flight.out_date} to {flight.return_date}.\nFlight has a stopover, via {flight.via_city}.\n{link_text}"
            else:
                message_text = f"Low price alert! Only £{flight.price} to fly from {flight.origin_city}-{flight.origin_airport} to {flight.destination_city}-{flight.destination_airport}, from {flight.out_date} to {flight.return_date}.\n{link_text}"
            print("Send SMS\n", message_text)
            notification_manager.send_email(message_text)
            notification_manager.send_sms(
                message=message_text
            )
    except AttributeError:
        print("No flights with one (3) or zero stopover")
        continue
