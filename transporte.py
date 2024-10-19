import sys

ARCHIVO_PARTES = sys.argv[1]


def main():

    # leerArchivoTareas(ARCHIVO_TAREAS)
    # leerArchivoGanancias(ARCHIVO_GANANCIAS)

    rutas = [
        ("A", "B"),
        ("A", "D"),
        ("A", "E"),
        ("B", "C"),
        ("C", "D"),
        ("C", "E"),
        ("D", "E"),
    ]

    nodos = extraerNodos(rutas)

    idPorNodos = {nodo: i + 1 for i, nodo in enumerate(nodos)}

    idNodoOrigen = 0
    idNodoDestino = len(nodos) + 1
    idPorNodos["origen"] = idNodoOrigen
    idPorNodos["destino"] = idNodoDestino

    aristas = generarAristasBidireccionales(rutas, idPorNodos)
    aristas.append((idPorNodos["origen"], idPorNodos["B"], len(nodos)))

    aristas.append((idPorNodos["A"], idPorNodos["destino"], len(nodos)))
    max_flow = fordFulkerson(idPorNodos.values(), aristas, idNodoOrigen, idNodoDestino)
    # considerar si esto da cero es porque no encontró camino
    print("El flujo máximo es:", max_flow)


# ======================= LECTURA ARCHIVOS =======================


def leerArchivoPartes(nombreArchivo):
    lista_partes = []

    # with open(nombreArchivo, 'r') as archivo:
    #     for linea in archivo:
    #         (x1, y, x2) = map(int, linea.strip().split(','))
    #         lista_partes.append((x1, y, x2))

    return lista_partes


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


# ======================= FORD - FULKERSON =======================


def fordFulkerson(nodes, edges, source, sink):
    n = len(nodes)

    # Inicializamos el flujo como una matriz n x n de ceros
    flow = [[0] * n for _ in range(n)]

    # Creamos el grafo residual basado en las aristas originales
    residual_graph = createResidualGraph(n, edges, flow)

    # Inicializamos el flujo máximo
    max_flow = 0

    # Mientras haya un camino s-t en el grafo residual
    while True:
        # Buscar un camino de aumento P en el grafo residual
        parent = DFS(residual_graph, source, sink, n)

        # Si no hay más caminos, salimos del bucle
        if parent[sink] == -1:
            break

        # Encontrar el flujo máximo que puede pasar por el camino
        # (cuello de botella)
        path_flow = float("Inf")
        v = sink
        while v != source:
            u = parent[v]
            path_flow = min(path_flow, residual_graph[u][v])
            v = u

        # Actualizamos el flujo en el camino P
        updateFlow(flow, residual_graph, parent, path_flow, source, sink)

        # Sumar el flujo encontrado al flujo máximo
        max_flow += path_flow

    return max_flow


def createResidualGraph(n, edges, flow):
    # Inicializamos el grafo residual como una matriz n x n de ceros
    residual_graph = [[0] * n for _ in range(n)]

    # Por cada arista original (u, v, capacidad), creamos las
    # aristas del grafo residual
    for u, v, capacity in edges:
        residual_graph[u][v] = capacity  # Capacidad hacia adelante

    return residual_graph


def updateFlow(flow, residual_graph, parent, path_flow, source, sink):
    # Recorremos el camino de aumento y actualizamos
    # el flujo y el grafo residual
    v = sink
    while v != source:
        u = parent[v]
        # Aumentamos el flujo en la arista hacia adelante
        flow[u][v] += path_flow
        # Disminuimos el flujo en la arista hacia atrás (reencauzamos flujo)
        flow[v][u] -= path_flow

        # Actualizamos el grafo residual

        # Reducimos la capacidad hacia adelante
        residual_graph[u][v] -= path_flow
        # Aumentamos la capacidad hacia atrás
        residual_graph[v][u] += path_flow

        v = u


def DFS(graph, source, sink, n):
    # DFS para encontrar un camino s-t en el grafo residual
    stack = [source]
    visited = [-1] * n  # Lista que guarda el padre de cada nodo en el camino
    visited[source] = source

    while stack:
        u = stack.pop()

        for v in range(n):
            # Si no ha sido visitado y tiene capacidad
            if visited[v] == -1 and graph[u][v] > 0:
                visited[v] = u
                if v == sink:
                    return visited
                stack.append(v)

    return visited


if __name__ == "__main__":
    main()
