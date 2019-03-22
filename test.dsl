suspect = "person" with "red" "shirt"
corsa = "vehicle" with "blue" "body"
zone = "lobby"
threshold = 3

track suspect inzone zone incr person_counter
track corsa

when person_counter > threshold do alert("esto es una alerta", "123", "asdasd")