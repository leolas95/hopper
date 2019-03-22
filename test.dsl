suspect = "person" with "red" "shirt"
zone = "lobby"
threshold = 3

track suspect inzone zone incr person_counter

when person_counter > threshold do alert("esto es una alerta")