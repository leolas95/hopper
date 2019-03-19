cam1 = camera name: "room"
suspect = "person" with "red" "shirt", "blue" "trousers", "green" "hat"
zona = "lobby"
vehicle_threshold = 4

detect activity "running" in zona from cam1
detect activity "talking"

track suspect in "room" 
track min = 3 "vehicle" with "blue" "color" in zona incr vehicle_counter

on activity "running" do alert()

when vehicle_counter > vehicle_threshold do alert()