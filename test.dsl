suspect = "person" with "red" "shirt"
corsa = "vehicle" with "blue" "body"
zone = "lobby"
threshold = 3
camera1 = camera number: 0
camera2 = camera ip: 192.168.2.2
camera3 = camera name: "camera1"
camera4 = camera number: 0
camera5 = camera number: 1
camera6 = camera number: 3
camera6 = camera ip: 192.123.108.20

detect activity "running" inzone "lobby" from camera1, camera2

track suspect inzone "lobby", "hall1" from camera1, camera2, camera3 incr person_counter
track corsa

when person_counter > threshold do alert("esto es una alerta", "123", "asdasd")

on activity "running" do alert("asd")