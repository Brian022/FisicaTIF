import pygame
import math
import numpy as np
import typer
import logging

COLORES = [
    (217, 237, 146),
    (93, 115, 126),
    (30, 96, 145),
    (62, 63, 63),
    (143, 45, 86),
    (116, 0, 184),
    (56, 4, 14),
]

class Cuerpo:
    def __init__(
        self, x, y, masa, velocidad, color, factor_rebote, ancho_pantalla, alto_pantalla
    ):
        self.x = x
        self.y = y
        self.masa = masa
        self.radio = int(math.sqrt(masa) * 2)
        self.vx, self.vy = velocidad
        self.color = color
        self.trazo = []
        self.factor_rebote = factor_rebote
        self.ancho_pantalla = ancho_pantalla
        self.alto_pantalla = alto_pantalla

    def calcular_fuerza_gravitatoria(self, cuerpos: list, g: float):
        fuerza = (0, 0)
        for cuerpo in cuerpos:
            if cuerpo != self:
                fuerza += calcular_fuerza_gravitacional(self, cuerpo, g)
        fuerza_x, fuerza_y = sumar_tuplas(fuerza)
        self.actualizar(fuerza_x, fuerza_y)

    def actualizar(self, fuerza_x: float, fuerza_y: float):
        ax = fuerza_x / self.masa
        ay = fuerza_y / self.masa
        self.vx += ax
        self.vy += ay
        self.x += self.vx
        self.y += self.vy
        self.verificar_limites()
        self.actualizar_trazo()

    def actualizar_trazo(self):
        self.trazo.append((self.x, self.y))
        if len(self.trazo) == 100:
            self.trazo.pop(0)

    def verificar_limites(self):
        if self.y < 0:
            self.y = 0
            self.vy *= -self.factor_rebote
        elif self.y > self.alto_pantalla:
            self.y = self.alto_pantalla
            self.vy *= -self.factor_rebote
        if self.x < 0:
            self.x = 0
            self.vx *= -self.factor_rebote
        elif self.x > self.ancho_pantalla:
            self.x = self.ancho_pantalla
            self.vx *= -self.factor_rebote

    def dibujar(self, pantalla):
        for punto in self.trazo:
            pygame.draw.circle(pantalla, self.color, punto, 1)
        pygame.draw.circle(pantalla, self.color, (int(self.x), int(self.y)), self.radio)


def calcular_fuerza_gravitacional(p1: Cuerpo, p2: Cuerpo, g: float) -> tuple:
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    distancia = max(1, math.sqrt(dx**2 + dy**2))
    if distancia < 40:
        return (0, 0)
    fuerza = (g * p1.masa * p2.masa) / (distancia**2)
    angulo = math.atan2(dy, dx)
    fuerza_x = fuerza * math.cos(angulo)
    fuerza_y = fuerza * math.sin(angulo)
    return (fuerza_x, fuerza_y)


def sumar_tuplas(tupla: tuple) -> tuple:
    pares = 0
    impares = 0
    for i in range(len(tupla)):
        if i % 2 == 0:
            pares += tupla[i]
        else:
            impares += tupla[i]
    return (pares, impares)


def main(
    ancho: int = typer.Option(800, help="Ancho de la pantalla"),
    alto: int = typer.Option(600, help="Alto de la pantalla"),
    max_cuerpos: int = typer.Option(
        10, help="Número máximo de cuerpos en la simulación."
    ),
    factor_rebote: float = typer.Option(
        0.5, help="Factor de rebote para los límites de la pantalla."
    ),
    masa: int = typer.Option(10, help="Masa de los cuerpos."),
    g: int = typer.Option(9.8, help="Constante gravitacional."),
    fps: int = typer.Option(60, help="FPS."),
):
    pygame.init()
    pantalla = pygame.display.set_mode((ancho, alto))
    reloj = pygame.time.Clock()

    lado = 200
    x = np.sqrt(lado**2 - (lado / 2) ** 2)
    x_inicial = ancho / 2 - lado / 2
    y_inicial = 400

    cuerpo1 = Cuerpo(
        x_inicial,
        y_inicial,
        masa=masa,
        velocidad=(0.1, 0.1),
        color=(116, 148, 196),
        factor_rebote=factor_rebote,
        alto_pantalla=alto,
        ancho_pantalla=ancho,
    )
    cuerpo2 = Cuerpo(
        (x_inicial + (x_inicial + lado)) / 2,
        y_inicial - x,
        masa=masa,
        velocidad=(-0.1, 0.1),
        color=(106, 77, 97),
        factor_rebote=factor_rebote,
        alto_pantalla=alto,
        ancho_pantalla=ancho,
    )
    cuerpo3 = Cuerpo(
        x_inicial + lado,
        y_inicial,
        masa=masa,
        velocidad=(0.1, -0.1),
        color=(195, 212, 7),
        factor_rebote=factor_rebote,
        alto_pantalla=alto,
        ancho_pantalla=ancho,
    )
    cuerpos = [cuerpo1, cuerpo2, cuerpo3]

    corriendo = True
    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if len(cuerpos) < max_cuerpos:
                    raton = pygame.mouse.get_pos()
                    cuerpos.append(
                        Cuerpo(
                            raton[0],
                            raton[1],
                            masa=masa,
                            velocidad=(0.1, 0.1),
                            color=COLORES[len(cuerpos) - 3],
                            factor_rebote=factor_rebote,
                            alto_pantalla=alto,
                            ancho_pantalla=ancho,
                        )
                    )
                else:
                    logging.warning("Máximo de cuerpos!")

        pantalla.fill((0, 0, 0))

        for cuerpo in cuerpos:
            cuerpo.calcular_fuerza_gravitatoria(cuerpos, g=g)
            cuerpo.dibujar(pantalla)

        pygame.display.update()
        reloj.tick(fps)

    pygame.quit()

if __name__ == "__main__":
    typer.run(main)
