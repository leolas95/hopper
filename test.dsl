suspect = target "person" with "red" "shirt", "blue" "trousers", "green" "hat"
lobby = zone "lobby"
cam1 = camera number: 2

; esto es un comentario
track suspect inzone cam1 from cam1 incr person_counter

when person_counter > 5 do alert("asdasd:")
