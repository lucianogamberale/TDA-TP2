import sys

columnas = int(sys.argv[1])
filas = int(sys.argv[2])
archivo = sys.argv[3]

def leer_matriz(archivo, columnas, filas):
    matriz = []
    with open(archivo, 'r') as f:
        for i, linea in enumerate(f):
            if i >= columnas:
                break
            valores = list(map(int, linea.strip().split(',')))
            matriz.append(valores[:filas])
    return matriz


def main():
    matriz = leer_matriz(archivo, filas, columnas)
    n = len(matriz)
    m = len(matriz[0])
    optimos = [[0] * m for _ in range(n)]
    recorridos = [[[] for _ in range(m)] for _ in range(n)]
    maximo_global = 0
    recorrido_maximo = []

    for i in range(n):
        for j in range(m):
            maximo_local = matriz[i][j]
            recorrido_local = [(i, j)]

            for k in range(i, -1, -1):
                for l in range(j, -1, -1):
                    if matriz[i][j] < matriz[k][l]:
                        nuevo_valor = optimos[k][l] + matriz[i][j]
                        if nuevo_valor > maximo_local:
                            maximo_local = nuevo_valor
                            recorrido_local = recorridos[k][l] + [(i, j)]


            optimos[i][j] = maximo_local
            recorridos[i][j] = recorrido_local
            if maximo_local >= maximo_global:
                maximo_global = maximo_local
                recorrido_maximo = recorrido_local

    print("Manzanas:", recorrido_maximo)
    print("Ganancia máxima:", maximo_global)

if __name__ == "__main__":
    main()
