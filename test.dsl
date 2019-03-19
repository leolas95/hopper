cam1 = camera name: "room"
suspect = "person" with "red" "shirt", "blue" "trousers", "green" "hat"
zona = "lobby"

detect activity "running" in zona from cam1
detect activity "talking"

track suspect in "room"
track "vehicle" with "blue" "color" in zona

on activity "running" do alert()

when cam1 > 1 do f()