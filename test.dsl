suspect = "person" with "red" "shirt"
corsa = "vehicle" with "blue" "body"
zone = "lobby"
threshold = 3
camera1 = camera number: 123
camera2 = camera ip: 192.168.5.5
camera3 = camera name: "asd"
camera4 = camera number: 2
camera5 = camera number: 4
camera6 = camera number: 6
camera6 = camera ip: 192.123.108.20

detect activity "running" inzone "hall1"

track suspect inzone "lobby", "hall2" from camera1, camera2, camera3 incr person_counter
track corsa

when person_counter > threshold do alert("esto es una alerta", "123", "asdasd")

on activity "running" do alert("asd")