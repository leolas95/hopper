cam1 = camera name: "room"
suspect = "person" with "red" "shirt", "blue" "trousers", "green" "hat"
zona = "lobby"

detect activity "running" in zona from cam1
detect activity "talking"

track suspect in "room" 
track min = 3 "vehicle" with "blue" "color" in zona incr vehicle_counter

on activity "running" do alert()

when 2 > 6 do f()