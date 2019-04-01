suspect = target "person" with "red" "shirt"
lobby = zone "lobby"
cam1 = camera number: 2

; esto es un comentario
track suspect inzone lobby from cam1 incr person-counter

when person-counter >= 1 do alert("Alerta")