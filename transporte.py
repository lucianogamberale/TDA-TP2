import sys

ARCHIVO_RUTAS = sys.argv[1]

NO_VISITADO = -1

ARISTA_NO_VISITADA = ""
ARISTA_ORIGEN = "origin"
ARISTA_FORWARD = "forward"
ARISTA_BACKWARD = "backward"


def main():

    rutas = leerArchivoRutas(ARCHIVO_RUTAS)

    minNumeroRutas = minimoNumeroRutasQueGeneranDesconexion(rutas)
    print(
        "Minimo numero de rutas que al cortarlas provoque desconexion:", minNumeroRutas
    )


# ======================= LECTURA ARCHIVOS =======================


def leerArchivoRutas(nombreArchivo):
    rutas = []

    with open(nombreArchivo, "r") as archivo:
        for linea in archivo:
            # Elimina espacios en blanco y saltos de línea
            linea = linea.strip()
            # Divide la línea por la coma y crea una tupla
            origen, destino = linea.split(",")
            rutas.append((origen, destino))

    return rutas


# ======================= FUNCIÓN PRINCIPAL =======================


def minimoNumeroRutasQueGeneranDesconexion(rutas):

    nodos = extraerNodos(rutas)

    mapeoNodoConId = {nodo: i + 1 for i, nodo in enumerate(nodos)}
    idOrigen = 0
    idDestino = len(nodos) + 1
    mapeoNodoConId["origen"] = idOrigen
    mapeoNodoConId["destino"] = idDestino
    idNodos = mapeoNodoConId.values()

    aristas = generarAristasBidireccionales(rutas, mapeoNodoConId)

    flujosMaximos = []

    for nodo, id in mapeoNodoConId.items():
        if id == idOrigen or id == idDestino:
            continue
        if id == 1:
            aristas.append((idOrigen, id, len(nodos)))
            continue

        aristas.append((mapeoNodoConId[nodo], idDestino, len(nodos)))
        flujoMaximo = fordFulkerson(idNodos, aristas, idOrigen, idDestino)
        aristas.pop()

        flujosMaximos.append(flujoMaximo)

    return min(flujosMaximos)


# ======================= REDUCCION =======================


def extraerNodos(rutas):
    nodos = set()

    for u, v in rutas:
        nodos.add(u)
        nodos.add(v)

    return list(nodos)


def generarAristasBidireccionales(rutas, mapeoNodoConId):
    aristas = []

    for u, v in rutas:
        aristas.append((mapeoNodoConId[u], mapeoNodoConId[v], 1))
        aristas.append((mapeoNodoConId[v], mapeoNodoConId[u], 1))

    return aristas


# ======================= FORD - FULKERSON PUBLICO =======================


def fordFulkerson(nodos, aristas, origen, destino):

    flujoMaximo = 0
    cantidadNodos = len(nodos)
    flujo = [[0] * cantidadNodos for _ in range(cantidadNodos)]

    # Creamos dos matrices para el grafo residual:
    # - una para las aristas hacia adelante
    # - otra para las aristas hacia atrás
    residualForward, residualBackward = crearGrafoResidual(cantidadNodos, aristas)

    # Buscar un camino de aumento P en el grafo residual utilizando DFS
    caminoDFS = DFS(residualForward, residualBackward, origen, destino, cantidadNodos)

    # Mientras haya un camino s-t en el grafo residual
    while caminoDFS[destino][0] != NO_VISITADO:

        # Busco cuello de botella en el camino de aumento
        cuelloBotella = calcularCuelloBotella(
            caminoDFS, residualForward, residualBackward, origen, destino
        )

        # Actualizo flujo y grafos residuales con camino de aumento
        actualizarFlujo(
            flujo,
            residualForward,
            residualBackward,
            caminoDFS,
            cuelloBotella,
            origen,
            destino,
        )

        flujoMaximo += cuelloBotella

        # Busco camino de aumento P en el grafo residual utilizando DFS
        caminoDFS = DFS(
            residualForward, residualBackward, origen, destino, cantidadNodos
        )

    return flujoMaximo


# ======================= FORD - FULKERSON PRIVADO =======================


def crearGrafoResidual(cantidadNodos, aristas):
    # Inicializamos dos grafos residuales: uno para las aristas hacia adelante
    # y otro para las aristas hacia atrás
    residualForward = [[0] * cantidadNodos for _ in range(cantidadNodos)]
    residualBackward = [[0] * cantidadNodos for _ in range(cantidadNodos)]

    for u, v, capacidad in aristas:
        # Capacidad hacia adelante
        residualForward[u][v] = capacidad
        # Capacidad hacia atrás inicialmente es 0
        residualBackward[v][u] = 0

    return residualForward, residualBackward


def calcularCuelloBotella(
    caminoDFS, residualForward, residualBackward, origen, destino
):
    cuelloBotella = float("Inf")
    v = destino
    while v != origen:
        u = caminoDFS[v][0]
        if caminoDFS[v][1] == ARISTA_FORWARD:
            cuelloBotella = min(cuelloBotella, residualForward[u][v])
        elif caminoDFS[v][1] == ARISTA_BACKWARD:
            cuelloBotella = min(cuelloBotella, residualBackward[u][v])
        v = u

    return cuelloBotella


def actualizarFlujo(
    flujo, residualForward, residualBackward, caminoDFS, cuelloBotella, origen, destino
):
    v = destino
    while v != origen:
        u = caminoDFS[v][0]

        if caminoDFS[v][1] == ARISTA_FORWARD:
            flujo[u][v] += cuelloBotella
            residualForward[u][v] -= cuelloBotella
            residualBackward[v][u] += cuelloBotella
        elif caminoDFS[v][1] == ARISTA_BACKWARD:
            flujo[v][u] -= cuelloBotella
            residualForward[v][u] += cuelloBotella
            residualBackward[u][v] -= cuelloBotella

        v = u


# ======================= DFS =======================


def DFS(residualForward, residualBackward, origen, destino, cantidadNodos):

    nodosVisitados = [(NO_VISITADO, ARISTA_NO_VISITADA)] * cantidadNodos
    nodosVisitados[origen] = (origen, ARISTA_ORIGEN)

    return DFSRecursivo(
        residualForward,
        residualBackward,
        origen,
        destino,
        cantidadNodos,
        nodosVisitados,
    )


def DFSRecursivo(
    residualForward,
    residualBackward,
    nodoActual,
    destino,
    cantidadNodos,
    nodosVisitados,
):

    # si llegué al sink, retorno el camino
    if nodoActual == destino:
        return nodosVisitados

    for i in range(cantidadNodos):
        # si el nodo no fue visitado y hay camino hacia adelante
        if nodosVisitados[i][0] == NO_VISITADO and residualForward[nodoActual][i] > 0:
            nodosVisitados[i] = (nodoActual, ARISTA_FORWARD)

            # busco un camino desde el nodo i en adelante
            result = DFSRecursivo(
                residualForward,
                residualBackward,
                i,
                destino,
                cantidadNodos,
                nodosVisitados,
            )
            # si llegué al destino, tengo un camino y lo retorno
            if result[destino][0] != NO_VISITADO:
                return nodosVisitados

            nodosVisitados[i] = (NO_VISITADO, ARISTA_NO_VISITADA)

        # si el nodo no fue visitado y hay camino hacia atras
        if nodosVisitados[i][0] == NO_VISITADO and residualBackward[nodoActual][i] > 0:
            nodosVisitados[i] = (nodoActual, ARISTA_BACKWARD)

            # busco un camino desde el nodo i en adelante
            result = DFSRecursivo(
                residualForward,
                residualBackward,
                i,
                destino,
                cantidadNodos,
                nodosVisitados,
            )
            # si llegué al destino, tengo un camino y lo retorno
            if result[destino][0] != NO_VISITADO:
                return nodosVisitados

            nodosVisitados[i] = (NO_VISITADO, ARISTA_NO_VISITADA)

    return nodosVisitados


if __name__ == "__main__":
    main()
